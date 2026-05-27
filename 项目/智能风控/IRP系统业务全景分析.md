# IRP 智能风控决策平台 — 系统业务全景分析

## 一、系统总览

IRP (Intelligent Risk Platform) 是百融云创的智能风控决策平台，采用微服务架构，共 8 个独立服务。

**注意**：Owl 内部包含三个独立进程——`owl-execution`（流程编排）、`seagull-web`（变量/指标/算子计算引擎）、`owl_py`（Python表达式服务）。IRP真正执行计算的是 seagull-web 而非 owl-execution。

```
tamer (网关 :8090)
  → peregrine (策略管理 :8082)
    → owl-execution (LiteFlow流程编排 :9391)
      → seagull-web (指标计算引擎, Feign调用)
        → owl_py (Python表达式 :80, Feign调用)
    → raptor (规则引擎 :9034, 含URule Rete内核)
  ← nest (用户中心 :9389)
  ← kestrel (运营管理)
  ← merlin (模型管理, Feign调algo-service)
    → algo-service (机器学习算法, Python FastAPI+Celery)
```

**技术栈**：
- **Java服务**（6个）：Java 17 + Spring Boot 3.3.4 + Spring Cloud 2023.0.3 + Maven + MySQL + Redis + RocketMQ + Nacos + LiteFlow 2.12.4
- **Python服务**（1个）：Python 3.10+ FastAPI + Celery + scikit-learn 1.7.2 + XGBoost 3.1.1 + Optuna 4.5.0
- **Python脚本服务**（1个）：owl_py Flask, 被seagull-web Feign调用

**Merlin ↔ Algo 集成**：Merlin 通过 `PythonExecuteFeign`（Feign HTTP）调用 algo-service 的 REST API 进行数据质检、特征工程、模型训练、任务管理。algo-service 是纯Python服务，独立部署，通过 Celery 异步执行训练任务。

---

## 二、Raptor — URule规则引擎内核

Raptor的执行分为**编排层**和**规则引擎内核层**。编排层在前一版本已详述，本章聚焦URule内核的Rete算法实现。

所有URule内核代码位于 **`raptor-plugin-sdk`** 模块，非外部jar包。

### 2.1 编译管线：XML → KnowledgeBase → KnowledgePackage → KnowledgeSession

**文件**: `raptor-plugin-sdk/src/main/java/tech/raptor/ruleengine/rule/builder/KnowledgeBuilder.java`

```java
// 第64-139行 newBuildKnowledgeBase(content, ruleName, resourceLibrary)
public KnowledgeBase[] newBuildKnowledgeBase(String content, String ruleName, ResourceLibrary lib) {
    // 第70行: dom4j解析GZIP解压后的XML
    Element root = this.parseResource(content);

    // 第73-108行: 根据XML根节点名称识别规则类型
    // "rule-set" → RuleSetParser
    // "decision-table" → DecisionTable → DecisionTableRulesBuilder
    // "decision-tree" → DecisionTree → DecisionTreeRulesBuilder
    // "crosstab" → CrosstabDefinition → CrosstabRulesBuilder
    // "scorecard" → ScoreRule

    // 第112-127行: runType="1"(顺序执行) → 每个规则独立编译为一个KnowledgeBase
    // 否则所有规则编译为一个KnowledgeBase

    // 第124/132行: ★ Rete网络构建 ★
    this.reteBuilder.buildRete(rules, lib);

    // 第131行: LoopRule特殊处理 — 嵌套构建子KnowledgePackageWrapper
    this.buildLoopRules(resource, lib);
}
```

编译管线依赖（第43-58行注入的Builder链）：
- `DecisionTableRulesBuilder` — 决策表行列→规则列表转换
- `DecisionTreeRulesBuilder` — 决策树节点→if-else规则转换
- `ScriptDecisionTableRulesBuilder` — 脚本决策表
- `CrosstabRulesBuilder` — 交叉表→规则转换
- `DSLRuleSetBuilder` — DSL规则
- `ReteBuilder` — **核心**：规则条件→Rete网络编译
- `RulesRebuilder` — 规则引用重建（变量名、bean方法解析）

### 2.2 Rete网络构建（ReteBuilder）

**文件**: `raptor-plugin-sdk/src/main/java/tech/raptor/ruleengine/rule/model/rete/builder/ReteBuilder.java`

```java
// 第35-65行 buildRete(List<Rule>, ResourceLibrary)
public Rete buildRete(List<Rule> rules, ResourceLibrary lib) {
    // 第42-50行: 按activationGroup(互斥组)分组
    // 同一互斥组内规则互斥——只触发优先级最高的那个
    Map<String, List<Rule>> activationRulesMap = new HashMap<>();

    // 第53-58行: 无LHS条件的规则 → noLhsRules(无条件触发)
    // 第60行: 有条件的规则 → buildBranch()构建Rete分支
    // 第63行: 互斥组 → buildActivationRetesMap()为每个规则构建独立Rete网络
}
```

**`buildBranch()`** — 单条规则的Rete分支构建（第110-129行）：
```
Rule.criteria (条件树根节点)
  → ObjectTypeNode    按对象类型过滤（如"java.util.HashMap"）
  → CriteriaNode      条件节点（如 age > 18）
  → JunctionNode      AND/OR 组合节点
  → TerminalNode      终止节点，持有Rule引用
```

**Rete算法的核心价值**：多个规则共享相同的条件节点。当fact进入网络，条件只评估一次，多个规则可复用评估结果。例如100条规则都检查 `age > 18`，Rete网络中只有一个CriteriaNode处理这个条件。

**`buildActivationRetesMap()`**（第68-108行）：互斥组内规则按 `salience`（优先级）排序，每个规则独立拥有一个Rete网络。运行时，高优先级规则先匹配——匹配成功则跳过组内其他规则。

### 2.3 KnowledgeBase → KnowledgePackage → KnowledgeSession 三层懒加载

**KnowledgeBase** (`raptor-plugin-sdk/.../builder/KnowledgeBase.java` 第43-82行):
```java
// 轻量包装器，持有Rete + 无LHS规则 + Flow映射
// getKnowledgePackage() — 双重检查锁定懒加载
//   首次调用时创建KnowledgePackageImpl:
//     注入Rete + 无LHS规则 + Flow映射
//     buildWithElseRules() — 遍历Rete找有otherwise的规则，建elseRulesMap
//     提取VariableCategory → parameters类型映射
```

**KnowledgePackageImpl** (`raptor-plugin-sdk/.../runtime/KnowledgePackageImpl.java`):
```java
private Rete rete;                              // Rete网络
private Map<String, FlowDefinition> flowMap;    // 规则流
private Map<String, String> parameters;         // 参数类型映射
private Map<Rule, Rule> elseRulesMap;           // else规则映射(原规则→else规则)
private List<Rule> noLhsRules;                  // 无条件规则
// newReteInstance() → 运行时刻复制Rete网络
```

**KnowledgeSessionImpl** (`raptor-plugin-sdk/.../runtime/KnowledgeSessionImpl.java` 第92-127行):
构造函数：
1. 遍历KnowledgePackage[] → 初始化ReteInstance列表
2. 按参数类型映射赋初始值（Integer→0, Long→0L, List→new ArrayList等）
3. `initContext()` → ContextImpl + EvaluationContextImpl + FlowContextImpl 三层上下文
4. 创建Agenda → 三层RuleBox

### 2.4 fireRules() — 规则执行的完整链路

```java
// KnowledgeSessionImpl 第167行 → 第235行 execute()
RuleExecutionResponse execute(Map<String, Object> parameters) {
    // === 阶段1: 参数准备（第236-252行）===
    // 遍历factMaps，将参数值注入parameterMap
    // 如果参数在facts中不存在，自动插入

    // === 阶段2: Rete网络匹配（第253-257行）===
    for (Object fact : facts) {
        evaluationRete(fact);
        // → reteInstance.enter(evaluationContext, fact)
        //   → ObjectTypeNode 类型匹配
        //   → CriteriaNode 条件求值
        //   → JunctionNode 组合判断
        //   → TerminalNode 创建Activation
        //     → 根据group类型分配到Agenda的对应RuleBox
    }

    // === 阶段3: Agenda执行（第258-260行）===
    agenda.buildElseRules();   // 为有otherwise的未触发规则创建else规则
    agenda.buildNoLhsRules();  // 加入无条件规则
    agenda.execute(filter, max);

    // === 阶段4: 返回结果（第260-264行）===
    return new ExecutionResponseImpl(
        firedRules,      // 触发规则列表
        matchedRules,    // 匹配规则列表
        actionValues,    // 动作返回值列表
        criteriaList,    // 评估过的条件列表
        duration         // 执行耗时
    );
}
```

### 2.5 Agenda — 三层RuleBox优先级体系

**文件**: `raptor-plugin-sdk/.../runtime/agenda/Agenda.java`

```
优先级 高 → 低:
┌────────────────────────────────────┐
│ 1. AgendaGroupRuleBox              │  agenda-group 分组的规则
│    按组名分组，同组内优先级排序      │
├────────────────────────────────────┤
│ 2. ActivationGroupRuleBox          │  activation-group 互斥组
│    组内只触发优先级最高的一个规则    │
├────────────────────────────────────┤
│ 3. ActivationRuleBox               │  无分组的普通规则
│    按salience排序执行              │
└────────────────────────────────────┘
```

### 2.6 ActivationImpl.execute() — 单条规则的最终执行

**文件**: `raptor-plugin-sdk/.../runtime/agenda/ActivationImpl.java`

```java
// 第35-102行
public void execute(Context context, List<RuleInfo> executedRules, List<ActionValue> actionValues) {
    // 1. 触发 ActivationBeforeFiredEvent 事件
    // 2. 检查 enabled、effectiveDate(生效日期)、expiresDate(失效日期)
    // 3. ★按规则类型分发:
    if (rule instanceof LoopRule) {
        loopRule.execute(context, ...);  // 嵌套循环，创建子Session
    } else if (rule instanceof ScoreRule) {
        scoreRule.execute(context, ...);  // 评分累加
    } else {
        for (Action action : rhs.getActions()) {  // 遍历RHS的动作列表
            action.execute(context, ...);
        }
    }
    // 4. 触发 ActivationAfterFiredEvent 事件
}
```

### 2.7 四大Action类型

| Action | 类 | 执行方式 |
|--------|---|---------|
| **ExecuteMethodAction** | `ExecuteMethodAction.java` | `ApplicationContext.getBean()` → 反射调用 |
| **VariableAssignAction** | `VariableAssignAction.java` | 计算右侧值 → 写入左侧变量(支持嵌套属性) |
| ConsolePrintAction | 控制台输出 | 调试用 |
| ExecuteCommonFunctionAction | 通用函数 | 内置函数调用 |

**ExecuteMethodAction** (第37-124行):
```java
// Spring容器中获取Bean → 按方法名+参数类型反射匹配 → 调用
Object bean = applicationContext.getBean(springBean.getId());
Method method = classMatch(bean.getClass(), methodName, parameters);
// @ActionId注解的值作为返回值的标识
// 特殊处理 getOuterDataAction → 数据懒加载
```

**VariableAssignAction** (第42-87行):
```java
// 右侧: 计算值(字面量/变量引用/命名引用)
// 左侧: 按variableCategory找目标对象 → 写入属性
// Enum特殊处理: 反射获取枚举类 → Enum.valueOf()解析
```

**BuiltInActionLibraryBuilder** (第113-146行): 扫描Spring容器中所有 `@ActionBean` 注解的Bean → 提取 `@ActionMethod` 标注的方法 → 构建 SpringBean→Method→Parameter 树 → 注入 ResourceLibrary.actionLibraries。

### 2.8 五种规则类型的XML格式与编译

所有规则存储在 `t_rule_details.ruleExecuteData`，经 GZIP+Base64 编码。解压后为XML，按根节点分流到不同的Parser+Builder。

#### 规则集 (rule-set)

```xml
<rule-set runType="0|1">  <!-- 0=全部执行, 1=顺序执行(支持中断) -->
  <variable-library>...</variable-library>
  <rule name="rule1" salience="10" enabled="true"
        effective-date="2024-01-01" expires-date="2025-01-01">
    <if>
      <and>
        <atom left-var-category="param" left-var="age" op="GreaterThen">
          <value content="18" type="Integer"/>
        </atom>
      </and>
    </if>
    <then>
      <var-assign var-category="result" var="adult">
        <value content="true" type="Boolean"/>
      </var-assign>
    </then>
    <otherwise>
      <var-assign var-category="result" var="adult">
        <value content="false" type="Boolean"/>
      </var-assign>
    </otherwise>
  </rule>
</rule-set>
```

**顺序执行中断**：`runType="1"` 时每个规则独立编译为一个KnowledgeBase，SetDecisionPlugin遍历执行，中断条件（5个条件AND）满足则break。

#### 决策表 (decision-table)

```xml
<decision-table>
  <row num="1"/><row num="2"/>
  <column num="1" type="Criteria">       <!-- 条件列 -->
    <condition op="GreaterThen">
      <left var="score"/><value content="90" type="Integer"/>
    </condition>
  </column>
  <column num="2" type="Assignment">     <!-- 赋值列 -->
    <left var="grade"/><value content="A" type="String"/>
  </column>
  <cell row="1" col="1"/><cell row="1" col="2"/>
</decision-table>
```

每行 → 一条规则。条件列 → LHS的AND组合。赋值列 → RHS的VariableAssignAction。

#### 决策树 (decision-tree)

```xml
<decision-tree>
  <variable-tree-node var="score">
    <condition-tree-node op="GreaterThen">
      <value content="60"/>
      <action-tree-node>                   <!-- 真分支: score>60 -->
        <var-assign><value content="pass"/></var-assign>
      </action-tree-node>
      <condition-tree-node op="GreaterThen">  <!-- 假分支嵌套判断 -->
        <value content="90"/>
        <action-tree-node>...</action-tree-node>
      </condition-tree-node>
    </condition-tree-node>
  </variable-tree-node>
</decision-tree>
```

遍历树节点 → 生成if-else嵌套规则。

#### 评分卡 (scorecard)

```xml
<scorecard scoring-type="custom" base-score="600">
  <attribute-row>                     <!-- 评分维度 -->
    <condition-row>
      <joint junction-type="and">
        <condition op="Equal"><value content="男"/></condition>
      </joint>
    </condition-row>
  </attribute-row>
  <cell row="1" col="1" var="gender"/>
  <cell row="1" col="2"><value content="男"/></cell>     <!-- 变量 -->
  <cell row="1" col="3"><value content="50"/></cell>     <!-- 条件 -->
  <custom-col name="weight">                             <!-- 分值 -->
    <cell><value content="1.5"/></cell>
  </custom-col>
</scorecard>
```

每行 → 一个ScoreRule。执行时累加命中行的分值。ScoreRule.execute() 递归处理子规则。

#### 交叉表 (crosstab)

二维决策表。`CrosstabDefinition` 定义行列交叉的条件和结果。`CrosstabRulesBuilder` 将交叉点条件组合转为规则列表。

### 2.9 完整调用链（从HTTP到Action执行）

```
POST /api/openapi/rpc/strategy/execute
  → CoreStrategyService.strategyExecute()   [第88-196行]
    → buildInputParam() 扁平Map→树形VarCategory
    → CoreRuleRunService.testRun()           [第88-123行]
      → cacheService.getChainId() → LiteFlow Chain
      → cacheService.buildAllRuleCodedLibrary() → ResourceLibrary
      → ChainService.execFlowForResp()       [第67-83行]
        → LiteflowRuleContext构建
        → flowExecutor.execute2Resp() → LiteFlow
          → GeneraComponent.process()        [第34-73行]
            → ComponentServiceFactory.getService()
            → SetDecisionPlugin.nodeExec()   [第48-99行]
              → PackageServletHandler.getFactsMap() → Facts
              → KnowledgeSessionFactory.newKnowledgeSession()
              → session.fireRules(parameters)
                → evaluationRete(fact) → Rete匹配
                → Agenda收集 → 三层RuleBox执行
                → ActivationImpl.execute()
                  → ExecuteMethodAction / VariableAssignAction
              → handResultVariableValue() → 写回值
              → 检查interrupted → break?
            → setUruleResultContextBean() → 写回Context
        → getRuleOutputContent() → 最终结果
```

### 2.10 PackageServletHandler — Facts与参数管理

**文件**: `raptor-plugin-sdk/.../console/servlet/respackage/PackageServletHandler.java`

```java
// getFactsMap() [第116-135行]: VariableCategory→Facts
//   PARAM_CATEGORY("param") → HashMap<String,Object>
//   其他类别 → GeneralEntity(clazz)
//   所有变量 → buildObject()设置默认值

// getParameters() [第137-147行]: Facts→Parameters
//   HashMap类型 → 直接作为parameters返回
//   其他类型 → 插入session

// handResultVariableValue() [第149-162行]: 执行后写回
//   Map类型 → session.getParameters()
//   GeneralEntity → getter获取属性值

// buildObject() [第299-337行]: 支持嵌套属性(点号分割)
//   处理List/Set/Map/Enum的默认值初始化
//   Enum: 反射获取字段类型 → Enum.valueOf()解析
```

### 2.11 核心难点

1. **Rete网络编译**：XML规则→条件树→ObjectTypeNode→CriteriaNode→JunctionNode→TerminalNode有向图。共享条件节点是Rete算法的核心优化。
2. **三层Agenda优先级**：AgendaGroupBox>ActivationGroupBox>ActivationBox。互斥组内规则各有独立Rete网络确保互斥。
3. **顺序执行中断**：`runType="1"` 每规则独立KnowledgeBase，五条件AND判断中断（含`firedRules.size()==1`且非else）。
4. **决策表/树→规则统一管道**：表格/树形→RulesBuilder转换为规则列表→统一走Rete编译。
5. **Action反射执行**：Spring容器+反射调用Bean方法，自动参数类型匹配，`@ActionId`注解。
6. **缓存一致性**：Caffeine本地+RocketMQ广播+synchronized锁，最终一致性。

---

## 三、Owl — 执行引擎与指标计算系统

### 3.1 核心概念：三个独立进程

Owl不是单一服务，内部有**三个独立进程**：

```
owl-execution (:9391)               seagull-web                    owl_py (:80)
┌──────────────────────┐    Feign   ┌──────────────────────┐ Feign ┌──────────────┐
│ LiteFlow流程编排      │ ────────→ │ 变量/指标存储与计算   │ ────→ │ Python表达式  │
│ - BizNode(调外部API)  │           │ - QueryDataService    │       │ - /cal 路由   │
│ - DerivedNode(调计算) │           │ - Aviator/Janino引擎  │       │ - AST安全检查  │
│ - Mapping/Switch/...  │           │ - 算子注册管理        │       │ - exec()执行   │
└──────────────────────┘           └──────────────────────┘       └──────────────┘
```

**关键纠正**：指标计算不在 owl-execution 中。owl-execution 中的 `DataDerivedNode` 通过 Feign 远程调用 seagull-web，seagull-web 才是真正执行表达式计算的服务。Aviator和Janino表达式在 seagull-web 本地执行（进程内），Python表达式通过 Feign 调用 owl_py。

### 3.2 指标存储：`t_vc_var_base_def` 表

**实体类**: `seagull-domain/src/main/java/tech/seagull/domain/entities/VcVarBaseDef.java`

这是指标系统的**核心存储表**，每个指标对应一条记录：

| 字段 | 类型 | 含义 | 示例值 |
|------|------|------|--------|
| `graphNodeCode` | String | 所属图节点编码（逻辑分组） | `"risk_score_node"` |
| `graphCode` | String | 所属图谱编码 | `"anti_fraud"` |
| `varName` | String | 变量/指标名 | `"total_risk_score"` |
| `varDesc` | String | 描述 | `"综合风险评分"` |
| **`varLang`** | Integer | **执行引擎**：0=Aviator, 1=Python, 2=Janino | `0` |
| **`varContent`** | String | **表达式/脚本源码** | `"round(score_a*0.3+score_b*0.7,2)"` |
| **`varParam`** | String | **输入参数JSON数组** | `[{"paramCode":"score_a","jsonPath":"$.data.credit_score","graphNodeCode":"biz_credit"}]` |
| `dataType` | String | 结果数据类型 | `"Double"` |
| `defaultValue` | String | 默认值 | `"0.0"` |
| `categoryCode` | String | 分类编码 | `"risk_metrics"` |
| `status` | Integer | 状态 | `5`（启用） |

**`varParam` 字段详解**（反序列化为 `List<VcVarParamVo>`）：
```json
[{
  "paramCode": "score_a",              // 参数编码（对应varContent表达式中的变量名）
  "jsonPath": "$.data.credit_score",   // 从上下文JSON中提取值的JSONPath
  "paramType": 0,                       // 参数类型
  "graphNodeCode": "biz_credit"        // 数据来源节点
}]
```

`varContent` 中的变量名必须与 `varParam` 中定义的 `paramCode` 对应。执行时，引擎先按 `varParam` 从上下文提取所有参数值，再执行表达式。

### 3.3 指标计算的完整数据流

```
POST /owl-execution/service {serviceCode:"xxx", serviceParam:{...}}
  ↓
OwlDataExecuteServiceImpl.callDataServiceExec()
  → DataServicePubEntity → publishType=METRIC
  → owlFlowMgrService.flowExecute() → LiteFlow动态构建Chain
  ↓
LiteFlow节点依次执行:
  │
  ├─[1] StartNode: 初始化
  │
  ├─[2] BizNode: ★调用外部API获取原始数据★
  │   nodeData: {"bizCode":"credit_api","bizType":"1-api",
  │              "inputParamMappingList":[
  │                {"paramCode":"idCard","sourceJsonPath":"$.serviceParam.idCard"}]}
  │   执行: HTTP → 征信系统 → {credit_score:720, loan_count:5, ...}
  │   结果 → contextBean["biz_credit"]
  │
  ├─[3] DataDerivedNode: ★指标计算发生在此★
  │   nodeData: {"relationNodes":[{"graphNodeCode":"risk_metrics_node"}]}
  │   执行: dataDerivationExec(graphNodeCode, contextBean)
  │     → SeagullFeign.varQueryCommonTest() [Feign HTTP]
  │     → POST /api/seagull/varquery/execute/test
  │     → {logicalKey:"risk_metrics_node", serviceParam: contextBean(整个上下文)}
  │     → seagull-web: QueryDataService.varQuery()
  │       → 查 t_vc_var_base_def WHERE graphNodeCode='risk_metrics_node' AND status=5
  │       → 得到指标列表 + varParam + varContent
  │       → 从serviceParam中按JSONPath提取各指标的依赖数据
  │       → Dispatcher→WorkerPool→Aviator/Janino/Python 批量执行
  │       → 返回 {total_risk_score:685.5, debt_ratio:0.35, ...}
  │   结果 → contextBean["risk_metrics_node"]
  │
  ├─[4] DataMappingNode: JSONPath映射重组
  │
  ├─[5] DataServiceOutput: 类型转换(Integer/Double/Date/BigDecimal)
  │
  └─[6] EndNode: 收集contextBean → 返回
```

**关键设计原则**：BizNode获取原始数据，DataDerivedNode计算派生指标。两者通过 contextBean 共享数据，下游节点可消费所有上游节点的输出。

### 3.4 指标计算引擎（seagull-web 内部）

#### 3.4.1 varQuery() 入口

**文件**: `seagull-web/src/main/java/tech/seagull/query/service/QueryDataService.java`

```java
// 第82-101行
public Map<String, Object> varQuery(RequestContentBase request) {
    String logicalKey = request.getLogicalKey();  // = graphNodeCode

    // 1. 验证VarDomain状态(ENABLE/DISABLE)
    // 2. 获取该graphNodeCode下所有变量定义(从缓存)
    List<VcVarBaseDefVo> varDefs = vcVarBaseDefCache.get(logicalKey);

    // 3. 按varLang分流
    if (varDefs.get(0).getVarLang() == LangEnum.PYTHON) {
        return getDataByPythonExecute(request);  // → owl_py远程
    } else {
        return getDataByLocalExecute(request);   // → Aviator/Janino本地
    }
}
```

**`getDataByLocalExecute()`**（第129-169行）：
```java
// 1. 用VarJsonPathCache中预缓存的JSONPath从serviceParam提取数据
JSONObject context = new JSONObject(request.getServiceParam());
Map<String, Map<String, JSONPath>> pathMap = varJsonPathCache.get(logicalKey);
// 遍历所有JSONPath → 从context提取值 → 构建 env Map

// 2. 分发执行
Map<String, VarExecuteResult> results = dispatcher.dispatch(varDefs, env, langEnum);
```

#### 3.4.2 Dispatcher → WorkerPool → Worker 执行链

```
Dispatcher.dispatch()               [第21-24行]
  → WorkerPool.dispatch()           [第26-59行]
    → LocalWorkerSelector 选Worker
    → 每200个变量一批分组(批量并行)
    → SpringWorker.process()        [第116-126行]
      → if Janino: janinoWorker.queryResultBySqlLogic()
      → else:      aviatorWorker.queryResultBySqlLogic()
```

每200个变量一批，实现**批量并行处理**，避免大量变量时单线程瓶颈。

#### 3.4.3 AviatorWorker — Aviator引擎执行细节

**文件**: `seagull-web/src/main/java/tech/seagull/query/actuator/worker/AviatorWorker.java`

```java
// 第27-87行
for (VcVarBaseDefVo var : batch) {
    // 1. 检查varParam定义的所有参数在env中是否都有值 — 缺任一参数则跳过
    if (anyParamMissing(var.getVarParams(), env)) continue;

    // 2. 缓存键 = varId + "##" + updateTime (版本变化自动失效)
    String cacheKey = var.getId() + "##" + var.getUpdateTime();

    // 3. 从Aviator实例查已缓存的编译后Expression
    Expression compiled = aviatorEvaluatorInstance.getCachedExpression(cacheKey);

    // 4. 缓存未命中 → 编译varContent → 缓存
    if (compiled == null) {
        compiled = aviatorEvaluatorInstance.compile(cacheKey, var.getVarContent(), true);
    }

    // 5. 用env作为变量环境执行表达式
    Object result = compiled.execute(env);
    // 6. 包装结果: VarExecuteResult(varName, result, costTime)
}
```

**AviatorEvaluatorUtils** (`seagull-web/src/main/java/tech/seagull/util/AviatorEvaluatorUtils.java`)：
- 维护 `AviatorEvaluatorInstance[]` 实例池，数量 = `CPU核数/15 + 1`
- 轮询调度（AtomicLong计数器，每次 `getAndIncrement() % len`）
- 所有自定义函数注册到**每个**实例

#### 3.4.4 JaninoWorker — Janino引擎执行细节（性能最高）

**文件**: `seagull-web/src/main/java/tech/seagull/util/JaninoScriptCompiler.java`

```java
// 第78-110行: executeWithJanino()
// 1. 缓存键 = varName + "_" + updateTime
// 2. compile() → doCompile() (第143-213行):
//    a. generateJavaCode() — ★自动生成完整Java类源码★
//    b. SimpleCompiler.cook(javaCode) — Janino编译为字节码
//    c. compiler.getClassLoader().loadClass(className) — 加载类
//    d. 反射获取 static Object execute(Map params) 方法
// 3. compiled.getExecuteMethod().invoke(null, params) — 反射调用
```

**generateJavaCode()** 生成的类（第218-278行）：
```java
import java.util.*;
import tech.seagull.util.AviatorFunctionCaller;

public class Script_totalRiskScore {
    public static Object execute(Map params) {
        String PA01 = (String) params.get("PA01");
        Double PD02 = (Double) params.get("PD02");

        // 用户varContent经文法转换后的Java代码:
        //   Aviator字符串 'xxx' → Java "xxx"
        //   Aviator List<Type> → Java List
        //   Aviator def var → Java Object var
        //   Aviator var as Type → Java (Type) var
        return AviatorFunctionCaller.call("round",
            Double.parseDouble(PA01) * 0.3 + PD02 * 0.7, 2);
    }
}
```

**关键**：Janino代码中通过 `AviatorFunctionCaller` 调用Aviator自定义函数，实现了**函数库跨引擎统一**。

#### 3.4.5 Python引擎 — 跨进程远程执行

调用链：`seagull-web → PythonServiceFeign.cal() → HTTP → owl_py Flask /cal`

**Python端** (`owl_py/server.py` 第70-138行)：
```python
@app.route('/cal', methods=['POST'])
def cal():
    # 1. 从MySQL查询Python变量定义
    #    WHERE graph_node_code=code AND tenant_code=tenant AND status=5 AND var_lang=1
    rows = get_var_defs(graph_code, tenant_code)

    # 2. 遍历每个变量
    for row in rows:
        # 3. 根据varParam从serviceParam提取参数值
        params = {}
        for p in json.loads(row.var_param):
            params[p['paramCode']] = jsonpath_extract(service_param, p['jsonPath'])

        # 4. AST静态分析 + exec()动态执行
        result = PythonExpressionExecutor.exec_with_dict_param(row.var_content, params)
        result_data[row.var_name] = result
```

#### 3.4.6 三引擎性能对比

**单表达式执行耗时**（源码级推算）：

| 引擎 | 首次执行 | 缓存命中（纯算术） | 慢查询阈值（源码） |
|------|---------|------------------|------------------|
| **Janino** | 5-50ms（JVM字节码编译） | 0.01-0.5ms | compile>50ms \|\| exec>50ms → warn |
| **Aviator** | 0.5-5ms（含编译缓存写入） | 0.1-2ms | 单变量>20ms → error |
| **Python (owl_py)** | 10-50ms（HTTP往返）+ 1-10ms（exec） | 无缓存（每次HTTP调用） | — |

**关键纠正：Janino 的性能加速边界**

Janino 不会自动将 Aviator 函数调用转换为 Java 代码。`convertToJavaCode()` 只做简单文本替换（单引号→双引号、`def`→`Object`、去泛型），**函数调用需要用户显式写为 Java 兼容格式**。当表达式中引用算子时，Janino 生成的代码通过 `AviatorFunctionCaller` 桥接回 Aviator 引擎执行：

```java
// Aviator 表达式（用户直接写）
round(score_a * 0.3 + score_b * 0.7, 2)

// Janino 对应的写法（需显式调用桥接器）
AviatorFunctionCaller.call("round", params, score_a * 0.3 + score_b * 0.7, 2)
```

**`AviatorFunctionCaller` 的隐藏性能陷阱**（`AviatorFunctionCaller.java` 第101-116行）：
- `formatArg()` 将数值直接内联为字面量拼入表达式字符串：`"round(0.85,2)"`
- 不同记录的计算结果不同 → 不同表达式字符串 → **Aviator 表达式缓存全部 miss**
- 每次调用都触发 Aviator 的 parse → compile → execute 完整链路

```java
// AviatorFunctionCaller.java
private static String formatArg(Object arg, Map<String, Object> env) {
    if (arg instanceof Number || arg instanceof Boolean) {
        return String.valueOf(arg);  // ← 数值被内联为字面量！每次不同值 = 新表达式
    }
}
```

**Janino 实际加速效果取决于表达式中的算子调用密度**：

```
纯算术（无算子）
  score_a * 0.3 + score_b * 0.7
  → 100% JVM 字节码，JIT 全内联
  → ≈100x 加速 ✓

少量算子调用
  round(score_a * 0.3 + score_b * 0.7, 2)
  → 算术部分走字节码 + round() 走 AviatorFunctionCaller
  → 5-10x 加速

中等算子调用
  round(date.Day(startDate, endDate) / 30, 2)
  → 嵌套 AviatorFunctionCaller，每次不同日期 → 不同表达式字符串
  → 2-3x 加速

重度算子调用
  全是算子嵌套，几乎没有纯算术
  → 等价回退到 Aviator 解释执行，外加桥接开销
  → ≈1x（无优势）
```

**引擎原理差异**：

| 维度 | Aviator | Janino | Python |
|------|---------|--------|--------|
| 执行方式 | 解释执行 AST | 纯计算→字节码，算子→桥接回Aviator | `exec()` 动态执行 |
| 函数库 | 原生注册，直接查表调用 | `AviatorFunctionCaller` 桥接（回 Aviator） | 独立实现 |
| 进程边界 | seagull-web 进程内 | seagull-web 进程内 | **跨进程 HTTP 调用** |
| JIT 优化 | 否 | **仅纯计算部分**（热点被 C2 编译） | 否（CPython 无 JIT） |
| 算子调用性能 | 注册表O(1)查找→直接方法调用 | 桥接→拼字符串→Aviator重编译→执行 | HTTP往返→exec() |

**并发吞吐模型**（`SpringWorker.java`）：

```
线程池: core=max=32, queue=300000, CallerRunsPolicy
分批: 每200个变量一个批次, 所有批次提交到线程池并发执行

N 个变量 → ceil(N/200) 个批次 → 32线程并发消费
```

**典型请求性能估算**（纯表达式计算，不含 DB 查询和网络往返）：

| 变量数 | Aviator | Janino（低算子密度） | Janino（高算子密度） | Python |
|--------|---------|---------------------|---------------------|--------|
| 200（1批次） | 20-400ms | **2-100ms** | ≈20-400ms | 25-100ms |
| 1000（5批次） | 100-400ms | **10-100ms** | ≈100-400ms | 125-500ms |
| 5000（25批次） | 500-2000ms | **50-500ms** | ≈500-2000ms | 625-2500ms |

**端到端链路耗时**（含 DB 查询 + Feign 往返）：

```
owl-execution DataDerivedNode
  → Feign(1-3ms) → seagull-web QueryDataService
    → 查 t_vc_var_base_def (1-2ms)
      → SpringWorker 并发执行
        → 返回结果
```

| 环节 | 耗时 |
|------|------|
| owl-execution → seagull-web Feign 往返 | 2-6ms |
| DB 查变量定义 | 1-2ms |
| 表达式计算（Janino低算子密度, 200变量） | 2-100ms |
| 表达式计算（Janino高算子密度, 200变量） | 20-400ms |
| **端到端总计（最佳情况）** | **5-110ms** |
| **端到端总计（高算子密度）** | **25-410ms** |

**选型建议**：

| 场景 | 推荐引擎 | 理由 |
|------|---------|------|
| 纯算术表达式（比率/加权/四则运算） | **Janino** | 100% 走 JVM 字节码，真正 100x 加速 |
| 少量算子 + 大量算术 | **Janino** | 热点路径在算术部分，仍有 5-10x 收益 |
| 重度算子嵌套（日期处理、集合运算） | **Aviator** | Janino 桥接回退无收益，Aviator 直接调用更简洁 |
| 频繁调参/AB测试（变量频繁改） | **Aviator** | 解释执行对变更友好，无 Janino 重编译成本 |
| 需要 Python 生态（numpy/pandas） | Python | 仅有此场景使用，接受网络延迟代价 |

**真正的瓶颈不在表达式引擎**：owl-execution 的 BizNode 调用外部 API 获取原始数据通常需要 50-500ms，远超表达式计算本身。seagull-web 的纯计算能力远高于当前业务负载，32 线程 + 300K 队列对于 CPU 密集型表达式计算是过剩配置，瓶颈在于上游数据获取。

### 3.5 算子系统

#### 3.5.1 算子的定义和存储

**实体类**: seagull-web中的 `FunctionEntity`，对应数据库函数表：

| 字段 | 含义 |
|------|------|
| `funcName` | 函数名，如 `date.Day(env,dateStr)` |
| `funcCode` | 全限定类名 |
| `funcDesc` | 描述 |
| `exeLan` | 执行语言（当前仅AVIATOR） |
| `returnType` | 返回类型 |
| `funcSourceCode` | SYSTEM（系统内置）/ CUSTOMER（用户自定义） |
| `function` | Java源代码字符串（用户自定义函数） |
| `params` | 参数定义JSON |

#### 3.5.2 算子的注册加载

**文件**: `seagull-web/src/main/java/tech/seagull/web/service/FunctionService.java`

```java
// 第309-336行: loadFunction() — 系统内置函数加载
// 1. 类路径扫描 tech/seagull/avitor/function/**/*.class
// 2. 查找 @FunctionDesc 注解的类(如 @FunctionDesc(name="date.Day", description="取日期天"))
// 3. 反射实例化为 BaseFunction 或 BaseVariadicFunction
// 4. AviatorEvaluatorUtils.addFunction() → 注册到所有Aviator实例

// 第392-417行: parse() — 用户自定义函数
// 1. 接收Java源码字符串
// 2. JavaStringCompiler 编译为字节码
// 3. 加载类 → 提取 call() 方法
// 4. 注册到Aviator + 元数据存入数据库
```

#### 3.5.3 预定义函数库（30+个函数）

**模块**: `seagull-function-avitor`

按类别组织在 `tech/seagull/avitor/function/` 下：

| 类别 | 函数 | 功能 |
|------|------|------|
| **date** | Year, Month, Day, Hour, Minute, Second, Millisecond | 日期提取 |
| **num** | Round, ThousandBit, ValueOf | 数值处理 |
| **table** | Sort, Select, Distinct, AddColumn | 表格操作 |
| **set** | Union, Intersect, Subtract, Disjunction, ContainsAny, IsEqual, IsSubSeq | 集合运算 |
| **json** | Flat, CastJsonArray | JSON处理 |
| **idCard** | Gender, Birthday, NativePlace, GetLast | 身份证信息提取 |
| **aggs** | Sum, Avg, Max, Min, Count | 聚合计算 |
| **array** | Sum, Avg, Max, Min, Count | 数组聚合 |
| **finance** | ContinuousMax, ContinuousTimes | 金融专用 |
| **sys** | Nvl, Decode | 空值处理/条件解码 |
| **operation** | And, Or | 逻辑运算 |

每个函数标注 `@FunctionDesc(name="category.FuncName", description="...")`，在Aviator和Janino中均可使用。

### 3.6 三种表达式引擎对比

| 维度 | Aviator | Janino | Python |
|------|---------|--------|--------|
| 执行位置 | seagull-web进程内 | seagull-web进程内 | owl_py独立进程 |
| 性能 | 中等（解释执行） | **最高**（编译为字节码） | 最慢（跨进程+Py解释） |
| 缓存键 | `id+updateTime` | `varName+updateTime` | MySQL查询缓存 |
| 自定义函数 | 直接注册到Aviator实例 | 通过AviatorFunctionCaller桥接 | 无(写Python代码) |
| 实例池 | CPU核数/15+1 轮询 | 无（编译类线程安全） | 无（Flask多worker） |
| 适用场景 | 简单表达式/条件 | 复杂计算逻辑 | 需Python生态 |

### 3.7 变量回溯完整机制

**文件**: `owl-baffle/src/main/java/tech/owl/baffle/service/back/VcVarBackService.java`（约2240行）

三种触发模式：
| 模式 | 触发 | 线程池 | 锁 |
|------|------|--------|-----|
| 手动 | API→CompletableFuture.runAsync() | core10/max10/queue200 | RedissonLock(backCode,15s) |
| 定时 | Quartz→VarBackConsumerListener→timeExecute() | core9/max40/queue12000 | 同上 |
| 重试 | 失败自动 | core20/max30/queue12000 | 同上 |

**BackEvent工厂模式**：`BackEventFactory` 通过 BeanPostProcessor 自动发现所有 `BackEvent` 实现，按 `VarBackTypeEnum` 路由到对应Handler。

**核心流程**（以 BackApiDataBaseEvent 为例）：

```
1. setInvokeResult(): 从BfVarBackDb读数据源配置
   → Freemarker处理SQL模板 → 增量查询(基于lastMaxId)
   → 字段映射(resultTransform) → List<VarBackExecuteInputDTO>

2. getExecuteResultVO(): 对每条数据并行执行
   → executionFeign.callDataServiceExecGzip() → owl-execution
   → LiteFlow: BizNode→DerivedNode→... → 指标计算结果

3. saveData():
   成功 → GZIP压缩 → BfVarBackBase.varContent
   失败 → BfVarBackFailDetail(inputJson + failureReason)
   状态 → BfVarBackHis
```

**安全措施**：ZIP压缩比>1000:1 拒绝（防zip bomb），批次size=10，RedissonLock按backCode粒度防重。

### 3.8 LiteFlow 节点 nodeData 格式汇总

| 节点 | nodeData JSON结构 |
|------|------------------|
| BizNode | `{"bizCode":"xxx","bizType":"1-api","inputParamMappingList":[{"paramCode":"x","sourceJsonPath":"$.x"}]}` |
| DerivedNode | `{"relationNodes":[{"graphNodeCode":"metrics_node","graphNodeName":"指标计算","graphNodeType":"DataServiceDerived"}]}` |
| MappingNode | `{"relationNodeMapping":[{"graphNodeCode":"xxx","relationBizList":[{"dataMappingList":{"$.old":"newField"}}]}]}` |
| SwitchNode | `{"switchNodeItemList":[{"contionList":[{"jsonPath":"$.x","op":1,"value":"y"}],"logicOp":1}]}` |

### 3.9 核心难点

1. **三进程分离架构**：owl-execution编排+sagull-web计算+owl_py Python，通过Feign串联。DerivedNode远程调用seagull-web获取指标结果。
2. **三种表达式引擎分层**：Aviator(CACHE+函数库)→Janino(编译为字节码最高性能)→Python(跨进程)。Janino通过AviatorFunctionCaller复用Aviator函数库。
3. **指标定义与算子分离**：指标存 `t_vc_var_base_def`（表达式+参数JSONPath），算子通过 `@FunctionDesc` 注册到Aviator实例池。运行时动态组合。
4. **批量并行执行**：每200个变量一批→WorkerPool分发→Aviator实例池轮询。实例数=CPU核数/15+1，经验值。
5. **变量回溯全链路**：BackEvent工厂→SQL增量拉取→Feign调owl-execution→LiteFlow→指标计算→GZIP压缩存储。RedissonLock防重。
6. **CustomThreadBuilder风险**：core2/max10/queue10/AbortPolicy，第23个并发即拒绝。

### 3.10 特征工程 — 变量推导系统（seagull-web）

Owl的特征工程（变量推导）核心在seagull-web，由变量模板、变量定义、推导域三层组成。

#### 3.10.1 概念分层

| 概念 | 表/实体 | 角色 |
|------|---------|------|
| **VarTemplate** (变量模板) | `t_vc_var_template` | 可复用的计算模板，定义因子参数+表达式骨架 |
| **VcVarBaseDef** (变量定义) | `t_vc_var_base_def` | 实际变量，含varContent(表达式) + varParam(JSONPath参数映射) |
| **VarDomain** (推导域) | `t_vc_var_domain` | 一组变量的计算域，storeType=3为基础推导 |
| **VcDomainSourcePub** | `t_vc_domain_source_pub` | 推导域→上游源节点映射 |
| **VcVarPoolBaseDef** | `t_vc_var_pool_base_def` | 预构建变量池，可batchInsert到推导域复用 |

#### 3.10.2 变量定义核心字段

**实体**: `seagull-domain/.../entities/VcVarBaseDef.java`  
**表**: `t_vc_var_base_def`

| 字段 | 说明 |
|------|------|
| `graphNodeCode` | 所属推导域编码(Domain code) |
| `graphCode` | 所属流程/图编码 |
| `varName` | 变量名 — 作为输出JSON的key |
| `varLang` | 执行语言: **0=Aviator, 1=Python, 2=Janino** |
| `varContent` | **表达式/脚本代码** |
| `varParam` | **JSON数组**，每个VcVarParamVo: `{paramCode, jsonPath, paramType, graphNodeCode}` |
| `status` | 生命周期: NEW → TEST_PASS → ENABLE |
| `defaultValue` | 计算失败时的回退值 |
| `templateCode` | 引用的模板编码 |

**varParam映射机制**: 每个参数通过`jsonPath`从上游节点(由`graphNodeCode`指定)的输出JSON中提取值，注入到表达式的`paramCode`变量中执行。

#### 3.10.3 变量生命周期

```
NEW (新建) → 编辑表达式/参数
  → testRun() 测试执行 → 成功 → TEST_PASS (测试通过)
    → enable() 启用 → ENABLE (生效中，可被执行)
      → disable() 禁用 → 回到 TEST_PASS

约束: enable()前必须 status=TEST_PASS，否则抛 ENABLE_VAR_NOT_TEST_PASS
```

#### 3.10.4 模板与因子

**VarTemplate** (`t_vc_var_template`): 定义可复用的表达式骨架。`templateConfig`为JSON，定义可配置的因子参数；`codeLogic`为表达式代码，含占位符。

**因子(VcFactors/VcFactorsItem)**: 模板中可配置的选择参数，通过`t_vc_var_template_ref_factors`关联。实例化模板时用户选择因子值，系统替换占位符生成最终的`varContent`。

#### 3.10.5 变量池复用机制

预构建变量库(`t_vc_var_pool_base_def`)中的变量可通过`VcVarBaseDefService.batchInsert()`导入到任意推导域：
```
POST /api/seagull/varbase/batchInsert {ids:[...], graphNodeCode, graphCode}
  → 复制 varContent/varParam/varLang 到目标域
  → 生成新Snowflake ID → insert到 t_vc_var_base_def
```

#### 3.10.6 推导域与源映射

**VarDomain** (`t_vc_var_domain`, storeType=3):
- 流程保存时(`OwlFlowMgrServiceImpl.flowSaveOrUpdate()`)遍历所有DataServiceDerived节点
- 为每个DerivedNode构建`DataDerivationData`(上游relationNodes列表)
- Feign批量发送到seagull-web `/api/seagull/vardomain/batchSave`

**VcDomainSourcePub** (`t_vc_domain_source_pub`):
- 记录推导域依赖的上游数据源节点
- `pubResult`字段: JSON定义上游输出字段结构
- 流程发布时(`enableOrDisable()`)调 `/api/seagull/vardomain/enable` 激活

#### 3.10.7 运行时执行全链路

```
LiteFlow DataDerivationNode.process()
  │
  ├─ 获取flow node data → 反序列化 DataDerivationData
  │   (relationNodes: 上游源节点列表)
  │
  ├─ dataDerivationExec()
  │   POST /api/seagull/varquery/execute
  │   body: {logicalKey=graphNodeCode, serviceParam=contextBean(上游所有节点输出)}
  │     │
  │     └─ seagull-web QueryDataService.varQuery(graphNodeCode)
  │         → 查 t_vc_var_base_def WHERE graphNodeCode AND status=ENABLE
  │         → Dispatcher → WorkerPool(200变量/批) → 按varLang分发:
  │             ├─ AviatorWorker: AviatorEvaluatorUtils.getNextInstance()
  │             │   └─ 从varParam提取JSONPath值→注入参数→execute(varContent)
  │             ├─ JaninoWorker: JaninoScriptCompiler.executeWithJanino()
  │             │   └─ 编译为字节码→执行(通过AviatorFunctionCaller桥接复用函数库)
  │             └─ PythonWorker(owl_py): HTTP /cal_single
  │                 └─ 查MySQL t_vc_var_base_def→exec_with_dict_param()
  │
  └─ 结果写入context: put(graphNodeCode, derivedResultMap)
       → 下游MappingNode/OutputNode通过graphNodeCode读取
```

#### 3.10.8 相关数据库表汇总

| 表 | 用途 | 服务库 |
|----|------|--------|
| `t_vc_var_base_def` | 变量/特征定义(表达式+参数映射) | seagull |
| `t_vc_var_domain` | 变量推导域(storeType=3) | seagull |
| `t_vc_domain_source_pub` | 域→源节点映射 | seagull |
| `t_vc_var_test` | 变量测试用例 | seagull |
| `t_vc_var_pool_base_def` | 预构建变量池 | seagull |
| `t_vc_var_template` | 变量模板 | seagull |
| `t_vc_var_template_ref_factors` | 模板→因子关联 | seagull |
| `t_vc_ref_function` | 变量引用的函数追踪 | seagull |
| `t_dc_flow_node` | 流程节点(nodeData含DataDerivationData) | owl |

#### 3.10.9 特征工程核心难点

1. **模板→变量→域三层抽象**: 模板定义骨架(因子参数化)→变量实例化(填充因子+参数)→域组织成计算单元。每层独立版本管理。
2. **跨语言引擎调度**: 同一域内混合Aviator/Janino/Python变量，WorkerPool按varLang路由到不同执行器。Python还需跨进程HTTP调用。
3. **JSONPath参数注入**: varParam定义每个参数从哪个上游节点的哪个JSON路径取值，执行时动态解析注入。
4. **变量池跨域复用**: 预构建变量导入新域时需重新映射graphNodeCode和graphCode，参数JSONPath可能与新域上游结构不兼容。

### 3.11 owl-execution 负载均衡与重试机制

owl-execution 是唯一内置多节点负载均衡的服务。`LoadBalanceNode` 提供三种策略，均支持失败后的递归重试。

#### 3.11.1 完整调用链路

```
LiteFlow 引擎
  └─ LoadBalanceNode.process()            ← 负载均衡层
       ├─ 策略选择（主备/权重/轮询）
       ├─ 节点选择 + 失败递归重试
       └─ executeBiz()                     ← API 调用层
            └─ OwlFlowExecServiceImpl.invokeAPi(inputParam, bizCode, online)
                 └─ OwlDataExecuteServiceImpl.callLocalDataServiceExec(dto)
                      └─ OwlExecBO.execute()  ← 树形并行执行
                           └─ runnable.apply() → HTTP 调用三方接口
```

**两层线程池**：

| 层级 | 池 | core | max | queue | 拒绝策略 |
|------|-----|------|-----|-------|---------|
| LiteFlow 节点并行 | CustomThreadBuilder | 2 | 10 | 10 | **AbortPolicy** |
| 单次 API 调用内部 | OwlExecBO.createExecutorService() | leafCnt | leafCnt | leafCnt | 默认(AbortPolicy) |

`OwlExecBO` 的线程池每次 API 调用临时创建，用完即销毁。leafCnt 是 BO 树中的叶子节点数——父节点并行执行后结果合并，因此需要 leafCnt 个线程。

**文件**: `owl-execution/src/main/java/tech/owl/execution/component/liteflow/node/LoadBalanceNode.java`

#### 3.11.2 三种策略统一的有效性判定

三个策略共用同一判定逻辑（`LoadBalanceNode.java:143-156, 283-306`）：

```java
// 成功条件: result != null && result 是合法 JSON && code ∈ {SUCCESS, SUCCESS_NO_DATA}
if (result != null && JSONUtil.isTypeJSON(result.toString())) {
    JSONObject json = JSON.parseObject(result.toString());
    if (json.containsKey("code") && (code == SUCCESS || code == SUCCESS_NO_DATA)) {
        return json;  // 成功
    }
}
// 否则递归重试下一个节点
```

失败定义：result 为 null、非 JSON、code 不存在、code 不是 SUCCESS/SUCCESS_NO_DATA。

#### 3.11.3 策略1 — 主备模式 (MAIN_STANDBY, type=1)

**严格优先级降级**（`LoadBalanceNode.java:250-281`）：

```java
private JSONObject primaryBackup(List<LoadBalanceData> nodes, Integer index, Map inputParam)
```

节点按 `isMaster` 降序排列（主节点在前，备节点在后）。采用递归算法：

```
index=0 试主节点
  ├─ 有效 → 返回结果
  └─ 无效 → primaryBackup(nodes, index+1, inputParam)
       ├─ index=1 试备节点1
       │    ├─ 有效 → 返回
       │    └─ 无效 → primaryBackup(nodes, index+2, ...)
       └─ ...直到 index >= nodes.size()
            → 返回 {"code":500, "message":"Failed to execute all main and standby"}
            → 外层转为 ServiceException 抛出
```

| 特性 | 说明 |
|------|------|
| 选择算法 | 严格优先级，主→备1→备2，不会跳过 |
| 重试范围 | 所有配置节点 |
| 分布式协调 | 无（本地决策） |
| 适用场景 | 主备部署，备机性能弱，仅在主机故障时使用 |

#### 3.11.4 策略2 — 权重模式 (WEIGHT, type=3)

**两阶段：加权随机选择 + 失败降级为轮询**（`LoadBalanceNode.java:91-128, 216-248`）：

**第一阶段 — 加权随机选择**：

```java
// ⚠️ 方法名为 weightedRoundRobin，但使用 SecureRandom 随机选择
SecureRandom sr = new SecureRandom();
int r = (int)(sr.nextDouble() * 100) + 1;      // 1~100
int pos = Math.abs(r % totalWeight);

// 按权重区间定位节点
int weightSum = 0;
for (int i = 0; i < nodes.size(); i++) {
    weightSum += weights.get(i);
    if (pos < weightSum) return nodes.get(i);
}
```

**关键事实**：名为 weightedRoundRobin，实际是加权随机（weighted random）。类中定义了 `AtomicInteger weightCounter` 但从未使用。短期内请求分布不一定符合权重比例。

**第二阶段 — 失败降级为轮询重试**：

```
权重随机选一个节点
  ├─ 成功 → 返回
  └─ 失败 → 排除该节点 → 剩余按权重降序排列 → 转入 roundRobin 重试
                ├─ 第1个成功 → 返回
                ├─ 第1个失败 → 第2个…
                └─ 全部失败 → ServiceException
```

| 特性 | 说明 |
|------|------|
| 选择算法 | 加权随机（非轮询），失败后转纯轮询 |
| 重试范围 | 排除失败节点后的剩余节点 |
| 分布式协调 | 无（本地 SecureRandom） |
| 适用场景 | 异构机器按性能比分配流量 |
| ⚠️ 注意 | 短时间窗口内不保证权重比例精确 |

#### 3.11.5 策略3 — 轮询模式 (ROTATION, type=2)

**Redis 分布式轮询**（`LoadBalanceNode.java:162-198`）：

```java
private JSONObject roundRobin(nodes, count, inputParam, graphCode) {
    if (count == nodes.size()) {
        return {"code":500, "message":"Rotation retries all failed"};  // 终止
    }

    // Redis 原子递增，多个 owl-execution 实例共享计数器
    Long increment = redisCacheClient.increment(
        "DsRoundRobin:" + graphCode, 1L);
    int curIndex = Math.abs(increment.intValue() % nodes.size());

    Object result = executeBiz(nodes.get(curIndex), inputParam);

    if (valid(result)) return wrapSuccess(result);
    return roundRobin(nodes, count + 1, inputParam, graphCode);  // 递归重试
}
```

| 特性 | 说明 |
|------|------|
| 选择算法 | Redis `INCR` 原子递增 + 取模，真正的分布式轮询 |
| 重试范围 | 所有配置节点（逐个尝试） |
| 分布式协调 | **有**（Redis key=`DsRoundRobin:{graphCode}`） |
| 适用场景 | 同构机器均匀分配流量 |
| 计数器 | 只增不减，永不重置。取模运算使其自然循环 |
| 全部失败 | 返回 500 JSON → 外层转抛 ServiceException |

#### 3.11.6 底层 invokeAPi — 无容错的薄弱环节

三个策略最终都通过 `executeBiz()` 调用 `OwlFlowExecServiceImpl.invokeAPi()`（`OwlFlowExecServiceImpl.java:29-48`）：

```java
public Object invokeAPi(inputParam, bizCode, online, logtrace, language) {
    DataServicePubEntity pub = dataServicePubService.queryServicePubCode(bizCode);
    OwlDataExecDTO dto = OwlDataExecDTO.builder()
        .input(inputParam).dataServicePubCode(bizCode).online(online).build();

    Object o = iOwlDataExecuteService.callLocalDataServiceExec(dto);

    if (o == null) {
        throw new BizException(UNKNOWN_ERROR, "invoke third api exception");
    }
    return o;
}
```

这一层**没有任何容错机制**：

| 缺失能力 | 现状 | 风险 |
|----------|------|------|
| **超时控制** | `OwlExecBO.execute()` → `CompletableFuture.supplyAsync()` → `future.get()` 无超时参数 | 三方 API 卡住时线程永久阻塞 |
| **重试** | null 直接抛 `BizException` | 一次性网络抖动导致整条链路失败 |
| **熔断** | 无状态记录 | 下游宕机时每次都照常调用，加重雪崩 |
| **默认值降级** | 无 | 无法在 API 不可用时使用缓存的旧值或静态默认值 |

`BizNode` 的判定逻辑同样简单（`BizNode.java:58-75`）：

```java
Integer[] successCodes = {ResultEnum.SUCCESS.getCode(), ResultEnum.SUCCESS_NO_DATA.getCode()};
if (!Arrays.asList(successCodes).contains(code)) {
    throw new ServiceException(jsonObject.get("message") + ",bizCode:" + bizCode);
}
```

只检查 code，无重试、无超时、无降级。

#### 3.11.7 策略对比总览

| 维度 | 主备 (type=1) | 权重 (type=3) | 轮询 (type=2) |
|------|:---:|:---:|:---:|
| 选择算法 | 严格优先级 | 加权随机 | Redis 分布式轮询 |
| 失败策略 | 顺序降级到备机 | 排除失败节点→转轮询 | 逐个轮询重试 |
| 重试范围 | 所有配置节点 | 排除失败节点后的剩余 | 所有配置节点 |
| 分布式协调 | 无 | 无 | 有(Redis INCR) |
| 全部失败 | ServiceException | ServiceException | 500 JSON→转异常 |
| 适用场景 | 主备部署 | 异构机器 | 同构集群 |

#### 3.11.8 三个深层问题

**1. 线程池 AbortPolicy + 小队列**

```
CustomThreadBuilder: core=2, max=10, queue=10, AbortPolicy
```

10 个线程全忙且队列 10 个满时，第 21 个任务直接抛 `RejectedExecutionException`。在高并发风控场景，LiteFlow 节点并行度高时此池极易打满。

**2. 权重策略名不副实**

`weightedRoundRobin` 每次 new `SecureRandom`，不维护任何状态。10 个请求权重 7:3，实际分布可能是 8:2 或 5:5——短期内不保证比例。对金融风控场景，可能导致某个三方渠道被意外压垮。

**3. 计数器永不归零且无上限保护**

`DsRoundRobin:{graphCode}` 的 Redis INCR 只增不减，虽然 Long 范围足够大，但没有监控手段感知异常流量。如果某个 graphCode 被异常高频调用，计数器增长速度会成为盲点。

#### 3.11.9 容错能力总结

LoadBalanceNode 的多节点负载均衡是 owl-execution **唯一的容错手段**。它的核心价值是：**"下游服务多实例部署时，选一个活着的"**。但没有解决"所有实例都慢或都出问题"的场景——后者需要熔断、降级、超时控制，这些在 owl-execution 中全部缺失。

```
容错层级对比:
  LoadBalanceNode:  ★★★☆☆  节点级重试，覆盖多实例故障
  invokeAPi:        ☆☆☆☆☆  零容错，无超时/无重试/无熔断
  OwlExecBO:        ★★☆☆☆  仅有线程池 AbortPolicy 兜底
```

### 4.1 双层变量架构

IRP的变量系统采用**双层架构**：peregrine负责变量管理+运行时校验+缓存，raptor负责变量持久化存储+查询。

```
peregrine (管理层)                    raptor (存储层)
┌─────────────────────────┐          ┌──────────────────────────┐
│ CommonVariableService   │  Feign   │ CommonVariableService    │
│  ├─ CRUD (分类树)       │ ──────→  │  (MyBatis-Plus Service)  │
│  ├─ XML/Excel 导入      │          │  ├─ getCommonVarByType()  │
│  ├─ 复杂对象解析        │          │  ├─ queryByOrgName()      │
│  └─ checkSheetList()    │          │  └─ updateRegexCodeById() │
├─────────────────────────┤          └──────────────────────────┘
│ StrategyVariableService │          t_common_variable
│  ├─ 必填参数校验        │          ┌──────────────────────────┐
│  ├─ 正则校验            │          │ parentId (树形结构)       │
│  └─ Redis 3天缓存       │          │ variableShowName/Name     │
└─────────────────────────┘          │ variableType (0/1/2/3)   │
                                     │ dataType (S/N/D)         │
Feign接口:                           │ regexCode/defaultValue   │
CommonVariableFeign→raptor           │ complexObjectContent(JSON)│
StrategyVariableFeign→raptor         └──────────────────────────┘
```

### 4.2 CommonVariable — 变量定义实体

**表**: `t_common_variable`（raptor库）  
**实体**: `raptor-infrastructure-mysql/.../entity/CommonVariable.java`

| 字段 | 类型 | 说明 |
|------|------|------|
| `parentId` | Long | 父节点ID，0=根分类，构建树形结构 |
| `variableShowName` | String | 变量显示名（中文） |
| `variableName` | String | 变量英文名（唯一标识） |
| `variableDesc` | String | 变量描述 |
| `dataType` | String | 数据类型: S=字符串, N=数字, D=日期 |
| `variableType` | Integer | **0=INPUT** 入参, **1=OUTPUT** 出参, **2=CONSTANT** 常量, **3=INTERMEDIATE** 中间变量 |
| `defaultValue` | String | 默认值 |
| `regexCode` | String | 正则校验编码 |
| `inputType` | String | 输入控件类型 |
| `outerRefId` | String | 外部引用ID |
| `outerParamPath` | String | 外部参数路径(JSONPath) |
| `complexObjectContent` | String | 复杂对象定义(JSON, 支持LoopList嵌套) |

**树形结构**: parentId区分分类节点与变量节点。系统初始化4个根分类：`param`, `Basic_Information`, `Basic_Information_Company`, `System_Inner_Param`。分类节点parentId=0；变量节点parentId指向分类节点ID。

**权限隔离**: `authCode = tenantCode + "_" + organizeCode`，多组级权限范围过滤。

### 4.3 CommonVariableService — 变量管理核心

**文件**: `peregrine-app/.../service/CommonVariableService.java`（约1055行）

**XML/Excel双格式导入管线**：

```
uploadFile() → initVariableFile()
  ├─ parseFileForXml(): XML格式 → 递归解析<variable>节点树
  │   └─ 支持 complexObjectContent (LoopList嵌套结构)
  └─ parseFileForExcel(): Excel格式 → POI逐Sheet读取
      └─ checkSheetList(): 校验Sheet完整性（表头+数据类型+正则）

→ CommonVariableFeign.saveBatch() → raptor持久化
```

**关键方法**：
- `getInputVariableList()`: 获取策略入参变量列表（variableType=0），含搜索+分页
- `getOutputParamList()`: 获取出参变量列表（variableType=1）
- `getComplexObjectContentAndCheck()`: 递归解析复杂对象定义，校验LoopList循环引用

### 4.4 StrategyVariableService — 运行时校验层

**文件**: `peregrine-app/.../service/StrategyVariableService.java`（约163行）

**核心机制**：策略执行前对传入变量做**必填校验**和**正则校验**。

```
checkRequiredParams(strategyId, packageId, inputParams)
  → Redis GET "variableRequired:{strategyId}_{packageId}"
  → 比对 inputParams 是否包含所有 isRequired=1 的变量
  → 缺失则抛出 ServiceException

checkRegexValidation(strategyId, packageId, inputParams)
  → Redis GET "variableRegex:{strategyId}_{packageId}"
  → 对每个有 regexCode 的变量执行正则匹配
  → 不匹配则抛出 ServiceException
```

**Redis缓存** (3天TTL)：
| Key模式 | Value | 用途 |
|---------|-------|------|
| `strategyApiParam:{strategyId}_{packageId}` | StrategyApiParam JSON | 策略API参数完整配置 |
| `variableRequired:{strategyId}_{packageId}` | requiredVarMap | 必填变量列表 |
| `variableRegex:{strategyId}_{packageId}` | regexMap | 变量→正则映射 |

### 4.5 StrategyVariableVo — 策略-变量绑定

**文件**: `peregrine-interface/.../vo/StrategyVariableVo.java`

| 字段 | 类型 | 说明 |
|------|------|------|
| `strategyId` | Long | 策略ID |
| `ruleCode` | String | 规则编码 |
| `variableShowName` | String | 变量显示名 |
| `variableName` | String | 变量名 |
| `isComVar` | Integer | **1=引用CommonVariable**，0=自定义 |
| `refComVarId` | Long | 引用的CommonVariable ID |
| `isRequired` | Integer | **1=执行时必填** |
| `outerRefId` | String | 外部引用标识 |
| `outerParamPath` | String | 外部参数JSONPath |
| `complexObjectContent` | String | 复杂对象结构定义 |

**isComVar机制**: 变量可从CommonVariable公共池引用（isComVar=1, refComVarId指向t_common_variable.id），或策略内自定义。公共变量更新后所有引用策略自动生效。

### 4.6 变量执行调用链

```
策略请求 → peregrine接收参数
  → StrategyVariableService.checkRequiredParams() → Redis缓存
  → StrategyVariableService.checkRegexValidation() → Redis缓存
  → Feign → owl-execution (LiteFlow工作流)
    → BizNode: 调外部API获取原始数据
    → DerivedNode: Feign → seagull-web /api/seagull/varquery/execute
      → Dispatcher → WorkerPool(200/批) → Aviator/Janino/Python Worker
      → 表达式: varContent + varParam(JSONPath参数映射)
```

### 4.7 核心难点

1. **双层架构一致性**: peregrine管理层变更→Feign同步raptor存储层→Redis缓存刷新。三层数据一致性依赖缓存TTL+主动刷新。
2. **XML/Excel双格式兼容**: 同一导入管线处理两种格式，复杂对象(LoopList)需递归解析校验。
3. **公共变量引用机制**: isComVar实现变量复用，变更一处、全局生效，但也带来兼容性风险。
4. **正则校验缓存化**: 策略执行时正则校验结果不走DB，全量缓存Redis(3天TTL)，缓存穿透时回源查询。

---

## 五、Nest — 用户组织中心

- **RBAC**：Tenant→Organization→User→Role→Permission→PermissionUrl
- **starter**：ThreadLocal上下文(CurrentUser/CurrentDict/CurrentSystem)、JWT+AuthInterceptor、5种数据权限、`@SkipDataAccess`/`@ForceDataAccess` 注解、WebSocket+RocketMQ站内信

---

## 六、Kestrel — 运营管理与名单系统

### 6.1 名单模块架构

名单(roster)是Kestrel内**独立的子应用**，由3个Maven模块组成：

```
kestrel/
├── roster-common/          # 枚举、异常、工具类(DesKit等)
├── kestrel-op-db/
│   └── roster-db-base/     # Entity、Mapper、CrudService(5张表)
└── roster-app/             # Controller、Service、VO、Param、AOP
```

网关路由: `/gateway/api/roster/**` → `roster-app`，白名单放行 `/api/roster/contains`。

### 6.2 名单类型与状态机

**三种名单类型** (`RosterTypeEnum`):
| 类型 | 编码 | 含义 |
|------|------|------|
| `WHITE_LIST` | 1 | 白名单 — 命中则放行 |
| `BLACK_LIST` | 2 | 黑名单 — 命中则拒绝 |
| `GRAY_LIST` | 3 | 灰名单 — 标记/人工审核 |

**两级状态机**:

```
名单级别:  RosterStatusEnum
  ENABLE(1) ⇄ DISABLE(2)

条目级别:  RosterDetailStatusEnum
  ENABLE(1) ⇄ DISABLE(2)

审核级别:  AuditStatusEnum
  APPROVING(1) → APPROVED(2) / REJECTED(3) / REVOKED(4)
```

每个条目有**独立的时间窗口** `validStartTime`/`validEndTime`（默认2999-12-31），过期自动失效。

### 6.3 数据模型（5张表）

| 表 | 实体 | 核心字段 |
|----|------|---------|
| `t_roster` | RosterEntity | id, name, code, type(1/2/3), status(1/2), auditStatus(1-4) |
| `t_roster_detail` | RosterDetailEntity | rosterId, rosterCode(冗余), entityType, entityId, dataSource, joinReason, validStartTime, validEndTime, status, auditStatus |
| `t_roster_audit` | RosterAuditEntity | rosterId, rosterName, auditType, auditReason, auditStatus, auditOpinion |
| `t_roster_detail_audit` | RosterDetailAuditEntity | rosterId, rosterDetailId, entityType, entityId, auditType, auditReason, auditStatus, auditOpinion |
| `t_roster_operation_log` | RosterOperationLogEntity | rosterId, operationType(1-16), operationDesc(JSON), operationTime, operator |

所有实体继承 `BaseEntity`：tenantCode, organizeCode, createTime/updateTime, createCn/updateCn, isTest, isDeleted(软删除)。

### 6.4 API端点矩阵

**RosterController** — `/api/roster`（名单CRUD，11个端点）:

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/roster/page` | 分页查询，支持type/status/auditStatus/关键字过滤 |
| POST | `/api/roster/add` | 新增名单，@DistributedLock(name+code)，初始status=DISABLED |
| POST | `/api/roster/edit` | 编辑名单，@DistributedLock(id)，记录变更前后JSON |
| GET | `/api/roster/delete` | 软删除，name/code追加时间戳后缀避免唯一约束冲突 |
| GET | `/api/roster/info` | 单条详情（含dataSize/validDataSize统计） |
| GET | `/api/roster/enable` | 启用，@DistributedLock(id) |
| GET | `/api/roster/disable` | 禁用，@DistributedLock(id) |
| GET | `/api/roster/revoke` | 撤回审核，auditStatus→REJECTED |
| **POST** | **`/api/roster/contains`** | **核心API：查实体是否在名单中（DES Token认证）** |
| POST | `/api/roster/export` | FastExcel流式导出，5000/页 |
| GET | `/api/roster/downloadApi` | Thymeleaf模板→PDF API文档 |

**RosterDetailController** — `/api/roster/detail`（条目管理，14个端点）: 含单条/批量 enable/disable/delete，importBatch模板下载。

### 6.5 contains() 核心逻辑

名单消费的唯一入口，由风控决策系统调用：

```
POST /api/roster/contains {rosterCode, entityType, entityId, token}
  │
  ├─ 1. 令牌解密
  │   DesKit.decrypt(token, "8df2ae61") → "roster:{tenantCode}:{loginName}"
  │   算法: DES/ECB/PKCS5Padding
  │
  ├─ 2. 用户解析
  │   Feign → nest-app /api/nest/sign/userInfoByLoginName
  │   → ThreadLocal CurrentUser 设置权限上下文
  │
  └─ 3. 匹配检查
      RosterDetailService.contains():
        → 查 t_roster: code={rosterCode} AND tenantCode AND organizeCode
        → 验证: 存在 AND is_deleted=0 AND status=ENABLE
        → 查 t_roster_detail: rosterCode + entityType + entityId
            + status=ENABLE + validStartTime ≤ now ≤ validEndTime
        → 返回 true/false
```

### 6.6 Token认证机制

**加密格式**: `DesKit.encrypt("roster:tenantCode:loginName")`

**DesKit** (`roster-common/.../util/DesKit.java`):
- 算法: DES/ECB/PKCS5Padding
- 密钥: `8df2ae61`
- 无需网关JWT，网关白名单直接放行 `/api/roster/contains`

### 6.7 批量导入流程

```
用户上传Excel → nest-app文件存储(返回fileId)
  → POST /api/roster/detail/importBatch?rosterId=X&fileId=Y
    → NestRpcService: Feign下载文件（解析Content-Disposition文件名）
    → EasyExcel.read(): 逐行解析
    → buildRosterDetailEntity(): 逐行校验
        ├─ entityType名称→编码映射（从配置中心RdConfigUtil获取）
        ├─ dataSource名称→编码映射
        ├─ 日期格式解析（validStartTime/validEndTime）
        └─ entityType+dataSource存在性校验
    → 去重（同entityType+entityId已存在则跳过）
    → Lists.partition(rows, 500) → saveBatch() 分批入库
```

**限制**: 最多5000行，500条/批，超出抛异常。

### 6.8 操作日志系统

**OperationTypeEnum** (16种操作类型):

| 级别 | 操作 | 日志JSON格式 |
|------|------|-------------|
| 名单 | ADD(1)/EDIT(2)/ENABLE(3)/DISABLE(4)/DOWNLOAD_API(5) | `{name, description, code, type}` |
| 条目 | ADD(11) | `{id, entityId, entityType}` |
| 条目 | EDIT(12) | 仅变更字段 `{entityId, entityType, dataSource, joinReason, validStartTime, validEndTime}` |
| 条目 | ENABLE(13)/DISABLE(14)/DELETE(15) | 批量: `[{id, entityId, entityType}, ...]` |
| 条目 | BATCH_UPLOAD(16) | `{fileId, fileName}` |

### 6.9 安全机制

- **@DistributedLock** (Redisson): 所有写操作加分布式锁，key=`roaster-app:lock:{tenantCode}:{organizeCode}:{keyTag}:{SpEL}`, wait=3s/lease=30s
- **软删除**: RosterEntity删除时name/code追加时间戳后缀(`_yyyyMMddHHmmss`)，避免唯一约束冲突后复用
- **数据隔离**: MyBatis-Plus TenantInterceptor + 组织拦截器自动注入租户/组织过滤
- **并发控制**: `RosterDetailEntityCrudService.getRosterValidDataSizeMap()` 使用SQL原生 `NOW()` 过滤有效时间窗口

### 6.10 核心难点

1. **无缓存直查DB**: contains()每次请求直接查库，未使用Redis缓存。高并发下DB压力大，需依赖MySQL索引优化。
2. **DES Token安全性**: `8df2ae61`硬编码密钥，DES可被暴力破解，Token格式固定无时间戳防重放。
3. **批量导入限制**: ≤5000行/次，超限直接拒绝。大名单需多次导入。
4. **独立时间窗口**: 每个条目的validStartTime/validEndTime独立管理，查询需逐条判断时间有效性。
5. **审核与状态解耦**: 名单/条目的status和auditStatus独立管理，需人工配合操作（先提交审核→通过→手动启用）。
6. **软删除唯一约束处理**: 采用name+时间戳后缀避免唯一约束冲突，但无法完全防止并发删除。

### 6.11 Zero 监控与运维模块

Zero 是 Kestrel 的核心运营子系统（6 个 Maven 子模块），提供 IRP 平台**唯一的集中式监控和运维能力**。

#### 6.11.1 告警引擎

五层体系：**指标定义 → 规则配置 → 信号触发 → 模板渲染 → 多渠道发送**：

```
AlarmIndex (指标: 归属/统计方法/时间维度/过滤条件 → 动态SQL)
  → AlarmRule (规则: 绑定指标+阈值+Cron+渠道+严重级别, Redis自增编号)
    → AlarmCronService.timeExecute() (Quartz定时评估)
      → 动态生成SQL → 对比阈值(>, >=, =, <, <=, !=)
        → AlarmSignal (告警事件: 创建→认领→转派→关闭, 批量操作)
          → AlarmSendService + AlarmTemplate (多渠道+模板发送)
```

| 能力 | 实现 |
|------|------|
| 渠道 | 短信、邮件、钉钉、飞书、企业微信、站内信(Nest) — `AlarmChannelConfig` CRUD 管理 |
| 模板 | `AlarmTemplate` CRUD，消息内容可复用 |
| 延迟发送 | 告警消息存 Redis Hash → 延迟 Cron 后发送，避免瞬时抖动误报 |
| 防重 | Redis 分布式锁防重复执行 |
| 生命周期 | 创建→认领→转派→关闭（含原因），全状态追踪 |

**关键文件**: `zero-service/.../service/AlarmCronService.java`, `zero-app/.../controller/Alarm{Index,Rule,Signal,ChannelConfig,Template}Controller.java`

#### 6.11.2 交易策略监控 BI

`TradeStrategyMonitorController` 提供风控业务专属监控仪表盘，数据源来自 RocketMQ 消费 Peregrine 的 `peregrine-inboundMonitor-topic`：

| 监控维度 | API | 说明 |
|---------|-----|------|
| 调用量趋势 | `tradeVolumeMonitor` | 按时段统计决策服务调用量 |
| 决策结果分布 | `tradeResultMonitor` | 通过/拒绝/人工审核 比例 |
| 风险事件趋势 | `tradeResultRiskMonitorChar` + `tradeResultRiskCount` | 风险事件明细+计数 |
| 规则命中排名 | `ruleHitRank` | Top N 命中规则分析 |
| PSI 统计 | `psiStatistical` | 群体稳定性指标（模型漂移检测） |
| 分箱管理 | `getBinning/updateBinning` | 风险评分分段配置 |
| 回捞分析 | `backScoreDistribution` | 回捞策略效果分析 |

**每日聚合作业** (`TradeStrategyMonitorJob.java`):
```
@Scheduled(cron = "0 0 3 * * ?")  // 每天凌晨3点
Redis分布式锁(key=zero.scheduler.trade.monitor)
逐笔交易数据 → TradeStrategyMonitorDay 日汇总表
支持 compensateHistoryMonitorDay() 历史数据补偿
```

#### 6.11.3 RocketMQ 数据消费

Kestrel Zero 通过 5 个 Consumer 消费各服务生产的监控数据：

| Consumer | Topic | 数据用途 |
|----------|-------|---------|
| `InboundMonitorConsumer` | `peregrine-inboundMonitor-topic` | 交易策略入站 → TradeStrategyMonitor |
| `InboundExceptionConsumer` | `peregrine-inboundException-topic` | 入站异常记录 |
| `DataServicePubCallRecordConsumer` | `owl-dataservicepub-callrecord-topic` | Owl 数据服务调用记录 |
| `ChildRuleHitConsumer` | `risk-report-common-topic` | Raptor 规则命中详情 |
| （通过 Feign 查询） | — | 业务基础调用记录 |

所有记录支持分页查询、详情查看、Excel 导出。

#### 6.11.4 Quartz 定时任务管理

`SysJobController` + `SysJobLogController`（RuoYi 风格）：

| 能力 | 说明 |
|------|------|
| 任务 CRUD | 创建/更新/删除，Cron 表达式验证 |
| 生命周期控制 | 暂停/恢复/立即触发 |
| 执行日志 | 开始/结束时间、成功/失败、异常信息、耗时 |
| 错误策略 | 默认/忽略/触发并继续/不执行 |
| 并发控制 | 支持并发和非并发执行 |
| 自动启动 | `@PostConstruct init()` 启动所有已启用任务 |

#### 6.11.5 数据补偿修复

`CompensateDataController` 提供管理员后门，当定时任务因数据延迟或异常导致缺失时重新处理：

| API | 功能 |
|-----|------|
| `compensateHistoryMonitorDay` | 重新生成所有历史日汇总 |
| `compensateHistoryMonitorDayForTenantCode` | 按租户+日期精确补偿 |
| `compensateHistoryMonitor` | 按租户+时间范围补偿监控数据 |
| `compensateStrategyHitRule` | 重新处理规则命中数据 |

#### 6.11.6 Flowable BPMN 审批流引擎

运营审批流程管理（非风控决策流）:

| 组件 | 功能 |
|------|------|
| `FlowController` | BPMN 定义管理：创建/部署/撤回/删除 |
| `FlowTaskExtController` | 任务管理：启动流程、查询表单、获取待办 |
| `FormExtController` | 表单 CRUD |
| `MqOaMessageReceiver` | 流程完成事件 → RocketMQ 回调 OA 系统 |

#### 6.11.7 RocketMQ 管理工具

`MqAdminService`: 查询消费者客户端 IP 和订阅信息、测试消息发送。

#### 6.11.8 监控数据流全景

整个 IRP 平台的监控数据通过 **RocketMQ 异步生产-消费** 汇聚到 Kestrel Zero：

```
生产端（各服务）                          消费端（Kestrel Zero）
─────────────────                       ──────────────────────
peregrine  → peregrine-inboundMonitor-topic    → InboundMonitorConsumer  → BI仪表盘
peregrine  → peregrine-inboundException-topic  → InboundExcpConsumer     → 异常统计
owl        → owl-dataservicepub-callrecord-topic → OwlCallRecordConsumer  → 调用记录报表
raptor     → risk-report-common-topic           → ReportCommonConsumer   → 决策报告
raptor     → risk-report-alarm-email-topic       → AlarmEmailConsumer    → 告警邮件
```

**关键特征**：
- **Kestrel Zero 是唯一监控聚合点**：Raptor 和 Owl 自身不具备独立监控能力，只生产数据到 RocketMQ
- **Peregrine 是进件监控数据源**：在调用 owl-execution 前后采集进件请求/响应/异常数据
- **全异步解耦**：监控数据生产与业务调用同事务但不阻塞

#### 6.11.9 Raptor 和 Owl 的自身可观测性

| 服务 | 监控机制 | 覆盖范围 |
|------|---------|---------|
| **Owl** | `OwlCallResultAdvice` AOP — 记录所有 Feign 调用耗时(StopWatch)、参数、结果 | owl-common 全局拦截 |
| **Owl** | `OwlExecInvokerAspect` AOP — 记录执行器调用耗时、成功/失败 | owl-execution 调用入口 |
| **Owl** | `OwlLogAdvice` AOP — 请求日志 + StopWatch 耗时 | owl-execution Controller 层 |
| **Raptor** | `@Trace` (SkyWalking) — `fireRules()` 和 `startProcess()` 方法追踪 | KnowledgeSessionImpl 核心方法 |
| **Raptor** | `CacheController` — Caffeine 缓存统计 REST 端点 | 缓存命中率/大小 |
| **Raptor** | `PingController` — 基础存活检查 | 健康探针 |
| **Raptor** | `ReportMqMessage` — 决策报告写入 RocketMQ | 每次决策执行 |

**关键缺失**：
- **无 Micrometer/Prometheus 指标暴露**：没有任何 `/actuator/metrics` 端点，无法对接 Prometheus + Grafana
- **无 Spring Boot Actuator 健康检查**：无 `/actuator/health`、`/actuator/info` 端点（Raptor 仅有一个简陋 PingController）
- **无分布式追踪**：Raptor 使用了 SkyWalking `@Trace` 注解但 Owl 未使用，跨服务调用链的完整 trace 不可见
- **无熔断/降级监控**：owl-execution 的 `invokeAPi()` 无超时、无重试、无熔断，调用失败直接抛异常，没有熔断器状态可观测
- **无 JVM 指标暴露**：堆内存、GC、线程池状态等在服务内部不可见
- **无业务 SLA 指标**：决策耗时 P99/P95/P50、各节点耗时分布不可见
- **seagull-web 零监控**：指标引擎无任何 AOP、埋点、耗时统计，调用完全黑盒

---

## 七、Tamer — API网关

### 6.11 名单在决策流中的生效机制（业务场景）

**关键发现**：名单(roster)没有任何代码级集成——peregrine、owl-execution、raptor的Java代码中**零引用**roster模块。名单是通过**owl-execution的BizNode配置化调用**进入决策链的。

#### 6.11.1 生效机制：BizNode → RemoteServiceFeign → roster

```
LiteFlow 决策链:
  DataServiceStart → BizNode(查名单) → SwitchNode(判断) → BizNode(查征信) → ... → DataServiceOutput
                          │                    │
                          │  true/false        │
                          ▼                    ▼
              POST /api/roster/contains   在黑名单? → 直接输出REJECT, 终止链路
                                          在白名单? → 跳过后续风控规则, 直接PASS
                                          在灰名单? → 转人工审核分支
```

**技术实现**：
1. Owl管理中心(`owl-management`)注册一个数据服务发布(`t_dc_data_service_pub`)，指向roster
2. 为该服务配置元数据(`t_dc_inc_metadata`)：`url = "http://roster-app/api/roster/contains"`, `httpMethod = 1(POST)`
3. 流程编排时拖入一个 `DataServiceBiz` 节点，`bizCode` 选择该数据服务
4. 运行时 BizNode.process() → `owlFlowExecService.invokeAPi(inputParam, bizCode)` → `RemoteServiceFeign.doPostJSON(path, params)` → HTTP调用roster
5. 返回 `{code:200, data: true/false}` → 存入LiteFlow上下文
6. 下游 `DataServiceSwitch` 节点根据结果分支路由

**核心代码路径**：
- `BizNode.java:90` — `Object result = invokeAPi(inputParam, bizCode);`
- `BizNode.java:137` — `owlFlowExecService.invokeAPi(inputParam, bizCode, ...)`
- `OwlExecInvoker.java:58` — `responseBody = remoteServiceFeign.doPostJSON(path, ...)`
- `IncMetadataEntity.java:36` — `url` 字段存储目标HTTP地址

#### 6.11.2 典型业务场景

| 场景 | 名单类型 | 决策流位置 | 逻辑 |
|------|---------|-----------|------|
| **贷前拒黑** | 黑名单 | 链路最前端(BizNode #1) | 身份证/手机号命中黑名单→直接REJECT，不执行后续查征信/跑规则，节省计算资源 |
| **VIP免审** | 白名单 | 黑名单检查之后 | 命中白名单→跳过风控规则，直接返回PASS+高额度，提升VIP体验 |
| **灰名单转人工** | 灰名单 | 规则引擎之前 | 命中灰名单→输出MANUAL_REVIEW，待人工审核后决定 |
| **贷后监控** | 黑名单 | 批量回溯 | 定时回溯存量客户，发现新入黑名单→触发预警 |
| **反欺诈联动** | 黑名单 | 实时决策 | 外部反欺诈系统发现欺诈→通过API写入黑名单→实时决策链立即生效 |

#### 6.11.3 与特征工程的对比

| 维度 | 特征工程(seagull-web) | 名单(roster) |
|------|----------------------|-------------|
| **调用方式** | DerivedNode硬编码Feign调用 | BizNode配置化HTTP调用 |
| **配置位置** | `t_vc_var_base_def`(变量) + `VarDomain`(域) | `t_dc_data_service_pub`(服务发布) + `t_dc_inc_metadata`(URL) |
| **返回数据** | 计算后的指标值(数字/字符串) | 布尔值(true/false) |
| **对决策流影响** | 提供数据供后续规则判断 | 直接决定流程分支(拒绝/通过/转人工) |
| **代码集成度** | 深度集成(seagull-interface Feign) | 零代码集成(纯配置驱动) |

#### 6.11.4 名单命中判断：哪些字段参与匹配

**参与命中的字段（6个条件AND，全部满足才算命中）：**

| 条件 | 匹配来源 | 匹配方式 | 说明 |
|------|---------|---------|------|
| `rosterCode` | defaultValue配置 | `=` | 确定查哪个名单 |
| `entityType` | defaultValue配置或sourceJsonPath提取 | `=` | 实体类型，如 `"phone"` |
| `entityId` | sourceJsonPath从请求JSON中提取 | `=` | 实体值，如 `"13800138000"` |
| `isDeleted = false` | 系统字段 | `=` | 名单条目未被删除 |
| `status = ENABLE` | 名单自身的启用开关 | `=` | 整个名单处于启用状态 |
| `validStartTime ≤ now ≤ validEndTime` | 导入时配置的时间窗口 | `≤` / `≥` | 当前时间在生效窗口内 |

**不参与命中判断的字段：**

| 字段 | 用途 |
|------|------|
| `dataSource`（数据来源） | 仅审计记录，标注数据从哪个渠道来 |
| `joinReason`（加入原因） | 仅审计记录，说明为什么加入名单 |

**核心代码** (`RosterDetailService.java:198-207`):
```java
LambdaQueryWrapper<RosterDetailEntity> queryWrapper = Wrappers.lambdaQuery(RosterDetailEntity.class)
    .eq(RosterDetailEntity::getRosterCode, param.getRosterCode())     // 名单编码
    .eq(RosterDetailEntity::getEntityType, param.getEntityType())     // 实体类型
    .eq(RosterDetailEntity::getEntityId, param.getEntityId())         // 实体ID
    .eq(RosterDetailEntity::getIsDeleted, Boolean.FALSE)              // 未删除
    .eq(RosterDetailEntity::getStatus, RosterDetailStatusEnum.ENABLE.getCode())  // 状态启用
    .le(RosterDetailEntity::getValidStartTime, LocalDateTime.now())   // 已生效
    .ge(RosterDetailEntity::getValidEndTime, LocalDateTime.now());    // 未失效
return this.rosterDetailEntityCrudService.exists(queryWrapper);       // 返回 true/false
```

**具体例子**：假设请求长这样：

```json
{"phone": "13800138000", "idCard": "310101199001011234", "amount": "50000"}
```

BizNode 的 `inputParamMappingList` 配置了 `sourceJsonPath` 从请求中提取字段：

```json
// inputParamMappingList 配置
[
  {"paramCode": "entityType", "sourceJsonPath": null},     // 无映射→用 defaultValue="phone"
  {"paramCode": "entityId",   "sourceJsonPath": "phone"},  // 从请求 JSON 的 phone 字段提取
  {"paramCode": "rosterCode", "sourceJsonPath": null}      // 无映射→用 defaultValue="BLACKLIST_PHONE"
]
```

构建出的名单查询请求体：

```json
{"rosterCode": "BLACKLIST_PHONE", "entityType": "phone", "entityId": "13800138000", "token": "..."}
```

名单表中数据（导入时配置）：

```
| entityType | entityId       | dataSource | joinReason | validStartTime      | validEndTime        |
|------------|----------------|------------|------------|---------------------|---------------------|
| phone      | 13800138000    | 风控系统   | 历史欺诈   | 2024-01-01 00:00:00 | 2999-12-31 23:59:59 |
| phone      | 13900139000    | 人工导入   | 投诉举报   | 2025-06-01 00:00:00 | 2025-12-31 23:59:59 |
```

匹配过程：
- 请求 `entityType`="phone" == 第1行 `entityType`="phone" ✓
- 请求 `entityId`="13800138000" == 第1行 `entityId`="13800138000" ✓
- 当前时间 `2026-05-26` ∈ `[2024-01-01, 2999-12-31]` ✓
- → **命中！返回 true**

#### 6.11.5 rosterCode 参数值来源：defaultValue 配置机制

**关键问题**：你怎么知道请求要走 `BLACKLIST_PHONE` 这个名单而不是别的？

**答案**：`rosterCode` 的值是**运营人员在Owl管理中心配置数据服务时写在 `t_dc_inc_input_param.defaultValue` 里的固定值**，不是在请求里传的，也不是从上游节点算出来的。

**配置方式**：每个名单检查是Owl管理中心里的一个独立数据服务发布。在参数配置中，`rosterCode` 设置一个固定的 `defaultValue`：

```
t_dc_inc_input_param 表（数据服务参数配置）
┌──────────────────────────┬─────────────┬──────────────────┬──────────────────┬─────────────────────┐
│ dataServicePubCode       │ paramCode   │ defaultValue     │ sourceJsonPath   │ 说明                │
├──────────────────────────┼─────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ DS_BLACKLIST_PHONE       │ rosterCode  │ BLACKLIST_PHONE  │ (空)             │ ← 写死，指向具体名单 │
│ DS_BLACKLIST_PHONE       │ entityType  │ phone            │ (空)             │ ← 写死              │
│ DS_BLACKLIST_PHONE       │ entityId    │ (空)             │ $.phone          │ ← 从请求JSON中提取  │
│ DS_BLACKLIST_IDCARD      │ rosterCode  │ BLACKLIST_IDCARD │ (空)             │ ← 另一个名单        │
│ DS_BLACKLIST_IDCARD      │ entityType  │ idCard           │ (空)             │ ← 写死              │
│ DS_BLACKLIST_IDCARD      │ entityId    │ (空)             │ $.idCard         │ ← 从请求JSON中提取  │
└──────────────────────────┴─────────────┴──────────────────┴──────────────────┴─────────────────────┘
```

**defaultValue 生效机制**：`OwlExecInputBO.getMap()` (`OwlExecInputBO.java:58-61`)：
```java
return this.list.stream()
    .filter(vo -> input.containsKey(vo.getParamCode()))  // rosterCode 在 map 中（值为 null）
    .collect(Collectors.toMap(OwlExecInputVO::getParamCode,
        vo -> input.getOrDefault(vo.getParamCode(), vo.getDefaultValue()),  // null → defaultValue!
        (a, b) -> a));
```

`BizNode.handlerInputParam()` 遍历所有参数定义（来自 `t_dc_inc_input_param`），把 `rosterCode` 放入 resultMap——如果请求中没有，值就是 null。到 `OwlExecBO.getOutput()` 的 `getMap()` 时，发现值为 null 就用 `defaultValue` 补全。**注意**：这个 `defaultValue` 取的是 `OwlExecInputVO.defaultValue`，由 `OwlExecInputConvert`（MapStruct）从 `IncInputParamEntity.defaultValue` 自动映射（同名字段）得来。

#### 6.11.6 完整参数流转链路

```
外部请求                     BizNode                    OwlExecBO                  roster API
{"phone":"13800138000"}  →  handlerInputParam()    →   getMap()              →   POST /api/roster/contains
  │                            │                        │                          │
  │  BizNodeData:               │ 遍历 t_dc_inc_         │ 遍历 OwlExecInputVO:     │  {"rosterCode": "BLACKLIST_PHONE",
  │  bizCode = "DS_            │   input_param:          │  .filter(containsKey)     │   "entityType": "phone",
  │    BLACKLIST_PHONE"        │                          │  .getOrDefault(default)   │   "entityId": "13800138000",
  │                            │  rosterCode  = null  →  │                          │   "token": "..."}
  │  inputParamMappingList:    │  entityType  = null  →  │  rosterCode              │
  │  [{paramCode:"entityId",   │  entityId    = "1380"→  │    null→"BLACKLIST_PHONE" │     │
  │    sourceJsonPath:"phone"}]│                          │  entityType              │     ▼
  │                            │  构建 resultMap:         │    null→"phone"          │  RosterDetailService
  │                            │  {rosterCode: null,     │  entityId                │  .contains()
  │                            │   entityType: null,     │    "13800138000"         │     │
  │                            │   entityId:             │                          │     ▼
  │                            │    "13800138000"}        │  构建完整请求体           │  SELECT ... WHERE
  │                            │       │                  │       │                  │  rosterCode='BLACKLIST_PHONE'
  │                            │       └──────────────────┘       │                  │  AND entityType='phone'
  │                            │                                  │                  │  AND entityId='13800138000'
  │                            │         invokeAPi()              │                  │  AND isDeleted=0
  │                            │              │                   │                  │  AND status=ENABLE
  │                            │              ▼                   │                  │  AND validStartTime ≤ now
  │                            │  OwlFlowExecServiceImpl          │                  │  AND validEndTime ≥ now
  │                            │  .invokeAPi(inputParam, bizCode) │                  │
  │                            │              │                   │                  │     │
  │                            │              ▼                   │                  │     ▼
  │                            │  callLocalDataServiceExec()      │                  │  exists() → true/false
  │                            │              │                   │                  │
  │                            │              ▼                   │                  │
  │                            │  OwlExecBO.execute(input) ───────┘                  │
  │                            │  → getOutput() → getMap() → 补全 defaultValue
  │                            │  → runnable.apply() → HTTP POST /api/roster/contains
```

**三阶段参数解析**：
1. **BizNode 阶段**：从 `FLOW_EXECUTE_INPUT_PARAM`（外部请求参数）取值，或从 `sourceJsonPath` 映射的上游节点输出中提取。无值的参数放入 null
2. **OwlExecBO 阶段**：`OwlExecInputBO.getMap()` 对配置的参数列表过滤（只保留 `input.containsKey` 为 true 的参数），值为 null 的用 `OwlExecInputVO.defaultValue` 补全
3. **HTTP调用阶段**：最终的完整参数作为 JSON body 发送给 roster 服务的 `/api/roster/contains`

#### 6.11.7 多名单场景的配置方式

在一个决策链中检查多个名单（如手机号黑名单 + 身份证黑名单），只需在 LiteFlow 链中配置两个独立的 `DataServiceBiz` 节点，各自指向不同的 `bizCode`：

```
决策链:
  Start → BizNode(DS_BLACKLIST_PHONE) → Switch(命中→REJECT, 未命中→继续)
        → BizNode(DS_BLACKLIST_IDCARD) → Switch(命中→REJECT, 未命中→继续)
        → BizNode(查征信) → DerivedNode(特征计算) → Raptor(规则引擎) → Output
```

每个 `bizCode` 对应一个独立的数据服务发布，各自在 `t_dc_inc_input_param` 中配置了不同的 `rosterCode` 默认值和不同的 `entityType`/`entityId` 映射规则。**BizNode 本身不关心自己查的是什么名单——它只知道调用某个 `bizCode` 指向的 HTTP 接口，把参数传过去，拿到 true/false。** 所有名单相关的语义（名单编码、匹配哪些实体类型）全部由运营在Owl管理中心的配置决定，零代码耦合。

---

## 七、Tamer — API网关

- **路由**：`routes.yml`，`/gateway/` 前缀，StripPrefix=1
- **过滤链**：DecryptFilter(RSA解密AES Key→AES解密body) → AuthFilter(白名单→JWT→Feign Nest→URL权限)
- **动态开关**：Redis pub/sub热更新5个开关

---

## 八、Merlin — 模型全生命周期管理平台

Merlin 是模型全生命周期管理平台，覆盖**模型注册→工作流审批→模型训练→评估→部署**全流程。6个Maven模块，依赖nest-user（用户/组织/权限）、kestrel-api（Flowable审批流包装）、algo-service（算法训练执行）。

### 8.1 模块架构

```
merlin-domain      — 实体类、枚举、DTO、事件
merlin-repository  — MyBatis-Plus Mapper, 数据库访问
merlin-service     — ★核心业务逻辑★ AclService、WorkflowEventService、ModelService
merlin-app         — Spring Boot启动 + 17个Controller
merlin-flow        — Flowable审批流定义
merlin-db          — Flyway数据库迁移SQL
```

**MerlinApplication**: `@SpringBootApplication(scanBasePackages="tech.merlin")`, `@EnableFeignClients("tech.merlin")`, 启动端口通过 `server.port` 配置。

### 8.2 模型类型与状态机

**模型类型** (`ModelTypeEnum`):

| 类型 | 枚举值 | 可用算法 |
|------|--------|---------|
| 分类 | `CLASSIFICATION` | XGBoost, LightGBM, LogisticRegression, GBDT, RandomForest, DecisionTree, MLP, SVC |
| 回归 | `REGRESSION` | XGBoost, LightGBM, LinearRegression, GBDT, RandomForest, DecisionTree, MLP, SVR |
| 聚类 | `CLUSTER` | KMeans, MiniBatchKMeans, GaussianMixture |

**模型阶段状态机** (`ModelStageStatusEnum`, 5种状态):

```
PENDING_REGISTRATION(1) ⇄ PENDING_REVIEW(2)
       ↓                        ↓
REGISTRATION_COMPLETED(3)  REVIEW_COMPLETED(4)
                              PROCESS_TERMINATED(5)
```

**`ModelStageStateMachine`** (`merlin-service/.../workflow/ModelStageStateMachine.java`):

```java
// onTaskCompleted(): 审批完成 → 状态推进
//   nextOp=APPROVE → PENDING_REVIEW
//   nextOp=FORM → PENDING_REGISTRATION  
//   nextOp=null → terminal(REGISTRATION_COMPLETED/REVIEW_COMPLETED)

// onTaskReturned(): 审批退回 → 状态回退
//   prevOp=APPROVE → PENDING_REVIEW
//   prevOp=FORM → PENDING_REGISTRATION

// onActivityCancelled(): 审批取消 → 同回退逻辑
```

### 8.3 模型七阶段（Phase I-VII）

| 阶段 | 功能 | 关键能力 |
|------|------|---------|
| **I - 注册** | 模型注册、工作流审批 | Flowable BPMN → Kestrel包装, 5种状态流转 |
| **II - 生命周期** | 版本管理、状态变更 | 模型版本链, 激活/停用/废弃 |
| **III - 权限** | ACL多层权限 | INDIVIDUAL_LEVEL/DEPARTMENTAL_LEVEL/BANK_WIDE, USE/VIEW |
| **IV - 数据集** | 数据集管理、质检 | 数据源配置、特征列表、PythonExecuteFeign质检 |
| **V - 特征工程** | 特征选择、预处理 | 特征列表、编码方式、缺失值处理 |
| **VI - 训练** | AutoML训练管道 | Feign → algo-service, Optuna超参搜索 |
| **VII - 部署** | 模型部署、预测服务 | 模型文件管理、预测接口封装 |

### 8.4 ACL权限系统

**核心文件**: `merlin-service/.../service/acl/AclService.java`（约1486行）

```java
// 多级权限查询 — 并行 CompletableFuture
CompletableFuture<AclResult> personalFuture = 
    CompletableFuture.supplyAsync(() -> queryPersonalAcl(modelCode, userCode));
CompletableFuture<AclResult> orgFuture = 
    CompletableFuture.supplyAsync(() -> queryOrgAcl(modelCode, userCode));

// 合并结果: 个人权限优先，组织权限兜底
AclResult result = personalFuture.join().merge(orgFuture.join());
```

**权限层级**：INDIVIDUAL_LEVEL(个人) > DEPARTMENTAL_LEVEL(部门) > BANK_WIDE(全行)
**权限类型**：USE(使用模型)、VIEW(查看模型详情)
**阶段作用域**：`AclStageEntity` 关联模型特定阶段

### 8.5 工作流引擎

**接口**: `WorkflowEngineGateway` — 统一审批网关接口

```java
public interface WorkflowEngineGateway {
    Deployment deploy(String bpmnXml, String processKey);   // 部署流程定义
    ProcessInstance start(String processKey, Map vars);     // 启动流程实例
    List<Task> getTasks(String assignee);                    // 查询待办任务
    void complete(String taskId, Map variables);             // 完成审批
}
```

**Kestrel实现**: Feign调用 kestrel-api → Flowable BPMN引擎。BPMN自定义属性存储在documentation JSON中。

**四种事件处理器** (`merlin-service/.../workflow/event/`):
| 事件 | Handler | 触发时机 |
|------|---------|---------|
| TaskCompleted | `TaskCompletedEventHandler` | 审批完成 → ModelStageStateMachine推进 |
| TaskAssigned | `TaskAssignedEventHandler` | 任务分配 → 通知 |
| ActivityCancelled | `ActivityCancelledEventHandler` | 审批取消 → 状态回退 |
| ProcessCancelled | `ProcessCancelledEventHandler` | 流程取消 → 清理 |

### 8.6 训练管道 — Merlin→Algo调用链

**PythonExecuteFeign** (`merlin-service/.../feign/python/PythonExecuteFeign.java`):

```java
@FeignClient(name = "python-feature-service", url = "${python-feature-service.url}")
public interface PythonExecuteFeign {
    @PostMapping("/api/v1/dataset/qc")       // 数据质检
    Result qcFeatureStatistics(@RequestBody DatasetQcRequest dto);
    
    @PostMapping("/api/v1/dataset/process")   // 数据预处理
    Result callDatasetsProcess(@RequestBody DatasetProcessRequest dto);
    
    @PostMapping("/api/v1/job/status")        // 查询任务状态
    Result queryJobResult(@RequestBody JobStatusRequest dto);
    
    @PostMapping("/api/v1/algo/train")        // 启动训练
    Result train(@RequestBody TrainRequest dto);
    
    @PostMapping("/api/v1/job/revoke")        // 撤销任务
    Result revoke(@RequestBody RevokeRequest dto);
}
```

**训练启动完整流程**:

```
Controller.saveAndRun(ModelTrainDTO)
  → ModelService.save(modelEntity)       // 保存模型元数据
  → ModelService.startTraining()
    → 构建AlgorithmTrainDTO:
        datasource: {连接信息, 表名, 分区}
        features: [{name, type, encoding}]
        target: {column, positive_label}
        weight/split/preprocess: {...}
        search_strategy: {method: "bayesian", n_trials: 100}
        algo_params: {algorithm: "xgboost", ...}
        save_model: {format: "pkl", path: "minio://..."}
        history: [{modelCode, version}]  // 历史模型版本
    → PythonExecuteFeign.train(dto)       // Feign → algo-service
      → POST /api/v1/algo/train
```

**异步训练结果处理** (`ModelTrainTaskStrategy.java`):

```java
// PowerJob调度, 检查训练任务完成状态
// FAILURE → update model status to TRAIN_FAILED
// SUCCESS → save report JSON (accuracy/AUC/F1/ROC/Lift/Gain), release Redis lock
// Redis distributed lock per model: MODEL_TRAINING_LOCK_KEY_PREFIX + modelCode
```

**PowerJob 任务策略**（5种）:
| 策略 | 功能 |
|------|------|
| `DataProcessTaskStrategy` | 数据预处理异步任务 |
| `FeatureStatisticsTaskStrategy` | 特征统计计算 |
| `ModelTrainTaskStrategy` | 训练结果监听+状态更新 |
| `ModelDeployTaskStrategy` | 模型部署任务 |
| `ModelReportTaskStrategy` | 模型报告生成 |

### 8.7 核心难点

1. **多级ACL权限**: 个人/部门/全行三级，CompletableFuture并行查询，个人优先组织兜底
2. **Flowable工作流集成**: Kestrel包装Flowable, 4种EventHandler驱动状态机
3. **跨语言异步训练**: Merlin(Java) → Feign → algo-service(Python FastAPI) → Celery → MySQL backend
4. **PowerJob任务编排**: 5种策略，Redis分布式锁防并发训练
5. **BPMN自定义属性**: 审批流documentation JSON注入业务元数据

---

## 九、Algo-Service — 机器学习算法微服务

algo-service 是纯Python 3.10+ FastAPI服务，Celery异步任务处理，提供**AutoML训练、决策树策略、分箱、评分卡、模型评估**等ML能力。配置项通过 Pydantic BaseSettings 管理。

### 9.1 项目结构

```
algo_service/
├── main.py              — FastAPI 应用, 9个Router注册, 中文验证错误翻译
├── settings.py           — Pydantic Settings(HTTP/MySQL/Redis/OSS/LLM配置), GRAPH_COMPONENTS注册
├── router/               — 9个路由模块(train, decision, binning, dataset, job, model_valid, ...)
├── service/              — 业务服务层(train.py, model_valid.py, ...)
├── train_service/        — ★AutoML训练核心★
│   ├── core/trainer_engine.py    — TrainEngine: 训练+评估+曲线导出
│   ├── train/trainers/           — Trainer(XGBoost/LogisticRegression/GBDT ...)
│   ├── train/search/             — AutoSearcher(BayesianSearch Optuna)
│   └── schema/                   — Pydantic schema
├── core/
│   ├── decision/         — ★决策树策略引擎★ (decision_train.py, llm_decision_train.py, rule_extractor.py)
│   ├── score_card/       — 评分卡 (LogisticRegressionScorecard + BinningTransformer)
│   └── binning/          — 7种分箱方法
├── graph/                — ★Graph组件系统★ (@pipeline_sidecar装饰器, 动态模块注册)
├── component/            — ComponentTask: importlib动态加载+reload
├── workers/              — Celery App, PreRegisteredTask, 8个task模块
└── model/                — SQLAlchemy ORM模型
```

### 9.2 FastAPI接口矩阵（9个Router, 17+端点）

| Router | 端点 | 功能 |
|--------|------|------|
| **train** | `POST /api/v1/algo/train` | 启动训练(sync/async), 评分卡特殊处理binlib |
| **decision** | `POST /api/v1/decision/train` | 决策树训练(CART/RF/XGB) |
| **decision** | `POST /api/v1/decision/llm_train` | LLM辅助决策训练(8阶段pipeline) |
| **decision** | `POST /api/v1/decision/extract_rules` | 规则提取(DFS遍历决策树节点) |
| **binning** | `POST /api/v1/binning/{method}` | 7种分箱方法 |
| **dataset** | `POST /api/v1/dataset/qc` | 数据质检+特征统计 |
| **dataset** | `POST /api/v1/dataset/process` | 数据预处理+特征工程 |
| **job** | `GET /api/v1/job/status/{task_id}` | 查询Celery任务状态 |
| **job** | `POST /api/v1/job/revoke` | 撤销Celery任务 |
| **model_valid** | `POST /api/v1/model_valid/create` | 模型验证评估 |
| **component** | `POST /api/v1/component_task/create` | Graph组件动态调用 |
| **health_probe** | `GET /api/v1/health` | 健康检查 |

**全局异常处理** (`main.py`):
```python
# 中文验证错误翻译: 通过 model_json_schema() 获取字段title
def get_field_title_from_model(model_class, field_name):
    schema = model_class.model_json_schema()
    return schema["properties"][field_name].get("title", field_name)

# RequestValidationError → 中文字段名+错误信息
# ServiceHandleException → HTTP 400 with detail
# Exception → HTTP 500, 记录traceback
```

### 9.3 AutoML训练引擎

#### 9.3.1 TrainEngine — 训练+评估一体化

**核心文件**: `train_service/core/trainer_engine.py` (约263行)

```
TrainEngine.execute():
  trainer.with_target_encoder()
  → searcher.with_trainer(trainer)
  → searcher.search(n_trials)  — Optuna超参优化
  → best_model = trainer.train(best_params)  — 全量训练
  → export_model_perf()  — 评估指标+曲线
```

**`export_model_perf()` 输出**:
```python
{
    "accuracy": 0.85,
    "auc": 0.92,               # binary: roc_auc_score, multi: AUC per class
    "f1": 0.83,
    "precision": 0.81,
    "recall": 0.80,
    "roc_curve": [...],        # 100-point插值, dict per class
    "lift_curve": [...],       # 累计Lift
    "gain_curve": [...],       # InfoGainCalculator
    "pr_curve": [...],         # Precision-Recall
    "confusion_matrix": [[...]], 
    "feature_importance": [    # feature_importances_ 或 coef_
        {"feature": "age", "importance": 0.35},
        {"feature": "income", "importance": 0.28}
    ],
    "trial_info": [...]       # Optuna trials + rolling best value
}
```

#### 9.3.2 Trainer — 基类与具体实现

**核心文件**: `train_service/train/trainers/trainer.py` (约388行)

```python
class Trainer(ABC):
    # objective(trial) → 返回CV评估指标, Optuna优化目标
    #   - StratifiedKFold/shuffle CV
    #   - eval_set for XGBoost early stopping
    
    # build_param(trial) → gen_parameters(trial)  — abstract
    # build_search_model() → sklearn estimator       — abstract
    
    # train(best_params):
    #   构建 sklearn Pipeline(preprocess + classifier)
    #   fit with sample_weight
    #   返回 (pipeline, SplitedDataset)
    
    # get_feature_importance():
    #   feature_importances_ → XGBoost mean over classes
    #   coef_ → abs, mean over classes
```

**数据集分割** (`SplitedDataset`):
- `auto`: 随机分割 train/test
- `time_seq`: 按时间范围分割

**具体实现**:
| 文件 | 类 | 算法 |
|------|---|------|
| `trainer_xgb.py` | `TrainerXgb` | build_search_model→xgb.XGBClassifier, train_type="odd" |
| `trainer_lgb.py` | `TrainerLgb` | lightgbm.LGBMClassifier |
| `trainer_lr.py` | `TrainerLr` | sklearn LogisticRegression |
| `trainer_gbdt.py` | `TrainerGbdt` | sklearn GradientBoostingClassifier |
| `trainer_rf.py` | `TrainerRf` | RandomForestClassifier |
| `trainer_dt.py` | `TrainerDt` | DecisionTreeClassifier |
| `trainer_mlp.py` | `TrainerMlp` | MLPClassifier |
| `trainer_svc.py` | `TrainerSvc` | SVC |

#### 9.3.3 BayesianSearch — Optuna超参搜索

**核心文件**: `train_service/train/search/bayesian_search.py` (约45行)

```python
class BayesianSearch(AutoSearcher):
    def search(self, n_trials=100):
        study = optuna.create_study(direction="maximize")  # 最大化AUC/F1
        study.optimize(self.trainer.objective, n_trials=n_trials)
        self.best_params = study.best_trial.params
        self.best_score = study.best_trial.value
        return self.trainer.train(self.best_params)
```

### 9.4 决策树策略引擎

#### 9.4.1 三种分裂模式

| 模式 | 说明 |
|------|------|
| **full** | 全自动, 决策树完整生长(max_depth参数控制) |
| **auto** | 自动化最优单分裂: `_auto_single_split()` → max_depth=1 CART |
| **manual** | 手动指定特征+阈值: `_manual_split(feature, threshold/categories)` |

#### 9.4.2 _XGBTreeAdapter — XGBoost→sklearn树适配

```python
class _XGBTreeAdapter:
    # XGBoost trees_to_dataframe() → sklearn-style tree_ 接口
    # children_left/children_right/feature/threshold/value 数组
    # 使XGBoost训练的树也能走 _build_tree_node() DFS遍历
```

#### 9.4.3 目标编码 (Bayesian Smoothing)

```python
# discrete特征 → target encoding with Bayesian smoothing
encoded_value = (n * category_rate + m * global_rate) / (n + m)
# smooth_factor = m = 20
```

#### 9.4.4 完整训练流程 (decision_train.py, 约638行)

```
start_decision_train():
1. 加载数据 → label mapping → process_history → parent_conditions filter
2. _target_encode_discrete_features() → Bayesian平滑
3. 数据分割 (train/test)
4. _build_model(algo_type):
     DecisionTree → DecisionTreeClassifier
     RandomForest → RandomForestClassifier (选best tree by node count)
     XGBoost → XGBClassifier → _XGBTreeAdapter
5. _extract_sklearn_tree() → _build_tree_node() DFS
     continuous特征: threshold (≤/>)
     discrete特征: encoding_maps→categories (in)
6. extract_rules() → rule路径(DSF)+语言表达式
```

#### 9.4.5 规则提取器 (rule_extractor.py, 约176行)

```python
def extract_rules(tree_root: DecisionTreeNode):
    # DFS遍历树节点, 收集边上的SplitCondition
    # continuous: age <= 30, age > 30
    # discrete: city in ['北京','上海']
    # 输出: [rule_path, language_expr, action]

def make_split_condition(node, branch):
    # 子节点阈值 → SplitCondition
    # get_language_expression() → 自然语言规则
```

### 9.5 LLM辅助决策训练 (llm_decision_train.py, 约353行)

8阶段Pipeline:

```
1. Load data + label mapping
2. qc_select_features → 硬编码数据质检
3. ★llm_select_features★ → LLM选出有业务价值的特征
4. ★llm_select_algo★ → LLM选择算法(CART/RF/XGB) + 超参数
5. _build_model → fit → _extract_sklearn_tree → _build_tree_node
6. extract_rules → DFS→规则路径
7. ★llm_filter_rules★ → LLM精选+排序规则
8. Return LLMDecisionTrainResult
```

**LLM配置**: OpenAI兼容接口(via `settings.LLM_*`), Chat Completions API

### 9.6 分箱系统 — 7种方法

| 方法 | 类型 | 说明 |
|------|------|------|
| **ChiSquare** | 有监督 | 卡方合并, 最大化特征与目标的关联 |
| **IV-Optimal** | 有监督 | IV(Information Value)最优分箱 |
| **DecisionTree** | 有监督 | 决策树分箱, 最优分裂点 |
| **MonteCarlo** | 无监督 | 蒙特卡洛采样分箱 |
| **EqualWidth** | 无监督 | 等宽分箱 |
| **EqualFrequency** | 无监督 | 等频分箱 |
| **KMeans** | 无监督 | K均值聚类分箱 |

### 9.7 评分卡系统

**核心文件**: `core/score_card/score_card_service.py` (约200行)

```python
class ScorecardService:
    # LogisticRegressionScorecard with BinningTransformer
    # BinningTransformer: WOE编码, 每个bin计算WOE=ln((bad_rate)/(good_rate))

    def train_from_datasource():
        pipeline = LogisticRegressionScorecard(
            binning=BinningTransformer(method="chi_square"),
            score_calibration=ScoreCalibration(base_score=600, pdo=20)
        )
        pipeline.fit(X_train, y_train)
        # export: scores, probs, binning_results, score_ranges
    
    def _build_report_data():
        # train/test scores distribution
        # binning_results: 每个特征每个bin的WOE, bad_rate, count
        # score_ranges: quantile-based score bands
```

**评分标定**: log-odds → scores, `Score = base_score - pdo * log2(odds)`

### 9.8 Graph组件系统

**注册机制** (`settings.py`):
```python
def register_component():
    # Path.rglob("graph/**/*.py") 扫描
    # GRAPH_COMPONENTS["binary_classification.xgbclassifier_binary"] = module_path
```

**@pipeline_sidecar 装饰器**:
```python
@pipeline_sidecar(name="preprocess", after="qc", before="train")
def preprocess_component(data, config):
    # sklearn Pipeline chaining across components
    ...
```

**ComponentTask** (`component/`):
```python
# importlib.import_module → reload → 调用 component 入口函数
# 支持热更新，无需重启服务
```

**典型Graph组件** (`graph/train/binary_classification/xgbclassifier_binary.py`, 约89行):
```python
# 1. 读取parquet数据
# 2. XGBClassifier.fit
# 3. cloudpickle dump model.pkl
# 4. 导出feature_table Excel
# 5. 生成predict_official.py
# pkl_data: {label_encoder, pipeline, output, output_prob, positive_label, model_type, feature_table}
```

### 9.9 Celery异步任务架构

**核心文件**: `workers/celery_app.py` (约103行)

```python
class PreRegisteredTask(Task):
    # apply_async时先INSERT PENDING状态到MySQL, 再入Redis队列
    # 3s countdown延迟，确保DB记录先于Worker消费

# Broker: Redis
# Backend: MySQL (LONGBLOB存储结果)
# Global key prefix: settings.CELERY_BROKER_PREFIX
# Result backend: "{rest}" for task result keys
```

**8个task模块**: train, decision, binning, dataset, model_valid, component, evaluation, score_card

### 9.10 核心难点

1. **Optuna贝叶斯优化**: objective(CV) + create_study(direction) + optimize(n_trials), 支持早停
2. **XGBoost→sklearn树适配**: _XGBTreeAdapter将XGB trees_to_dataframe()转换为sklearn tree_接口，统一规则提取
3. **LLM专家知识注入**: 8阶段pipeline，LLM选择特征+算法+超参+过滤规则
4. **Graph组件动态注册**: importlib+reload热更新, @pipeline_sidecar组成sklearn Pipeline
5. **Celery任务状态追踪**: PreRegisteredTask预登记PENDING, MySQL LONGBLOB存结果
6. **中文本地化验证错误**: 反射Pydantic model_json_schema()提取字段title

---

## 十、关键技术决策总结

| 维度 | 方案 | 核心原因 |
|------|------|---------|
| 规则流程编排 | LiteFlow 2.12.4 | 动态EL，热更新，子流程递归 |
| 规则匹配引擎 | URule Rete算法 | 共享条件节点、三层Agenda、互斥组独立Rete网络 |
| 规则存储格式 | XML+GZIP+Base64 | 统一格式，压缩存储，编译时解压，五种规则类型统一管道 |
| 规则动作执行 | Spring Bean反射+@ActionBean/@ActionMethod | Bean方法调用、变量赋值、枚举解析 |
| 指标表达式引擎 | Aviator+Janino+Python三层 | 按复杂度/性能分层，Janino编译为字节码性能最优 |
| 指标存储 | t_vc_var_base_def(表达式+JSONPath参数映射) | varContent=表达式, varParam=依赖参数JSONPath |
| 算子存储 | @FunctionDesc注解+DB函数表+FunctionService | 扫描注册、Aviator实例池、Janino通过AviatorFunctionCaller桥接 |
| 指标计算位置 | seagull-web(独立进程) | 与流程编排解耦，Feign远程调用 |
| 并行执行 | CompletableFuture(Api模式)+LiteFlow WHEN(Metric模式) | BFS最大宽度自适应线程池 |
| 批量处理 | 200个变量/批+WorkerPool | 避免大量变量时单线程瓶颈 |
| 缓存一致性 | Caffeine+RocketMQ广播 | 最终一致性，按ruleCode:ruleVersion粒度锁 |
| 变量回溯 | BackEvent工厂+Feign调owl-execution+RedissonLock | 数据拉取→指标计算→压缩存储全链路 |
| 网关安全 | RSA+AES混合加密 | 前端加密，网关解密转发 |
| 模型生命周期 | Merlin 7阶段模型管理(Phase I-VII) | 注册→审批→训练→评估→部署全链路，Flowable BPMN工作流编排 |
| 模型审批流 | Kestrel(Flowable)+4种EventHandler+状态机 | WorkflowEngineGateway统一接口, onTaskCompleted/Returned/Cancelled驱动状态流转 |
| 模型权限 | 三级ACL(个人/部门/全行)+CompletableFuture并行查询 | 个人优先组织兜底，USE/VIEW权限，阶段级作用域 |
| 训练管道 | Merlin(Java) → PythonExecuteFeign(HTTP) → algo-service(Python FastAPI) | 跨语言异步训练，PowerJob调度+Redis分布式锁防并发 |
| AutoML | Optuna BayesianSearch + 8种Trainer(XGBoost/LightGBM/...)+TrainEngine | Bayes超参优化，多目标CV，完整评估曲线(ROC/Lift/Gain/PR) |
| 决策树策略 | CART/RF/XGB三算法 + _XGBTreeAdapter + DFS规则提取 | XGB→sklearn树适配统一接口，规则路径→自然语言表达式 |
| LLM辅助决策 | 8阶段pipeline: qc→llm_select_features→llm_select_algo→train→extract→llm_filter | LLM注入专家知识选择特征+算法+超参+过滤规则 |
| 分箱系统 | 7种方法(卡方/IV/决策树/蒙特卡洛/等宽/等频/KMeans) | 有监督+无监督全覆盖，WOE编码 |
| 评分卡 | LogisticRegressionScorecard + BinningTransformer + score calibration | log-odds→scores标定(base_score+pdo) |
| Celery异步 | PreRegisteredTask(PENDING预登记)+Redis broker+MySQL LONGBLOB backend | 任务状态全程可追踪，8个task模块 |
| Graph组件 | @pipeline_sidecar + importlib动态注册+reload热更新 | sklearn Pipeline跨组件链式调用，无需重启 |
| 变量双层架构 | peregrine(管理层)+raptor(存储层)通过Feign同步 | 管理层CRUD+校验+缓存, 存储层MyBatis-Plus查询, 职责分离 |
| 变量导入 | XML/Excel双格式→parseFileForXml/parseFileForExcel公共管线 | 兼容历史XML+新Excel格式,复杂对象(LoopList)递归解析 |
| 策略变量校验 | Redis缓存(3天TTL) → checkRequiredParams + checkRegexValidation | 策略执行前必填+正则校验,缓存化避免每次查DB |
| 公共变量复用 | isComVar=1 refComVarId→CommonVariable | 变量定义一次全局复用,变更一处全局生效 |
| 特征工程模板 | Template(factors参数化)→VarBaseDef(实例化)→VarDomain(计算域) | 三层抽象,模板定义骨架,因子参数化,变量实例化,域组织执行 |
| 特征工程执行 | DataDerivationNode→SeagullFeign→WorkerPool(200/批)→3引擎 | LiteFlow节点触发→Feign远程调seagull-web→按varLang分发执行 |
| 变量池复用 | VcVarPoolBaseDef → batchInsert() → t_vc_var_base_def | 预构建变量跨域导入,减少重复定义 |
| 名单类型 | WHITE_LIST(1)/BLACK_LIST(2)/GRAY_LIST(3) | 白名单放行/黑名单拒绝/灰名单标记人工审核 |
| 名单查询 | `POST /api/roster/contains` → DesKit解密Token → 时间窗口匹配 | DES/ECB/PKCS5Padding加密token,entityType+entityId精确匹配,独立validStartTime/EndTime |
| 名单批量导入 | EasyExcel解析→逐行校验→去重→Lists.partition(500) saveBatch | ≤5000行,500条/批,entityType/dataSource编码映射+存在性校验 |
| 名单并发安全 | @DistributedLock(Redisson) + 软删除(name+时间戳后缀) | 名单/条目所有写操作加锁(wait=3s/lease=30s),name/code删除后追加时间戳避免唯一冲突 |

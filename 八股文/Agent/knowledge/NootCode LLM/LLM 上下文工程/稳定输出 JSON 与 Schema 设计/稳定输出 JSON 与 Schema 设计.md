# 稳定输出 JSON 与 Schema 设计

来源：https://www.nootcode.com/problems/stable-json-output-schema-design

## 面试直接回答卡
Q: 面试中如何直接回答“如何让模型稳定输出 JSON，Schema 应该怎么设计？”

A:
- 要让模型稳定输出 JSON，不能只在 prompt 里写“请输出 JSON”。更可靠的做法是定义明确 schema，并在模型输出后用 parser 和 schema validator 做确定性校验。
- Schema 设计要尽量减少歧义：字段名稳定、类型明确、枚举受限、必填项清楚、单位写进字段名或说明里，比如 `amount_cent` 比 `amount` 更不容易出错。
- 对可选字段要明确什么时候为空，数组元素结构要固定，字符串长度、数字范围、时间格式都要约束。不要让模型自由发明字段。
- 如果模型支持函数调用或结构化输出模式，优先使用这些能力；否则也要通过 prompt 示例、JSON fenced block、stop sequence、重试修复和后置校验组合实现。
- 工程上要把 JSON 输出当成不可信输入处理：先 parse，再 validate，再业务校验，再进入下游系统。格式稳定不是靠模型自觉，而是靠 schema 契约和失败处理。

## Schema 设计卡
Q: 一个好的 JSON schema 应该具备什么特点？

A:
- 字段名明确，例如 `risk_level`、`reasons`、`needs_human_review`。
- 类型明确，例如 string、integer、boolean、array、object。
- 枚举受限，例如 `risk_level` 只能是 `low|medium|high`。
- 单位明确，例如金额用 `amount_cent`，时间用 ISO 8601。
- 必填和可选字段清楚，避免模型自由补字段。
- 嵌套层级不要过深，降低生成错误概率。

## 具体例子卡
Q: 风控输出 JSON 可以怎么设计？

A:
- 示例 schema 字段：`risk_level`、`reasons`、`evidence_ids`、`needs_human_review`。
- `risk_level` 用枚举，避免模型输出“比较危险”这种自然语言。
- `reasons` 是字符串数组，每条原因简短说明。
- `evidence_ids` 只能引用工具返回的证据 id，防止模型编造来源。
- `needs_human_review` 是 boolean，给下游流程一个明确分支。

## 可追问原理卡
Q: 为什么模型输出 JSON 容易不稳定？

A:
- LLM 本质是逐 token 生成文本，不是 AST 生成器。
- 引号、逗号、括号、转义字符都可能生成错误。
- 上下文中多个示例 schema 可能互相污染。
- 用户输入包含特殊字符时，模型可能没有正确转义。
- 输出 token 上限过小会导致 JSON 没闭合。

## 校验链路卡
Q: JSON 输出进入下游前的校验链路是什么？

A:
- 第一步 parse，确保是合法 JSON。
- 第二步 schema validate，检查字段、类型、枚举、必填项。
- 第三步业务 validate，检查金额、状态、权限、引用 id。
- 第四步安全 validate，检查敏感信息、危险动作、越权字段。
- 第五步失败处理，可修复错误重试，不可修复错误拒绝或人工确认。

## 边界卡
Q: 只靠 prompt 示例能保证 JSON 稳定吗？

A:
- 不能。示例能提高模型模仿概率，但不是确定性保证。
- 模型可能输出解释文字、漏字段、类型错、枚举越界。
- 上下文变长或任务变复杂时，格式稳定性会下降。
- 结构化输出能力和函数调用可以提升稳定性，但仍要校验。
- 下游系统必须把模型输出当不可信输入。

## 正确性审查卡
Q: 设计 JSON schema 时有哪些误区？

A:
- 不要用自由文本字段承载关键决策，例如 `action: "随便处理一下"`。
- 不要让金额、时间、单位含糊不清。
- 不要让模型自由发明字段，schema 应设置额外字段策略。
- 不要把业务校验放进 prompt 后就不做程序校验。
- 不要忽略输出 token 上限，JSON 被截断会直接导致解析失败。

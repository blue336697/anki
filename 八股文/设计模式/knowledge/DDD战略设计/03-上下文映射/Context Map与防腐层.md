# Context Map 与防腐层
## 01-上下文关系
Q: Context Map 解决什么问题？
A:
- 它描述上下文间依赖方向、团队关系和模型翻译策略，而不只是画服务调用箭头。
- 常见关系有 Partnership、Shared Kernel、Customer/Supplier、Conformist、ACL、Open Host Service。
- 上下游影响发布节奏和协商权，必须显式记录谁定义契约、谁承担转换。
- 关系会演进，不能把一次架构图当永久事实。
## 02-ACL
Q: Anti-Corruption Layer 为什么不是普通 DTO mapper？
A:
- ACL 隔离外部模型语义，把供应商状态、错误和生命周期翻译成当前上下文语言。
- 它可包含 adapter、facade、translator 和缓存/容错，不让外部概念渗入领域对象。
- 外部 API 变化集中影响 ACL，核心模型保持稳定；代价是额外代码与数据损失决策。
- 若只是字段同名复制而无语义隔离，称不上防腐层。
## 03-共享内核
Q: Shared Kernel 为什么风险高？
A:
- 两个上下文共享一小部分模型/代码，减少重复，但任何修改都需共同协商和同步发布。
- 共享范围必须极小、所有权明确并有兼容测试；不能把公共实体 jar 当默认复用方案。
- 团队节奏或语言已分化时，应复制简单值或通过契约集成。
- 复用成本包括耦合，DRY 不能凌驾于上下文自治。
## 04-代码示例
Q: 外部物流状态怎样通过 ACL 进入订单上下文？
A:
```java
enum DeliveryStatus { IN_TRANSIT, DELIVERED, FAILED }
final class CarrierTranslator {
    DeliveryStatus translate(String external) {
        return switch (external) {
            case "SIGNED" -> DeliveryStatus.DELIVERED;
            case "LOST", "REJECTED" -> DeliveryStatus.FAILED;
            default -> DeliveryStatus.IN_TRANSIT;
        };
    }
}
```
- 领域层不认识 `SIGNED` 等供应商术语，新增承运商只新增 adapter/translator。
## 05-集成边界
Q: 跨上下文集成应怎样选择同步调用还是事件？
A:
- 需要立即决策且对方可用性可纳入 SLO 时使用同步契约；事实传播和松耦合更适合事件。
- 事件会带来最终一致、重复、乱序和版本兼容，不能用“解耦”掩盖复杂度。
- 同步链过长放大延迟与故障，事件链过长则难追踪业务完成状态。
- 选择应由业务一致性和失败补偿决定，不是技术偏好。


# Composite、Bridge 与 Flyweight
## 01-Composite
Q: Composite 如何统一叶子与容器的处理？
A:
- 叶子和组合实现同一 Component，组合递归持有子节点，让客户端统一调用树结构。
- 适合组织树、表达式、权限节点；递归操作需防环、深度和重复访问。
- 透明接口简单但叶子可能出现无意义 add；安全接口区分容器能力。
- 不要把任意父子表都强制做 Composite。
## 02-Bridge
Q: Bridge 如何避免两个独立维度产生子类爆炸？
A:
- 把抽象维度和实现维度分成两个可组合层，例如 Notification×Channel。
- 两边可独立扩展，抽象持有 implementor；它通常在设计时主动拆分。
- Adapter 多为事后兼容已有接口，Bridge 是预先分离变化轴。
- 若只有一个稳定维度，桥接只增加间接层。
## 03-Flyweight
Q: Flyweight 如何节省大量细粒度对象内存？
A:
- 把可共享的 intrinsic state 放共享对象，context 提供位置等 extrinsic state。
- 共享对象必须不可变/线程安全，缓存 key 完整表达内部状态。
- 字符字形、商品静态描述等可共享；用户余额等可变身份状态不可共享。
- 缓存无界会把节省变泄漏，需生命周期策略。
## 04-代码
Q: Bridge 的通知渠道怎样实现？
A:
```java
interface Channel { void deliver(String message); }
abstract class Notification {
    protected final Channel channel;
    Notification(Channel c){ channel=c; }
    abstract void send();
}
final class Alert extends Notification {
    Alert(Channel c){ super(c); }
    void send(){ channel.deliver("告警"); }
}
```
- Alert 和 Sms/Email Channel 可独立新增。
## 05-对比
Q: 三种模式分别处理哪类结构问题？
A:
- Composite 处理整体—部分递归结构，Bridge 处理正交变化维度，Flyweight 处理海量重复状态。
- 它们可组合：树叶节点引用共享样式，并通过 Bridge 渲染。
- 模式名不能替代问题证明，应先展示对象数量、变化轴或树形需求。
- 使用后仍要验证并发、缓存和递归边界。


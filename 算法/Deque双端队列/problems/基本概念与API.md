# Deque 基本概念与 API

## 什么是 Deque
`Deque`（Double Ended Queue，双端队列）是 Java 中允许 {{c1::在两端进行插入和删除}} 的线性集合。发音为 "deck"。

```java
// Deque 是接口，ArrayDeque 是首选实现
Deque<Integer> deque = new ArrayDeque<>();
```

继承关系：`Deque` extends {{c2::Queue}}，Queue extends Collection。

## 为什么用 ArrayDeque 而非 LinkedList
| | ArrayDeque | LinkedList |
|------|:--:|:--:|
| 底层 | 循环数组 | 双向链表 |
| 内存 | 紧凑 | 每个元素多占一个 Node 对象 |
| 性能 | 更快 | 较慢 |
| null | 不允许 | 允许（但不推荐） |

{{c1::ArrayDeque 是 Deque 的首选实现}}，官方明确说它比 Stack 快、比 LinkedList 快。

## 两大 API 族对比（必须记住）

| 操作 | 抛异常版 | 返回特殊值版 |
|------|------|------|
| **头部插入** | `addFirst(e)` | `offerFirst(e)` |
| **尾部插入** | `addLast(e)` | `offerLast(e)` |
| **头部删除** | `removeFirst()` | `pollFirst()` |
| **尾部删除** | `removeLast()` | `pollLast()` |
| **头部查看** | `getFirst()` | `peekFirst()` |
| **尾部查看** | `getLast()` | `peekLast()` |

记忆规则：{{c1::add/remove/get 失败抛异常}}，{{c2::offer/poll/peek 失败返回 null/false}}

## Deque 也可作为 Stack 和 Queue 使用
```java
// 作为栈（Stack） — 推荐替代 Stack 类
deque.push(e);     // = addFirst(e)
deque.pop();       // = removeFirst()
deque.peek();      // = peekFirst()

// 作为队列（Queue） — 推荐替代 LinkedList
deque.offer(e);    // = offerLast(e)
deque.poll();      // = pollFirst()
deque.peek();      // = peekFirst()
```

## 其他常用 API
- `isEmpty()` — 判断是否为空
- `size()` — 返回元素个数
- `contains(o)` — 是否包含某元素（O(n)，不常用）
- `clear()` — 清空
- `descendingIterator()` — 获取反向迭代器
- `removeFirstOccurrence(o)` / `removeLastOccurrence(o)` — 删除第一个/最后一个匹配元素

## 关键限制
- ArrayDeque {{c1::不允许插入 null 元素}}
- ArrayDeque {{c2::无容量限制}}（自动扩容，初始容量16，每次扩容翻倍）
- 不是线程安全的：{{c3::多线程需用 Collections.synchronizedDeque() 或 LinkedBlockingDeque}}

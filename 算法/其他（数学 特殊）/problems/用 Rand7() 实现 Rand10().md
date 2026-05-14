# 用 Rand7() 实现 Rand10()

## 题干
给定方法 rand7() 可生成 [1,7] 范围内的均匀随机整数，试写一个方法 rand10() 生成 [1,10] 范围内的均匀随机整数。不能使用系统的 Math.random() 方法。

## 复杂度
期望时间：{{c1::O(1)}} — 拒绝采样的期望拒绝次数为常数
空间：{{c1::O(1)}}

## 关键技巧
拒绝采样核心：
1. 范围扩展：(rand7()-1)*7 + rand7() 生成 [1,49] 的均匀分布
2. 拒绝策略：只取 <=40 的结果映射到 [1,10]
3. 余数再利用：被拒绝的 41~49 减40后变为1~9，再乘以7扩大范围，继续拒绝采样
4. 每级都充分利用被拒绝的样本，减少总调用次数

## 题解(拒绝采样)
将范围扩展到1~49，拒绝41~49并重新利用余数扩展，多级拒绝最小化浪费。

```java
class Solution extends SolBase {
    public int rand10() {
        while (true) {
            int res = (super.rand7() - 1) * 7 + super.rand7();
            if (res <= 40)
                return 1 + res % 10;
            res = (res - 40 - 1) * 7 + super.rand7();
            if (res <= 60)
                return 1 + res % 10;
            res = (res - 60 - 1) * 7 + super.rand7();
            if (res <= 20)
                return 1 + res % 10;
        }
    }
}
```

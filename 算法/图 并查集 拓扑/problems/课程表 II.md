# 课程表 II

## 题干
返回你为了学完所有课程所安排的学习顺序。如果有多个正确的顺序，返回任意一种。如果不可能完成所有课程，返回空数组。
![image 1.png](image%201.png)

![image 2.png](image%202.png)

## 复杂度
时间：{{c1::O(V+E)}} — BFS遍历所有顶点和边
空间：{{c1::O(V+E)}} — 邻接表+入度数组+结果数组

## 关键技巧
与课程表 I 的唯一区别：需要记录排序结果。
BFS出队顺序天然构成拓扑排序，只需在出队时将节点加入结果数组。
最后判断：若 index == numCourses 则返回结果数组，否则返回 new int[0]。

## 题解(BFS拓扑排序)
BFS拓扑排序+记录顺序：在课程表I的基础上，出队时将节点加入结果数组，若完成数不等于总课程数则返回空数组。

```java
class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        // 1.课号和对应的入度
        Map<Integer, Integer> inDegree = new HashMap<>();
        // 将所有的课程先放入
        for (int i = 0; i < numCourses; i++) {
            inDegree.put(i, 0);
        }
        // 2.依赖关系, 依赖当前课程的后序课程
        Map<Integer, List<Integer>> adj = new HashMap<>();

        // 初始化入度和依赖关系
        // 入度：指明有几个前置任务  依赖关系：指明前置任务具体是啥
        for (int[] relate : prerequisites) {
            // (3,0), 想学3号课程要先完成0号课程, 更新3号课程的入度和0号课程的依赖(邻接表)
            int cur = relate[1];
            int next = relate[0];
            // 1.更新入度
            inDegree.put(next, inDegree.get(next) + 1);
            // 2.当前节点的邻接表
            if (!adj.containsKey(cur)) {
                adj.put(cur, new ArrayList<>());
            }
            adj.get(cur).add(next);
        }

        // 3.BFS, 将入度为0的课程放入队列, 队列中的课程就是没有先修, 可以学的课程
        Queue<Integer> q = new LinkedList<>();
        for (int key : inDegree.keySet()) {
            if (inDegree.get(key) == 0) {
                q.offer(key);
            }
        }

        int[] res = new int[numCourses];
        int i = 0;
        // 取出一个节点, 对应学习这门课程.
        // 遍历当前邻接表, 更新其入度; 更新之后查看入度, 如果为0, 加入到队列
        while (!q.isEmpty()) {
            // 从这里取出来的节点入度都为0
            int cur = q.poll();
            // 在这就要更新，因为最后一个没有任何依赖关系的节点是不存在与邻接表中的，他就是结果集
            // 的最后一个节点，所以要在这就加入进去
            res[i++] = cur;
            // 遍历当前课程的邻接表, 更新后继节点的入度
            // 入度为0，但又不存在邻接表中说明没有依赖关系即没有后续了
            if (!adj.containsKey(cur)) {
                continue;
            }
            List<Integer> successorList = adj.get(cur);
            // 更新入度列表，将新的入度更新进去，并将入度为0的加入队列
            for (int k : successorList) {
                inDegree.put(k, inDegree.get(k) - 1);
                if (inDegree.get(k) == 0) {
                    q.offer(k);
                }
            }
        }
        // 如果存在回路关系，我们遍历当进行消除入度后，如果还存在入度不为0的就说明存在环
        for (int key : inDegree.keySet()) {
            if (inDegree.get(key) != 0) {
                return new int[0];
            }
        }
        return res;
    }
}
```

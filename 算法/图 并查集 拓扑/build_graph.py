"""Build APKG for 图/并查集/拓扑 (Graph). 4 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301500, '算法::图::原理通识')
add_basic(d0, 'DFS网格搜索模板',
    'void dfs(int[][] grid, int i, int j){<br>'
    '&nbsp;&nbsp;if(i&lt;0 || i&gt;=m || j&lt;0 || j&gt;=n) return;<br>'
    '&nbsp;&nbsp;if(grid[i][j] != 1) return;<br>'
    '&nbsp;&nbsp;grid[i][j] = 2; // 标记已访问<br>'
    '&nbsp;&nbsp;dfs(grid,i-1,j); dfs(grid,i+1,j);<br>'
    '&nbsp;&nbsp;dfs(grid,i,j-1); dfs(grid,i,j+1);<br>}')
add_cloze(d0, 'BFS拓扑排序模板',
    '// 1. 构建入度数组和邻接表<br>'
    'int[] inDegree = new int[numCourses];<br>'
    'List&lt;Integer&gt;[] adj = new List[numCourses];<br>'
    'for(int[] edge : prerequisites){<br>'
    '&nbsp;&nbsp;adj[edge[1]].add(edge[0]);<br>'
    '&nbsp;&nbsp;inDegree[edge[0]]++;<br>}<br>'
    '// 2. 入度为0的节点入队<br>'
    'Queue&lt;Integer&gt; q = new LinkedList&lt;&gt;();<br>'
    'for(i=0;i&lt;numCourses;i++)<br>'
    '&nbsp;&nbsp;if(inDegree[i]==0) q.offer(i);<br>'
    '// 3. BFS：出队时减少后继入度<br>'
    'while(!q.isEmpty()){<br>'
    '&nbsp;&nbsp;int cur = {{c1::q.poll()}};<br>'
    '&nbsp;&nbsp;for(int next : adj[cur]){<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if({{c2::--inDegree[next] == 0}})<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;q.offer(next);<br>'
    '&nbsp;&nbsp;}<br>}<br>'
    '// 4. 判断是否所有节点都已处理')
add_basic(d0, '并查集基础',
    '核心操作：<br>'
    '1. find(x)：查找根节点 + 路径压缩<br>'
    '&nbsp;&nbsp;if(parent[x] != x) parent[x] = find(parent[x]);<br>'
    '&nbsp;&nbsp;return parent[x];<br>'
    '2. union(x,y)：合并两个集合<br>'
    '&nbsp;&nbsp;int rx = find(x), ry = find(y);<br>'
    '&nbsp;&nbsp;if(rx != ry) parent[rx] = ry;<br>'
    '3. 初始化：每个节点的parent指向自己')
add_cloze(d0, '环检测方法比较',
    '1. BFS拓扑排序：统计入度为0的节点数，若{{c1::count != n}}则有环<br>'
    '2. DFS三色标记：0=未访问，1=正在访问，-1=已访问；遍历时遇到{{c2::状态为1}}的节点则有环<br>'
    '3. 并查集：适用于无向图，若合并时发现{{c3::两端已在同一集合}}则有环<br>')

# ============================================================
# 1. 岛屿的最大面积
# ============================================================
p = '岛屿的最大面积'
d = make_deck(1747301501, f'算法::图::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含了一些 0 和 1 的非空二维数组 grid，'
    '一个岛屿是由四个方向（水平或垂直）的 1 组成的组。'
    '找到给定的二维数组中最大的岛屿面积。如果没有岛屿，则返回面积为 0。'
    + img('image.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n)}} — 每个格子最多访问一次<br>'
    '空间：{{c2::O(m*n)}} — 递归栈最坏情况下需要遍历整个网格')

add_basic(d, make_front(p, '题解(DFS)'),
    '经典DFS flood fill：遍历网格，遇到1则DFS计算面积，标记已访问为2，取最大面积。<br>'
    + code(
        'class Solution {\n'
        '    public int maxAreaOfIsland(int[][] grid) {\n'
        '        int maxArea = 0;\n'
        '        for (int i = 0; i &lt; grid.length; i++) {\n'
        '            for (int j = 0; j &lt; grid[0].length; j++) {\n'
        '                if (grid[i][j] == 1) {\n'
        '                    maxArea = Math.max(dfs(grid, i, j), maxArea);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return maxArea;\n'
        '    }\n'
        '\n'
        '    private int dfs(int[][] grid, int i, int j) {\n'
        '        if (i &lt; 0 || j &lt; 0 || i &gt;= grid.length\n'
        '                || j &gt;= grid[0].length || grid[i][j] == 0\n'
        '                || grid[i][j] == 2) {\n'
        '            return 0;\n'
        '        }\n'
        '        grid[i][j] = 2;\n'
        '        return 1 + dfs(grid, i + 1, j)\n'
        '                + dfs(grid, i - 1, j)\n'
        '                + dfs(grid, i, j + 1)\n'
        '                + dfs(grid, i, j - 1);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'DFS模板三步：<br>'
    '1. 越界或不满足条件（grid[i][j]!=1）返回0<br>'
    '2. 标记已访问（grid[i][j]=2），防止重复计算<br>'
    '3. 递归四个方向并累加：1 + dfs(上下左右)<br>'
    '本质：将连通区域的大小通过递归返回值累加起来。')

# ============================================================
# 2. 课程表
# ============================================================
p = '课程表'
d = make_deck(1747301502, f'算法::图::{p}')
add_basic(d, make_front(p, '题干'),
    '你这个学期必须选修 numCourses 门课程，prerequisites[i]=[a,b] 表示先修课程 b 才能学 a。'
    '判断是否可能完成所有课程的学习。' + img('image.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(V+E)}} — 构建图+BFS遍历所有顶点和边<br>'
    '空间：{{c2::O(V+E)}} — 邻接表和入度数组')

add_basic(d, make_front(p, '题解(BFS拓扑排序)'),
    'BFS拓扑排序：构建入度表和邻接表，入度为0的课入队，BFS过程中减少后继入度，最后检查是否所有课都学完。<br>'
    + code(
        'class Solution {\n'
        '    public boolean canFinish(int numCourses, int[][] prerequisites) {\n'
        '        // 1.课号和对应的入度\n'
        '        Map&lt;Integer, Integer&gt; inDegree = new HashMap&lt;&gt;();\n'
        '        // 将所有的课程先放入\n'
        '        for (int i = 0; i &lt; numCourses; i++) {\n'
        '            inDegree.put(i, 0);\n'
        '        }\n'
        '        // 2.依赖关系, 依赖当前课程的后序课程\n'
        '        Map&lt;Integer, List&lt;Integer&gt;&gt; adj = new HashMap&lt;&gt;();\n'
        '\n'
        '        // 初始化入度和依赖关系\n'
        '        for (int[] relate : prerequisites) {\n'
        '            // (3,0), 想学3号课程要先完成0号课程, 更新3号课程的入度和0号课程的依赖(邻接表)\n'
        '            int cur = relate[1];\n'
        '            int next = relate[0];\n'
        '            // 1.更新入度\n'
        '            inDegree.put(next, inDegree.get(next) + 1);\n'
        '            // 2.当前节点的邻接表\n'
        '            if (!adj.containsKey(cur)) {\n'
        '                adj.put(cur, new ArrayList&lt;&gt;());\n'
        '            }\n'
        '            adj.get(cur).add(next);\n'
        '        }\n'
        '\n'
        '        // 3.BFS, 将入度为0的课程放入队列, 队列中的课程就是没有先修, 可以学的课程\n'
        '        Queue&lt;Integer&gt; q = new LinkedList&lt;&gt;();\n'
        '        for (int key : inDegree.keySet()) {\n'
        '            if (inDegree.get(key) == 0) {\n'
        '                q.offer(key);\n'
        '            }\n'
        '        }\n'
        '        int count = 0;\n'
        '        // 取出一个节点, 对应学习这门课程.\n'
        '        // 遍历当前邻接表, 更新其入度; 更新之后查看入度, 如果为0, 加入到队列\n'
        '        while (!q.isEmpty()) {\n'
        '            int cur = q.poll();\n'
        '            count++;\n'
        '            // 遍历当前课程的邻接表, 更新后继节点的入度\n'
        '            if (!adj.containsKey(cur)) {\n'
        '                continue;\n'
        '            }\n'
        '            List&lt;Integer&gt; successorList = adj.get(cur);\n'
        '\n'
        '            for (int k : successorList) {\n'
        '                inDegree.put(k, inDegree.get(k) - 1);\n'
        '                if (inDegree.get(k) == 0) {\n'
        '                    q.offer(k);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '\n'
        '        // 4.选了的课等于总课数，true，否则false\n'
        '        return count == numCourses;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(DFS环检测)'),
    'DFS三色标记检测环：0=未访问，1=正在访问，-1=已访问。遍历过程中遇到状态为1的节点说明存在环。<br>'
    + code(
        'class Solution {\n'
        '    // 通过邻接表来表示图的每个节点的连接关系\n'
        '    public boolean canFinish(int numCourses, int[][] prerequisites) {\n'
        '        // 设置一个存储总共课程的集合\n'
        '        List&lt;List&lt;Integer&gt;&gt; adjacency = new ArrayList&lt;&gt;();\n'
        '        // 总共有多少门课程，adjacency中就有多少个list\n'
        '        for (int i = 0; i &lt; numCourses; i++)\n'
        '            adjacency.add(new ArrayList&lt;&gt;());\n'
        '        // 对应每个节点的访问记录，标记是否已经访问过\n'
        '        // 0：未被访问过\n'
        '        // -1：已被其他节点为起点的遍历访问\n'
        '        // 1：已被当前节点为起点的遍历访问\n'
        '        int[] flags = new int[numCourses];\n'
        '        for (int[] cp : prerequisites)\n'
        '            // 将需要先学的课程的值得到，该值对应的邻接表的位置\n'
        '            // 就是该节点的位置\n'
        '            // 并将前置课程学习完后才能学习的课程加入到该位置\n'
        '            adjacency.get(cp[1]).add(cp[0]);\n'
        '        for (int i = 0; i &lt; numCourses; i++)\n'
        '            // 循环遍历以不同节点为起点的dfs 只要返回false，\n'
        '            // if成立即说明有环，返回false\n'
        '            if (!dfs(adjacency, flags, i)) return false;\n'
        '        return true;\n'
        '    }\n'
        '\n'
        '    private boolean dfs(List&lt;List&lt;Integer&gt;&gt; adjacency,\n'
        '                        int[] flags, int i) {\n'
        '        if (flags[i] == 1) return false;\n'
        '        if (flags[i] == -1) return true;\n'
        '        // 如果未被访问过，则标记\n'
        '        flags[i] = 1;\n'
        '        // 然后遍历对应位置的后续学习课程\n'
        '        for (Integer j : adjacency.get(i))\n'
        '            if (!dfs(adjacency, flags, j)) return false;\n'
        '        flags[i] = -1;\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'BFS拓扑排序：入度为0的课先学，BFS过程中减后继入度，最后 count==numCourses 则无环。<br>'
    'DFS三色标记：遍历过程中遇到状态为1（正在访问中）的节点说明存在环。<br>'
    '两者都能检测有向图中的环，BFS拓扑更直观，DFS三色标记更省空间（无需维护队列）。')

# ============================================================
# 3. 检测循环依赖
# ============================================================
p = '检测循环依赖'
d = make_deck(1747301503, f'算法::图::{p}')
add_basic(d, make_front(p, '题干'),
    '给定 n 个项目及其依赖关系，判断是否存在循环依赖。'
    '依赖关系 prerequisites[i]=[a,b] 表示项目 a 依赖于项目 b（b 完成后才能进行 a）。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(V+E)}} — 构建图+BFS遍历<br>'
    '空间：{{c2::O(V+E)}} — 邻接表和入度数组')

add_basic(d, make_front(p, '题解(BFS拓扑排序)'),
    'BFS拓扑排序：入度为0的节点入队，BFS出队顺序即拓扑序列，若结果集大小不等于n则有环。<br>'
    + code(
        'class Solution {\n'
        '    public List&lt;Integer&gt; haveCircularDependency(int n,\n'
        '            List&lt;List&lt;Integer&gt;&gt; prerequisites) {\n'
        '        List&lt;List&lt;Integer&gt;&gt; g = new ArrayList&lt;&gt;();\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            g.add(new ArrayList&lt;&gt;());\n'
        '        }\n'
        '        int[] indeg = new int[n];\n'
        '        List&lt;Integer&gt; res = new ArrayList&lt;&gt;();\n'
        '\n'
        '        for (List&lt;Integer&gt; pre : prerequisites) {\n'
        '            int a = pre.get(0), b = pre.get(1);\n'
        '            g.get(a).add(b);\n'
        '            indeg[b]++;\n'
        '        }\n'
        '\n'
        '        Queue&lt;Integer&gt; q = new LinkedList&lt;&gt;();\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            if (indeg[i] == 0) q.offer(i);\n'
        '        }\n'
        '\n'
        '        while (!q.isEmpty()) {\n'
        '            int t = q.poll();\n'
        '            res.add(t);\n'
        '            for (int j : g.get(t)) {\n'
        '                indeg[j]--;\n'
        '                if (indeg[j] == 0) {\n'
        '                    q.offer(j);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '\n'
        '        if (res.size() == n) return res;\n'
        '        else return new ArrayList&lt;&gt;();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '本质同课程表：BFS拓扑排序判断DAG。<br>'
    '若有循环依赖，环中所有节点的入度永不为0，无法入队。<br>'
    '最终 res.size() != n 则说明存在环。<br>'
    '也可用DFS三色标记法：遇到状态为1（正在访问中）的节点则有环。')

# ============================================================
# 4. 课程表 II
# ============================================================
p = '课程表 II'
d = make_deck(1747301504, f'算法::图::{p}')
add_basic(d, make_front(p, '题干'),
    '返回你为了学完所有课程所安排的学习顺序。'
    '如果有多个正确的顺序，返回任意一种。如果不可能完成所有课程，返回空数组。'
    + img('image 1.png') + img('image 2.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(V+E)}} — BFS遍历所有顶点和边<br>'
    '空间：{{c2::O(V+E)}} — 邻接表+入度数组+结果数组')

add_basic(d, make_front(p, '题解(BFS拓扑排序)'),
    'BFS拓扑排序+记录顺序：在课程表I的基础上，出队时将节点加入结果数组，若完成数不等于总课程数则返回空数组。<br>'
    + code(
        'class Solution {\n'
        '    public int[] findOrder(int numCourses, int[][] prerequisites) {\n'
        '        // 1.课号和对应的入度\n'
        '        Map&lt;Integer, Integer&gt; inDegree = new HashMap&lt;&gt;();\n'
        '        // 将所有的课程先放入\n'
        '        for (int i = 0; i &lt; numCourses; i++) {\n'
        '            inDegree.put(i, 0);\n'
        '        }\n'
        '        // 2.依赖关系, 依赖当前课程的后序课程\n'
        '        Map&lt;Integer, List&lt;Integer&gt;&gt; adj = new HashMap&lt;&gt;();\n'
        '\n'
        '        // 初始化入度和依赖关系\n'
        '        // 入度：指明有几个前置任务  依赖关系：指明前置任务具体是啥\n'
        '        for (int[] relate : prerequisites) {\n'
        '            // (3,0), 想学3号课程要先完成0号课程, 更新3号课程的入度和0号课程的依赖(邻接表)\n'
        '            int cur = relate[1];\n'
        '            int next = relate[0];\n'
        '            // 1.更新入度\n'
        '            inDegree.put(next, inDegree.get(next) + 1);\n'
        '            // 2.当前节点的邻接表\n'
        '            if (!adj.containsKey(cur)) {\n'
        '                adj.put(cur, new ArrayList&lt;&gt;());\n'
        '            }\n'
        '            adj.get(cur).add(next);\n'
        '        }\n'
        '\n'
        '        // 3.BFS, 将入度为0的课程放入队列, 队列中的课程就是没有先修, 可以学的课程\n'
        '        Queue&lt;Integer&gt; q = new LinkedList&lt;&gt;();\n'
        '        for (int key : inDegree.keySet()) {\n'
        '            if (inDegree.get(key) == 0) {\n'
        '                q.offer(key);\n'
        '            }\n'
        '        }\n'
        '\n'
        '        int[] res = new int[numCourses];\n'
        '        int i = 0;\n'
        '        // 取出一个节点, 对应学习这门课程.\n'
        '        // 遍历当前邻接表, 更新其入度; 更新之后查看入度, 如果为0, 加入到队列\n'
        '        while (!q.isEmpty()) {\n'
        '            // 从这里取出来的节点入度都为0\n'
        '            int cur = q.poll();\n'
        '            // 在这就要更新，因为最后一个没有任何依赖关系的节点是不存在与邻接表中的，他就是结果集\n'
        '            // 的最后一个节点，所以要在这就加入进去\n'
        '            res[i++] = cur;\n'
        '            // 遍历当前课程的邻接表, 更新后继节点的入度\n'
        '            // 入度为0，但又不存在邻接表中说明没有依赖关系即没有后续了\n'
        '            if (!adj.containsKey(cur)) {\n'
        '                continue;\n'
        '            }\n'
        '            List&lt;Integer&gt; successorList = adj.get(cur);\n'
        '            // 更新入度列表，将新的入度更新进去，并将入度为0的加入队列\n'
        '            for (int k : successorList) {\n'
        '                inDegree.put(k, inDegree.get(k) - 1);\n'
        '                if (inDegree.get(k) == 0) {\n'
        '                    q.offer(k);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        // 如果存在回路关系，我们遍历当进行消除入度后，如果还存在入度不为0的就说明存在环\n'
        '        for (int key : inDegree.keySet()) {\n'
        '            if (inDegree.get(key) != 0) {\n'
        '                return new int[0];\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '与课程表 I 的唯一区别：需要记录排序结果。<br>'
    'BFS出队顺序天然构成拓扑排序，只需在出队时将节点加入结果数组。<br>'
    '最后判断：若 index == numCourses 则返回结果数组，否则返回 new int[0]。')

if __name__ == '__main__':
    print(build('../../牌组/图并查集拓扑.apkg'))

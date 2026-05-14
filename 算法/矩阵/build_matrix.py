"""Build APKG for 矩阵 (Matrix). 14 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301300, '算法::矩阵::原理通识')
add_basic(d0, '矩阵遍历模式',
    '1. 螺旋遍历：定义上下左右四边界，按右->下->左->上顺序循环，每完成一个方向收缩对应边界<br>'
    '2. 对角线遍历：每条对角线的行列坐标和为定值，交替 x 从大到小 / y 从大到小<br>'
    '3. 右上角搜索：matrix[i][j] 相当于二叉搜索树的根节点，比 target 大则删列(j--)，比 target 小则删行(i++)')
add_cloze(d0, '原地旋转两种方法',
    '1. 四元交换法：matrix[start][start+j], matrix[end-j][start], matrix[end][end-j], matrix[start+j][end] 四元素{{c1::顺时针}}交换<br>'
    '2. 翻转法：先沿{{c2::反对角线(右上-左下)}}翻转，再沿{{c3::水平中线}}上下翻转 = 顺时针旋转90度')
add_basic(d0, '网格 DFS/BFS 模板',
    '方向数组：int[][] dirs = {{1,0},{-1,0},{0,1},{0,-1}}<br>'
    '标记已访问：修改原值（如 1->2）或使用 visited 布尔数组<br>'
    '防止越界：检查 i,j 是否在 [0, rows) 和 [0, cols) 范围内<br>'
    '关键技巧：从边界开始遍历（被围绕的区域），逆向标记不被包围的区域')

# ============================================================
# 1. 有序矩阵中第K小的元素
# ============================================================
p = '有序矩阵中第K小的元素'
d = make_deck(1747301301, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 n x n 矩阵，其中每行和每列元素均按升序排序，找到矩阵中第 k 小的元素。'
    '注意：它是排序后的第 k 小元素，而不是第 k 个不同的元素。')

add_cloze(d, make_front(p, '复杂度'),
    '小根堆：时间 {{c1::O(k log n)}}，空间 {{c2::O(n)}} -- 堆中最多 n 行各一个元素')

add_basic(d, make_front(p, '题解(小根堆+归并)'),
    '小根堆+归并思想：每行第一个入队，每次弹出最小值后该行右移，k-1次后堆顶即答案。<br>'
    + code(
        'class Solution {\n'
        '    public int kthSmallest(int[][] matrix, int k) {\n'
        '        PriorityQueue&lt;int[]&gt; queue = new PriorityQueue&lt;&gt;((n1, n2) ->\n'
        '            matrix[n1[0]][n1[1]] - matrix[n2[0]][n2[1]]);\n'
        '        int len = matrix.length;\n'
        '        for (int i = 0; i &lt; len; i++)\n'
        '            queue.offer(new int[]{i, 0});\n'
        '        while (--k &gt; 0) {\n'
        '            int[] min = queue.poll();\n'
        '            int x = min[0], y = min[1] + 1;\n'
        '            if (y &lt; len)\n'
        '                queue.offer(new int[]{x, y});\n'
        '        }\n'
        '        int[] min = queue.poll();\n'
        '        return matrix[min[0]][min[1]];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '归并思想：每行的第一个元素是当前行最小的，用优先队列维护各行当前最小元素的竞争。<br>'
    '队列中存储 (行号, 列号)，比较器用 matrix[row][col] 的值。<br>'
    '每次弹出后，将该行的下一个元素（col+1）入队。弹出 k 次即为答案。')

# ============================================================
# 2. 省份数量
# ============================================================
p = '省份数量'
d = make_deck(1747301302, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '有 n 个城市，其中一些彼此相连，另一些没有相连。省份是一组直接或间接相连的城市，组内不含其他没有相连的城市。'
    '给定 n x n 矩阵 isConnected，isConnected[i][j]=1 表示第 i 个城市和第 j 个城市直接相连。返回矩阵中省份的数量。')

add_cloze(d, make_front(p, '复杂度'),
    '并查集：时间 {{c1::O(n^2 * alpha(n))}}，空间 {{c2::O(n)}} -- father 映射表')

add_basic(d, make_front(p, '题解(并查集)'),
    '并查集模板：add/merge/findAnc，遍历左下角矩阵合并连通节点，连通分量数即省份数。<br>'
    + code(
        'class Solution {\n'
        '    public int findCircleNum(int[][] isConnected) {\n'
        '        UnionFind uf = new UnionFind();\n'
        '        int n = isConnected.length;\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            uf.add(i);\n'
        '            for (int j = 0; j &lt; i; j++) {\n'
        '                if (isConnected[i][j] == 1) {\n'
        '                    uf.merge(i, j);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return uf.getProvinces();\n'
        '    }\n'
        '\n'
        '    class UnionFind {\n'
        '        Map&lt;Integer, Integer&gt; father;\n'
        '        int numsOfProvince;\n'
        '\n'
        '        public UnionFind() {\n'
        '            this.father = new HashMap&lt;&gt;();\n'
        '            this.numsOfProvince = 0;\n'
        '        }\n'
        '\n'
        '        public void add(int x) {\n'
        '            if (!father.containsKey(x)) {\n'
        '                father.put(x, null);\n'
        '                numsOfProvince++;\n'
        '            }\n'
        '        }\n'
        '\n'
        '        public void merge(int x, int y) {\n'
        '            int rootX = findAnc(x);\n'
        '            int rootY = findAnc(y);\n'
        '            if (rootX != rootY) {\n'
        '                father.put(rootX, rootY);\n'
        '                numsOfProvince--;\n'
        '            }\n'
        '        }\n'
        '\n'
        '        public int findAnc(int x) {\n'
        '            int rootX = x;\n'
        '            while (father.get(rootX) != null) {\n'
        '                rootX = father.get(rootX);\n'
        '            }\n'
        '            while (father.get(x) != null) {\n'
        '                int old_father = father.get(x);\n'
        '                father.put(x, rootX);\n'
        '                x = old_father;\n'
        '            }\n'
        '            return rootX;\n'
        '        }\n'
        '\n'
        '        public boolean isConnected(int x, int y) {\n'
        '            return findAnc(x) == findAnc(y);\n'
        '        }\n'
        '\n'
        '        public int getProvinces() {\n'
        '            return numsOfProvince;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '并查集核心操作：<br>'
    '1. add(x)：加入孤立节点，连通分量数+1<br>'
    '2. merge(x,y)：若两个节点祖先不同，将一个祖先指向另一个，连通分量数-1<br>'
    '3. findAnc(x)：查找祖先 + 路径压缩，将所有子节点直接挂到根节点<br>'
    '遍历左下角矩阵即可，因为 isConnected[i][j]==isConnected[j][i]。')

# ============================================================
# 3. 矩阵置零
# ============================================================
p = '矩阵置零'
d = make_deck(1747301303, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 m x n 的矩阵，如果一个元素为 0，则将其所在行和列的所有元素都设为 0。请使用原地算法。'
    '进阶：一个直观的解决方案是使用 O(mn) 的额外空间，一个简单的改进方案是使用 O(m+n) 的额外空间。'
    '你能想出一个仅使用常量空间的解决方案吗？')

add_cloze(d, make_front(p, '复杂度'),
    'O(1)空间：时间 {{c1::O(mn)}}，空间 {{c2::O(1)}}<br>'
    'O(m+n)空间：时间 {{c3::O(mn)}}，空间 {{c4::O(m+n)}}')

add_basic(d, make_front(p, '题解(O(1)空间)'),
    'O(1)空间：用第一行和第一列作为标志位，rowZero/colZero 单独记录第一行/列自身的0。<br>'
    + code(
        'class Solution {\n'
        '    public void setZeroes(int[][] matrix) {\n'
        '        int m = matrix.length, n = matrix[0].length;\n'
        '        boolean rowZero = false, colZero = false;\n'
        '        // Mark if first column has zero\n'
        '        for (int i = 0; i &lt; m; i++) {\n'
        '            if (matrix[i][0] == 0)\n'
        '                colZero = true;\n'
        '        }\n'
        '        // Mark if first row has zero\n'
        '        for (int j = 0; j &lt; n; j++) {\n'
        '            if (matrix[0][j] == 0)\n'
        '                rowZero = true;\n'
        '        }\n'
        '        // Use first row/col as markers\n'
        '        for (int i = 1; i &lt; m; i++) {\n'
        '            for (int j = 1; j &lt; n; j++) {\n'
        '                if (matrix[i][j] == 0) {\n'
        '                    matrix[0][j] = matrix[i][0] = 0;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        // Set zeros based on markers\n'
        '        for (int i = 1; i &lt; m; i++) {\n'
        '            for (int j = 1; j &lt; n; j++) {\n'
        '                if (matrix[i][0] == 0 || matrix[0][j] == 0) {\n'
        '                    matrix[i][j] = 0;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        // Fill first row\n'
        '        if (rowZero) {\n'
        '            for (int j = 0; j &lt; n; j++)\n'
        '                matrix[0][j] = 0;\n'
        '        }\n'
        '        // Fill first column\n'
        '        if (colZero) {\n'
        '            for (int i = 0; i &lt; m; i++)\n'
        '                matrix[i][0] = 0;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'O(1)空间的精髓：复用矩阵的第一行和第一列作为标记数组。<br>'
    '但第一行和第一列自身也可能有0，所以用 rowZero 和 colZero 两个布尔变量单独记录。<br>'
    '顺序很重要：先标记 -> 再置零（1..m, 1..n 区域）-> 最后处理第一行和第一列。')

# ============================================================
# 4. 搜索二维矩阵
# ============================================================
p = '搜索二维矩阵'
d = make_deck(1747301304, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个高效的算法来判断 m x n 矩阵中，是否存在一个目标值。'
    '该矩阵具有如下特性：每行中的整数从左到右按升序排列；每行的第一个整数大于前一行的最后一个整数。')

add_cloze(d, make_front(p, '复杂度'),
    '右上角搜索：时间 {{c1::O(m+n)}}，空间 {{c2::O(1)}}<br>'
    '二分查找(展平)：时间 {{c3::O(log(mn))}}，空间 {{c4::O(1)}}')

add_basic(d, make_front(p, '题解(右上角搜索)'),
    '右上角是BST的根：比target大则左移(j--)，小则下移(i++)。<br>'
    + code(
        'class Solution {\n'
        '    public boolean searchMatrix(int[][] matrix, int target) {\n'
        '        if (matrix.length == 0 && matrix[0].length == 0)\n'
        '            return false;\n'
        '        int i = 0, j = matrix[0].length - 1;\n'
        '        while (i &lt; matrix.length && j &gt;= 0) {\n'
        '            if (target &lt; matrix[i][j])\n'
        '                j--;\n'
        '            else if (target &gt; matrix[i][j])\n'
        '                i++;\n'
        '            else\n'
        '                return true;\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '两种思路：<br>'
    '1. 右上角搜索 O(m+n)：将矩阵视为 BST，右上角为根，向左变小，向下变大。<br>'
    '2. 展平二分 O(log(mn))：将二维坐标映射为一维索引 mid -> matrix[mid/n][mid%n]。<br>'
    '本题每行首元素大于上一行尾元素，所以两种方法都适用。')

# ============================================================
# 5. 搜索二维矩阵 II
# ============================================================
p = '搜索二维矩阵 II'
d = make_deck(1747301305, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个高效的算法来搜索 m x n 矩阵 matrix 中的一个目标值 target。'
    '该矩阵具有以下特性：每行的元素从左到右升序排列；每列的元素从上到下升序排列。')

add_cloze(d, make_front(p, '复杂度'),
    '右上角搜索：时间 {{c1::O(m+n)}}，空间 {{c2::O(1)}}<br>'
    '逐行二分：时间 {{c3::O(m log n)}}，空间 {{c4::O(1)}}')

add_basic(d, make_front(p, '题解(右上角搜索)'),
    '比 target 大 -> 排除当前列(j--)，比 target 小 -> 排除当前行(i++)。<br>'
    + code(
        'class Solution {\n'
        '    public boolean searchMatrix(int[][] matrix, int target) {\n'
        '        if (matrix.length == 0 && matrix[0].length == 0)\n'
        '            return false;\n'
        '        int i = 0, j = matrix[0].length - 1;\n'
        '        while (i &lt; matrix.length && j &gt;= 0) {\n'
        '            if (matrix[i][j] &gt; target) {\n'
        '                j--;\n'
        '            } else if (matrix[i][j] &lt; target) {\n'
        '                i++;\n'
        '            } else {\n'
        '                return true;\n'
        '            }\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '与搜索二维矩阵的区别：本题只保证每行每列有序，不保证行间严格递增，所以不能用展平二分。<br>'
    '右上角搜索本质：每次排除一行或一列，最多 m+n 步。<br>'
    '逐行二分是另一种备选方案，在 m 远小于 n 时更优。')

# ============================================================
# 6. 岛屿数量
# ============================================================
p = '岛屿数量'
d = make_deck(1747301306, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个由 1（陆地）和 0（水）组成的二维网格，请你计算网格中岛屿的数量。'
    '岛屿总是被水包围，并且每座岛屿只能由水平方向/竖直方向上相邻的陆地连接形成。')

add_cloze(d, make_front(p, '复杂度'),
    'DFS：时间 {{c1::O(mn)}}，空间 {{c2::O(mn)}} -- 递归栈最坏情况')

add_basic(d, make_front(p, '题解(DFS)'),
    "网格DFS模板：三种状态(0=海洋, 1=未遍历陆地, 2=已遍历陆地)，遇'1'启动DFS标记整个岛屿。<br>"
    + code(
        'class Solution {\n'
        '    public int numIslands(char[][] grid) {\n'
        '        int count = 0;\n'
        '        for (int i = 0; i &lt; grid.length; i++) {\n'
        '            for (int j = 0; j &lt; grid[0].length; j++) {\n'
        "                if (grid[i][j] == '1') {\n"
        '                    dfs(grid, i, j);\n'
        '                    count++;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return count;\n'
        '    }\n'
        '\n'
        '    public void dfs(char[][] grid, int i, int j) {\n'
        '        if (i &lt; 0 || j &lt; 0 || i &gt;= grid.length\n'
        "            || j &gt;= grid[0].length || grid[i][j] == '0'\n"
        "            || grid[i][j] == '2')\n"
        '            return;\n'
        "        grid[i][j] = '2';\n"
        '        dfs(grid, i + 1, j);\n'
        '        dfs(grid, i - 1, j);\n'
        '        dfs(grid, i, j + 1);\n'
        '        dfs(grid, i, j - 1);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '网格 DFS 模板：<br>'
    '1. 边界检查：越界、海洋(0)、已访问(2) -> return<br>'
    '2. 标记当前为已访问(2)，防止重复遍历死循环<br>'
    '3. 四方向递归<br>'
    "每次从'1'启动 DFS 后 count++，代表发现一个新岛屿。BFS 同理，只是用队列代替递归。")

# ============================================================
# 7. 螺旋矩阵
# ============================================================
p = '螺旋矩阵'
d = make_deck(1747301307, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个 m 行 n 列的矩阵 matrix，请按照顺时针螺旋顺序，返回矩阵中的所有元素。'
    + img('image.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(mn)}} -- 每个元素访问一次<br>空间：{{c2::O(1)}} -- 除结果列表外')

add_basic(d, make_front(p, '题解(边界收缩)'),
    '边界收缩法：右->下->左->上循环，每完成一个方向立即收缩对应边界并检查是否交叉。<br>'
    + code(
        'class Solution {\n'
        '    public List&lt;Integer&gt; spiralOrder(int[][] matrix) {\n'
        '        if (matrix == null || matrix[0].length == 0)\n'
        '            return null;\n'
        '        List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '        int up = 0;\n'
        '        int under = matrix.length - 1;\n'
        '        int left = 0;\n'
        '        int right = matrix[0].length - 1;\n'
        '        while (true) {\n'
        '            // Right\n'
        '            for (int i = left; i &lt;= right; i++)\n'
        '                list.add(matrix[up][i]);\n'
        '            if (++up &gt; under)\n'
        '                break;\n'
        '            // Down\n'
        '            for (int i = up; i &lt;= under; i++)\n'
        '                list.add(matrix[i][right]);\n'
        '            if (--right &lt; left)\n'
        '                break;\n'
        '            // Left\n'
        '            for (int i = right; i &gt;= left; i--)\n'
        '                list.add(matrix[under][i]);\n'
        '            if (--under &lt; up)\n'
        '                break;\n'
        '            // Up\n'
        '            for (int i = under; i &gt;= up; i--)\n'
        '                list.add(matrix[i][left]);\n'
        '            if (++left &gt; right)\n'
        '                break;\n'
        '        }\n'
        '        return list;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '边界收缩法：定义 up, under, left, right 四个边界指针。<br>'
    '每次完成一个方向的遍历后，立即收缩对应边界（如 ++up），并检查是否与对侧边界交叉。<br>'
    '关键：使用 ++up &gt; under 而非 up++ &gt; under，确保先收缩再判断。<br>'
    '同一模板稍作修改即可用于螺旋矩阵 II（填充数字）。')

# ============================================================
# 8. 螺旋矩阵 II
# ============================================================
p = '螺旋矩阵 II'
d = make_deck(1747301308, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个正整数 n，生成一个包含 1 到 n^2 所有元素，且元素按顺时针顺序螺旋排列的 n x n 正方形矩阵 matrix。'
    + img('image 1.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n^2)}} -- 填充 n^2 个格子<br>空间：{{c2::O(1)}} -- 除结果矩阵外')

add_basic(d, make_front(p, '题解(边界收缩)'),
    '与螺旋矩阵I对称：四个方向填充数字，边界逐步收缩，while(num&lt;=n*n)控制。<br>'
    + code(
        'class Solution {\n'
        '    public int[][] generateMatrix(int n) {\n'
        '        int left = 0, right = n - 1, top = 0, low = n - 1;\n'
        '        int[][] res = new int[n][n];\n'
        '        int num = 1, target = n * n;\n'
        '        while (num &lt;= target) {\n'
        '            // Left to right\n'
        '            for (int i = left; i &lt;= right; i++)\n'
        '                res[top][i] = num++;\n'
        '            top++;\n'
        '            // Top to bottom\n'
        '            for (int i = top; i &lt;= low; i++)\n'
        '                res[i][right] = num++;\n'
        '            right--;\n'
        '            // Right to left\n'
        '            for (int i = right; i &gt;= left; i--)\n'
        '                res[low][i] = num++;\n'
        '            low--;\n'
        '            // Bottom to top\n'
        '            for (int i = low; i &gt;= top; i--)\n'
        '                res[i][left] = num++;\n'
        '            left++;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '与螺旋矩阵 I 的代码高度对称：<br>'
    '螺旋矩阵 I：读取数据到 list，break 方式退出<br>'
    '螺旋矩阵 II：写入数据到矩阵，num &lt;= target 方式退出<br>'
    '核心都是四个方向 + 边界收缩。正方形矩阵无需 break 检查，直接 while(num&lt;=n*n) 即可。')

# ============================================================
# 9. 最小路径和
# ============================================================
p = '最小路径和'
d = make_deck(1747301309, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含非负整数的 m x n 网格 grid，请找出一条从左上角到右下角的路径，使得路径上的数字总和为最小。'
    '每次只能向下或者向右移动一步。')

add_cloze(d, make_front(p, '复杂度'),
    'DP(原地)：时间 {{c1::O(mn)}}，空间 {{c2::O(1)}} -- 原地修改 grid<br>'
    'DP(新建)：时间 {{c3::O(mn)}}，空间 {{c4::O(mn)}}')

add_basic(d, make_front(p, '题解(DP原地)'),
    'dp[i][j] = min(上,左) + grid[i][j]，分四种情况：非边界、仅第一行、仅第一列、起点。<br>'
    + code(
        'class Solution {\n'
        '    public int minPathSum(int[][] grid) {\n'
        '        for (int i = 0; i &lt; grid.length; i++) {\n'
        '            for (int j = 0; j &lt; grid[0].length; j++) {\n'
        '                if (i != 0 && j != 0)\n'
        '                    grid[i][j] = grid[i][j]\n'
        '                        + Math.min(grid[i - 1][j], grid[i][j - 1]);\n'
        '                else if (i == 0 && j != 0)\n'
        '                    grid[i][j] = grid[i][j] + grid[i][j - 1];\n'
        '                else if (i != 0 && j == 0)\n'
        '                    grid[i][j] = grid[i][j] + grid[i - 1][j];\n'
        '            }\n'
        '        }\n'
        '        return grid[grid.length - 1][grid[0].length - 1];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '经典矩阵 DP 模板：dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]<br>'
    '可原地修改 grid，因为每个位置只依赖左和上（已处理过的位置），不会影响后续计算。<br>'
    '第一行只能从左边来，第一列只能从上面来，需要单独处理。起点 grid[0][0] 保持原值。')

# ============================================================
# 10. 二维数组中的查找
# ============================================================
p = '二维数组中的查找'
d = make_deck(1747301310, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '在一个 n * m 的二维数组中，每一行都按照从左到右递增的顺序排序，每一列都按照从上到下递增的顺序排序。'
    '请完成一个高效的函数，输入这样的一个二维数组和一个整数，判断数组中是否含有该整数。')

add_cloze(d, make_front(p, '复杂度'),
    '右上角搜索：时间 {{c1::O(m+n)}}，空间 {{c2::O(1)}}')

add_basic(d, make_front(p, '题解(右上角搜索)'),
    '右上角BST：比target小则i++删行，大则j--删列。<br>'
    + code(
        'class Solution {\n'
        '    public boolean findNumberIn2DArray(int[][] matrix, int target) {\n'
        '        if (matrix.length == 0 || matrix[0].length == 0)\n'
        '            return false;\n'
        '        int i = 0, j = matrix[0].length - 1;\n'
        '        while (i &lt; matrix.length && j &gt;= 0) {\n'
        '            if (matrix[i][j] &lt; target)\n'
        '                i++;\n'
        '            else if (matrix[i][j] &gt; target)\n'
        '                j--;\n'
        '            else\n'
        '                return true;\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '与搜索二维矩阵 II 完全相同的问题（剑指 Offer 版本）。<br>'
    '右上角搜索 O(m+n)：遇到比 target 小的元素删除整行(i++)，遇到大的删除整列(j--)。<br>'
    '核心：将矩阵视为二叉搜索树，右上角为根节点。')

# ============================================================
# 11. 旋转图像
# ============================================================
p = '旋转图像'
d = make_deck(1747301311, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 n x n 的二维矩阵 matrix 表示一个图像。请你将图像顺时针旋转 90 度。'
    '你必须在原地旋转图像，这意味着你需要直接修改输入的二维矩阵。请不要使用另一个矩阵来旋转图像。'
    + img('image 2.png') + img('image 3.png'))

add_cloze(d, make_front(p, '复杂度'),
    '四元交换：时间 {{c1::O(n^2)}}，空间 {{c2::O(1)}}<br>'
    '翻转法：时间 {{c3::O(n^2)}}，空间 {{c4::O(1)}}')

add_basic(d, make_front(p, '题解(四元交换)'),
    '分层处理：外层控制圈数(i)，内层旋转当前圈四个位置，每次交换4个元素。<br>'
    + img('image 2.png') + img('image 3.png')
    + code(
        'class Solution {\n'
        '    public void rotate(int[][] matrix) {\n'
        '        int len = matrix.length;\n'
        '        for (int i = 0; i &lt; len / 2; i++) {\n'
        '            int start = i;\n'
        '            int end = len - i - 1;\n'
        '            for (int j = 0; j &lt; end - start; j++) {\n'
        '                int temp = matrix[start][start + j];\n'
        '                matrix[start][start + j] = matrix[end - j][start];\n'
        '                matrix[end - j][start] = matrix[end][end - j];\n'
        '                matrix[end][end - j] = matrix[start + j][end];\n'
        '                matrix[start + j][end] = temp;\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(翻转法)'),
    '先沿反对角线翻转，再沿水平中线翻转 = 顺时针旋转90度。<br>'
    + img('image 4.png')
    + code(
        'class Solution {\n'
        '    public void rotate(int[][] matrix) {\n'
        '        if (matrix.length == 0\n'
        '            || matrix.length != matrix[0].length) {\n'
        '            return;\n'
        '        }\n'
        '        int nums = matrix.length;\n'
        '        // Flip along anti-diagonal\n'
        '        for (int i = 0; i &lt; nums; ++i) {\n'
        '            for (int j = 0; j &lt; nums - i; ++j) {\n'
        '                int temp = matrix[i][j];\n'
        '                matrix[i][j] = matrix[nums - 1 - j][nums - 1 - i];\n'
        '                matrix[nums - 1 - j][nums - 1 - i] = temp;\n'
        '            }\n'
        '        }\n'
        '        // Flip along horizontal midline\n'
        '        for (int i = 0; i &lt; (nums &gt;&gt; 1); ++i) {\n'
        '            for (int j = 0; j &lt; nums; ++j) {\n'
        '                int temp = matrix[i][j];\n'
        '                matrix[i][j] = matrix[nums - 1 - i][j];\n'
        '                matrix[nums - 1 - i][j] = temp;\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 12. 对角线遍历
# ============================================================
p = '对角线遍历'
d = make_deck(1747301312, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个大小为 m x n 的矩阵 mat，请以对角线遍历的顺序，用一个数组返回这个矩阵中的所有元素。'
    + img('image 5.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(mn)}} -- 每个元素访问一次<br>空间：{{c2::O(1)}} -- 除结果数组外')

add_basic(d, make_front(p, '题解(坐标和规律)'),
    '每条对角线坐标和为定值i，bXFlag交替方向，x从大到小则y从小到大。<br>'
    + code(
        'class Solution {\n'
        '    public int[] findDiagonalOrder(int[][] matrix) {\n'
        "        if (matrix == null || matrix.length == 0)\n"
        '            return new int[0];\n'
        '        int m = matrix.length;\n'
        '        int n = matrix[0].length;\n'
        '        int[] nums = new int[m * n];\n'
        '        int k = 0;\n'
        '        boolean bXFlag = true;\n'
        '        for (int i = 0; i &lt; m + n; i++) {\n'
        '            int pm = bXFlag ? m : n;\n'
        '            int pn = bXFlag ? n : m;\n'
        '            int x = (i &lt; pm) ? i : pm - 1;\n'
        '            int y = i - x;\n'
        '            while (x &gt;= 0 && y &lt; pn) {\n'
        '                nums[k++] = bXFlag ? matrix[x][y]\n'
        '                                     : matrix[y][x];\n'
        '                x--;\n'
        '                y++;\n'
        '            }\n'
        '            bXFlag = !bXFlag;\n'
        '        }\n'
        '        return nums;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '对角线遍历规律：<br>'
    '1. 对角线条数 = m + n（坐标和从 0 到 m+n-1）<br>'
    '2. 每条对角线上坐标和为定值 i，x 从大到小则 y 从小到大（或反过来）<br>'
    '3. 奇偶趟方向交替，用 bXFlag 标识<br>'
    '4. 起始坐标确定：x = min(i, pm-1)，y = i - x')

# ============================================================
# 13. 不同路径 II
# ============================================================
p = '不同路径 II'
d = make_deck(1747301313, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '一个机器人位于一个 m x n 网格的左上角。机器人每次只能向下或者向右移动一步。'
    '机器人试图达到网格的右下角。现在考虑网格中有障碍物，障碍物在网格中用 1 表示。'
    '那么从左上角到右下角将会有多少条不同的路径？')

add_cloze(d, make_front(p, '复杂度'),
    'DP：时间 {{c1::O(mn)}}，空间 {{c2::O(mn)}}<br>'
    'DFS+记忆化：时间 {{c3::O(mn)}}，空间 {{c4::O(mn)}}')

add_basic(d, make_front(p, '题解(DP)'),
    'dp[i][j] = dp[i-1][j] + dp[i][j-1]，障碍物位置 dp=0。<br>'
    + code(
        'class Solution {\n'
        '    public int uniquePathsWithObstacles(int[][] grid) {\n'
        '        if (grid == null || grid.length == 0)\n'
        '            return 0;\n'
        '        int m = grid.length;\n'
        '        int n = grid[0].length;\n'
        '        int[][] dp = new int[m][n];\n'
        '        // Init first column\n'
        '        for (int i = 0; i &lt; m && grid[i][0] == 0; i++) {\n'
        '            dp[i][0] = 1;\n'
        '        }\n'
        '        // Init first row\n'
        '        for (int j = 0; j &lt; n && grid[0][j] == 0; j++) {\n'
        '            dp[0][j] = 1;\n'
        '        }\n'
        '        for (int i = 1; i &lt; m; i++) {\n'
        '            for (int j = 1; j &lt; n; j++) {\n'
        '                if (grid[i][j] != 1)\n'
        '                    dp[i][j] = dp[i - 1][j] + dp[i][j - 1];\n'
        '            }\n'
        '        }\n'
        '        return dp[m - 1][n - 1];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '不同路径 I 的升级版，增加了障碍物。<br>'
    '初始化：第一行和第一列遇到障碍物后，之后的位置都不可达（dp=0），所以用 && grid[i][0]==0 控制。<br>'
    '转移：dp[i][j] = grid[i][j]==1 ? 0 : dp[i-1][j] + dp[i][j-1]。<br>'
    '障碍物位置路径数为 0，因为不能经过障碍物。')

# ============================================================
# 14. 被围绕的区域
# ============================================================
p = '被围绕的区域'
d = make_deck(1747301314, f'算法::矩阵::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个 m x n 的矩阵 board，由若干字符 X 和 O 组成，捕获所有被围绕的区域：'
    '将矩阵中被 X 围绕的 O 替换为 X，边界上的 O 以及与边界 O 相连的 O 不被围绕。')

add_cloze(d, make_front(p, '复杂度'),
    'DFS：时间 {{c1::O(mn)}}，空间 {{c2::O(mn)}} -- 递归栈')

add_basic(d, make_front(p, "题解(DFS+逆向思维)"),
    "逆向思维：从边界O出发DFS标记为'*'，剩余O->X被围绕，'*'->O还原。<br>"
    + code(
        'class Solution {\n'
        '    public void solve(char[][] board) {\n'
        '        int m = board.length;\n'
        '        int n = board[0].length;\n'
        '        // Start DFS from edge O, mark as \'*\'\n'
        '        for (int i = 0; i &lt; m; i++) {\n'
        '            for (int j = 0; j &lt; n; j++) {\n'
        '                boolean isEdge = i == 0 || j == 0\n'
        '                    || i == m - 1 || j == n - 1;\n'
        "                if (isEdge && board[i][j] == 'O')\n"
        '                    dfs(board, i, j);\n'
        '            }\n'
        '        }\n'
        '        // Second pass: capture surrounded, restore safe\n'
        '        for (int i = 0; i &lt; m; i++) {\n'
        '            for (int j = 0; j &lt; n; j++) {\n'
        "                if (board[i][j] == 'O') {\n"
        "                    board[i][j] = 'X';\n"
        '                }\n'
        "                if (board[i][j] == '*') {\n"
        "                    board[i][j] = 'O';\n"
        '                }\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '\n'
        '    public void dfs(char[][] board, int i, int j) {\n'
        '        if (i &lt; 0 || j &lt; 0 || i &gt;= board.length\n'
        "            || j &gt;= board[0].length || board[i][j] == 'X'\n"
        "            || board[i][j] == '*')\n"
        '            return;\n'
        "        board[i][j] = '*';\n"
        '        dfs(board, i - 1, j);\n'
        '        dfs(board, i + 1, j);\n'
        '        dfs(board, i, j - 1);\n'
        '        dfs(board, i, j + 1);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '逆向思维：与其找被围绕的 O，不如先标记所有与边界相连的 O（它们不会被围绕）。<br>'
    '三步走：<br>'
    "1. 从边界 O 出发 DFS，标记为中间符号 '*'<br>"
    '2. 遍历整个矩阵：剩余的 O -> X（被围绕），* -> O（还原）<br>'
    '核心：边界上的 O 及其相邻 O 永远不会被围绕，它们是与外界连通的"安全区"')

if __name__ == '__main__':
    print(build('../../牌组/算法/矩阵.apkg'))

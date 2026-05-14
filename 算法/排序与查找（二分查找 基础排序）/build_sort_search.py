"""Build APKG for 排序与查找 (Sort & Search). 13 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301000, '算法::排序与查找::原理通识')
add_basic(d0, '二分查找模板',
    '二分查找核心三要素：<br>'
    '1. 循环条件：while(left &lt;= right) — 取等号可在循环内直接return<br>'
    '2. 区间收缩：left=mid+1, right=mid-1 — 搜索区间用闭区间[left,right]<br>'
    '3. 返回值：循环内找到返回mid，循环外根据题意返回left或right')
add_cloze(d0, '二分查找「二段性」原理',
    '二段性：存在一个分界点，使得数组分为满足条件的{{c1::前半段}}和不满足条件的{{c2::后半段}}<br>'
    'mid = {{c3::left + (right - left) / 2}}<br>'
    '根据 nums[mid] 与 target 的关系，确定哪一段{{c4::必然有解}}，收缩到那一侧')
add_basic(d0, '排序算法对比',
    '归并排序：O(n log n)时间，O(n)空间，稳定排序，适合链表<br>'
    '快速排序：O(n log n)平均，O(n^2)最坏，O(log n)空间，不稳定<br>'
    '堆排序：O(n log n)时间，O(1)空间，不稳定<br>'
    '二分查找：O(log n)时间，O(1)空间，前提是数组有序')
add_basic(d0, '归并排序核心思想',
    '归并排序=分治法：将数组不断二分直到长度为1，然后两两合并。<br>'
    '实现方式：<br>'
    '1. 递归（自顶向下）：快慢指针找中点，递归排序左右，合并两个有序链表/数组<br>'
    '2. 迭代（自底向上）：从步长intv=1开始，每次合并两个长度为intv的子数组')

# ============================================================
# 1. 搜索旋转排序数组
# ============================================================
p = '搜索旋转排序数组'
d = make_deck(1747301001, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '整数数组 nums 按升序排列，在预先未知的某个下标 k 上进行了旋转。'
    '例如 [0,1,2,4,5,6,7] 在下标 3 处旋转后变为 [4,5,6,7,0,1,2]。'
    '给你旋转后的数组 nums 和一个整数 target，如果 nums 中存在 target 则返回索引，否则返回 -1。'
    '要求 O(log n) 时间复杂度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分)'),
    '核心：判断左半还是右半有序，然后判断target落在哪个区间。<br>'
    + code(
        'class Solution {\n'
        '    public int search(int[] nums, int target) {\n'
        '        int len = nums.length;\n'
        '        int left = 0, right = len - 1;\n'
        '        while (left &lt;= right) {\n'
        '            int mid = left + (right - left) / 2;\n'
        '            if (nums[mid] == target)\n'
        '                return mid;\n'
        '            // 左半部分是有序的\n'
        '            if (nums[0] &lt;= nums[mid]) {\n'
        '                if (nums[0] &lt;= target && target &lt; nums[mid])\n'
        '                    right = mid - 1;\n'
        '                else\n'
        '                    left = mid + 1;\n'
        '            } else {\n'
        '                // 右半部分是有序的\n'
        '                if (nums[mid] &lt; target && target &lt;= nums[right])\n'
        '                    left = mid + 1;\n'
        '                else\n'
        '                    right = mid - 1;\n'
        '            }\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '旋转排序数组二分核心：<br>'
    '1. 比较 nums[0] 和 nums[mid] 确定哪一半有序<br>'
    '2. 判断 target 是否在有序的那一半范围内<br>'
    '3. 若在有序范围内则收缩到有序侧，否则收缩到另一侧<br>'
    '边界条件：nums[0] &lt;= nums[mid] 用 &lt;= 处理 mid=0 的情况')

# ============================================================
# 2. 搜索旋转数组
# ============================================================
p = '搜索旋转数组'
d = make_deck(1747301002, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '与「搜索旋转排序数组」不同：数组中存在重复元素。'
    '给定一个可能存在重复元素值的数组 nums，和一个目标值 target。'
    '如果 nums 中存在 target，返回索引值最小的一个，否则返回 -1。')
add_cloze(d, make_front(p, '复杂度'),
    '平均：时间 {{c1::O(log n)}}，空间 {{c2::O(1)}}<br>'
    '最坏(全重复)：时间 {{c3::O(n)}} — 无法二分，退化为线性')
add_basic(d, make_front(p, '题解(二分+去重)'),
    '处理重复：先跳过首尾相等的元素；找到target后继续向左搜索最小索引。<br>'
    + code(
        'class Solution {\n'
        '    public int search(int[] nums, int target) {\n'
        '        int len = nums.length;\n'
        '        int left = 0, right = len - 1;\n'
        '        int res = Integer.MAX_VALUE;\n'
        '        while (left &lt;= right) {\n'
        '            // 跳过首尾重复元素\n'
        '            while (left &lt; right && nums[left] == nums[right])\n'
        '                right--;\n'
        '            int mid = left + (right - left) / 2;\n'
        '            if (nums[mid] == target) {\n'
        '                res = Math.min(res, mid);\n'
        '                right = mid - 1; // 继续向左找更小的索引\n'
        '            }\n'
        '            if (nums[left] &lt;= nums[mid]) {\n'
        '                if (nums[left] &lt;= target && target &lt;= nums[mid])\n'
        '                    right = mid - 1;\n'
        '                else\n'
        '                    left = mid + 1;\n'
        '            } else {\n'
        '                if (nums[mid] &lt;= target && target &lt;= nums[right])\n'
        '                    left = mid + 1;\n'
        '                else\n'
        '                    right = mid - 1;\n'
        '            }\n'
        '        }\n'
        '        return res == Integer.MAX_VALUE ? -1 : res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与无重复版本的核心区别：<br>'
    '1. 预处理：while(left&lt;right && nums[left]==nums[right]) right-- 跳过首尾重复<br>'
    '2. 找到 target 后不直接返回，而是记录最小值并继续向左搜索<br>'
    '3. 最坏情况（全重复数组）退化为 O(n)')

# ============================================================
# 3. 合并区间
# ============================================================
p = '合并区间'
d = make_deck(1747301003, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '以数组 intervals 表示若干个区间的集合，其中 intervals[i] = [start_i, end_i]。'
    '合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 排序开销<br>空间：{{c2::O(n)}} — 结果列表')
add_basic(d, make_front(p, '题解(排序+合并)'),
    '按左端点排序后，依次判断新区间是否与已合并区间的最后一个重叠。<br>'
    + code(
        'class Solution {\n'
        '    public int[][] merge(int[][] intervals) {\n'
        '        if (intervals.length == 0)\n'
        '            return new int[0][2];\n'
        '        // 按左端点升序排序\n'
        '        Arrays.sort(intervals, (n1, n2) -&gt; n1[0] - n2[0]);\n'
        '        List&lt;int[]&gt; res = new ArrayList&lt;&gt;();\n'
        '        for (int[] interval : intervals) {\n'
        '            // 不重叠，直接添加\n'
        '            if (res.size() == 0 || res.get(res.size() - 1)[1] &lt; interval[0])\n'
        '                res.add(interval);\n'
        '            else\n'
        '                // 重叠，合并：更新last.end = max(last.end, cur.end)\n'
        '                res.get(res.size() - 1)[1] = Math.max(res.get(res.size() - 1)[1], interval[1]);\n'
        '        }\n'
        '        return res.toArray(new int[0][]);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '区间合并模板：<br>'
    '1. 按 start 升序排序<br>'
    '2. 遍历每个区间：若不重叠(last.end &lt; cur.start)则直接加入；否则更新 last.end = max(last.end, cur.end)<br>'
    '3. 转数组：res.toArray(new int[0][])')

# ============================================================
# 4. 寻找两个正序数组的中位数
# ============================================================
p = '寻找两个正序数组的中位数'
d = make_deck(1747301004, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个大小分别为 m 和 n 的正序数组 nums1 和 nums2。'
    '找出这两个正序数组的中位数，要求时间复杂度 O(log(m+n))。'
    + img('image.png') + img('image 1.png') + img('image 2.png') + img('image 3.png'))
add_cloze(d, make_front(p, '复杂度'),
    '二分法：时间 {{c1::O(log(min(m,n)))}} — 在较短数组上二分<br>'
    '第k小法：时间 {{c2::O(log(m+n))}} — 每次排除 k/2 个元素<br>'
    '暴力合并：时间 {{c3::O(m+n)}}，空间 {{c4::O(m+n)}}')
add_basic(d, make_front(p, '题解(第k小数法)'),
    '每次排除 k/2 个元素：比较两数组第k/2位置的元素，较小的那一半之前不可能包含第k小元素。<br>'
    + code(
        'class Solution {\n'
        '    public double findMedianSortedArrays(int[] nums1, int[] nums2) {\n'
        '        int n = nums1.length;\n'
        '        int m = nums2.length;\n'
        '        // 将偶数和奇数情况合并：求第(left)小和第(right)小的平均值\n'
        '        int left = (n + m + 1) / 2;\n'
        '        int right = (n + m + 2) / 2;\n'
        '        return (getKth(nums1, 0, n - 1, nums2, 0, m - 1, left)\n'
        '                + getKth(nums1, 0, n - 1, nums2, 0, m - 1, right)) * 0.5;\n'
        '    }\n'
        '\n'
        '    private int getKth(int[] nums1, int start1, int end1,\n'
        '                       int[] nums2, int start2, int end2, int k) {\n'
        '        int len1 = end1 - start1 + 1;\n'
        '        int len2 = end2 - start2 + 1;\n'
        '        // 保证len1较短，简化空数组处理\n'
        '        if (len1 &gt; len2)\n'
        '            return getKth(nums2, start2, end2, nums1, start1, end1, k);\n'
        '        // 短数组为空，直接从长数组取\n'
        '        if (len1 == 0)\n'
        '            return nums2[start2 + k - 1];\n'
        '        // 找第1小就是取两个数组头部的较小值\n'
        '        if (k == 1)\n'
        '            return Math.min(nums1[start1], nums2[start2]);\n'
        '        // 每次排除 k/2 个元素\n'
        '        int i = start1 + Math.min(len1, k / 2) - 1;\n'
        '        int j = start2 + Math.min(len2, k / 2) - 1;\n'
        '        if (nums1[i] &gt; nums2[j])\n'
        '            return getKth(nums1, start1, end1, nums2, j + 1, end2, k - (j - start2 + 1));\n'
        '        else\n'
        '            return getKth(nums1, i + 1, end1, nums2, start2, end2, k - (i - start1 + 1));\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(逻辑遍历)'),
    '逻辑上两个数组粘连，物理上分别遍历，走到第 len/2 步即得到中位数。<br>'
    + code(
        'class Solution {\n'
        '    public double findMedianSortedArrays(int[] A, int[] B) {\n'
        '        int m = A.length;\n'
        '        int n = B.length;\n'
        '        int len = m + n;\n'
        '        int left = -1, right = -1;\n'
        '        int aStart = 0, bStart = 0;\n'
        '        for (int i = 0; i &lt;= len / 2; i++) {\n'
        '            // left保存上一个值（处理偶数长度时需要两个数取平均）\n'
        '            left = right;\n'
        '            if (aStart &lt; m && (bStart &gt;= n || A[aStart] &lt; B[bStart]))\n'
        '                right = A[aStart++];\n'
        '            else\n'
        '                right = B[bStart++];\n'
        '        }\n'
        '        if ((len &amp; 1) == 0)\n'
        '            return (left + right) / 2.0;\n'
        '        else\n'
        '            return right;\n'
        '    }\n'
        '}'
    )
    + img('image 4.png'))
add_basic(d, make_front(p, '关键技巧'),
    '三种解法：<br>'
    '1. 第k小数法（推荐）：求第 (len+1)/2 和 (len+2)/2 小的数的平均值，每次排除 k/2 个<br>'
    '2. 逻辑遍历：O(m+n)，维护 left 和 right 两个变量，right 存当前值，left 存上一个值<br>'
    '3. 二分法（最优）：在较短数组上二分，通过公式确定另一数组的分割位置')

# ============================================================
# 5. 排序链表
# ============================================================
p = '排序链表'
d = make_deck(1747301005, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给你链表的头节点 head，将其按升序排列并返回排序后的链表。'
    '要求 O(n log n) 时间复杂度和 O(1) 空间复杂度。'
    + img('image 5.png') + img('image 6.png') + img('image 7.png'))
add_cloze(d, make_front(p, '复杂度'),
    '迭代归并：时间 {{c1::O(n log n)}}，空间 {{c2::O(1)}}<br>'
    '递归归并：时间 {{c3::O(n log n)}}，空间 {{c4::O(log n)}}(递归栈)')
add_basic(d, make_front(p, '题解(递归归并)'),
    '快慢指针找中点（fast从head.next开始保证偶长时中点在左侧），递归断开并排序，最后合并。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode sortList(ListNode head) {\n'
        '        if (head == null || head.next == null)\n'
        '            return head;\n'
        '        // 快慢指针找中点，fast从head.next开始保证偶数长度时中点在左侧\n'
        '        ListNode fast = head.next, slow = head;\n'
        '        while (fast != null && fast.next != null) {\n'
        '            slow = slow.next;\n'
        '            fast = fast.next.next;\n'
        '        }\n'
        '        // 断开链表\n'
        '        ListNode tmp = slow.next;\n'
        '        slow.next = null;\n'
        '        // 递归排序左右\n'
        '        ListNode left = sortList(head);\n'
        '        ListNode right = sortList(tmp);\n'
        '        // 合并两个有序链表\n'
        '        ListNode h = new ListNode(0);\n'
        '        ListNode res = h;\n'
        '        while (left != null && right != null) {\n'
        '            if (left.val &lt; right.val) {\n'
        '                h.next = left;\n'
        '                left = left.next;\n'
        '            } else {\n'
        '                h.next = right;\n'
        '                right = right.next;\n'
        '            }\n'
        '            h = h.next;\n'
        '        }\n'
        '        // 链接剩余部分\n'
        '        h.next = left != null ? left : right;\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    )
    + img('image 8.png') + img('image 9.png'))
add_basic(d, make_front(p, '题解(迭代归并)'),
    '自底向上：步长从1开始翻倍，每轮截取两个长度为intv的段进行合并。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode sortList(ListNode head) {\n'
        '        int intv = 1; // 归并步长\n'
        '        int len = 0;\n'
        '        ListNode h1, h2, pre, res;\n'
        '        res = new ListNode(0);\n'
        '        res.next = head;\n'
        '        // 获取链表长度\n'
        '        ListNode h = head;\n'
        '        while (h != null) {\n'
        '            h = h.next;\n'
        '            len++;\n'
        '        }\n'
        '        // 自底向上归并排序\n'
        '        while (intv &lt; len) {\n'
        '            pre = res;\n'
        '            h = res.next;\n'
        '            while (h != null) {\n'
        '                int i = intv;\n'
        '                h1 = h;\n'
        '                // 截取h1段（长度为intv）\n'
        '                while (i &gt; 0 && h != null) {\n'
        '                    i--;\n'
        '                    h = h.next;\n'
        '                }\n'
        '                if (i &gt; 0) break; // 只有h1没有h2了\n'
        '                // 截取h2段\n'
        '                i = intv;\n'
        '                h2 = h;\n'
        '                while (i &gt; 0 && h != null) {\n'
        '                    h = h.next;\n'
        '                    i--;\n'
        '                }\n'
        '                int c1 = intv, c2 = intv - i;\n'
        '                // 合并h1和h2\n'
        '                while (c1 &gt; 0 && c2 &gt; 0) {\n'
        '                    if (h1.val &lt; h2.val) {\n'
        '                        pre.next = h1;\n'
        '                        h1 = h1.next;\n'
        '                        c1--;\n'
        '                    } else {\n'
        '                        pre.next = h2;\n'
        '                        h2 = h2.next;\n'
        '                        c2--;\n'
        '                    }\n'
        '                    pre = pre.next;\n'
        '                }\n'
        '                // 链接剩余段\n'
        '                pre.next = c1 == 0 ? h2 : h1;\n'
        '                while (c1 &gt; 0 || c2 &gt; 0) {\n'
        '                    pre = pre.next;\n'
        '                    c1--;\n'
        '                    c2--;\n'
        '                }\n'
        '                // 链接余下链表，防止丢失\n'
        '                pre.next = h;\n'
        '            }\n'
        '            intv *= 2;\n'
        '        }\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '归并排序链表的两种实现：<br>'
    '1. 递归：快慢指针找中点（fast从head.next开始），断开，递归排序左右，合并<br>'
    '2. 迭代：步长intv从1翻倍到len，每轮截取两个长度为intv的段合并<br>'
    '关键细节：迭代法中pre.next=h不能丢，否则余下链表会丢失')

# ============================================================
# 6. 下一个排列
# ============================================================
p = '下一个排列'
d = make_deck(1747301006, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '整数数组的一个排列就是将其所有成员以序列或线性顺序排列。'
    '下一个排列是指其整数的下一个字典序更大的排列。如果不存在下一个更大的排列，'
    '则必须将数组重新排列成字典序最小的排列（即升序排列）。必须原地修改，只允许使用额外常数空间。'
    + img('image 10.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 三次遍历（不使用Arrays.sort时）<br>'
    '若使用Arrays.sort：{{c2::O(n log n)}}<br>空间：{{c3::O(1)}}')
add_basic(d, make_front(p, '题解(标准算法)'),
    '从右往左找第一对 nums[i]&gt;nums[i-1]，i-1是待交换元素，将i到末尾排序后找第一个大于i-1的交换。<br>'
    + code(
        'class Solution {\n'
        '    public void nextPermutation(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        for (int i = len - 1; i &gt; 0; i--) {\n'
        '            // 找到待换元素 i-1\n'
        '            if (nums[i] &gt; nums[i - 1]) {\n'
        '                // 将 [i, len) 升序排列\n'
        '                Arrays.sort(nums, i, len);\n'
        '                // 在升序区间中找第一个大于 nums[i-1] 的元素并交换\n'
        '                for (int j = i; j &lt; len; j++) {\n'
        '                    if (nums[j] &gt; nums[i - 1]) {\n'
        '                        int temp = nums[j];\n'
        '                        nums[j] = nums[i - 1];\n'
        '                        nums[i - 1] = temp;\n'
        '                        return;\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        // 已是最大排列，整体升序\n'
        '        Arrays.sort(nums);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '下一个排列算法步骤：<br>'
    '1. 从右向左找第一个 nums[i] &gt; nums[i-1]，i-1 即「较小数」<br>'
    '2. 对 [i, n) 区间排序（或反转，因为该区间必为降序）<br>'
    '3. 在 [i, n) 中找第一个大于 nums[i-1] 的元素，与 nums[i-1] 交换<br>'
    '4. 若不存在 nums[i]&gt;nums[i-1]，说明已是最大排列，整体升序即可')

# ============================================================
# 7. x 的平方根
# ============================================================
p = 'x 的平方根'
d = make_deck(1747301007, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个非负整数 x，计算并返回 x 的算术平方根。'
    '由于返回类型是整数，结果只保留整数部分，小数部分将被舍去。不允许使用内置指数函数和算符。')
add_cloze(d, make_front(p, '复杂度'),
    '二分法：时间 {{c1::O(log x)}}，空间 {{c2::O(1)}}<br>'
    '牛顿迭代：时间 {{c3::O(log x)}}（二次收敛），空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(二分查找)'),
    '找小于等于x的最大整数平方根：mid*mid&lt;=x时记录并向右逼近；注意用long防溢出。<br>'
    + code(
        'class Solution {\n'
        '    public int mySqrt(int x) {\n'
        '        long left = 0, right = 10000000;\n'
        '        long res = 0;\n'
        '        while (left &lt;= right) {\n'
        '            long mid = (left + right) / 2;\n'
        '            if (mid * mid &lt;= x) {\n'
        '                res = mid;\n'
        '                left = mid + 1;\n'
        '            } else {\n'
        '                right = mid - 1;\n'
        '            }\n'
        '        }\n'
        '        return (int) res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(牛顿迭代)'),
    '牛顿迭代公式：x_{n+1} = (x_n + N/x_n) / 2，二次收敛速度极快。<br>'
    + code(
        'class Solution {\n'
        '    int temp;\n'
        '\n'
        '    public int mySqrt(int x) {\n'
        '        temp = x;\n'
        '        if (x == 0)\n'
        '            return 0;\n'
        '        return (int) sqrts(x);\n'
        '    }\n'
        '\n'
        '    public double sqrts(double x) {\n'
        '        double res = (x + temp / x) / 2;\n'
        '        if (res == x) {\n'
        '            return x;\n'
        '        } else {\n'
        '            return sqrts(res);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二分法本质：找 &lt;=x 的最大元素（与搜索插入位置找 &gt;=x 的最小元素相对应）。<br>'
    '范围查询规律：&lt;= target 返回 right；&gt;= target 返回 left。<br>'
    '牛顿法：利用切线逼近零点，x_{n+1} = (x_n + N/x_n) / 2，收敛极快。')

# ============================================================
# 8. 在排序数组中查找元素的第一个和最后一个位置
# ============================================================
p = '在排序数组中查找元素的第一个和最后一个位置'
d = make_deck(1747301008, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个按照非递减顺序排列的整数数组 nums，和一个目标值 target。'
    '找出给定目标值在数组中的开始位置和结束位置。如果数组中不存在目标值 target，返回 [-1, -1]。'
    '要求 O(log n) 时间复杂度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 两次二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分+范围查询)'),
    '巧妙：找target+1的第一个位置-1就是target的最后一个位置。<br>'
    + code(
        'class Solution {\n'
        '    public int[] searchRange(int[] nums, int target) {\n'
        '        if (nums.length == 0)\n'
        '            return new int[]{-1, -1};\n'
        '        // 找第一个 &gt;= target 的位置\n'
        '        int leftIndex = binarySearch(nums, target);\n'
        '        // 找第一个 &gt;= target+1 的位置 - 1 = 最后一个 target\n'
        '        int rightIndex = binarySearch(nums, target + 1) - 1;\n'
        '        if (leftIndex &lt;= rightIndex && rightIndex &lt; nums.length\n'
        '                && target == nums[leftIndex] && target == nums[rightIndex])\n'
        '            return new int[]{leftIndex, rightIndex};\n'
        '        return new int[]{-1, -1};\n'
        '    }\n'
        '\n'
        '    // 二分查找：返回第一个 &gt;= target 的位置\n'
        '    public int binarySearch(int[] nums, int target) {\n'
        '        int left = 0;\n'
        '        int right = nums.length - 1;\n'
        '        while (left &lt;= right) {\n'
        '            int mid = (left + right) / 2;\n'
        '            if (nums[mid] &gt;= target)\n'
        '                right = mid - 1;\n'
        '            else\n'
        '                left = mid + 1;\n'
        '        }\n'
        '        return left;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二分查找范围查询规律：<br>'
    '变化条件                      | 返回值<br>'
    '&gt;= target (nums[mid]&gt;=target,right=mid-1) | left = 第一个 &gt;= target 的位置<br>'
    '&lt;= target (nums[mid]&lt;=target,left=mid+1)  | right = 最后一个 &lt;= target 的位置<br>'
    '技巧：找 target 的最后一个位置 = 找 target+1 的第一个位置 - 1')

# ============================================================
# 9. 寻找峰值
# ============================================================
p = '寻找峰值'
d = make_deck(1747301009, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '峰值元素是指其值严格大于左右相邻值的元素。'
    '给你一个整数数组 nums，找到峰值元素并返回其索引。数组可能包含多个峰值，返回任何一个峰值所在位置即可。'
    '假设 nums[-1] = nums[n] = -∞。要求 O(log n) 时间复杂度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分/爬坡法)'),
    '爬坡法：比较mid和mid+1，哪边大就往哪边走，大的那侧必然存在峰值。<br>'
    + code(
        'class Solution {\n'
        '    public int findPeakElement(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        if (len == 0)\n'
        '            return -1;\n'
        '        int left = 0, right = len - 1;\n'
        '        while (left &lt; right) {\n'
        '            int mid = (left + right) / 2;\n'
        '            // mid可能是峰值，左侧含mid一定存在峰值\n'
        '            if (nums[mid] &gt; nums[mid + 1])\n'
        '                right = mid;\n'
        '            // 上坡方向一定有峰值\n'
        '            else\n'
        '                left = mid + 1;\n'
        '        }\n'
        '        return right;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '爬坡法二分核心（无需有序数组也能二分）：<br>'
    '1. 核心规律：若 nums[mid] &gt; nums[mid+1]，则左侧（含mid）必有峰值<br>'
    '2. 若 nums[mid] &lt; nums[mid+1]，则右侧必有峰值<br>'
    '3. 为什么成立：边界为负无穷，沿上升方向走一定能到达一个峰值<br>'
    '4. while(left &lt; right) 不用取等号，因为保证有解且最终收敛到峰值')

# ============================================================
# 10. 寻找旋转排序数组中的最小值
# ============================================================
p = '寻找旋转排序数组中的最小值'
d = make_deck(1747301010, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '已知一个长度为 n 的数组，预先按照升序排列，经由 1 到 n 次旋转后得到输入数组。'
    '数组中的元素互不相同。找出数组中的最小元素。要求 O(log n) 时间复杂度。'
    + img('image 11.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分)'),
    '比较 nums[mid] 与 nums[right]：mid&gt;right 时最小值必在右侧，否则在左侧含mid。<br>'
    + code(
        'class Solution {\n'
        '    public int findMin(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        if (nums == null || len == 0)\n'
        '            return -5500;\n'
        '        int left = 0;\n'
        '        int right = nums.length - 1;\n'
        '        while (left &lt; right) {\n'
        '            // 地板除，mid更靠近left\n'
        '            int mid = left + (right - left) / 2;\n'
        '            // 最小值在mid右侧\n'
        '            if (nums[mid] &gt; nums[right])\n'
        '                left = mid + 1;\n'
        '            // 最小值在mid或其左侧\n'
        '            else\n'
        '                right = mid;\n'
        '        }\n'
        '        return nums[left];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '旋转数组找最小值核心：<br>'
    '1. 比较 nums[mid] 与 nums[right]（不是 nums[0]！）<br>'
    '2. mid &gt; right → 最小值在 mid 右侧 → left = mid + 1<br>'
    '3. mid &lt;= right → 最小值在 mid 或其左侧 → right = mid<br>'
    '4. while(left &lt; right) 不取等号，mid 使用地板除靠左<br>'
    '5. 与「搜索旋转排序数组」区分：本题用right做参考，搜索题用left做参考')

# ============================================================
# 11. 删除排序数组中的重复项
# ============================================================
p = '删除排序数组中的重复项'
d = make_deck(1747301011, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个非严格递增排列的数组 nums，请你原地删除重复出现的元素，'
    '使每个元素只出现一次，返回删除后数组的新长度。元素的相对顺序应保持一致。'
    '不要使用额外的数组空间，必须在原地修改输入数组并在使用 O(1) 额外空间的条件下完成。')
add_cloze(d, make_front(p, '复杂度'),
    '双指针：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '哈希法：时间 {{c3::O(n)}}，空间 {{c4::O(n)}}')
add_basic(d, make_front(p, '题解(双指针)'),
    'i指向已处理的不重复数组末尾，j向前探索，遇到新元素就放到i+1位置。<br>'
    + code(
        'class Solution {\n'
        '    public int removeDuplicates(int[] nums) {\n'
        '        if (nums.length &lt;= 1)\n'
        '            return nums.length;\n'
        '        int i = 0, j = 1;\n'
        '        while (j &lt; nums.length) {\n'
        '            if (nums[i] != nums[j]) {\n'
        '                nums[i + 1] = nums[j];\n'
        '                i++;\n'
        '            }\n'
        '            j++;\n'
        '        }\n'
        '        return i + 1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '排序数组去重双指针模板：<br>'
    'i = 0（原地指针），j = 1（探索指针）<br>'
    'nums[i] != nums[j] 时，nums[++i] = nums[j]<br>'
    '最终长度 = i + 1<br>'
    '优化：可在 j-i&gt;1 时才赋值，避免无意义覆盖（原数组本就无重复时）')

# ============================================================
# 12. 数组中的逆序对
# ============================================================
p = '数组中的逆序对'
d = make_deck(1747301012, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '在数组中的两个数字，如果前面一个数字大于后面的数字，则这两个数字组成一个逆序对。'
    '输入一个数组，求出这个数组中的逆序对的总数。')
add_cloze(d, make_front(p, '复杂度'),
    '归并法：时间 {{c1::O(n log n)}}，空间 {{c2::O(n)}}(辅助数组)<br>'
    '暴力法：时间 {{c3::O(n^2)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(归并排序)'),
    '归并时每当右半部分元素被选中，左半部分从i到mid的所有元素都大于它，形成 mid-i+1 个逆序对。<br>'
    + code(
        'class Solution {\n'
        '    int res = 0;\n'
        '\n'
        '    public int reversePairs(int[] nums) {\n'
        '        this.res = 0;\n'
        '        sortArray(nums);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return nums;\n'
        '        int len = nums.length;\n'
        '        // 迭代归并：步长从1翻倍\n'
        '        for (int i = 1; i &lt; len; i *= 2)\n'
        '            mergePass(nums, i, len);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    // 一趟归并\n'
        '    public void mergePass(int[] nums, int length, int len) {\n'
        '        int i;\n'
        '        for (i = 0; i + 2 * length - 1 &lt; len; i = i + 2 * length)\n'
        '            merge(nums, i, i + length - 1, i + 2 * length - 1);\n'
        '        // 处理剩余子表\n'
        '        if (i + length - 1 &lt; len - 1)\n'
        '            merge(nums, i, i + length - 1, len - 1);\n'
        '    }\n'
        '\n'
        '    // 归并两个有序子数组\n'
        '    public void merge(int[] nums, int low, int mid, int high) {\n'
        '        int[] temp = new int[high - low + 1];\n'
        '        int i = low, j = mid + 1, k = 0;\n'
        '        while (i &lt;= mid && j &lt;= high) {\n'
        '            if (nums[i] &lt;= nums[j]) {\n'
        '                temp[k++] = nums[i++];\n'
        '            } else {\n'
        '                // 关键：右侧元素更小时统计逆序对\n'
        '                res += mid - i + 1;\n'
        '                temp[k++] = nums[j++];\n'
        '            }\n'
        '        }\n'
        '        while (i &lt;= mid) temp[k++] = nums[i++];\n'
        '        while (j &lt;= high) temp[k++] = nums[j++];\n'
        '        // 复制回原数组\n'
        '        for (k = 0, i = low; i &lt;= high; k++, i++)\n'
        '            nums[i] = temp[k];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '归并排序天然适合统计逆序对：<br>'
    '在 merge 过程中，当右侧元素 nums[j] 小于左侧元素 nums[i] 时，<br>'
    '左侧从 i 到 mid 共 (mid - i + 1) 个元素都大于 nums[j]，直接累加到计数器。<br>'
    '原理：左右子数组已分别有序，一旦 nums[i] &gt; nums[j]，则左子数组剩余部分全部 &gt; nums[j]。')

# ============================================================
# 13. 轮转数组
# ============================================================
p = '轮转数组'
d = make_deck(1747301013, f'算法::排序与查找::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums，将数组中的元素向右轮转 k 个位置，其中 k 是非负数。'
    '要求使用空间复杂度为 O(1) 的原地算法。')
add_cloze(d, make_front(p, '复杂度'),
    '三次反转：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}')
add_basic(d, make_front(p, '题解(三次反转)'),
    '三次反转：[1,2,3,4,5,6,7] k=3 → 整体反转 → 反转前k → 反转剩余 → [5,6,7,1,2,3,4]。<br>'
    + code(
        'class Solution {\n'
        '    public void rotate(int[] nums, int k) {\n'
        '        int n = nums.length;\n'
        '        if (n == 1)\n'
        '            return;\n'
        '        k = k % n;\n'
        '        reverse(nums, 0, n - 1);\n'
        '        reverse(nums, 0, k - 1);\n'
        '        reverse(nums, k, n - 1);\n'
        '    }\n'
        '\n'
        '    public void reverse(int[] nums, int start, int end) {\n'
        '        int temp;\n'
        '        while (start &lt; end) {\n'
        '            temp = nums[start];\n'
        '            nums[start] = nums[end];\n'
        '            nums[end] = temp;\n'
        '            start++;\n'
        '            end--;\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '三次反转法（简单且空间O(1)）：<br>'
    '1. k %= n（处理k大于n的情况）<br>'
    '2. 整体反转 [0, n-1]<br>'
    '3. 反转前 k 个 [0, k-1]<br>'
    '4. 反转后 n-k 个 [k, n-1]<br>'
    '数学本质：(A^R B^R)^R = BA，其中 A=前n-k个，B=后k个')

if __name__ == '__main__':
    print(build('../../牌组/排序与查找.apkg'))

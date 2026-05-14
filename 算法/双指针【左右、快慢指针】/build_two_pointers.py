"""Build APKG for 双指针 (Two Pointers). 16 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747300400, '算法::双指针::原理通识')
add_basic(d0, '双指针核心分类',
    '1. 左右指针（对撞指针）：i=0, j=n-1，向中间移动，用于有序数组、两数/三数/四数之和<br>'
    '2. 快慢指针：fast步长2, slow步长1，用于环形检测、链表中点、倒数第k个<br>'
    '3. 滑动窗口（前后指针）：right扩张, left收缩，用于子串/子数组')
add_basic(d0, '双指针去重技巧',
    '排序+跳过重复：if(i&gt;0 && nums[i]==nums[i-1]) continue<br>'
    'while(i&lt;j && nums[i]==nums[++i]) — 跳过重复的i<br>'
    'while(i&lt;j && nums[j]==nums[--j]) — 跳过重复的j')
add_cloze(d0, '快慢指针核心：fast步长={{c1::2}}, slow步长={{c2::1}}，相遇说明{{c3::有环}}<br>'
    '环入口：头结点和相遇点各走一步，{{c4::再次相遇即为环入口}}')

# ============================================================
# 1. 三数之和
# ============================================================
p = '三数之和'
d = make_deck(1747300401, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含 n 个整数的数组 nums，判断 nums 中是否存在三个元素 a,b,c 使得 a+b+c=0。'
    '找出所有和为 0 且不重复的三元组。' + img('image.png'))
add_cloze(d, make_front(p, '指针策略'),
    '固定 k 遍历，双指针 i=k+1, j=n-1 对撞。<br>'
    'sum&lt;0 → {{c1::i++}}；sum&gt;0 → {{c2::j--}}<br>'
    '去重：k层 {{c3::k>0 && nums[k]==nums[k-1] → continue}}<br>'
    'i/j层 {{c4::while(i&lt;j && nums[i]==nums[++i])}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n²)}} — 外层O(n)，内层双指针O(n)<br>空间：{{c2::O(1)}} — 不计结果集')
add_basic(d, make_front(p, '题解(排序+双指针)'),
    '排序后固定k，i和j对撞。注意三层去重。'
    + code(
        'class Solution {\n'
        '    public List&lt;List&lt;Integer&gt;&gt; threeSum(int[] nums) {\n'
        '        Arrays.sort(nums);\n'
        '        List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '        for(int k = 0; k &lt; nums.length - 2; k++){\n'
        '            if(nums[k] &gt; 0) break;\n'
        '            if(k &gt; 0 && nums[k] == nums[k - 1]) continue;\n'
        '            int i = k + 1, j = nums.length - 1;\n'
        '            while(i &lt; j){\n'
        '                int sum = nums[k] + nums[i] + nums[j];\n'
        '                if(sum &lt; 0){\n'
        '                    i++;\n'
        '                } else if (sum &gt; 0) {\n'
        '                    j--;\n'
        '                } else {\n'
        '                    res.add(new ArrayList&lt;Integer&gt;(Arrays.asList(nums[k], nums[i], nums[j])));\n'
        '                    while(i &lt; j && nums[i] == nums[++i]);\n'
        '                    while(i &lt; j && nums[j] == nums[--j]);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 2. 最接近的三数之和
# ============================================================
p = '最接近的三数之和'
d = make_deck(1747300402, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包括 n 个整数的数组 nums 和一个目标值 target。找出 nums 中的三个整数，'
    '使得它们的和与 target 最接近。返回这三个数的和。假定每组输入只存在唯一答案。'
    + img('image 1.png') + img('image 2.png') + img('image 3.png'))
add_cloze(d, make_front(p, '指针策略'),
    '固定 i 遍历，双指针 start=i+1, end=n-1 对撞。<br>'
    '优化1：跳过重复 → {{c1::while(nums[end]==nums[end+1]) end--}}<br>'
    '优化2：判断 min(最小三数和) {{c2::&gt; target}} → 直接 break<br>'
    '优化3：判断 max(最大三数和) {{c3::&lt; target}} → 直接 break')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n²)}} — 排序+两层遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(排序+双指针优化)'),
    '三数之和变形：维护与target的最小差值，三层优化大幅剪枝。'
    + code(
        'class Solution {\n'
        '    public int threeSumClosest(int[] nums, int target) {\n'
        '        Arrays.sort(nums);\n'
        '        int ans = nums[0] + nums[1] + nums[2];\n'
        '        for(int i = 0; i &lt; nums.length - 2; i++){\n'
        '            int start = i + 1, end = nums.length - 1;\n'
        '            while(start != end){\n'
        '                int min = nums[i] + nums[start] + nums[start + 1];\n'
        '                if(target &lt; min){\n'
        '                    if(Math.abs(ans - target) &gt; Math.abs(min - target))\n'
        '                        ans = min;\n'
        '                    break;\n'
        '                }\n'
        '                int max = nums[i] + nums[end] + nums[end - 1];\n'
        '                if(target &gt; max){\n'
        '                    if(Math.abs(ans - target) &gt; Math.abs(max - target))\n'
        '                        ans = max;\n'
        '                    break;\n'
        '                }\n'
        '                int sum = nums[start] + nums[end] + nums[i];\n'
        '                if(sum == target)\n'
        '                    return sum;\n'
        '                if(Math.abs(ans - target) &gt; Math.abs(sum - target)){\n'
        '                    ans = sum;\n'
        '                }\n'
        '                if(sum &gt; target){\n'
        '                    end--;\n'
        '                    while(start != end && nums[end] == nums[end+1])\n'
        '                        end--;\n'
        '                }else{\n'
        '                    start++;\n'
        '                    while(start != end && nums[start] == nums[start-1])\n'
        '                        start++;\n'
        '                }\n'
        '            }\n'
        '            while(i &lt; nums.length-2 && nums[i] == nums[i+1])\n'
        '                i++;\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 3. 四数之和
# ============================================================
p = '四数之和'
d = make_deck(1747300403, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含 n 个整数的数组 nums 和一个目标值 target，判断 nums 中是否存在 a,b,c,d '
    '使得 a+b+c+d=target。找出所有满足条件且不重复的四元组。')
add_cloze(d, make_front(p, '指针策略'),
    '两层枚举 i+j + 双指针 left+right。<br>'
    'i层去重：{{c1::i>0 && nums[i]==nums[i-1] → continue}}<br>'
    'j层去重：{{c2::j>i+1 && nums[j]==nums[j-1] → continue}}<br>'
    'sum&gt;target → {{c3::right--}}；sum&lt;target → {{c4::left++}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n³)}} — 两重循环+双指针<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(两层枚举+双指针)'),
    '三数之和外层加一重循环：两层for枚举i/j，内层双指针left/right。'
    + code(
        'class Solution {\n'
        '    public List&lt;List&lt;Integer&gt;&gt; fourSum(int[] nums, int target) {\n'
        '        List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '        int len = nums.length;\n'
        '        Arrays.sort(nums);\n'
        '        for(int i = 0; i &lt; len; i++){\n'
        '            if(i &gt; 0 && nums[i] == nums[i-1]) continue;\n'
        '            for(int j = i + 1; j &lt; len; j++){\n'
        '                if(j &gt; i + 1 && nums[j] == nums[j-1]) continue;\n'
        '                int left = j + 1, right = len - 1;\n'
        '                while(left &lt; right){\n'
        '                    int sum = nums[left] + nums[right] + nums[i] + nums[j];\n'
        '                    if(sum &gt; target)\n'
        '                        right--;\n'
        '                    else if(sum &lt; target)\n'
        '                        left++;\n'
        '                    else{\n'
        '                        res.add(new ArrayList&lt;&gt;(Arrays.asList(nums[i], nums[j], nums[left], nums[right])));\n'
        '                        while(left &lt; right && nums[right] == nums[--right]);\n'
        '                        while(left &lt; right && nums[left] == nums[++left]);\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 4. 盛最多水的容器
# ============================================================
p = '盛最多水的容器'
d = make_deck(1747300404, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定 n 个非负整数表示高度，每个柱子宽度为1。找出两条线，与x轴一起构成容器，'
    '使容器能容纳最多的水。' + img('image 4.png'))
add_cloze(d, make_front(p, '指针策略'),
    '左右指针 i=0, j=n-1 对撞。<br>'
    '每次移动{{c1::较矮一侧}}的指针：height[i] &lt; height[j] → {{c2::i++}}，否则 {{c3::j--}}<br>'
    '面积 = {{c4::min(height[i],height[j]) * (j-i)}}<br>'
    '原理：容量由短板决定，移动长板不可能增大面积')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针)'),
    '每次移动短板，计算当前面积并更新最大值。'
    + code(
        'class Solution {\n'
        '    public int maxArea(int[] height) {\n'
        '        if(height == null)\n'
        '            return 0;\n'
        '        int i = 0, j = height.length - 1, maxRes = 0;\n'
        '        while(i &lt; j){\n'
        '            maxRes = height[i] &lt; height[j]\n'
        '                ? Math.max(maxRes, (j - i) * height[i++])\n'
        '                : Math.max(maxRes, (j - i) * height[j--]);\n'
        '        }\n'
        '        return maxRes;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 5. 有效三角形的个数
# ============================================================
p = '有效三角形的个数'
d = make_deck(1747300405, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含非负整数的数组，统计其中可以组成三角形三条边的三元组个数。'
    + img('image 5.png'))
add_cloze(d, make_front(p, '指针策略'),
    '排序后固定最大边 i=n-1..2，双指针 l=0, r=i-1。<br>'
    '若 nums[l]+nums[r] &gt; nums[i] → {{c1::res += r-l; r--}}（l到r-1的所有组合都满足）<br>'
    '否则 → {{c2::l++}}（需要更大的和）')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n²)}} — 外层O(n)，内层双指针O(n)<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(排序+双指针)'),
    '固定最大边nums[i]，双指针找两边nums[l]+nums[r] &gt; nums[i]的组合。'
    + code(
        'class Solution {\n'
        '    public int triangleNumber(int[] nums) {\n'
        '        Arrays.sort(nums);\n'
        '        int n = nums.length;\n'
        '        int res = 0;\n'
        '        for (int i = n - 1; i &gt;= 2; --i) {\n'
        '            int l = 0, r = i - 1;\n'
        '            while (l &lt; r) {\n'
        '                if (nums[l] + nums[r] &gt; nums[i]) {\n'
        '                    res += r - l;\n'
        '                    --r;\n'
        '                } else {\n'
        '                    ++l;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 6. 和为s的两个数字
# ============================================================
p = '和为s的两个数字'
d = make_deck(1747300406, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个递增排序的数组和一个数字 target，在数组中查找两个数，使得它们的和正好是 target。'
    + img('image 6.png'))
add_cloze(d, make_front(p, '指针策略'),
    '左右指针 low=0, high=n-1 对撞。<br>'
    'sum&gt;target → {{c1::high--}}；sum&lt;target → {{c2::low++}}<br>'
    'sum==target → {{c3::返回结果}}<br>'
    '前提：数组{{c4::已排序}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(对撞指针)'),
    '利用递增特性，sum偏大则high--，偏小则low++。'
    + code(
        'class Solution {\n'
        '    public int[] twoSum(int[] nums, int target) {\n'
        '        int low = 0;\n'
        '        int high = nums.length - 1;\n'
        '        int[] res = new int[2];\n'
        '        while(true){\n'
        '            if(nums[low] + nums[high] == target){\n'
        '                res[0] = nums[low];\n'
        '                res[1] = nums[high];\n'
        '                return res;\n'
        '            } else if(nums[low] + nums[high] &gt; target)\n'
        '                high--;\n'
        '            else if(nums[low] + nums[high] &lt; target)\n'
        '                low++;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 7. 反转字符串
# ============================================================
p = '反转字符串'
d = make_deck(1747300407, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个函数，其作用是将输入的字符串反转过来。输入以字符数组 char[] 形式给出。')
add_cloze(d, make_front(p, '指针策略'),
    '左右指针 i=0, j=n-1 对撞。<br>'
    '每次 swap(s[i], s[j])，然后 {{c1::i++, j--}}<br>'
    '终止条件：{{c2::i &lt; j}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历，n/2次交换<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(对撞指针)'),
    '经典对撞指针，原地反转字符数组。'
    + code(
        'class Solution {\n'
        '    public void reverseString(char[] s) {\n'
        '        int i = 0, j = s.length - 1;\n'
        '        char temp;\n'
        '        while(i &lt; j){\n'
        '            temp = s[i];\n'
        '            s[i] = s[j];\n'
        '            s[j] = temp;\n'
        '            i++;\n'
        '            j--;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 8. 反转字符串中的单词 III
# ============================================================
p = '反转字符串中的单词 III'
d = make_deck(1747300408, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串，你需要反转字符串中每个单词的字符顺序，同时仍保留空格和单词的初始顺序。')
add_cloze(d, make_front(p, '指针策略'),
    'start={{c1::每个单词的起始位置}}，end={{c2::前进指针找空格}}<br>'
    'end 找到空格后 → {{c3::reverse(s, start, end-1)}}<br>'
    '然后 {{c4::start = ++end}}，继续找下一个单词')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个字符处理一次<br>空间：{{c2::O(1)}} — 原地操作')
add_basic(d, make_front(p, '题解(双指针)'),
    '外层end找空格分割单词，内层对撞指针反转每个单词。'
    + code(
        'class Solution {\n'
        '    public String reverseWords(String str) {\n'
        '        if(str == null)\n'
        '            return "";\n'
        '        char[] s = str.toCharArray();\n'
        '        int start = 0, end = 0;\n'
        '        while(end &lt; s.length){\n'
        '            while(end &lt; s.length && s[end] != \' \')\n'
        '                end++;\n'
        '            reverse(s, start, end - 1);\n'
        '            end++;\n'
        '            start = end;\n'
        '        }\n'
        '        return new String(s);\n'
        '    }\n'
        '\n'
        '    public void reverse(char[] s, int i, int j){\n'
        '        char temp;\n'
        '        while(i &lt; j){\n'
        '            temp = s[i];\n'
        '            s[i] = s[j];\n'
        '            s[j] = temp;\n'
        '            i++;\n'
        '            j--;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 9. 链表的中间结点
# ============================================================
p = '链表的中间结点'
d = make_deck(1747300409, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个头结点为 head 的非空单链表，返回链表的中间结点。'
    '如果有两个中间结点，则返回第二个中间结点。' + img('image 7.png'))
add_cloze(d, make_front(p, '指针策略'),
    '快慢指针：fast 每次走 {{c1::2步}}，slow 每次走 {{c2::1步}}<br>'
    'fast到达末尾(null)时，{{c3::slow 正好在中间}}<br>'
    '注意：偶数长度返回第二个中间结点')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — fast指针遍历一遍<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(快慢指针)'),
    'fast到末尾时slow正好在中点。while条件同时检查fast和fast.next。'
    + code(
        'class Solution {\n'
        '    public ListNode middleNode(ListNode head) {\n'
        '        ListNode fast = head, slow = head;\n'
        '        while(fast != null && fast.next != null){\n'
        '            fast = fast.next.next;\n'
        '            slow = slow.next;\n'
        '        }\n'
        '        return slow;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 10. 环形链表
# ============================================================
p = '环形链表'
d = make_deck(1747300410, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个链表，判断链表中是否有环。')
add_cloze(d, make_front(p, '指针策略'),
    '快慢指针（Floyd判环）：fast走{{c1::2步}}，slow走{{c2::1步}}<br>'
    '有环 → {{c3::fast == slow}}（两者在环中相遇）<br>'
    '无环 → fast 或 fast.next 为 null<br>'
    '注意：先移动再比较，排除初始时都指向 head')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 最坏 fast 追上一圈<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(快慢指针)'),
    '有环则快慢指针必然相遇。注意先移动再比较，排除初始都指向head的情况。'
    + code(
        'public class Solution {\n'
        '    public boolean hasCycle(ListNode head) {\n'
        '        ListNode fast = head, slow = head;\n'
        '        while(fast != null && fast.next != null) {\n'
        '            fast = fast.next.next;\n'
        '            slow = slow.next;\n'
        '            if(fast == slow) {\n'
        '                return true;\n'
        '            }\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 11. 环形链表 II
# ============================================================
p = '环形链表 II'
d = make_deck(1747300411, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个链表，返回链表开始入环的第一个节点。如果链表无环，则返回 null。')
add_cloze(d, make_front(p, '指针策略'),
    '1. 快慢指针相遇于环内某点<br>'
    '2. {{c1::头结点}}和{{c2::相遇点}}各放一个指针，每次各走一步<br>'
    '3. {{c3::再次相遇点}}即为环入口<br>'
    '数学证明：头到入口=a，入口到相遇=b，相遇到入口=c，则 a=c(mod n)')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 两次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(快慢指针+数学)'),
    '相遇点+头结点各走一步，再次相遇即为环入口。数学原理：a = c (mod n)。'
    + code(
        'public class Solution {\n'
        '    public ListNode detectCycle(ListNode head) {\n'
        '        if(head == null || head.next == null)\n'
        '            return null;\n'
        '        ListNode fast = head;\n'
        '        ListNode slow = head;\n'
        '        do{\n'
        '            fast = fast.next.next;\n'
        '            slow = slow.next;\n'
        '            if(slow == fast){\n'
        '                ListNode index1 = fast;\n'
        '                ListNode index2 = head;\n'
        '                while(index1 != index2){\n'
        '                    index1 = index1.next;\n'
        '                    index2 = index2.next;\n'
        '                }\n'
        '                return index1;\n'
        '            }\n'
        '        }while(fast != null && fast.next != null);\n'
        '        return null;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 12. 链表中倒数第k个节点
# ============================================================
p = '链表中倒数第k个节点'
d = make_deck(1747300412, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个链表，输出该链表中倒数第 k 个节点。' + img('image 8.png') + img('image 9.png'))
add_cloze(d, make_front(p, '指针策略'),
    '前后指针：former 先走 {{c1::k 步}}<br>'
    '然后 former 和 latter 一起走，直到 {{c2::former == null}}<br>'
    '此时 {{c3::latter}} 就是倒数第 k 个节点')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 两个指针各走一次<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(前后指针)'),
    'former先走k步，然后两个指针一起走直到former为null，latter即为倒数第k个。'
    + code(
        'class Solution {\n'
        '    public ListNode getKthFromEnd(ListNode head, int k) {\n'
        '        ListNode former = head, latter = head;\n'
        '        for(int i = 0; i &lt; k; i++)\n'
        '            former = former.next;\n'
        '        while(former != null) {\n'
        '            former = former.next;\n'
        '            latter = latter.next;\n'
        '        }\n'
        '        return latter;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 13. 删除链表的倒数第N个节点
# ============================================================
p = '删除链表的倒数第N个节点'
d = make_deck(1747300413, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个链表，删除链表的倒数第 n 个节点，并且返回链表的头结点。')
add_cloze(d, make_front(p, '指针策略'),
    '前后指针：preNode 先走 n 步，然后一起走直到 preNode.next == null。<br>'
    'preNode走n步后为null → 删除头结点。'
    '注意：提前一个结点结束（while条件为preNode.next != null），使resNode停在删除节点的前一个。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(前后指针)'),
    'preNode先走n步，然后一起走，resNode.next = resNode.next.next 完成删除。'
    + code(
        'class Solution {\n'
        '    public ListNode removeNthFromEnd(ListNode head, int n) {\n'
        '        ListNode preNode = head, resNode = head;\n'
        '        for(int i = 0; i &lt; n; i++)\n'
        '            preNode = preNode.next;\n'
        '        if(preNode == null)\n'
        '            return head.next;\n'
        '        while(preNode.next != null){\n'
        '            preNode = preNode.next;\n'
        '            resNode = resNode.next;\n'
        '        }\n'
        '        resNode.next = resNode.next.next;\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 14. 寻找重复数
# ============================================================
p = '寻找重复数'
d = make_deck(1747300414, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含 n+1 个整数的数组 nums，其数字都在 1 到 n 之间（包括 1 和 n）。'
    '假设只有一个重复的整数，找出这个重复的数。')
add_cloze(d, make_front(p, '指针策略'),
    '弗洛伊德判环：将数组视为 {{c1::链表}}，nums[i] 表示 i→nums[i] 的边<br>'
    '1. 快慢指针找到 {{c2::环中相遇点}}<br>'
    '2. 快指针回到0，两指针各走一步<br>'
    '3. 再次相遇点即为 {{c3::重复数（环入口）}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 最多走两圈<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(弗洛伊德判环)'),
    '数组值作为next指针，有重复必成环。环入口即重复数。'
    + code(
        'class Solution {\n'
        '    public int findDuplicate(int[] nums) {\n'
        '        int fast = 0, slow = 0;\n'
        '        while(true) {\n'
        '            fast = nums[nums[fast]];\n'
        '            slow = nums[slow];\n'
        '            if(slow == fast) {\n'
        '                fast = 0;\n'
        '                while(nums[slow] != nums[fast]) {\n'
        '                    fast = nums[fast];\n'
        '                    slow = nums[slow];\n'
        '                }\n'
        '                return nums[slow];\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 15. 无重复字符的最长子串
# ============================================================
p = '无重复字符的最长子串'
d = make_deck(1747300415, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，请你找出其中不含有重复字符的最长子串的长度。'
    + img('image 10.png'))
add_cloze(d, make_front(p, '指针策略'),
    '滑动窗口：start={{c1::窗口左边界}}，end={{c2::遍历指针（窗口右边界）}}<br>'
    '遇到重复字符 ch → start = {{c3::max(map.get(ch)+1, start)}}（跳过重复位置）<br>'
    '每次更新 max = {{c4::max(max, end-start+1)}}<br>'
    '用 HashMap 或 int[128] 记录字符上次出现位置')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(128)}} — 字符集大小')
add_basic(d, make_front(p, '题解(滑动窗口)'),
    '用int[128]记录字符上次出现位置，start只会向前跳不会后退。'
    + code(
        'class Solution {\n'
        '    public int lengthOfLongestSubstring(String s) {\n'
        '        int[] last = new int[128];\n'
        '        Arrays.fill(last, -1);\n'
        '        int res = 0, start = 0;\n'
        '        for(int end = 0; end &lt; s.length(); end++){\n'
        '            int idx = s.charAt(end);\n'
        '            start = Math.max(start, last[idx] + 1);\n'
        '            res = Math.max(res, end - start + 1);\n'
        '            last[idx] = end;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 16. 合并两个有序数组
# ============================================================
p = '合并两个有序数组'
d = make_deck(1747300416, f'算法::双指针::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个有序整数数组 nums1 和 nums2，将 nums2 合并到 nums1 中，使 nums1 成为一个有序数组。'
    'nums1 有足够空间容纳 nums2。')
add_cloze(d, make_front(p, '指针策略'),
    '从后往前合并，三个指针：<br>'
    'i = {{c1::nums1末尾（m+n-1）}}，m--和n--分别指向两个数组{{c2::最后一个有效元素}}<br>'
    '比较 nums1[m] 和 nums2[n]，大的放到 {{c3::nums1[i--]}}<br>'
    '结束条件：{{c4::n &lt; 0}}（nums2全部放完）')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m+n)}} — 每个元素处理一次<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(逆向双指针)'),
    '从后往前放，避免覆盖nums1未处理元素。每次挑大的放入末尾。'
    + code(
        'class Solution {\n'
        '    public void merge(int[] nums1, int m, int[] nums2, int n) {\n'
        '        int i = nums1.length - 1;\n'
        '        m--; n--;\n'
        '        while(n &gt;= 0){\n'
        '            if(m &gt;= 0 && nums1[m] &gt; nums2[n])\n'
        '                nums1[i--] = nums1[m--];\n'
        '            else\n'
        '                nums1[i--] = nums2[n--];\n'
        '        }\n'
        '    }\n'
        '}'
    ))

if __name__ == '__main__':
    print(build('../../牌组/双指针.apkg'))

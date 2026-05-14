"""Build APKG for 哈希表+前缀和+异或 (Hash Table + Prefix Sum + XOR). 18 problems, full-code solutions."""
import html
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    escaped = html.escape(java)
    return f'<pre><code class="language-java">{escaped}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301200, '算法::哈希表::原理通识')
add_basic(d0, 'HashMap 核心思想',
    'HashMap：通过哈希函数将 key 映射到数组索引，实现 O(1) 的查找/插入/删除。<br>'
    '核心应用场景：<br>'
    '1. 两数之和型：存值→索引映射，边遍历边检查 target-num 是否已存在<br>'
    '2. 频率统计：key=元素, value=出现次数<br>'
    '3. 分组映射：key=某个特征（余数/前缀和）, value=下标/次数<br>'
    '4. 节点映射：key=原节点, value=新节点（深拷贝链表）')
add_cloze(d0, '前缀和 + HashMap 模式',
    '前缀和定义：preSum[i] = sum(nums[0..i-1])，区间和 sum[i..j] = {{c1::preSum[j+1] - preSum[i]}}<br>'
    'HashMap 优化前缀和：<br>'
    '1. 和为K的子数组：遍历时维护 {{c2::preSum}}，检查 map.containsKey(preSum - k)<br>'
    '2. 和可被K整除的子数组：key = {{c3::余数}}，统计同余数出现次数，组合数 C(m,2)<br>'
    '3. 连续数组（0和1等量）：将0视为 {{c4::-1}}，问题转化为和为0的最长子数组')
add_basic(d0, '异或 (XOR) 核心性质',
    '1. 交换律：a ^ b ^ a = a ^ a ^ b = b<br>'
    '2. 自身异或为0：x ^ x = 0<br>'
    '3. 与0异或不变：x ^ 0 = x<br>'
    '4. 找不同值：全异或结果 = 两个不同值的异或<br>'
    '5. 取最低位1：mask = temp & (-temp) — 用于分组')

# ============================================================
# 1. 两数之和
# ============================================================
p = '两数之和'
d = make_deck(1747301201, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。'
    '你可以假设每种输入只会对应一个答案，且同一元素不能使用两遍。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历，HashMap 查找 O(1)<br>空间：{{c2::O(n)}} — HashMap 存储')
add_basic(d, make_front(p, '题解(HashMap)'),
    '边遍历边检查：若 target-nums[i] 已存在则直接返回，否则存入当前值。<br>'
    + code(
        'class Solution {\n'
        '    public int[] twoSum(int[] nums, int target) {\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        for(int i = 0; i < nums.length; i++){\n'
        '            if(map.containsKey(target - nums[i]))\n'
        '                return new int[]{map.get(target - nums[i]), i};\n'
        '            map.put(nums[i], i);\n'
        '        }\n'
        '        return new int[]{0,0};\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'HashMap 存值→索引映射，一次遍历完成查找和插入。<br>'
    '不能先全部 put 再查找，因为当 target = 2*num 时会匹配到自己。<br>'
    '正确做法：先检查 containsKey，再 put，确保不会用同一个元素两次。')

# ============================================================
# 2. 有效的字母异位词
# ============================================================
p = '有效的字母异位词'
d = make_deck(1747301202, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个字符串 s 和 t，编写一个函数来判断 t 是否是 s 的字母异位词。'
    '字母异位词：两个字符串中每个字符的出现次数相同。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历两个字符串<br>空间：{{c2::O(26)=O(1)}} — 固定大小数组')
add_basic(d, make_front(p, '题解(原地哈希)'),
    's对应字符++，t对应字符--，最后全0则互为异位词。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isAnagram(String s, String t) {\n'
        '        if(s == null || t == null || s.length() != t.length())\n'
        '            return false;\n'
        '        int[] hash = new int[26];\n'
        '        for(int i = 0; i < s.length(); i++){\n'
        '            hash[s.charAt(i) - \'a\'] ++;\n'
        '            hash[t.charAt(i) - \'a\'] --;\n'
        '        }\n'
        '        for(int i = 0; i < hash.length; i++){\n'
        '            if(hash[i] != 0)\n'
        '                return false;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '当 key 范围有限且连续时（如26个小写字母），用固定大小数组代替 HashMap。<br>'
    '数组比 HashMap 更快、更省内存（无装箱开销）。<br>'
    '本质是计数排序思想的简化版：字符→索引，值→计数。')

# ============================================================
# 3. 前 K 个高频元素
# ============================================================
p = '前 K 个高频元素'
d = make_deck(1747301203, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个整数数组 nums 和一个整数 k，请你返回其中出现频率前 k 高的元素。你可以按任意顺序返回答案。')
add_cloze(d, make_front(p, '复杂度'),
    '优先队列：时间 {{c1::O(n log k)}}，空间 {{c2::O(n)}}<br>'
    '桶排序：时间 {{c3::O(n)}}，空间 {{c4::O(n)}}')
add_basic(d, make_front(p, '题解(优先队列-小根堆)'),
    '用小根堆维护大小为k，堆顶是最小频率，遍历完后堆中留下的就是前k高。<br>'
    + code(
        'class Solution {\n'
        '    public int[] topKFrequent(int[] nums, int k) {\n'
        '        int[] res = new int[k];\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        for (int num : nums) {\n'
        '            map.put(num, map.getOrDefault(num, 0) + 1);\n'
        '        }\n'
        '        Set<Map.Entry<Integer, Integer>> entries = map.entrySet();\n'
        '        PriorityQueue<Map.Entry<Integer, Integer>> queue = new PriorityQueue<>((a, b) -> a.getValue() - b.getValue());\n'
        '        for(Map.Entry<Integer, Integer> entry: map.entrySet()){\n'
        '            queue.offer(entry);\n'
        '            if(queue.size() > k)\n'
        '                queue.poll();\n'
        '        }\n'
        '        for (int i = k - 1; i >= 0; i--) {\n'
        '            res[i] = queue.poll().getKey();\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(桶排序)'),
    '以频率作为数组下标（桶），频率相同的放同一桶，从高到低取前k个。<br>'
    + code(
        'class Solution {\n'
        '    public int[] topKFrequent(int[] nums, int k) {\n'
        '        int len = nums.length;\n'
        '        List<Integer> res = new ArrayList();\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        for(int num : nums){\n'
        '            map.put(num, map.getOrDefault(num, 0) + 1);\n'
        '        }\n'
        '        List<Integer>[] buckets = new List[nums.length+1];\n'
        '        for(int key : map.keySet()){\n'
        '            int count = map.get(key);\n'
        '            if(buckets[count] == null)\n'
        '                buckets[count] = new ArrayList<>();\n'
        '            buckets[count].add(key);\n'
        '        }\n'
        '        for(int i = buckets.length - 1; i >= 0 && res.size() < k; i--){\n'
        '            if(buckets[i] == null)\n'
        '                continue;\n'
        '            res.addAll(buckets[i]);\n'
        '        }\n'
        '        int[] res01 = new int[k];\n'
        '        for(int i = 0; i < res.size(); i++){\n'
        '            res01[i] = res.get(i);\n'
        '        }\n'
        '        return res01;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种解法取舍：<br>'
    '1. 小根堆 O(n log k)：适合 k 很小的情况，只维护 k 个元素<br>'
    '2. 桶排序 O(n)：适合 k 接近 n 的情况，不需要排序<br>'
    '小根堆为什么不能换成大根堆？因为出队只能从堆顶，大根堆会把频率最高的出掉。')

# ============================================================
# 4. 多数元素
# ============================================================
p = '多数元素'
d = make_deck(1747301204, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个大小为 n 的数组 nums，返回其中的多数元素。多数元素是指在数组中出现次数大于 n/2 的元素。'
    '你可以假设数组是非空的，并且给定的数组总是存在多数元素。' + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    'HashMap法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    'Boyer-Moore投票：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(HashMap)'),
    '统计频率，遇到计数 &gt; n/2 直接返回，提前退出。<br>'
    + code(
        'public class Solution {\n'
        '    public int majorityElement(int[] nums) {\n'
        '        Map<Integer, Integer> cnt = new HashMap<>();\n'
        '        int n = nums.length;\n'
        '        for (int x : nums) {\n'
        '            int c = cnt.getOrDefault(x, 0) + 1;\n'
        '            if (c > n / 2) return x;\n'
        '            cnt.put(x, c);\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'Boyer-Moore 投票算法（O(1)空间）：<br>'
    'candidate = nums[0], count = 1<br>'
    '遍历：若 count==0 则换 candidate，num==candidate 则 count++，否则 count--<br>'
    '原理：多数元素数量 &gt; n/2，一定能抵消所有其他元素并胜出。')

# ============================================================
# 5. 和为K的子数组
# ============================================================
p = '和为K的子数组'
d = make_deck(1747301205, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个整数数组 nums 和一个整数 k，请你统计并返回该数组中和为 k 的连续子数组的个数。'
    '注意：数组中有负数，不能用滑动窗口。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — HashMap 存前缀和')
add_basic(d, make_front(p, '题解(前缀和+HashMap)'),
    'preSum[j] - preSum[i-1] = k → preSum[i-1] = preSum[j] - k，找之前有多少个前缀和等于 preSum-k。<br>'
    + code(
        'class Solution {\n'
        '    public int subarraySum(int[] nums, int k) {\n'
        '        if(nums == null || nums.length == 0)\n'
        '            return 0;\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        map.put(0, 1);\n'
        '        int preSum = 0;\n'
        '        int count = 0;\n'
        '        for(int num : nums){\n'
        '            preSum += num;\n'
        '            if(map.containsKey(preSum - k))\n'
        '                count += map.get(preSum - k);\n'
        '            map.put(preSum, map.getOrDefault(preSum, 0) + 1);\n'
        '        }\n'
        '        return count;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心转化：区间和 = k → preSum[j] - preSum[i-1] = k → preSum[i-1] = preSum[j] - k<br>'
    'HashMap 的 key 存前缀和，value 存该前缀和出现的次数。<br>'
    '初始化 map.put(0,1) 处理从索引 0 开始的子数组。<br>'
    '注意：需要先 containsKey 检查再 put 当前 preSum（不能反过来），避免 k=0 时重复计数。')

# ============================================================
# 6. 和可被 K 整除的子数组
# ============================================================
p = '和可被 K 整除的子数组'
d = make_deck(1747301206, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums 和一个整数 k，返回其中元素之和可被 k 整除的（连续、非空）子数组的数目。'
    + img('image 1.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(min(n,k))}} — HashMap 存余数')
add_basic(d, make_front(p, '题解(前缀和+余数)'),
    '同余定理：若 preSum[j] 和 preSum[i-1] 对 k 同余，则区间和可被 k 整除。组合数 C(m,2) 计算。<br>'
    + code(
        'class Solution {\n'
        '    public int subarraysDivByK(int[] nums, int k) {\n'
        '        Map<Integer, Integer> map = new LinkedHashMap<>();\n'
        '        int sum = 0;\n'
        '        for(int i = 0; i < nums.length; i++){\n'
        '            sum += nums[i];\n'
        '            int mod = sum >= 0 ? sum % k : (k - (-sum) % k) % k;\n'
        '            if(map.containsKey(mod))\n'
        '                map.put(mod, map.get(mod) + 1);\n'
        '            else\n'
        '                map.put(mod, 1);\n'
        '        }\n'
        '        int res = 0;\n'
        '        for (Map.Entry<Integer, Integer> item : map.entrySet()) {\n'
        '            res += item.getValue() * (item.getValue() - 1) / 2;\n'
        '            if(item.getKey() == 0)\n'
        '                res += item.getValue();\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '同余定理：若 preSum[j] 和 preSum[i-1] 对 k 同余，则区间和可被 k 整除。<br>'
    '关键：负数的余数处理 — Java中 -1%5=-1，需转化为正余数：(k - (-sum)%k) % k<br>'
    '统计方法：遍历完后再按组合数公式 C(m,2) 计算，而非边遍历边算。')

# ============================================================
# 7. 连续数组
# ============================================================
p = '连续数组'
d = make_deck(1747301207, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个二进制数组 nums，找到含有相同数量的 0 和 1 的最长连续子数组，并返回该子数组的长度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — HashMap')
add_basic(d, make_front(p, '题解(前缀和+转化)'),
    '将0视为-1，问题转化为"前缀和相同的最远距离"，map只存首次出现位置。<br>'
    + code(
        'class Solution {\n'
        '    public int findMaxLength(int[] nums) {\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        map.put(0, -1);\n'
        '        int len = nums.length;\n'
        '        if(len <= 0)\n'
        '            return 0;\n'
        '        int cur = 0, maxLen = 0;\n'
        '        for(int i = 0; i < len; i++){\n'
        '            cur = nums[i] == 0 ? cur - 1 : cur + 1;\n'
        '            if(map.containsKey(cur))\n'
        '                maxLen = Math.max(maxLen, i - map.get(cur));\n'
        '            else\n'
        '                map.put(cur, i);\n'
        '        }\n'
        '        return maxLen;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '转化思想：0和1数量相等 → 将0当作-1 → 和为0的子数组。<br>'
    '与"和为K的子数组"的区别：<br>'
    '1. 本题求最长，map只存前缀和首次出现的位置（不更新）<br>'
    '2. K=0，且初始化 map.put(0, -1) 处理从索引0开始的情况')

# ============================================================
# 8. 只出现一次的数字
# ============================================================
p = '只出现一次的数字'
d = make_deck(1747301208, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非空整数数组，除了某个元素只出现一次以外，其余每个元素均出现两次。找出那个只出现了一次的元素。')
add_cloze(d, make_front(p, '复杂度'),
    'HashSet法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    'XOR法：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(HashSet)'),
    '第一次出现add成功，第二次出现add失败则remove，最后set只剩一个元素。<br>'
    + code(
        'class Solution {\n'
        '    public int singleNumber(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        Set<Integer> set = new HashSet<>();\n'
        '        for (int i = 0; i < len; i++) {\n'
        '            if (!set.add(nums[i])) {\n'
        '                set.remove(nums[i]);\n'
        '            }\n'
        '        }\n'
        '        return set.iterator().next();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(XOR)'),
    'a^b^a = b，成对出现的全部抵消为0，剩下单独的那个数。<br>'
    + code(
        'class Solution {\n'
        '    public int singleNumber(int[] nums) {\n'
        '        int res = nums[0];\n'
        '        for(int i = 1; i < nums.length; i++)\n'
        '            res = res ^ nums[i];\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'XOR 核心性质：a^a=0, a^0=a, a^b^a=b。<br>'
    '成对出现的数互相抵消后只剩单独的数。<br>'
    '局限性：只能用于"其他元素出现偶数次"的场景；若出现奇数次不适用。')

# ============================================================
# 9. 只出现一次的数字 III
# ============================================================
p = '只出现一次的数字 III'
d = make_deck(1747301209, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums，其中恰好有两个元素只出现一次，其余所有元素均出现两次。找出那两个只出现一次的元素。')
add_cloze(d, make_front(p, '复杂度'),
    'HashSet法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    'XOR+分组法：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(HashSet)'),
    '与只出现一次的数字 I 思路相同，最后 set 中剩两个元素。<br>'
    + code(
        'class Solution {\n'
        '    public int[] singleNumber(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        if(len < 2)\n'
        '            return null;\n'
        '        Set<Integer> set = new HashSet<>();\n'
        '        for(int i = 0; i < len; i++){\n'
        '            if(!set.add(nums[i])){\n'
        '                set.remove(nums[i]);\n'
        '            }\n'
        '        }\n'
        '        int[] res = new int[2];\n'
        '        int i = 0;\n'
        '        for(int item : set){\n'
        '            res[i++] = item;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(XOR+分组)'),
    '全异或得到 temp=a^b≠0，mask取最低位1将数组分成两组，a和b各在一边。<br>'
    + code(
        'class Solution {\n'
        '    public int[] singleNumber(int[] nums) {\n'
        '        int[] res = new int[2];\n'
        '        int temp = 0;\n'
        '        for(int num : nums){\n'
        '            temp ^= num;\n'
        '        }\n'
        '        int mask = temp & (-temp);\n'
        '        for (int num : nums) {\n'
        '            if ((num & mask) == 0) {\n'
        '                res[0] ^= num;\n'
        '            } else {\n'
        '                res[1] ^= num;\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '全异或得到 temp = a^b。temp≠0说明a和b至少有一位不同。<br>'
    'mask = temp & (-temp)：取 temp 最低位的 1，a和b在这一位上必然不同。<br>'
    '按 mask 分组异或，降维为两个"只出现一次的数字 I"。')

# ============================================================
# 10. 复制带随机指针的链表
# ============================================================
p = '复制带随机指针的链表'
d = make_deck(1747301210, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个长度为 n 的链表，每个节点包含一个额外增加的随机指针 random，该指针可以指向链表中的任何节点或空节点。'
    '构造这个链表的深拷贝。' + img('image 2.png') + img('image 3.png') + img('image 4.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 两次遍历链表<br>空间：{{c2::O(n)}} — HashMap 存原节点→新节点映射')
add_basic(d, make_front(p, '题解(HashMap映射)'),
    '原节点→新节点的映射，第一遍创建所有新节点，第二遍设置next和random。<br>'
    + code(
        'class Solution {\n'
        '    public Node copyRandomList(Node head) {\n'
        '        if(head==null) {\n'
        '            return null;\n'
        '        }\n'
        '        Map<Node,Node> map = new HashMap<Node,Node>();\n'
        '        Node p = head;\n'
        '        while(p!=null) {\n'
        '            Node newNode = new Node(p.val);\n'
        '            map.put(p,newNode);\n'
        '            p = p.next;\n'
        '        }\n'
        '        p = head;\n'
        '        while(p!=null) {\n'
        '            Node newNode = map.get(p);\n'
        '            if(p.next!=null) {\n'
        '                newNode.next = map.get(p.next);\n'
        '            }\n'
        '            if(p.random!=null) {\n'
        '                newNode.random = map.get(p.random);\n'
        '            }\n'
        '            p = p.next;\n'
        '        }\n'
        '        return map.get(head);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'HashMap 做节点映射（原节点 → 新节点），两次遍历：<br>'
    '第一遍创建所有新节点并建立映射关系<br>'
    '第二遍通过 map 将新节点的 next 和 random 指向对应的新节点<br>'
    'O(1)空间解法：交叉插入（A→A\'→B→B\'），但面试一般用 HashMap 版本更直观。')

# ============================================================
# 11. 最长连续序列
# ============================================================
p = '最长连续序列'
d = make_deck(1747301211, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个未排序的整数数组 nums，找出数字连续的最长序列（不要求序列元素在原数组中连续）的长度。'
    '请你设计并实现时间复杂度为 O(n) 的算法。' + img('image 5.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多被访问两次（外层set遍历 + 内层while）<br>空间：{{c2::O(n)}} — HashSet')
add_basic(d, make_front(p, '题解(HashSet)'),
    '只有当 x-1 不在 set 中时（说明x是起点），才开始向后数，避免重复计算。<br>'
    + code(
        'public class Solution {\n'
        '    public int longestConsecutive(int[] nums) {\n'
        '        Set<Integer> set = new HashSet<>();\n'
        '        for (int x : nums) set.add(x);\n'
        '        int ans = 0;\n'
        '        for (int x : set) {\n'
        '            if (!set.contains(x - 1)) {\n'
        '                int y = x, len = 1;\n'
        '                while (set.contains(y + 1)) {\n'
        '                    y++;\n'
        '                    len++;\n'
        '                }\n'
        '                ans = Math.max(ans, len);\n'
        '            }\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '判断起点：if(!set.contains(x-1)) — x是序列起点时才向后扩展。<br>'
    '内层while虽然看起来是O(n²)，但每个元素最多作为起点的后继被访问一次，仍是O(n)。<br>'
    '排序+DP也可解但O(n log n)，不满足题目要求。')

# ============================================================
# 12. 两个数组的交集
# ============================================================
p = '两个数组的交集'
d = make_deck(1747301212, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个数组 nums1 和 nums2，返回它们的交集。输出结果中的每个元素一定是唯一的。不考虑输出顺序。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n+m)}} — 遍历两个数组<br>空间：{{c2::O(n)}} — HashMap 存 nums1')
add_basic(d, make_front(p, '题解(HashMap去重)'),
    '用map的value标记状态：1=第一个数组出现过，2=已加入结果集。<br>'
    + code(
        'class Solution {\n'
        '    public int[] intersection(int[] nums1, int[] nums2) {\n'
        '        Map<Integer, Integer> map = new HashMap<>();\n'
        '        for(int i = 0; i < nums1.length; i++){\n'
        '            if(map.containsKey(nums1[i]))\n'
        '                continue;\n'
        '            else\n'
        '                map.put(nums1[i], 1);\n'
        '        }\n'
        '        int j = 0;\n'
        '        for(int i = 0; i < nums2.length; i++){\n'
        '            if(map.containsKey(nums2[i]) && map.get(nums2[i]) == 1){\n'
        '                nums1[j] = nums2[i];\n'
        '                map.put(nums2[i], map.get(nums2[i]) + 1);\n'
        '                j++;\n'
        '            }else\n'
        '                continue;\n'
        '        }\n'
        '        return Arrays.copyOf(nums1, j);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '去重技巧：map value 做状态标记<br>'
    '1：nums1中出现过（待选）<br>'
    '2：已经加入结果集（避免重复输出）<br>'
    '复用 nums1 数组空间存储结果，最后 copyOf 截取。')

# ============================================================
# 13. 第一个只出现一次的字符
# ============================================================
p = '第一个只出现一次的字符'
d = make_deck(1747301213, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '在字符串 s 中找出第一个只出现一次的字符。如果没有，返回一个单空格。')
add_cloze(d, make_front(p, '复杂度'),
    'HashMap法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    '数组法：时间 {{c3::O(n)}}，空间 {{c4::O(26)=O(1)}}')
add_basic(d, make_front(p, '题解(HashMap)'),
    '统计频率后再从头遍历，找到第一个count==1的字符。<br>'
    + code(
        'public class Solution {\n'
        '    public int firstUniqChar(String s) {\n'
        '        Map<Character, Integer> cnt = new HashMap<>();\n'
        '        for (int i = 0; i < s.length(); i++) {\n'
        '            char c = s.charAt(i);\n'
        '            cnt.put(c, cnt.getOrDefault(c, 0) + 1);\n'
        '        }\n'
        '        for (int i = 0; i < s.length(); i++) {\n'
        '            if (cnt.get(s.charAt(i)) == 1) return i;\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(数组-原地哈希)'),
    '由于只有小写字母，用int[26]更高效，字符→索引映射。<br>'
    + code(
        'class Solution {\n'
        '    public char firstUniqChar(String s) {\n'
        '        int[] temp = new int[26];\n'
        '        char[] charss = s.toCharArray();\n'
        '        for(char item:charss)\n'
        '            temp[item-\'a\']++;\n'
        '        for(char item:charss)\n'
        '            if(temp[item-\'a\']==1)\n'
        '                return item;\n'
        '        return \' \';\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '需要一个"稳定"的遍历顺序找到"第一个"：不能用 HashMap 遍历（无序），必须重新遍历原字符串。<br>'
    '字符范围有限（26字母）时，int[26] 比 HashMap 更快更省空间。')

# ============================================================
# 14. 缺失的第一个正数
# ============================================================
p = '缺失的第一个正数'
d = make_deck(1747301214, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个未排序的整数数组 nums，请你找出其中没有出现的最小的正整数。'
    '请你实现时间复杂度为 O(n) 并且只使用常数级别额外空间的解决方案。')
add_cloze(d, make_front(p, '复杂度'),
    '原地哈希：时间 {{c1::O(n)}} — 每个元素最多交换一次<br>空间：{{c2::O(1)}} — 原地交换，无额外存储')
add_basic(d, make_front(p, '题解(原地哈希)'),
    '将值x放到索引x-1的位置（x∈[1,n]），超出范围或已就位的跳过。用while而非if。<br>'
    + code(
        'class Solution {\n'
        '    public int firstMissingPositive(int[] nums) {\n'
        '        for(int i = 0; i < nums.length; i++){\n'
        '            while(nums[i] > 0 && nums[i] <= nums.length && nums[nums[i] - 1] != nums[i])\n'
        '                swap(nums, nums[i] - 1, i);\n'
        '        }\n'
        '        for(int i = 0; i < nums.length; i++){\n'
        '            if(nums[i] != i + 1)\n'
        '                return i + 1;\n'
        '        }\n'
        '        return nums.length + 1;\n'
        '    }\n'
        '\n'
        '    public void swap(int[] nums,int index1, int index2){\n'
        '        int temp = nums[index1];\n'
        '        nums[index1] = nums[index2];\n'
        '        nums[index2] = temp;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '原地哈希思想：数组本身作为哈希表，nums[i] 应该放在 nums[nums[i]-1] 位置。<br>'
    '关键细节：<br>'
    '1. 用 while 而非 if：交换后当前位置的新数仍需处理<br>'
    '2. nums[nums[i]-1] != nums[i] 防止死循环（相同值不交换）<br>'
    '3. 只处理 [1, n] 范围内的值，忽略 &lt;=0 和 &gt;n 的值')

# ============================================================
# 15. 整数反转
# ============================================================
p = '整数反转'
d = make_deck(1747301215, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个 32 位的有符号整数 x，返回将 x 中的数字部分反转后的结果。'
    '如果反转后整数超过 32 位有符号整数的范围 [-2^31, 2^31-1]，就返回 0。'
    + img('image 6.png') + img('image 7.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 数字位数<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(取余+溢出判断)'),
    '每次取末尾数字tmp=x%10，在res*10+tmp之前判断溢出。<br>'
    + code(
        'class Solution {\n'
        '    public int reverse(int x) {\n'
        '        int res = 0;\n'
        '        while(x != 0) {\n'
        '            int tmp = x % 10;\n'
        '            if (res > 214748364 || (res == 214748364 && tmp > 7)) {\n'
        '                return 0;\n'
        '            }\n'
        '            if (res < -214748364 || (res == -214748364 && tmp < -8)) {\n'
        '                return 0;\n'
        '            }\n'
        '            res = res * 10 + tmp;\n'
        '            x /= 10;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '溢出判断公式（Java int 范围 [-2147483648, 2147483647]）：<br>'
    '正溢出：res &gt; 214748364 || (res == 214748364 && tmp &gt; 7)<br>'
    '负溢出：res &lt; -214748364 || (res == -214748364 && tmp &lt; -8)<br>'
    '原理：214748364 是 MAX/10，7 是 MAX%10。必须在乘10之前判断。')

# ============================================================
# 16. 颜色分类
# ============================================================
p = '颜色分类'
d = make_deck(1747301216, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含红色(0)、白色(1)、蓝色(2)，一共 n 个元素的数组，原地对它们进行排序，'
    '使得相同颜色的元素相邻，并按照红色、白色、蓝色顺序排列。')
add_cloze(d, make_front(p, '复杂度'),
    '哈希计数法：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '三指针（荷兰国旗）：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}，一次遍历')
add_basic(d, make_front(p, '题解(HashMap计数)'),
    '统计0,1,2的个数，然后按顺序重填数组。<br>'
    + code(
        'class Solution {\n'
        '    public void sortColors(int[] nums) {\n'
        '        if(nums.length <= 1)\n'
        '            return;\n'
        '        Map<Integer, Integer> map = new LinkedHashMap<>();\n'
        '        map.put(0, 0);\n'
        '        map.put(1, 0);\n'
        '        map.put(2, 0);\n'
        '        for(int num : nums){\n'
        '            map.put(num, map.get(num) + 1);\n'
        '        }\n'
        '        for(int i = 0; i < map.get(0); i++){\n'
        '            nums[i] = 0;\n'
        '        }\n'
        '        int start = map.get(0);\n'
        '        for(int i = start; i < start + map.get(1); i++){\n'
        '            nums[i] = 1;\n'
        '        }\n'
        '        start += map.get(1);\n'
        '        for(int i = start; i < nums.length; i++){\n'
        '            nums[i] = 2;\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '荷兰国旗问题（三指针，一次遍历）：<br>'
    'p0=0（0的右边界），p2=n-1（2的左边界），i=0 遍历<br>'
    'nums[i]==0 → swap(nums,i,p0), p0++, i++<br>'
    'nums[i]==2 → swap(nums,i,p2), p2--（i不动，因为换过来的新值还需检查）<br>'
    'nums[i]==1 → i++<br>'
    '哈希计数法虽然简单，但需要两次遍历。三指针是真正的一道遍历。')

# ============================================================
# 17. 数组中重复的数据
# ============================================================
p = '数组中重复的数据'
d = make_deck(1747301217, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个长度为 n 的整数数组 nums，其中 nums 的所有整数都在范围 [1, n] 内，且每个整数出现一次或两次。'
    '请你找出所有出现两次的整数，并以数组形式返回。时间复杂度 O(n)，空间复杂度 O(1)。'
    + img('image 8.png'))
add_cloze(d, make_front(p, '复杂度'),
    '取反标记法：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '加n标记法：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(取反标记)'),
    '用原数组做标记：将nums[x-1]取反，若第二次访问时已为负数，则x是重复值。<br>'
    + code(
        'class Solution {\n'
        '    public List<Integer> findDuplicates(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        List<Integer> ans = new ArrayList<Integer>();\n'
        '        for (int i = 0; i < n; ++i) {\n'
        '            int x = Math.abs(nums[i]);\n'
        '            if (nums[x - 1] > 0) {\n'
        '                nums[x - 1] = -nums[x - 1];\n'
        '            } else {\n'
        '                ans.add(x);\n'
        '            }\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(加n标记)'),
    '每个数对应的索引加n，重复的数对应的索引会被加2次，值 &gt; 2n 的索引+1就是重复数。<br>'
    + code(
        'class Solution {\n'
        '    public List<Integer> findDuplicates(int[] nums) {\n'
        '        List<Integer> ret = new ArrayList<>();\n'
        '        int n = nums.length;\n'
        '        for(int i = 0; i < n; i++){\n'
        '            nums[(nums[i] - 1) % n] += n;\n'
        '        }\n'
        '        for(int i = 0; i < n; i++){\n'
        '            if(nums[i] > 2 * n) ret.add(i+1);\n'
        '        }\n'
        '        return ret;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '原地哈希思想：利用原数组做标记，不额外开数组。<br>'
    '方法1（取反）：访问过就取反，第二次访问时发现已是负数 → 重复<br>'
    '方法2（加n）：访问一次加n，访问两次加2n，最终值 &gt; 2n的索引即重复<br>'
    '共同前提：值范围 [1, n]，可以映射到索引 [0, n-1]。')

# ============================================================
# 18. 按权重随机选择
# ============================================================
p = '按权重随机选择'
d = make_deck(1747301218, f'算法::哈希表::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个正整数数组 w，其中 w[i] 代表第 i 个下标的权重。实现 pickIndex 函数，'
    '随机地从范围 [0, w.length - 1] 内选取一个下标，选取下标 i 的概率与 w[i] 成正比。')
add_cloze(d, make_front(p, '复杂度'),
    '构造：时间 {{c1::O(n)}}，空间 {{c2::O(n)}} — 前缀和数组<br>'
    'pickIndex：时间 {{c3::O(log n)}} — 二分查找')
add_basic(d, make_front(p, '题解(前缀和+二分)'),
    '前缀和将权重转化为区间长度，随机数t落在哪个区间就选对应下标。<br>'
    + code(
        'class Solution {\n'
        '    int[] sum;\n'
        '    public Solution(int[] w) {\n'
        '        int n = w.length;\n'
        '        sum = new int[n + 1];\n'
        '        for (int i = 1; i <= n; i++)\n'
        '            sum[i] = sum[i - 1] + w[i - 1];\n'
        '    }\n'
        '\n'
        '    public int pickIndex() {\n'
        '        int n = sum.length;\n'
        '        int t = (int) (Math.random() * sum[n - 1]) + 1;\n'
        '        int left = 1, right = n - 1;\n'
        '        while (left < right) {\n'
        '            int mid = left + (right - left) / 2;\n'
        '            if (sum[mid] >= t)\n'
        '                right = mid;\n'
        '            else\n'
        '                left = mid + 1;\n'
        '        }\n'
        '        return right - 1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '前缀和 + 二分查找的经典组合：<br>'
    'w=[1,3] → sum=[0,1,4]，区间(0,1]→0, (1,4]→1<br>'
    '随机数 t∈[1,4]，二分查找 sum[mid]&gt;=t 的最左位置。<br>'
    '返回 right-1 是因为 sum 从索引1开始映射到w的索引0。')

if __name__ == '__main__':
    print(build('../../牌组/算法/哈希表.apkg'))

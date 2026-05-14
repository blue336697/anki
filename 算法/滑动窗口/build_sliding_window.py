"""Build APKG for 滑动窗口 (Sliding Window). 4 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747300300, '算法::滑动窗口::原理通识')
add_basic(d0, '滑动窗口核心框架',
    '滑动窗口 = 双指针维护一个动态区间 [left, right)<br>'
    '关键三要素：<br>'
    '1. 窗口扩张：右指针 right++，加入新元素<br>'
    '2. 窗口收缩：左指针 left++，移除旧元素（while 满足条件）<br>'
    '3. 更新结果：在合适的时机更新答案')
add_cloze(d0, '滑动窗口适用场景：{{c1::子串/子数组}}问题，要求{{c2::连续}}且满足{{c3::某种单调性}}',
    '典型：最小覆盖子串、长度最小子数组、无重复字符最长子串')
add_basic(d0, '固定窗口 vs 可变窗口',
    '固定窗口：窗口长度固定为 k，right-left==k 时同时移动 left<br>'
    '可变窗口：while 不满足条件时收缩 left，窗口大小动态变化<br>'
    'need 数组技巧：正数=还需要，负数=多余，0=刚好满足')

# ============================================================
# 1. 最小覆盖子串
# ============================================================
p = '最小覆盖子串'
d = make_deck(1747300301, f'算法::滑动窗口::{p}')
add_basic(d, make_front(p, '题干'),
    '给定字符串 s 和 t，在 s 中找出包含 t 所有字符的最小子串。'
    '如果不存在则返回空字符串。' + img('image.png'))

add_cloze(d, make_front(p, '指针策略'),
    'right移动：{{c1::每次循环 right++，加入新字符}}<br>'
    'left移动：{{c2::当 count==0（窗口已满足）时，while need[s[left]] &lt; 0 收缩 left}}<br>'
    'need数组：正数={{c3::还需要}}，0={{c4::刚好满足}}，负数={{c5::多余}}')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m+n)}} — 每个字符被 left 和 right 各访问一次<br>空间：{{c2::O(128)}} — need 数组，常数级')

add_basic(d, make_front(p, '题解(滑动窗口)'),
    '用 need 数组计数，right 扩张时 count--，count=0 时收缩 left 过滤多余字符，更新最小窗口。<br>'
    + code(
'''class Solution {
    public String minWindow(String s, String t) {
        // need数组: 正数=还需要, 负数=多余
        int[] need = new int[128];
        for (int i = 0; i &lt; t.length(); i++) {
            need[t.charAt(i)]++;
        }
        int left = 0, right = 0, size = Integer.MAX_VALUE, count = t.length(), start = 0;
        while (right &lt; s.length()) {
            char c = s.charAt(right);
            if (need[c] &gt; 0) {
                count--;
            }
            need[c]--;
            if (count == 0) {
                // 收缩左边界，过滤多余字符
                while (left &lt; right && need[s.charAt(left)] &lt; 0) {
                    need[s.charAt(left)]++;
                    left++;
                }
                if (right - left + 1 &lt; size) {
                    size = right - left + 1;
                    start = left;
                }
                // 移动左边界，寻找下一个满足条件的窗口
                need[s.charAt(left)]++;
                left++;
                count++;
            }
            right++;
        }
        return size == Integer.MAX_VALUE ? "" : s.substring(start, start + size);
    }
}'''))

# ============================================================
# 2. 长度最小的子数组
# ============================================================
p = '长度最小的子数组'
d = make_deck(1747300302, f'算法::滑动窗口::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个含有 n 个正整数的数组和一个正整数 target。'
    '找出该数组中满足其和 >= target 的长度最小的连续子数组，返回其长度。')

add_cloze(d, make_front(p, '指针策略'),
    'right移动：{{c1::每次循环 sum+=nums[right++]}}，扩张窗口<br>'
    'left移动：{{c2::while(sum >= target)}} 收缩窗口，更新 min，sum-=nums[left++]<br>'
    '本质：不断扩张直到满足条件，然后不断收缩直到不满足，交替进行')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多入窗口一次、出窗口一次<br>空间：{{c2::O(1)}} — 只用了几个变量')

add_basic(d, make_front(p, '题解(滑动窗口)'),
    'right 扩张累加 sum，当 sum>=target 时收缩 left 并更新最小长度。<br>'
    + code(
'''class Solution {
    public int minSubArrayLen(int s, int[] nums) {
        int left = 0, right = 0, sum = 0, min = Integer.MAX_VALUE;
        while (right &lt; nums.length) {
            sum += nums[right++];
            while (sum &gt;= s) {
                min = Math.min(min, right - left);
                sum -= nums[left++];
            }
        }
        return min == Integer.MAX_VALUE ? 0 : min;
    }
}'''))

add_basic(d, make_front(p, '对比'),
    '与最小覆盖子串区别：最小覆盖用 need 数组计数字符，本题用 sum 计数和。<br>'
    '共同点：都是 right 扩张、while 条件收缩 left 的可变窗口模板。')

# ============================================================
# 3. 最大连续1的个数 III
# ============================================================
p = '最大连续1的个数 III'
d = make_deck(1747300303, f'算法::滑动窗口::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个由若干 0 和 1 组成的数组 A，最多可以将 K 个 0 变成 1，'
    '返回仅包含 1 的最长连续子数组的长度。')

add_cloze(d, make_front(p, '指针策略'),
    '题意转化：窗口中最多允许 {{c1::K 个 0}}<br>'
    'right移动：{{c2::每次遍历 end++，遇到 0 则 zero++}}<br>'
    'left移动：{{c3::while(zero > K)}} 收缩 start，遇到 0 则 zero--<br>'
    '更新结果：{{c4::每次循环都更新 res = max(res, end-start+1)}}')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多访问两次<br>空间：{{c2::O(1)}}')

add_basic(d, make_front(p, '题解(滑动窗口)'),
    '题意转化为窗口中最多 K 个 0，超过 K 时收缩左边界。<br>'
    + code(
'''class Solution {
    public int longestOnes(int[] nums, int k) {
        int len = nums.length;
        if (len == 0)
            return 0;
        int zero = 0, res = 0, start = 0;
        for (int end = 0; end &lt; len; end++) {
            if (nums[end] == 0)
                zero++;
            while (zero &gt; k) {
                if (nums[start++] == 0)
                    zero--;
            }
            res = Math.max(res, end - start + 1);
        }
        return res;
    }
}'''))

# ============================================================
# 4. 字符串的排列
# ============================================================
p = '字符串的排列'
d = make_deck(1747300304, f'算法::滑动窗口::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个字符串 s1 和 s2，写一个函数来判断 s2 是否包含 s1 的排列。'
    '即判断 s1 的排列之一是 s2 的子串。')

add_cloze(d, make_front(p, '指针策略'),
    'right移动：{{c1::加入新字符到窗口，更新 window 数组}}，匹配时 needCount++<br>'
    'left移动：{{c2::当窗口大小 right-left >= len1 时}}，收缩 left，移出字符更新 window<br>'
    '匹配条件：{{c3::needCount == pCount}}（窗口中每种字符数量都满足 needs）<br>'
    '关键：使用 needCount 记录已匹配的{{c4::字符种类数}}（而非字符个数）')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个字符最多进出窗口各一次<br>空间：{{c2::O(26)}} — 两个 count 数组')

add_basic(d, make_front(p, '题解(固定窗口)'),
    '固定窗口大小 = len1，直接滑动窗口比较两个词频数组是否相等。<br>'
    + code(
'''class Solution {
    public boolean checkInclusion(String s1, String s2) {
        int len1 = s1.length();
        int len2 = s2.length();
        if (len1 &gt; len2)
            return false;
        int[] targetCount1 = new int[26];
        int[] targetCount2 = new int[26];
        for (int i = 0; i &lt; len1; i++) {
            targetCount1[s1.charAt(i) - \'a\']++;
            targetCount2[s2.charAt(i) - \'a\']++;
        }
        for (int i = len1; i &lt; len2; i++) {
            if (Arrays.equals(targetCount1, targetCount2)) {
                return true;
            }
            targetCount2[s2.charAt(i) - \'a\']++;
            targetCount2[s2.charAt(i - len1) - \'a\']--;
        }
        return Arrays.equals(targetCount1, targetCount2);
    }
}'''))

add_basic(d, make_front(p, '题解(可变窗口)'),
    '通用滑动窗口模板（与438题通用）：needCount 记录已匹配字符种类数，right 扩张直到窗口大小>=len1，收缩 left。<br>'
    + code(
'''class Solution {
    public boolean checkInclusion(String s1, String s2) {
        int[] window = new int[26], needs = new int[26];
        int len1 = s1.length(), len2 = s2.length();
        for (int i = 0; i &lt; len1; i++) {
            needs[s1.charAt(i) - \'a\']++;
        }
        // s1中不同字符的种类数
        int pCount = 0;
        for (int i = 0; i &lt; 26; i++) {
            if (needs[i] &gt; 0) {
                pCount++;
            }
        }
        int left = 0, right = 0;
        int needCount = 0;
        while (right &lt; len2) {
            char ch = s2.charAt(right);
            right++;
            if (needs[ch - \'a\'] &gt; 0) {
                window[ch - \'a\']++;
                if (window[ch - \'a\'] == needs[ch - \'a\'])
                    needCount++;
            }
            while (right - left &gt;= len1) {
                if (needCount == pCount)
                    return true;
                char remove = s2.charAt(left);
                left++;
                if (needs[remove - \'a\'] &gt; 0) {
                    if (window[remove - \'a\'] == needs[remove - \'a\'])
                        needCount--;
                    window[remove - \'a\']--;
                }
            }
        }
        return false;
    }
}'''))

if __name__ == '__main__':
    print(build('../../牌组/算法/滑动窗口.apkg'))

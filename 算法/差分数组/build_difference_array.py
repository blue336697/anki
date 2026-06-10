"""Build APKG for 差分数组 (Difference Array). 3 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747302200, '算法::差分数组::原理通识')
add_basic(d0, '差分数组核心框架',
    '差分数组用于高效处理<b>区间增减</b>操作。<br>'
    '构建：diff[i] = arr[i] - arr[i-1]<br>'
    '区间更新 [l,r] +v：diff[l] += v; diff[r+1] -= v<br>'
    '还原：arr[i] = arr[i-1] + diff[i]（前缀和）<br>'
    '核心思想：<b>将对整个区间的修改转换为对两个端点的修改</b>')
add_cloze(d0,
    '差分数组三步走：<br>'
    'Step1：{{c1::构建 diff 数组，diff[i] = arr[i] - arr[i-1]}}<br>'
    'Step2：{{c2::区间更新：diff[l] += val, diff[r+1] -= val}}<br>'
    'Step3：{{c3::前缀和还原：arr[i] = arr[i-1] + diff[i]}}',
    '核心就是"端点操作 + 前缀和还原"')
add_cloze(d0,
    '差分数组适用场景信号：{{c1::区间增减}} + {{c2::最后问每个位置的值}}<br>'
    '看到"对某个区间统一加减，问最终结果"→差分数组<br>'
    'diff[r+1]-=v 中 r+1 是否越界：闭区间[l,r]用{{c3::r+1}}；左闭右开[l,r)用{{c4::r}}',
    '闭区间 vs 开区间的边界处理')
add_cloze(d0,
    '差分 vs 前缀和的关系：{{c1::差分是前缀和的逆运算}}<br>'
    '前缀和：arr → pre，求区间和<br>'
    '差分：diff → arr，做区间更新<br>'
    '{{c2::差分数组的前缀和 = 原数组}}',
    '一对互逆操作')

# ============================================================
# 1. 370. 区间加法
# ============================================================
p = '370. 区间加法'
d = make_deck(1747302201, f'算法::差分数组::{p}')
add_basic(d, make_front(p, '题干'),
    '假设你有一个长度为 length 的数组，初始值全为 0。'
    '给定一组更新操作 updates[i] = [startIdx, endIdx, inc]，'
    '对于每个操作，将数组中从下标 startIdx 到 endIdx（包含两端）的每个元素加上 inc。'
    '返回操作完成后的最终数组。<br><br>'
    '示例：length=5, updates=[[1,3,2],[2,4,3],[0,2,-2]] → [-2,0,3,5,3]')

add_cloze(d, make_front(p, '差分策略'),
    '构建差分数组：diff[i] = arr[i] - arr[i-1]（初始全 0 时 diff 也全 0）<br>'
    '区间更新：diff[start] += inc，diff[end+1] -= inc（注意 end+1 越界）<br>'
    '前缀和还原：遍历 diff，arr[i] = arr[i-1] + diff[i]<br>'
    '核心原理：<br>'
    '{{c1::diff[start] += inc}} — 从 start 开始，prefix sum 都会 +inc<br>'
    '{{c2::diff[end+1] -= inc}} — 从 end+1 开始，prefix sum 不再受 +inc 影响')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(U+N)}}，U 为更新次数（构建 diff），N 为数组长度（前缀和还原）<br>'
    '空间：{{c1::O(N)}} — diff 数组（可复用结果数组省去额外空间）')

add_basic(d, make_front(p, '题解（复用数组）'),
    '对每次更新 [start, end, inc]：res[start] += inc；若 end+1 &lt; length，res[end+1] -= inc。<br>'
    '遍历完所有更新后，对 res 做一次前缀和即得答案。<br>'
    + code(
'''class Solution {
    public int[] getModifiedArray(int length, int[][] updates) {
        int[] res = new int[length];
        // Build diff array in-place
        for (int[] update : updates) {
            int start = update[0];
            int end = update[1];
            int inc = update[2];
            res[start] += inc;
            if (end + 1 < length) {
                res[end + 1] -= inc;
            }
        }
        // Prefix sum to restore original array
        for (int i = 1; i < length; i++) {
            res[i] += res[i - 1];
        }
        return res;
    }
}'''))

# ============================================================
# 2. 1109. 航班预订统计
# ============================================================
p = '1109. 航班预订统计'
d = make_deck(1747302202, f'算法::差分数组::{p}')
add_basic(d, make_front(p, '题干'),
    '有 n 个航班，编号 1 到 n。给定预订记录 bookings[i] = [first_i, last_i, seats_i]，'
    '表示从 first_i 到 last_i（包含）的每个航班预定了 seats_i 个座位。'
    '返回长度为 n 的数组 answer，其中 answer[i] 是航班 i+1 的预订座位总数。<br><br>'
    '示例：bookings=[[1,2,10],[2,3,20],[2,5,25]], n=5 → [10,55,45,25,25]')

add_cloze(d, make_front(p, '差分策略'),
    '本质就是<b>区间加法</b>：在第 first 到 last 的每个航班上加 seats<br>'
    '索引映射：航班从 1 开始 → 数组从 0 开始<br>'
    '{{c1::diff[first-1] += seats}} — 起点处累加 seats，前缀和从此开始都 +seats<br>'
    '{{c2::diff[last] -= seats}} — 终点+1 处减去 seats，前缀和从此开始取消 +seats<br>'
    '与 370 题完全一样的模板，只是 1-based 转 0-based。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(B+N)}}，B 为 bookings 数量，N 为航班数<br>'
    '空间：{{c1::O(N)}} — 结果数组（复用为 diff）')

add_basic(d, make_front(p, '题解（差分数组）'),
    '航班编号是 1-based，需转换为 0-based。diff[first-1] += seats, diff[last] -= seats。'
    '最后前缀和还原即可。<br>'
    + code(
'''class Solution {
    public int[] corpFlightBookings(int[][] bookings, int n) {
        int[] ans = new int[n];
        // Apply difference array updates
        for (int[] booking : bookings) {
            int first = booking[0] - 1; // 1-based to 0-based
            int last = booking[1];       // last+1 position in 0-based
            int seats = booking[2];
            ans[first] += seats;
            if (last < n) {
                ans[last] -= seats;
            }
        }
        // Prefix sum to restore
        for (int i = 1; i < n; i++) {
            ans[i] += ans[i - 1];
        }
        return ans;
    }
}'''))

# ============================================================
# 3. 1094. 拼车
# ============================================================
p = '1094. 拼车'
d = make_deck(1747302203, f'算法::差分数组::{p}')
add_basic(d, make_front(p, '题干'),
    '车上最初有 capacity 个空座位，只能向一个方向行驶。'
    '给定行程 trips[i] = [numPassengers, from_i, to_i]，'
    '表示有 numPassengers 位旅客从 from_i 上车，到 to_i 下车'
    '（车开到 to_i 时旅客已下车，即旅客在 [from, to) 区间占用座位）。'
    '判断是否可以一次完成所有接载（任何时候车上人数都不超过 capacity）。<br><br>'
    '示例：trips=[[2,1,5],[3,3,7]], capacity=4 → false（1-3 有2人，3-5 有5人 > 4）')

add_cloze(d, make_front(p, '差分策略'),
    '差分数组记录每个位置<b>净增减人数</b>：<br>'
    '{{c1::diff[from] += num}} — 在 from 处上车 num 人，前缀和此处开始 +num<br>'
    '{{c2::diff[to] -= num}} — 在 to 处下车 num 人，前缀和此处开始 -num<br>'
    '（注意 to 不是 to+1，因为 [from, to) 是左闭右开区间）<br>'
    '前缀和遍历，检查累计人数是否超过 capacity：<br>'
    '{{c3::if (cur > capacity) return false}}')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(T+N)}}，T 为行程数，N 为最远距离（通常 ≤1000）<br>'
    '空间：{{c1::O(N)}} — diff 数组')

add_basic(d, make_front(p, '题解（差分数组）'),
    '先找到最远距离 maxTo 确定 diff 大小。对每个 trip 在 diff[from] += p, diff[to] -= p。'
    '遍历 diff 累加，中途检查是否超 capacity。<br>'
    + code(
'''class Solution {
    public boolean carPooling(int[][] trips, int capacity) {
        // Find the furthest stop to size the diff array
        int maxTo = 0;
        for (int[] trip : trips) {
            maxTo = Math.max(maxTo, trip[2]);
        }
        int[] diff = new int[maxTo + 2]; // +2 for safety
        // Apply difference array updates
        for (int[] trip : trips) {
            int num = trip[0];
            int from = trip[1];
            int to = trip[2];
            diff[from] += num; // board at from
            diff[to] -= num;   // alight at to (right-open interval)
        }
        // Prefix sum + capacity check
        int cur = 0;
        for (int i = 0; i <= maxTo; i++) {
            cur += diff[i];
            if (cur > capacity) {
                return false;
            }
        }
        return true;
    }
}'''))

add_basic(d, make_front(p, '易错提醒'),
    '1. 区间是 <b>[from, to)</b>（左闭右开），下车点不计入占用→ diff[to] 而非 diff[to+1] 处减去<br>'
    '2. 与 370/1109 的闭区间 [l, r] 不同，闭区间用 r+1，开区间用 r<br>'
    '3. capacity 是上限，检查条件是 cur <b>&gt;</b> capacity（严格大于才 false）<br>'
    '4. diff 数组尽量开大一点（maxTo+2），防止 to==maxTo 时越界')

if __name__ == '__main__':
    print(build('../../牌组/算法/差分数组.apkg'))

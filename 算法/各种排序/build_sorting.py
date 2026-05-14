"""Build APKG for 各种排序 (Sorting). 4 problems + 10 sorting algorithm decks."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


import html as _html


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    escaped = _html.escape(java)
    return f'<pre><code class="language-java">{escaped}</code></pre>'


# ═══════════════════════════════════════════════════════════════
# Principles Deck
# ═══════════════════════════════════════════════════════════════
d0 = make_deck(1747301600, '算法::排序::原理通识')

add_basic(d0, '常见排序算法对比',
    '<table border="1" cellpadding="4" cellspacing="0" style="margin:auto">'
    '<tr><th>算法</th><th>时间(平均)</th><th>时间(最坏)</th><th>空间</th><th>稳定</th></tr>'
    '<tr><td>冒泡</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>稳定</td></tr>'
    '<tr><td>选择</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>不稳定</td></tr>'
    '<tr><td>插入</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>稳定</td></tr>'
    '<tr><td>希尔</td><td>O(n^1.3)</td><td>O(n²)</td><td>O(1)</td><td>不稳定</td></tr>'
    '<tr><td>快排</td><td>O(n log n)</td><td>O(n²)</td><td>O(log n)</td><td>不稳定</td></tr>'
    '<tr><td>归并</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n)</td><td>稳定</td></tr>'
    '<tr><td>堆排</td><td>O(n log n)</td><td>O(n log n)</td><td>O(1)</td><td>不稳定</td></tr>'
    '<tr><td>计数</td><td>O(n+k)</td><td>O(n+k)</td><td>O(k)</td><td>稳定</td></tr>'
    '<tr><td>桶排</td><td>O(n+k)</td><td>O(n²)</td><td>O(n+k)</td><td>稳定</td></tr>'
    '<tr><td>基数</td><td>O(nk)</td><td>O(nk)</td><td>O(n+k)</td><td>稳定</td></tr>'
    '</table>')

add_cloze(d0, '排序算法核心思想速记',
    '冒泡：相邻比较交换，每轮{{c1::冒泡出最大值}}到最后<br>'
    '选择：每轮选{{c2::最小值}}放到前面<br>'
    '插入：将元素插入{{c3::已排序前缀}}的正确位置<br>'
    '快排：{{c4::partition}}确定基准位置，递归左右<br>'
    '归并：分治递归到单个元素，再{{c5::合并有序数组}}<br>'
    '堆排：建大根堆 → 交换堆顶和末尾 → {{c6::向下调整}}<br>'
    '计数：统计每个值的{{c7::出现次数}}，累加确定位置<br>'
    '基数：按{{c8::每位数字}}分配回收，从低位到高位')

add_cloze(d0, '排序算法稳定性与适用场景',
    '稳定的排序：{{c1::冒泡、插入、归并、计数、桶、基数}}<br>'
    '不稳定的排序：{{c2::选择、希尔、快排、堆排}}<br>'
    '数据量小且基本有序 → {{c3::插入排序}}(O(n)最优)<br>'
    '数据量大，内存够 → {{c4::归并排序}}(稳定)或快排(快)<br>'
    '数据量大，内存不够 → {{c5::堆排序}}(O(1)空间)<br>'
    '数据范围有限 → {{c6::计数排序}}(O(n+k))<br>'
    'Top-K问题 → {{c7::堆}} / QuickSelect')

add_basic(d0, 'Top-K 问题总结',
    'Top-K 大 → 小顶堆(size=k)，堆顶即第k大，O(n log k)<br>'
    'Top-K 小 → 大顶堆，同理<br>'
    'QuickSelect：基于partition，平均O(n)，最坏O(n²)<br>'
    '自实现大根堆：只需k-1次交换+调整即可返回堆顶')

# ═══════════════════════════════════════════════════════════════
# 1. 数组中的第K个最大元素
# ═══════════════════════════════════════════════════════════════
p = '数组中的第K个最大元素'
d = make_deck(1747301601, f'算法::排序::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数数组 nums 和整数 k，返回数组中第 k 个最大的元素。<br>'
    '注意：是排序后的第 k 个最大元素，而非第 k 个不同元素。'
    + img('image.png'))

add_cloze(d, make_front(p, '复杂度(PriorityQueue)'),
    'PriorityQueue小顶堆法：<br>'
    '时间 {{c1::O(n log k)}}<br>'
    '推导：遍历n个元素，每个元素入堆/出堆操作O(log k) → n × log k<br>'
    '空间 {{c2::O(k)}}<br>'
    '推导：堆中最多保留k个元素')

add_cloze(d, make_front(p, '复杂度(自实现大根堆)'),
    '自实现大根堆法：<br>'
    '时间 {{c1::O(n log n)}}<br>'
    '推导：建堆O(n)，但k次heapify每次O(log n) → 实际k次调整即O(k log n)，最坏k=n时为O(n log n)<br>'
    '空间 {{c2::O(1)}}<br>'
    '推导：原地建堆，全部操作在原数组上进行')

add_basic(d, make_front(p, '题解(PriorityQueue 小顶堆)'),
    '维护大小为 k 的小顶堆，堆顶即第 k 大。<br>'
    + code(
        'class Solution {\n'
        '    public int findKthLargest(int[] nums, int k) {\n'
        '        PriorityQueue<Integer> heap = new PriorityQueue<>();\n'
        '        for (int num : nums) {\n'
        '            heap.add(num);\n'
        '            if (heap.size() > k) {\n'
        '                heap.poll();\n'
        '            }\n'
        '        }\n'
        '        return heap.peek();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(自实现大根堆)'),
    '大根堆：天然与"第K大"语义一致，k-1次堆排序后堆顶即答案。<br>'
    + code(
        'class Solution {\n'
        '    public int findKthLargest(int[] nums, int k) {\n'
        '        int len = nums.length;\n'
        '        // 建大根堆：从最后一个非叶子节点向上调整\n'
        '        for (int i = len / 2 - 1; i >= 0; i--) {\n'
        '            heapify(nums, i, len);\n'
        '        }\n'
        '        // k-1 次交换+调整，堆顶即第k大\n'
        '        for (int i = 0; i < k - 1; i++) {\n'
        '            swap(nums, 0, len - 1 - i);\n'
        '            heapify(nums, 0, len - 1 - i);\n'
        '        }\n'
        '        return nums[0];\n'
        '    }\n'
        '\n'
        '    private void heapify(int[] nums, int root, int heapSize) {\n'
        '        int largest = root;\n'
        '        int left = 2 * root + 1;\n'
        '        int right = 2 * root + 2;\n'
        '        if (left < heapSize && nums[left] > nums[largest])\n'
        '            largest = left;\n'
        '        if (right < heapSize && nums[right] > nums[largest])\n'
        '            largest = right;\n'
        '        if (largest != root) {\n'
        '            swap(nums, root, largest);\n'
        '            heapify(nums, largest, heapSize);\n'
        '        }\n'
        '    }\n'
        '\n'
        '    private void swap(int[] nums, int i, int j) {\n'
        '        int temp = nums[i];\n'
        '        nums[i] = nums[j];\n'
        '        nums[j] = temp;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '小顶堆维护size=k：遍历数组逐个加入，超k则poll最小值，堆顶即第k大<br>'
    '大根堆更贴合语义：建堆后只需k-1次交换+调整，堆顶就是答案<br>'
    'heapify三步：(1)找largest (2)不相等则swap (3)递归向下调整<br>'
    '建堆从len/2-1开始：因为叶子节点(len/2到len-1)已经是单元素堆')

# ═══════════════════════════════════════════════════════════════
# 2. 最小的k个数
# ═══════════════════════════════════════════════════════════════
p = '最小的k个数'
d = make_deck(1747301602, f'算法::排序::{p}')

add_basic(d, make_front(p, '题干'),
    '输入整数数组 arr，找出其中最小的 k 个数。以任意顺序返回这 k 个数即可。')

add_cloze(d, make_front(p, '复杂度(QuickSelect)'),
    'QuickSelect法：<br>'
    '时间 平均 {{c1::O(n)}}，最坏 {{c2::O(n²)}}<br>'
    '推导(平均)：每次partition减少一半搜索范围 → n + n/2 + n/4 + ... &lt; 2n = O(n)<br>'
    '推导(最坏)：每次只排除一个元素(如已排序数组) → n + (n-1) + ... + 1 = O(n²)<br>'
    '空间 {{c3::O(log n)}}<br>'
    '推导：递归栈深度，每次减半→log n层')

add_cloze(d, make_front(p, '复杂度(大顶堆)'),
    '大顶堆法：<br>'
    '时间 {{c1::O(n log k)}}<br>'
    '推导：遍历n个元素，堆大小k，每次调整O(log k) → n log k<br>'
    '空间 {{c2::O(k)}}<br>'
    '推导：堆中最多存k+1个元素')

add_basic(d, make_front(p, '题解(QuickSelect)'),
    '改造快排partition：确定基准位置i后与k比较决定递归方向。<br>'
    + code(
        'class Solution {\n'
        '    public int[] getLeastNumbers(int[] arr, int k) {\n'
        '        if (k >= arr.length) return arr;\n'
        '        return quickSelect(arr, 0, arr.length - 1, k);\n'
        '    }\n'
        '\n'
        '    private int[] quickSelect(int[] arr, int left, int right, int k) {\n'
        '        int i = left, j = right;\n'
        '        while (i < j) {\n'
        '            // 必须先从右向左扫描\n'
        '            while (i < j && arr[left] <= arr[j]) j--;\n'
        '            while (i < j && arr[left] >= arr[i]) i++;\n'
        '            swap(arr, i, j);\n'
        '        }\n'
        '        swap(arr, left, i);\n'
        '        if (i > k)\n'
        '            return quickSelect(arr, left, i - 1, k);\n'
        '        if (i < k)\n'
        '            return quickSelect(arr, i + 1, right, k);\n'
        '        return Arrays.copyOf(arr, k);\n'
        '    }\n'
        '\n'
        '    private void swap(int[] arr, int i, int j) {\n'
        '        int temp = arr[i];\n'
        '        arr[i] = arr[j];\n'
        '        arr[j] = temp;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(大顶堆)'),
    '大顶堆维护size=k，堆顶是当前k个最小数中最大的。<br>'
    + code(
        'class Solution {\n'
        '    public int[] getLeastNumbers(int[] arr, int k) {\n'
        '        if (k == 0) return new int[0];\n'
        '        PriorityQueue<Integer> heap = new PriorityQueue<>((a, b) -> b - a);\n'
        '        for (int num : arr) {\n'
        '            if (heap.size() < k) {\n'
        '                heap.offer(num);\n'
        '            } else if (num < heap.peek()) {\n'
        '                heap.poll();\n'
        '                heap.offer(num);\n'
        '            }\n'
        '        }\n'
        '        int[] res = new int[k];\n'
        '        for (int i = 0; i < k; i++) res[i] = heap.poll();\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'QuickSelect改造partition：确定基准位置i后与k比较决定递归方向<br>'
    'i &gt; k → 答案在左区间；i &lt; k → 还需在右区间找；i == k → 返回前k个<br>'
    'QuickSelect平均O(n)优于堆的O(n log k)，注意必须先从右往左扫描<br>'
    '大顶堆法比小顶堆更高效（只存k个，空间小）')

# ═══════════════════════════════════════════════════════════════
# 3. 计算数组的小和
# ═══════════════════════════════════════════════════════════════
p = '计算数组的小和'
d = make_deck(1747301604, f'算法::排序::{p}')

add_basic(d, make_front(p, '题干'),
    '数组小和定义：对于数组中每个数，累加其左侧所有比它小的数的和。<br>'
    '示例：[1,3,4,2,5] 的小和 = 0 + 1 + (1+3) + 1 + (1+3+4+2) = 16。'
    + img('image 2.png') + img('image 3.png'))

add_cloze(d, make_front(p, '复杂度'),
    '时间 {{c1::O(n log n)}}<br>'
    '推导：归并排序每层merge遍历n个元素，共log n层 → O(n log n)<br>'
    '空间 {{c2::O(n)}}<br>'
    '推导：需要与数组等长的临时数组用于merge')

add_basic(d, make_front(p, '题解(归并排序求小和)'),
    '归并时若 nums[i] &lt;= nums[j]，右侧[j, right]共(right-j+1)个数都>=nums[i]，贡献小和。<br>'
    + code(
        'public class Main {\n'
        '    static int[] temp;\n'
        '\n'
        '    public static long sortAndMerge(int[] nums, int left, int right) {\n'
        '        if (left >= right) return 0;\n'
        '        int mid = left + (right - left) / 2;\n'
        '        long res = sortAndMerge(nums, left, mid)\n'
        '                 + sortAndMerge(nums, mid + 1, right);\n'
        '        int i = left, j = mid + 1, k = 0;\n'
        '        while (i <= mid && j <= right) {\n'
        '            if (nums[i] <= nums[j]) {\n'
        '                res += (right - j + 1) * nums[i];\n'
        '                temp[k++] = nums[i++];\n'
        '            } else {\n'
        '                temp[k++] = nums[j++];\n'
        '            }\n'
        '        }\n'
        '        while (i <= mid) temp[k++] = nums[i++];\n'
        '        while (j <= right) temp[k++] = nums[j++];\n'
        '        for (i = left, k = 0; i <= right; i++)\n'
        '            nums[i] = temp[k++];\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '核心：归并时若 nums[i] &lt;= nums[j]，右侧[j, right]共(right-j+1)个数>=nums[i]<br>'
    '贡献小和 = (right-j+1) × nums[i]<br>'
    '注意相等时必须用&lt;=计算(不能漏)，否则丢失贡献<br>'
    '本质是归并排序的"副产品"——利用合并时两侧已排序的性质直接累计')

# ═══════════════════════════════════════════════════════════════
# 各排序算法详解 — 每个算法独立牌组
# ═══════════════════════════════════════════════════════════════

# ============================
# 冒泡排序 (Bubble Sort)
# ============================
p = '冒泡排序'
d = make_deck(1747301610, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '冒泡排序：重复遍历数组，依次比较相邻元素，若顺序错误则交换。<br>'
    '每轮遍历将当前未排序部分的最大值"冒泡"到末尾位置。<br>'
    '如同气泡从水底升到水面，最大的气泡最先浮出。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：相邻比较 + 交换</b><br><br>'
    '1. 外层循环i从0到n-1，控制轮数<br>'
    '2. 内层循环j从0到n-1-i，比较arr[j]和arr[j+1]<br>'
    '3. 若arr[j] > arr[j+1]则交换，大的往后走<br>'
    '4. 每轮结束，当前最大元素到达正确位置(n-1-i)<br>'
    '5. 优化：若某轮没有交换发生，说明已有序，可提前结束')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '最坏(逆序)：外层n轮，内层每轮比较n-1-i次<br>'
    '→ (n-1)+(n-2)+...+1+0 = {{c1::n(n-1)/2}} = O(n²)<br>'
    '最好(已有序)：第一轮无交换直接退出 → O(n)<br>'
    '平均：每个元素期望移动n/3次 → 仍为 {{c2::O(n²)}}<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '只在swap时使用1个临时变量 → {{c3::O(1)}}<br><br>'
    '<b>稳定性：</b>{{c4::稳定}}(相等时不交换)')

add_basic(d, make_front(p, '题解'),
    '标准冒泡排序（含提前终止优化）<br>'
    + code(
        'public void bubbleSort(int[] arr) {\n'
        '    int n = arr.length;\n'
        '    for (int i = 0; i < n - 1; i++) {\n'
        '        boolean swapped = false;\n'
        '        // 每轮将最大值冒泡到末尾\n'
        '        for (int j = 0; j < n - 1 - i; j++) {\n'
        '            if (arr[j] > arr[j + 1]) {\n'
        '                int temp = arr[j];\n'
        '                arr[j] = arr[j + 1];\n'
        '                arr[j + 1] = temp;\n'
        '                swapped = true;\n'
        '            }\n'
        '        }\n'
        '        // 本轮无交换，已有序，提前结束\n'
        '        if (!swapped) break;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '最简单的排序算法，稳定，适合小数据量或基本有序的数据<br>'
    '提前终止优化(swapped标志)使最好情况降至O(n)<br>'
    '每次交换消除一个逆序对，总交换次数=逆序对数量<br>'
    '实际项目中几乎不用(性能太差)，面试至少会写')

# ============================
# 选择排序 (Selection Sort)
# ============================
p = '选择排序'
d = make_deck(1747301611, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '选择排序：每轮从未排序部分选出最小元素，放到已排序部分的末尾。<br>'
    '类似于打牌时每次从牌堆中选出最小的牌放到手中。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：选择最小值 + 交换到前面</b><br><br>'
    '1. 外层循环i从0到n-2，i之前是已排序区域<br>'
    '2. 每轮在[i, n-1]范围内找到最小值的索引min<br>'
    '3. 交换arr[i]和arr[min]，将最小值归位<br>'
    '4. 重复直到全部有序<br>'
    '5. 无论数据初始状态如何，比较次数固定')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '外层n-1轮，每轮在剩余元素中找最小值<br>'
    '比较次数：(n-1)+(n-2)+...+1+0 = {{c1::n(n-1)/2}}<br>'
    '无论数据是否有序，比较次数不变 → 始终 {{c2::O(n²)}}<br>'
    '交换次数：每轮最多1次 → 共n-1次交换<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '只需min和temp两个变量 → {{c3::O(1)}}<br><br>'
    '<b>稳定性：</b>{{c4::不稳定}}(交换可能打乱相等元素的相对顺序)<br>'
    '例：[5, 5, 2] 第一轮选最小2与第一个5交换 → 两个5的顺序改变了')

add_basic(d, make_front(p, '题解'),
    '标准选择排序<br>'
    + code(
        'public void selectionSort(int[] arr) {\n'
        '    int n = arr.length;\n'
        '    for (int i = 0; i < n - 1; i++) {\n'
        '        int minIdx = i;\n'
        '        // 在未排序区域[i, n-1]找最小值\n'
        '        for (int j = i + 1; j < n; j++) {\n'
        '            if (arr[j] < arr[minIdx]) {\n'
        '                minIdx = j;\n'
        '            }\n'
        '        }\n'
        '        // 将最小值交换到已排序区域末尾\n'
        '        if (minIdx != i) {\n'
        '            int temp = arr[i];\n'
        '            arr[i] = arr[minIdx];\n'
        '            arr[minIdx] = temp;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '选择排序的交换次数最少(n-1次)，但比较次数固定O(n²)<br>'
    '不稳定：跨位置交换会改变相等元素的相对顺序<br>'
    '性能与数据初始状态无关，适合交换成本高的场景<br>'
    '实际项目中几乎不用，但它是最直观的排序之一')

# ============================
# 插入排序 (Insertion Sort)
# ============================
p = '插入排序'
d = make_deck(1747301612, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '插入排序：将数组分为已排序前缀和未排序后缀，每次取后缀第一个元素，'
    '在已排序前缀中找到正确位置插入。<br>'
    '类似于打牌时摸到一张新牌，插入到手中有序牌的合适位置。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：向已排序前缀中插入新元素</b><br><br>'
    '1. 默认第一个元素为已排序前缀<br>'
    '2. 从i=1开始，取出arr[i]暂存为key<br>'
    '3. 在[0, i-1]已排序区域逆序遍历，将大于key的元素右移一位<br>'
    '4. 找到第一个不大于key的位置(j+1)，插入key<br>'
    '5. 逆序遍历比正序遍历更高效：可以边比较边移动')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '最坏(逆序)：每轮需将已排序部分全部右移<br>'
    '→ 1+2+...+(n-1) = {{c1::n(n-1)/2}} = O(n²)<br>'
    '最好(已有序)：每轮只比较1次无需移动 → {{c2::O(n)}}<br>'
    '平均：每个元素需要比较/移动一半的长度 → 约n²/4 → O(n²)<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '只用一个变量key暂存当前元素 → {{c3::O(1)}}<br><br>'
    '<b>稳定性：</b>{{c4::稳定}}(只有严格大于才右移，相等时不移动)')

add_basic(d, make_front(p, '题解'),
    '标准插入排序（逆序比较+移位）<br>'
    + code(
        'public void insertionSort(int[] arr) {\n'
        '    int n = arr.length;\n'
        '    // 第一个元素已有序，从第二个开始\n'
        '    for (int i = 1; i < n; i++) {\n'
        '        int key = arr[i];\n'
        '        int j = i - 1;\n'
        '        // 将大于key的元素右移\n'
        '        while (j >= 0 && arr[j] > key) {\n'
        '            arr[j + 1] = arr[j];\n'
        '            j--;\n'
        '        }\n'
        '        // 插入key到正确位置\n'
        '        arr[j + 1] = key;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '插入排序在数据基本有序时极快(O(n))，是希尔排序的基础<br>'
    '稳定：用arr[j] > key(不用>=)保证相等元素不交换<br>'
    '对小型数组(约&lt;20个元素)，插入排序比快排/归并更快(常数因子小)<br>'
    'Java的Arrays.sort对小于47个元素的数组使用插入排序')

# ============================
# 希尔排序 (Shell Sort)
# ============================
p = '希尔排序'
d = make_deck(1747301613, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '希尔排序：插入排序的改进版。先以较大步长(gap)分组进行插入排序，'
    '让元素快速接近最终位置；然后逐步缩小步长直到gap=1，即标准插入排序。<br>'
    '此时数组已基本有序，插入排序效率大幅提升。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：分组插入排序 + 缩小增量</b><br><br>'
    '1. 选择初始步长gap = n/2<br>'
    '2. 将所有距离为gap的元素分为一组，组内进行插入排序<br>'
    '3. gap = gap/2，重复步骤2<br>'
    '4. 当gap=1时，就是标准插入排序，但此时数据已基本有序<br><br>'
    '<b>为什么比插入排序快：</b><br>'
    '大步长时元素少交换快，小步长时数据已基本有序<br>'
    '本质是让元素"跳着"逼近目标位置，减少总的移动次数')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '希尔排序的时间复杂度取决于gap序列的选择<br>'
    '使用最简gap=n/2, n/4, ..., 1时：<br>'
    '最坏约{{c1::O(n²)}}(如gap=1时才有效排序)<br>'
    '使用Hibbard序列(1,3,7,15,...,2^k-1)最坏可降至{{c2::O(n^1.5)}}<br>'
    '平均复杂度经验值为 O(n^1.3)，但没有精确证明<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '原地排序，只有几个临时变量 → {{c3::O(1)}}<br><br>'
    '<b>稳定性：</b>{{c4::不稳定}}(同组内插入排序虽然稳定，但不同组之间可能打乱顺序)')

add_basic(d, make_front(p, '题解'),
    '希尔排序（gap = n/2, n/4, ..., 1）<br>'
    + code(
        'public void shellSort(int[] arr) {\n'
        '    int n = arr.length;\n'
        '    // gap逐步缩小\n'
        '    for (int gap = n / 2; gap > 0; gap /= 2) {\n'
        '        // 对每个gap分组做插入排序\n'
        '        for (int i = gap; i < n; i++) {\n'
        '            int key = arr[i];\n'
        '            int j = i - gap;\n'
        '            // 组内元素间隔为gap\n'
        '            while (j >= 0 && arr[j] > key) {\n'
        '                arr[j + gap] = arr[j];\n'
        '                j -= gap;\n'
        '            }\n'
        '            arr[j + gap] = key;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '希尔排序的唯一参数是gap序列，直接影响性能<br>'
    'gap=1时退化为插入排序，但数据已基本有序所以很快<br>'
    'gap序列有多种选择：Shell原始(n/2)、Hibbard(2^k-1)、Sedgewick等<br>'
    '面试记住n/2递减即可，关键是理解"分组预排序"的思想')

# ============================
# 快速排序 (Quick Sort)
# ============================
p = '快速排序'
d = make_deck(1747301614, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '快速排序：分治算法。每轮选一个基准(pivot)，通过partition将数组分为'
    '"小于基准"和"大于基准"两部分，再递归排序左右子数组。<br>'
    '是实际应用中最快的通用排序算法。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：partition划分 + 分治递归</b><br><br>'
    '1. 选择一个基准元素(pivot)，这里取最左元素<br>'
    '2. partition：双指针i(左)和j(右)，j先向左扫描找小于基准的元素，i向右扫描找大于基准的元素，交换<br>'
    '3. 当i==j时，将基准放到该位置 → 左边都&lt;=基准，右边都&gt;=基准<br>'
    '4. 递归排序左右两个子数组<br>'
    '5. 递归终止条件：区间长度&lt;=1<br><br>'
    '<b>为什么必须先从右向左扫描：</b><br>'
    '取最左为基准时，最后i和j相遇的位置才是基准的正确位置。<br>'
    '如果先从左扫描，i会停在大于基准的位置，交换后基准左侧会出现大于它的元素。')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导(平均)：</b><br>'
    '每次partition将数组大致平分 → 递归树深度约 log n<br>'
    '每层partition遍历n个元素 → 每层O(n)<br>'
    '总时间 = 层数×每层工作量 = {{c1::O(n log n)}}<br><br>'
    '<b>时间复杂度推导(最坏)：</b><br>'
    '每次partition只排除1个元素(如已排序数组取最左为基准)<br>'
    '递归深度变为n → 总时间=n+(n-1)+...+1 = {{c2::O(n²)}}<br>'
    '随机化选择基准可以避免最坏情况<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '递归栈深度：平均{{c3::O(log n)}}层，最坏{{c4::O(n)}}层 → O(log n)<br><br>'
    '<b>稳定性：</b>{{c5::不稳定}}(partition中的交换会打乱相等元素的相对顺序)')

add_basic(d, make_front(p, '题解(经典快排)'),
    '取最左为基准，双指针partition<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        quickSort(nums, 0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    private int partition(int[] nums, int left, int right) {\n'
        '        int i = left, j = right;\n'
        '        int pivot = nums[left];\n'
        '        while (i < j) {\n'
        '            // 必须先从右向左扫描\n'
        '            while (i < j && nums[j] >= pivot) j--;\n'
        '            nums[i] = nums[j];\n'
        '            while (i < j && nums[i] <= pivot) i++;\n'
        '            nums[j] = nums[i];\n'
        '        }\n'
        '        nums[i] = pivot;\n'
        '        return i;\n'
        '    }\n'
        '\n'
        '    private void quickSort(int[] nums, int left, int right) {\n'
        '        if (left >= right) return;\n'
        '        int p = partition(nums, left, right);\n'
        '        quickSort(nums, left, p - 1);\n'
        '        quickSort(nums, p + 1, right);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(简化版快排)'),
    '更简洁的写法，同样取最左为基准<br>'
    + code(
        'public void quickSort(int[] arr, int left, int right) {\n'
        '    if (left >= right) return;\n'
        '    int i = left, j = right;\n'
        '    int pivot = arr[left];\n'
        '    while (i < j) {\n'
        '        while (i < j && arr[j] >= pivot) j--;\n'
        '        if (i < j) arr[i++] = arr[j];\n'
        '        while (i < j && arr[i] < pivot) i++;\n'
        '        if (i < j) arr[j--] = arr[i];\n'
        '    }\n'
        '    arr[i] = pivot;\n'
        '    quickSort(arr, left, i - 1);\n'
        '    quickSort(arr, i + 1, right);\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'partition是快排的灵魂：双指针从两端向中间扫描<br>'
    '取最左为基准时必须先从右扫描，否则基准归位错误<br>'
    '最坏O(n²)发生在已排序数组取最左/最右为基准 → 可随机化避免<br>'
    '实际使用中快排常数因子小，通常比归并和堆排快2-3倍<br>'
    'Java的Arrays.sort对基本类型用快排变体(DualPivotQuickSort)')

# ============================
# 归并排序 (Merge Sort)
# ============================
p = '归并排序'
d = make_deck(1747301615, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '归并排序：经典分治算法。将数组递归拆分成单个元素(自然有序)，'
    '然后两两合并有序子数组，直到合并为完整的排序数组。<br>'
    '自底向上构建有序序列，思想类似于二叉树的后序遍历。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：递归拆分 + 合并有序数组</b><br><br>'
    '1. 递归将数组从中间(mid)拆分为左右两部分<br>'
    '2. 递归终止条件：区间长度&lt;=1(单个元素天然有序)<br>'
    '3. merge操作：合并两个已排序的子数组<br>'
    '   - 双指针i和j分别指向左右子数组的起始位置<br>'
    '   - 每次取较小的元素放入临时数组<br>'
    '   - 将剩余元素追加到临时数组末尾<br>'
    '   - 将临时数组写回原数组<br>'
    '4. 递归返回时，左右子数组都已有序，只需merge')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '每次递归将问题规模减半 → 递归树深度 {{c1::log n}}<br>'
    '每层merge遍历所有n个元素 → 每层O(n)<br>'
    '总时间 = 层数×每层工作量 = {{c2::O(n log n)}}<br>'
    '无论数据初始状态如何，比较次数稳定在n log n级别<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '每次merge需要临时数组存储当前区间结果<br>'
    '最大临时数组大小为n → {{c3::O(n)}}(递归栈log n层可忽略)<br>'
    '不能原地完成，这是归并排序的主要缺点<br><br>'
    '<b>稳定性：</b>{{c4::稳定}}(merge时遇到相等元素取左边的，保持原顺序)')

add_basic(d, make_front(p, '题解(自顶向下)'),
    '递归拆分至单个元素，再自底向上merge<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        mergeSort(nums, 0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    private void mergeSort(int[] arr, int left, int right) {\n'
        '        if (left >= right) return;\n'
        '        int mid = left + (right - left) / 2;\n'
        '        mergeSort(arr, left, mid);\n'
        '        mergeSort(arr, mid + 1, right);\n'
        '        merge(arr, left, mid, right);\n'
        '    }\n'
        '\n'
        '    private void merge(int[] arr, int left, int mid, int right) {\n'
        '        int[] temp = new int[right - left + 1];\n'
        '        int i = left, j = mid + 1, k = 0;\n'
        '        while (i <= mid && j <= right) {\n'
        '            temp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];\n'
        '        }\n'
        '        while (i <= mid) temp[k++] = arr[i++];\n'
        '        while (j <= right) temp[k++] = arr[j++];\n'
        '        for (i = 0; i < temp.length; i++)\n'
        '            arr[left + i] = temp[i];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(自底向上/非递归)'),
    '不用递归，直接从大小为1的段开始两两合并<br>'
    + code(
        'public void mergeSortIterative(int[] arr) {\n'
        '    int n = arr.length;\n'
        '    // size: 每次合并的子数组长度, 1,2,4,8,...\n'
        '    for (int size = 1; size < n; size *= 2) {\n'
        '        for (int left = 0; left < n - size; left += 2 * size) {\n'
        '            int mid = left + size - 1;\n'
        '            int right = Math.min(left + 2 * size - 1, n - 1);\n'
        '            merge(arr, left, mid, right);\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '归并排序是稳定排序，适合需要保持相对顺序的场景<br>'
    '稳定的前提：merge时用arr[i]&lt;=arr[j](用&lt;=不是&lt;)，相等取左边<br>'
    '主要代价是O(n)额外空间，无法像快排那样原地排序<br>'
    '自底向上的非递归版本避免了递归开销，适合链表排序<br>'
    '适合外部排序：分块读入内存排序后写回，再归并各块')

# ============================
# 堆排序 (Heap Sort)
# ============================
p = '堆排序'
d = make_deck(1747301616, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '堆排序：利用二叉最大堆(或最小堆)进行排序。<br>'
    '先建堆，然后反复将堆顶(最大元素)与堆末尾交换，缩小堆并向下调整，'
    '直到堆大小为1。<br>'
    '是空间最优的O(n log n)排序算法。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：建堆 + 反复交换堆顶和末尾</b><br><br>'
    '1. <b>建初堆</b>：从最后一个非叶节点(len/2-1)向上，对每个节点做向下调整(heapify)<br>'
    '   → 确保每个子树满足大根堆性质(父&gt;=子)<br>'
    '2. <b>排序过程</b>：重复n-1次<br>'
    '   a. 交换堆顶(索引0，最大值)和堆末尾(索引i)<br>'
    '   b. 堆大小减1，对新的堆顶做向下调整<br>'
    '3. <b>heapify向下调整</b>：比较父节点与左右子节点，与最大的子节点交换，递归向下<br>'
    '4. 堆顶始终是当前堆中的最大值')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '建堆：每个节点最多调整log n次，但大部分节点在底层 → 实际是{{c1::O(n)}}<br>'
    '证明：第k层共2^k个节点，每个最多下沉(h-k)层，级数求和得O(n)<br>'
    '排序：n-1次heapify，每次{{c2::O(log n)}} → O(n log n)<br>'
    '总时间：O(n) + O(n log n) = {{c3::O(n log n)}}<br>'
    '无论数据如何，堆排序的时间稳定在O(n log n)<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '全部操作在原数组上进行 → {{c4::O(1)}}<br>'
    '递归heapify可以改为while循环，消除递归栈<br><br>'
    '<b>稳定性：</b>{{c5::不稳定}}(交换堆顶和末尾会打乱顺序)')

add_basic(d, make_front(p, '题解(递归版heapify)'),
    '建大根堆 → 交换堆顶和末尾 → 向下调整<br>'
    + code(
        'public void heapSort(int[] nums) {\n'
        '    int n = nums.length;\n'
        '    // 建初堆：从最后一个非叶节点向上\n'
        '    for (int i = n / 2 - 1; i >= 0; i--) {\n'
        '        heapify(nums, n, i);\n'
        '    }\n'
        '    // 排序：依次将堆顶换到末尾\n'
        '    for (int i = n - 1; i > 0; i--) {\n'
        '        int temp = nums[0];\n'
        '        nums[0] = nums[i];\n'
        '        nums[i] = temp;\n'
        '        heapify(nums, i, 0);\n'
        '    }\n'
        '}\n'
        '\n'
        'private void heapify(int[] nums, int heapSize, int root) {\n'
        '    int largest = root;\n'
        '    int left = 2 * root + 1;\n'
        '    int right = 2 * root + 2;\n'
        '    if (left < heapSize && nums[left] > nums[largest])\n'
        '        largest = left;\n'
        '    if (right < heapSize && nums[right] > nums[largest])\n'
        '        largest = right;\n'
        '    if (largest != root) {\n'
        '        int temp = nums[root];\n'
        '        nums[root] = nums[largest];\n'
        '        nums[largest] = temp;\n'
        '        heapify(nums, heapSize, largest);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(迭代版heapify)'),
    '迭代版本避免递归开销<br>'
    + code(
        'private void heapifyIterative(int[] nums, int heapSize, int root) {\n'
        '    while (true) {\n'
        '        int largest = root;\n'
        '        int left = 2 * root + 1;\n'
        '        int right = 2 * root + 2;\n'
        '        if (left < heapSize && nums[left] > nums[largest])\n'
        '            largest = left;\n'
        '        if (right < heapSize && nums[right] > nums[largest])\n'
        '            largest = right;\n'
        '        if (largest == root) break;\n'
        '        int temp = nums[root];\n'
        '        nums[root] = nums[largest];\n'
        '        nums[largest] = temp;\n'
        '        root = largest;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '堆排序是唯一一个同时满足O(n log n)时间和O(1)空间的算法<br>'
    '索引计算：父→左子2i+1，右子2i+2；子→父(i-1)/2<br>'
    '最后一个非叶节点 = n/2-1（叶子节点从n/2开始）<br>'
    '建堆O(n)的关键：底层节点多但下沉少，顶层节点少但下沉多<br>'
    '实际速度通常慢于快排（常数因子大、缓存不友好）<br>'
    '大根堆得升序，小根堆得降序')

# ============================
# 计数排序 (Counting Sort)
# ============================
p = '计数排序'
d = make_deck(1747301617, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '计数排序：非比较排序。统计每个值出现的次数，然后按值的大小顺序依次输出。<br>'
    '适用于数据范围有限(很小)的整数排序。不是基于比较，可以突破O(n log n)下限。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：计数 + 前缀和确定位置</b><br><br>'
    '1. 找到数据范围[min, max]<br>'
    '2. 创建计数数组count[max-min+1]，统计每个值的出现次数<br>'
    '3. 对count做前缀和：count[i] += count[i-1]，此时count[i]表示值i+min排序后的最后位置+1<br>'
    '4. 逆序遍历原数组，根据count确定每个元素的最终位置<br>'
    '5. <b>逆序遍历是稳定版本的关键</b>：保证相等元素的原顺序<br><br>'
    '<b>稳定版本 vs 不稳定版本：</b><br>'
    '不稳定版：直接按计数输出即可。<br>'
    '稳定版：需前缀和+逆序回填，代码稍复杂但保持稳定性。')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '统计频率：遍历n个元素 → O(n)<br>'
    '计算前缀和：遍历k个桶 → O(k)，k = 值域大小<br>'
    '回填结果：逆序遍历n个元素 → O(n)<br>'
    '总时间 = {{c1::O(n+k)}}<br>'
    '当k &lt;&lt; n时线性O(n)，当k很大时退化为O(k)<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '计数数组大小k + 结果数组大小n → {{c2::O(n+k)}}<br>'
    '如果原地排序可省去结果数组 → 空间降为O(k)但不稳定<br><br>'
    '<b>稳定性：</b>{{c3::稳定}}(前缀和+逆序遍历版本)')

add_basic(d, make_front(p, '题解(稳定版)'),
    '前缀和+逆序回填，保持稳定性<br>'
    + code(
        'public void countingSort(int[] arr) {\n'
        '    if (arr.length == 0) return;\n'
        '    // 1. 找数据范围\n'
        '    int min = arr[0], max = arr[0];\n'
        '    for (int num : arr) {\n'
        '        if (num < min) min = num;\n'
        '        if (num > max) max = num;\n'
        '    }\n'
        '    // 2. 计数\n'
        '    int range = max - min + 1;\n'
        '    int[] count = new int[range];\n'
        '    for (int num : arr) count[num - min]++;\n'
        '    // 3. 前缀和：count[i] = 值i+min的最后一个位置+1\n'
        '    for (int i = 1; i < range; i++)\n'
        '        count[i] += count[i - 1];\n'
        '    // 4. 逆序回填（保证稳定）\n'
        '    int[] output = new int[arr.length];\n'
        '    for (int i = arr.length - 1; i >= 0; i--) {\n'
        '        int idx = --count[arr[i] - min];\n'
        '        output[idx] = arr[i];\n'
        '    }\n'
        '    System.arraycopy(output, 0, arr, 0, arr.length);\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(简化版/不稳定)'),
    '直接按计数输出，代码简单但不稳定<br>'
    + code(
        'public void countingSortSimple(int[] arr) {\n'
        '    int max = arr[0];\n'
        '    for (int num : arr) max = Math.max(max, num);\n'
        '    int[] count = new int[max + 1];\n'
        '    for (int num : arr) count[num]++;\n'
        '    int idx = 0;\n'
        '    for (int i = 0; i <= max; i++)\n'
        '        while (count[i]-- > 0) arr[idx++] = i;\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '计数排序是基数排序的基础，突破比较排序O(n log n)下限<br>'
    '前提条件：数据范围小且已知。范围太大则浪费空间<br>'
    '稳定版本的关键三步：统计→前缀和→逆序回填<br>'
    '逆序遍历原数组是稳定性的保证：相同元素后面的先放<br>'
    '只能排整数，不能排浮点数或字符串(可转为基数排序)')

# ============================
# 桶排序 (Bucket Sort)
# ============================
p = '桶排序'
d = make_deck(1747301618, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '桶排序：将数据均匀分配到多个桶(bucket)中，每个桶内用其他排序算法(如插入排序)排序，'
    '最后按桶的顺序依次取出所有元素。<br>'
    '适用于数据均匀分布的场景。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：分桶 + 桶内排序 + 合并</b><br><br>'
    '1. 确定桶的数量n和每个桶的范围<br>'
    '2. 遍历数组，根据映射函数将元素分配到对应的桶<br>'
    '3. 对每个非空桶内部进行排序(通常用插入排序，因为桶内数据少)<br>'
    '4. 按桶的顺序，将所有桶中的元素依次放回原数组<br><br>'
    '<b>映射函数：</b>桶索引 = (元素值 - 最小值) × (桶数 - 1) / (最大值 - 最小值)<br>'
    '确保元素均匀分布在各桶中。')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '最坏情况：所有元素落入同一个桶 → 桶内排序退化为O(n²)<br>'
    '即 {{c1::O(n²)}}（使用插入排序时）<br>'
    '平均情况：n个元素均匀分布在k个桶中，每桶n/k个元素<br>'
    '桶内排序O((n/k)²)，k个桶共k×(n/k)² = n²/k<br>'
    '当k≈n时 → {{c2::O(n)}}<br>'
    '（k取n时每桶平均1个元素，则退化为计数排序）<br><br>'
    '<b>空间复杂度推导：</b><br>'
    'k个桶存储n个元素 → {{c3::O(n+k)}}<br><br>'
    '<b>稳定性：</b>{{c4::取决于桶内排序算法}}（桶内用插入排序则稳定）')

add_basic(d, make_front(p, '题解'),
    '桶排序（桶内使用插入排序）<br>'
    + code(
        'public void bucketSort(int[] arr) {\n'
        '    if (arr.length == 0) return;\n'
        '    int n = arr.length;\n'
        '    // 1. 找数据范围\n'
        '    int min = arr[0], max = arr[0];\n'
        '    for (int num : arr) {\n'
        '        if (num < min) min = num;\n'
        '        if (num > max) max = num;\n'
        '    }\n'
        '    // 2. 创建n个桶\n'
        '    List<Integer>[] buckets = new List[n];\n'
        '    for (int i = 0; i < n; i++)\n'
        '        buckets[i] = new ArrayList<>();\n'
        '    // 3. 分配到桶\n'
        '    double range = (double)(max - min + 1);\n'
        '    for (int num : arr) {\n'
        '        int idx = (int)((num - min) * n / range);\n'
        '        buckets[idx].add(num);\n'
        '    }\n'
        '    // 4. 桶内排序并合并\n'
        '    int k = 0;\n'
        '    for (List<Integer> bucket : buckets) {\n'
        '        Collections.sort(bucket);\n'
        '        for (int num : bucket) arr[k++] = num;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '桶排序性能高度依赖数据的均匀分布程度<br>'
    '桶数量≈元素数量时效率最高，平均O(n)<br>'
    '映射函数的设计直接影响性能：要尽量均匀分配<br>'
    '桶内排序通常用插入排序(桶内元素少时最快)<br>'
    '本质是"分而治之"思想在不同维度上的应用')

# ============================
# 基数排序 (Radix Sort)
# ============================
p = '基数排序'
d = make_deck(1747301619, f'算法::排序::各排序算法::{p}')

add_basic(d, make_front(p, '题干'),
    '基数排序：非比较排序。从最低位(LSD)或最高位(MSD)开始，'
    '依次按每一位数字进行稳定排序(通常用计数排序作为子程序)。<br>'
    '适用于整数或定长字符串排序，可以处理较大数据范围。')

add_basic(d, make_front(p, '核心思想'),
    '<b>核心机制：逐位排序(LSD) + 计数排序作为稳定子程序</b><br><br>'
    'LSD(Least Significant Digit)基数排序：<br>'
    '1. 从最低位(个位)开始，到最高位结束<br>'
    '2. 每一位使用计数排序(10个桶，对应0-9数字)<br>'
    '3. 每次按当前位排序后收集回原数组<br>'
    '4. 由于计数排序是稳定的，高位的排序不会破坏低位的顺序<br><br>'
    '<b>为什么LSD是稳定的关键：</b><br>'
    '先按个位排→再按十位排→再按百位排...<br>'
    '当十位相同时，之前按个位排好的顺序得以保留 → 正确排序。')

add_cloze(d, make_front(p, '复杂度分析'),
    '<b>时间复杂度推导：</b><br>'
    '设最大数字有d位，每位数范围k(十进制k=10)<br>'
    '共d轮，每轮用计数排序O(n+k) → {{c1::O(d × (n+k))}}<br>'
    '通常k固定(如k=10)，d=log₁₀(max)<br>'
    '简写为：{{c2::O(nk)}}（k为位数）<br>'
    '当k较小时近似线性O(n)<br><br>'
    '<b>空间复杂度推导：</b><br>'
    '每轮计数排序需要temp(n) + count(k) → {{c3::O(n+k)}}<br><br>'
    '<b>稳定性：</b>{{c4::稳定}}(每轮计数排序是稳定的)')

add_basic(d, make_front(p, '题解(LSD)'),
    '从最低位到最高位，每位用计数排序<br>'
    + code(
        'public void radixSort(int[] arr) {\n'
        '    if (arr.length == 0) return;\n'
        '    // 1. 找最大值确定位数\n'
        '    int max = arr[0];\n'
        '    for (int num : arr) max = Math.max(max, num);\n'
        '    // 2. 从个位开始，按每位排序\n'
        '    int[] output = new int[arr.length];\n'
        '    for (int exp = 1; max / exp > 0; exp *= 10) {\n'
        '        int[] count = new int[10];\n'
        '        // 统计当前位的数字频率\n'
        '        for (int num : arr)\n'
        '            count[(num / exp) % 10]++;\n'
        '        // 前缀和\n'
        '        for (int i = 1; i < 10; i++)\n'
        '            count[i] += count[i - 1];\n'
        '        // 逆序回填（保证稳定）\n'
        '        for (int i = arr.length - 1; i >= 0; i--) {\n'
        '            int digit = (arr[i] / exp) % 10;\n'
        '            output[--count[digit]] = arr[i];\n'
        '        }\n'
        '        System.arraycopy(output, 0, arr, 0, arr.length);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '基数排序每次按一位排序，必须用稳定排序作为子排序<br>'
    'LSD更常用（代码简单），MSD可以提前终止(适合字符串)<br>'
    '基数r可以取16(十六进制)、256(字节)等，r大则位数少但计数数组大<br>'
    '复杂度和元素个数n、数字位数d、基数r都相关：O(d(n+r))<br>'
    '适合定长数据(固定位数整数、定长字符串)，不适合变长数据')

# ═══════════════════════════════════════════════════════════════
# 排序算法对比总结
# ═══════════════════════════════════════════════════════════════
pc = make_deck(1747301620, '算法::排序::各排序算法::综合对比')

add_basic(pc, '排序算法选择决策树',
    '<b>数据量小(n&lt;50)</b> → 插入排序（简单高效）<br>'
    '<b>数据基本有序</b> → 插入排序（接近O(n)）<br>'
    '<b>需要稳定</b> → 归并排序 / 插入排序<br>'
    '<b>内存严格受限</b> → 堆排序（O(1)空间）<br>'
    '<b>通用大数据</b> → 快速排序（实际最快）<br>'
    '<b>数据范围小</b> → 计数排序（O(n)）<br>'
    '<b>外部排序(磁盘)</b> → 归并排序<br>'
    '<b>链表排序</b> → 归并排序（不需要随机访问）<br>'
    '<b>数据均匀分布</b> → 桶排序（平均O(n)）')

add_cloze(pc, '各排序算法本质理解',
    '冒泡：相邻比较交换，O(n²)，{{c1::稳定}}，最简单<br>'
    '选择：选最小放前面，O(n²)，{{c2::不稳定}}，交换最少<br>'
    '插入：插入已排序前缀，O(n²)，{{c3::稳定}}，基本有序时最快<br>'
    '希尔：分组预排序+插入排序，{{c4::O(n^1.3)}}，不稳定<br>'
    '快排：partition分治，O(n log n)，{{c5::不稳定}}，实际最快<br>'
    '归并：分治合并有序数组，O(n log n)，{{c6::稳定}}，需O(n)空间<br>'
    '堆排：建堆+反复交换堆顶，O(n log n)，{{c7::不稳定}}，O(1)空间<br>'
    '计数：统计频率+前缀和，O(n+k)，{{c8::稳定}}，需值域小<br>'
    '桶排：分桶+桶内排序+合并，O(n+k)，取决于均匀性<br>'
    '基数：逐位排序(LSD/MSD)，O(nk)，{{c9::稳定}}，用计数排序做子程序')

add_cloze(pc, '面试高频排序对比',
    '为什么快排比归并快？快排{{c1::原地排序}}缓存友好，常数因子小；归并需{{c2::O(n)额外空间}}<br>'
    '为什么快排比堆排快？快排{{c3::局部性好}}，堆排跳跃访问{{c4::缓存不友好}}<br>'
    '为什么归并排序最稳定？比较次数固定{{c5::n log n}}，不受输入影响，且{{c6::稳定}}<br>'
    '堆排序最大优势：{{c7::O(1)空间}}的O(n log n)算法<br>'
    '计数/基数为什么能O(n)？{{c8::不基于比较}}，利用数据范围信息')

add_basic(pc, '排序可视化对比',
    '冒泡/选择/插入 → 适合学习和理解排序概念<br>'
    '快排 → partition是核心，理解才能写对<br>'
    '归并 → merge是核心，分治思想典型<br>'
    '堆排 → heapify是核心，理解堆结构<br>'
    '计数 → 前缀和是稳定版的关键<br>'
    '基数 → 计数排序的应用，逐位思想<br>'
    '希尔 → gap序列影响性能，理解"预排序"思想')

if __name__ == '__main__':
    print(build('../../牌组/算法/各种排序.apkg'))

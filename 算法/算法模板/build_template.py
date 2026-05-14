"""Build APKG for 算法模板 (Algorithm Templates). Single reference deck."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


d = make_deck(1747301800, '算法::模板')

# --- 手写堆 ---
add_basic(d, '模板 | 手写堆',
    '堆是完全二叉树，底层连续数组存储。<br>'
    '核心操作：<br>'
    '1. heapInsert(index)：上浮，(index-1)/2 找父节点，comparator比较<br>'
    '2. heapify(index, heapSize)：下沉，left=2*i+1, right=2*i+2，三者选最大/最小<br>'
    '3. swap(i, j)：交换值+更新indexMap<br>'
    '小根堆：comparator(a,b)-&gt;a-b，大根堆：comparator(a,b)-&gt;b-a')

add_cloze(d, '模板 | 手写堆 核心代码' + '<br><code>'
    + 'void heapInsert(int index){<br>'
    + '&nbsp;&nbsp;while(comparator.compare(heap.get(index),<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;heap.get({{c1::(index-1)/2}})) &lt; 0){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;swap(index, (index-1)/2);<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;index = (index-1)/2;<br>'
    + '&nbsp;&nbsp;}<br>}<br>'
    + 'void heapify(int index, int heapSize){<br>'
    + '&nbsp;&nbsp;int left = {{c2::index*2+1}};<br>'
    + '&nbsp;&nbsp;while(left &lt; heapSize){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;int best = left+1&lt;heapSize &&<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;comp(left+1,left)&lt;0 ? left+1 : left;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;best = comp(best,index)&lt;0 ? best : index;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;if(best==index) break;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;swap(best, index);<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;index = best; left = index*2+1;<br>'
    + '&nbsp;&nbsp;}<br>}</code>', '堆的核心：上浮和下沉两个操作')

add_basic(d, make_front('模板', '手写堆完整代码(小根堆)'),
    '带 indexMap 的通用小根堆实现，支持 resign 操作。<br>'
    + code(
        '/**\n'
        ' * 小根堆的实现：堆是完全二叉树，底层连续数组存储\n'
        ' */\n'
        'public class IndexMinHeap&lt;T&gt; {\n'
        '    private List&lt;T&gt; heap;\n'
        '    private Map&lt;T, Integer&gt; indexMap;\n'
        '    private int heapSize;\n'
        '    private Comparator&lt;? super T&gt; comparator;\n'
        '\n'
        '    public IndexMinHeap(Comparator&lt;? super T&gt; comparator) {\n'
        '        heap = new ArrayList&lt;&gt;();\n'
        '        indexMap = new HashMap&lt;&gt;();\n'
        '        heapSize = 0;\n'
        '        this.comparator = comparator;\n'
        '    }\n'
        '\n'
        '    public boolean isEmpty() { return heapSize == 0; }\n'
        '    public int size() { return heapSize; }\n'
        '    public boolean contains(T key) { return indexMap.containsKey(key); }\n'
        '\n'
        '    public void offer(T value) {\n'
        '        heap.add(value);\n'
        '        indexMap.put(value, heapSize);\n'
        '        heapInsert(heapSize++);\n'
        '    }\n'
        '\n'
        '    private void heapInsert(int index) {\n'
        '        while (comparator.compare(heap.get(index),\n'
        '                heap.get((index - 1) / 2)) &lt; 0) {\n'
        '            swap(index, (index - 1) / 2);\n'
        '            index = (index - 1) / 2;\n'
        '        }\n'
        '    }\n'
        '\n'
        '    private void swap(int i, int j) {\n'
        '        T t1 = heap.get(i);\n'
        '        T t2 = heap.get(j);\n'
        '        heap.set(i, t2);\n'
        '        heap.set(j, t1);\n'
        '        indexMap.put(t1, j);\n'
        '        indexMap.put(t2, i);\n'
        '    }\n'
        '\n'
        '    public T pull() {\n'
        '        T res = heap.get(0);\n'
        '        int end = heapSize - 1;\n'
        '        swap(0, end);\n'
        '        heap.remove(end);\n'
        '        indexMap.remove(res);\n'
        '        heapify(0, --heapSize);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void resign(T value) {\n'
        '        int valueIndex = indexMap.get(value);\n'
        '        heapInsert(valueIndex);\n'
        '        heapify(valueIndex, heapSize);\n'
        '    }\n'
        '\n'
        '    private void heapify(int index, int heapSize) {\n'
        '        int parent = index, left = parent * 2 + 1;\n'
        '        while (left &lt; heapSize) {\n'
        '            int largest = left + 1 &lt; heapSize &&\n'
        '                    (comparator.compare(heap.get(left + 1),\n'
        '                            heap.get(left)) &lt; 0) ?\n'
        '                    left + 1 : left;\n'
        '            largest = comparator.compare(heap.get(largest),\n'
        '                    heap.get(index)) &lt; 0 ? largest : index;\n'
        '            if (largest == index) break;\n'
        '            swap(largest, index);\n'
        '            index = largest;\n'
        '            left = index * 2 + 1;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

# --- 反转链表 ---
add_cloze(d, '模板 | 反转链表(迭代)' + '<br><code>'
    + 'ListNode pre=null, cur=head;<br>'
    + 'while(cur!=null){<br>'
    + '&nbsp;&nbsp;ListNode tail = {{c1::cur.next}};<br>'
    + '&nbsp;&nbsp;cur.next = pre;<br>'
    + '&nbsp;&nbsp;pre = cur;<br>'
    + '&nbsp;&nbsp;cur = tail;<br>}<br>'
    + 'return {{c2::pre}};</code>', '三指针：pre/cur/tail，tail保存下一个，cur.next指向前一个')

add_basic(d, make_front('模板', '反转链表完整代码'),
    '三指针迭代法：pre/cur/tail，O(n) 时间，O(1) 空间。<br>'
    + code(
        'public ListNode reverse(ListNode head) {\n'
        '    if (head == null || head.next == null) {\n'
        '        return head;\n'
        '    }\n'
        '    ListNode pre = null;\n'
        '    ListNode cur = head;\n'
        '    ListNode tail = null;\n'
        '    while (cur != null) {\n'
        '        tail = cur.next;\n'
        '        cur.next = pre;\n'
        '        pre = cur;\n'
        '        cur = tail;\n'
        '    }\n'
        '    return pre;\n'
        '}'
    ))

# --- 快速排序 ---
add_basic(d, '模板 | 手撕快速排序',
    '核心：partition 划分 + 递归<br>'
    '1. 选基准（随机选并swap到最左避免最坏情况）<br>'
    '2. 双指针：先从右向左找&lt;基准，再从左向右找&gt;=基准，交换<br>'
    '3. 基准落位到i==j的位置<br>'
    '4. 递归左右区间<br>'
    '关键：必须先从右向左扫描！时间复杂度 O(n log n)，不稳定')

add_cloze(d, '模板 | 快排 partition' + '<br><code>'
    + 'int partition(int[] nums, int l, int r){<br>'
    + '&nbsp;&nbsp;int i=l, j=r, pivot=nums[l];<br>'
    + '&nbsp;&nbsp;while(i&lt;j){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;while({{c1::j&gt;i && nums[j]&gt;=pivot}}) j--;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;nums[i]=nums[j];<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;while(i&lt;j && nums[i]&lt;=pivot) i++;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;nums[j]=nums[i];<br>'
    + '&nbsp;&nbsp;}<br>'
    + '&nbsp;&nbsp;nums[i]=pivot; return i;<br>}</code>',
    '先从右向左扫描找小于基准的，再从左向右找大于基准的，最后基准归位')

add_basic(d, make_front('模板', '快速排序完整代码(标准版)'),
    'partition 挖坑填数法，取最左为基准，必须先从右向左扫描。<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return null;\n'
        '        quickSort(nums, 0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public int partition(int[] nums, int start, int end) {\n'
        '        int left = start;\n'
        '        int right = end;\n'
        '        int finalNum = nums[left];\n'
        '        while (left &lt; right) {\n'
        '            while (right &gt; left && nums[right] &gt;= finalNum)\n'
        '                right--;\n'
        '            nums[left] = nums[right];\n'
        '            while (left &lt; right && nums[left] &lt;= finalNum)\n'
        '                left++;\n'
        '            nums[right] = nums[left];\n'
        '        }\n'
        '        nums[left] = finalNum;\n'
        '        return left;\n'
        '    }\n'
        '\n'
        '    public void quickSort(int[] nums, int start, int end) {\n'
        '        int i;\n'
        '        if (start &lt; end) {\n'
        '            i = partition(nums, start, end);\n'
        '            quickSort(nums, start, i - 1);\n'
        '            quickSort(nums, i + 1, end);\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front('模板', '快速排序完整代码(随机基准)'),
    '随机选基准并 swap 到最左，避免最坏情况 O(n^2)。<br>'
    + code(
        'class Solution {\n'
        '    private static final Random RANDOM = new Random(System.currentTimeMillis());\n'
        '\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        quickSort(nums, 0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void quickSort(int[] arr, int left, int right) {\n'
        '        if (left &gt;= right) return;\n'
        '        int randomIndex = RANDOM.nextInt(right - left + 1) + left;\n'
        '        swap(arr, left, randomIndex);\n'
        '\n'
        '        int i = left, j = right;\n'
        '        while (i &lt; j) {\n'
        '            while (j &gt; i && arr[j] &gt;= arr[left]) j--;\n'
        '            while (i &lt; j && arr[i] &lt;= arr[left]) i++;\n'
        '            swap(arr, i, j);\n'
        '        }\n'
        '        swap(arr, left, i);\n'
        '        quickSort(arr, left, i - 1);\n'
        '        quickSort(arr, i + 1, right);\n'
        '    }\n'
        '\n'
        '    public void swap(int[] arr, int i, int j) {\n'
        '        int temp = arr[i];\n'
        '        arr[i] = arr[j];\n'
        '        arr[j] = temp;\n'
        '    }\n'
        '}'
    ))

# --- 堆排序 ---
add_cloze(d, '模板 | 手撕堆排序' + '<br><code>'
    + '// 1. 建初堆：从 {{c1::n/2-1}} 到 0 依次调整<br>'
    + 'for(i=n/2-1; i&gt;=0; i--) heapify(nums,i,n-1);<br>'
    + '// 2. n-1趟排序<br>'
    + 'for(i=n-1; i&gt;=1; i--){<br>'
    + '&nbsp;&nbsp;swap(nums,0,i);<br>'
    + '&nbsp;&nbsp;heapify(nums,{{c2::0,i-1}});<br>}<br>'
    + '// heapify: 大根堆，left=2*i+1，选三者最大交换并下沉</code>',
    '建堆从最后一个非叶节点开始；排序每次交换堆顶和末尾，缩小堆再调整')

add_basic(d, make_front('模板', '堆排序完整代码(标准版)'),
    '大根堆排序：建堆 O(n) + n-1 趟交换调整 O(n log n)。<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        if (nums.length == 0) return null;\n'
        '        int i, n = nums.length, temp;\n'
        '        // 建初堆：从最后一个非叶节点开始\n'
        '        for (i = n / 2 - 1; i &gt;= 0; i--)\n'
        '            sift(nums, i, n - 1);\n'
        '        // n-1 趟排序\n'
        '        for (i = n - 1; i &gt;= 1; i--) {\n'
        '            temp = nums[0];\n'
        '            nums[0] = nums[i];\n'
        '            nums[i] = temp;\n'
        '            sift(nums, 0, i - 1);\n'
        '        }\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void sift(int[] nums, int low, int high) {\n'
        '        int i = low, j = 2 * i + 1;\n'
        '        int temp = nums[i];\n'
        '        while (j &lt;= high) {\n'
        '            if (j &lt; high && nums[j] &lt; nums[j + 1])\n'
        '                j++;\n'
        '            if (temp &lt; nums[j]) {\n'
        '                nums[i] = nums[j];\n'
        '                i = j;\n'
        '                j = 2 * i + 1;\n'
        '            } else break;\n'
        '        }\n'
        '        nums[i] = temp;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front('模板', '堆排序完整代码(简便版)'),
    '简化 heapify 写法：直接 swap 后继续下沉。<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        // 建初堆\n'
        '        for (int i = n / 2 - 1; i &gt;= 0; i--)\n'
        '            heapify(nums, i, n - 1);\n'
        '        // n-1 趟排序\n'
        '        for (int i = n - 1; i &gt;= 1; i--) {\n'
        '            swap(nums, 0, i);\n'
        '            heapify(nums, 0, i - 1);\n'
        '        }\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void heapify(int[] nums, int low, int high) {\n'
        '        int i = low, j = 2 * i + 1;\n'
        '        while (j &lt;= high) {\n'
        '            if (j &lt; high && nums[j] &lt; nums[j + 1]) j++;\n'
        '            if (nums[i] &lt; nums[j]) {\n'
        '                swap(nums, i, j);\n'
        '                i = j;\n'
        '                j = 2 * i + 1;\n'
        '            } else break;\n'
        '        }\n'
        '    }\n'
        '\n'
        '    public void swap(int[] nums, int i, int j) {\n'
        '        int temp = nums[i];\n'
        '        nums[i] = nums[j];\n'
        '        nums[j] = temp;\n'
        '    }\n'
        '}'
    ))

# --- 归并排序 ---
add_cloze(d, '模板 | 手撕归并排序(递归)' + '<br><code>'
    + 'void mergeSort(int l, int r){<br>'
    + '&nbsp;&nbsp;if(l&gt;=r) return;<br>'
    + '&nbsp;&nbsp;int m={{c1::l+(r-l)/2}};<br>'
    + '&nbsp;&nbsp;mergeSort(l,m); mergeSort(m+1,r);<br>'
    + '&nbsp;&nbsp;int i=l, j=m+1, k=0;<br>'
    + '&nbsp;&nbsp;while(i&lt;=m && j&lt;=r)<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;temp[k++]=nums[i]&lt;=nums[j]?{{c2::nums[i++]}}:nums[j++];<br>'
    + '&nbsp;&nbsp;while(i&lt;=m) temp[k++]=nums[i++];<br>'
    + '&nbsp;&nbsp;while(j&lt;=r) temp[k++]=nums[j++];<br>'
    + '&nbsp;&nbsp;for(i=l,k=0;i&lt;=r;) nums[i++]=temp[k++];<br>}</code>',
    '递归拆分+归并，O(n log n)，稳定，需要 O(n) 辅助空间')

add_basic(d, '模板 | 手撕归并排序(迭代)',
    '自底向上（非递归）：<br>'
    '1. intv=1，每次 intv*=2<br>'
    '2. mergePass：每次归并两个相邻 intv 长度的子表<br>'
    '3. 处理奇数/偶数剩余子表：if(i+length-1 &lt; len-1) 单独归并<br>'
    '优点：无递归开销，O(1)栈空间')

add_basic(d, make_front('模板', '归并排序完整代码(迭代版)'),
    '自底向上二路归并，非递归，O(n log n)，稳定，需 O(n) 辅助空间。<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        if (nums == null || nums.length == 0) return nums;\n'
        '        int len = nums.length;\n'
        '        for (int i = 1; i &lt; len; i *= 2)\n'
        '            mergePass(nums, i, len);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void mergePass(int[] nums, int length, int len) {\n'
        '        int i;\n'
        '        for (i = 0; i + 2 * length - 1 &lt; len; i = i + 2 * length)\n'
        '            merge(nums, i, i + length - 1, i + 2 * length - 1);\n'
        '        if (i + length - 1 &lt; len - 1)\n'
        '            merge(nums, i, i + length - 1, len - 1);\n'
        '    }\n'
        '\n'
        '    public void merge(int[] nums, int low, int mid, int high) {\n'
        '        int[] temp = new int[high - low + 1];\n'
        '        int i = low, j = mid + 1, k = 0;\n'
        '        while (i &lt;= mid && j &lt;= high) {\n'
        '            if (nums[i] &lt;= nums[j]) {\n'
        '                temp[k] = nums[i]; i++; k++;\n'
        '            } else {\n'
        '                temp[k] = nums[j]; j++; k++;\n'
        '            }\n'
        '        }\n'
        '        while (i &lt;= mid) { temp[k] = nums[i]; i++; k++; }\n'
        '        while (j &lt;= high) { temp[k] = nums[j]; j++; k++; }\n'
        '        for (k = 0, i = low; i &lt;= high; k++, i++)\n'
        '            nums[i] = temp[k];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front('模板', '归并排序完整代码(递归版v1)'),
    '递归拆分 + 原地 tmp 数组辅助合并，先复制到 tmp 再归并回 nums。<br>'
    + code(
        'class Solution {\n'
        '    int[] nums, tmp;\n'
        '\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        this.nums = nums;\n'
        '        tmp = new int[nums.length];\n'
        '        mergeSort(0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void mergeSort(int l, int r) {\n'
        '        if (l &gt;= r) return;\n'
        '        int m = l + (r - l) / 2;\n'
        '        mergeSort(l, m);\n'
        '        mergeSort(m + 1, r);\n'
        '        int i = l, j = m + 1;\n'
        '        for (int k = l; k &lt;= r; k++)\n'
        '            tmp[k] = nums[k];\n'
        '        for (int k = l; k &lt;= r; k++) {\n'
        '            if (i == m + 1)\n'
        '                nums[k] = tmp[j++];\n'
        '            else if (j == r + 1 || tmp[i] &lt;= tmp[j])\n'
        '                nums[k] = tmp[i++];\n'
        '            else\n'
        '                nums[k] = tmp[j++];\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front('模板', '归并排序完整代码(递归版v2)'),
    '递归拆分 + 临时数组合并，三 while 标准写法。<br>'
    + code(
        'class Solution {\n'
        '    int[] nums, temp;\n'
        '\n'
        '    public int[] sortArray(int[] nums) {\n'
        '        this.nums = nums;\n'
        '        temp = new int[nums.length];\n'
        '        mergeSort(0, nums.length - 1);\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public void mergeSort(int left, int right) {\n'
        '        if (left &gt;= right) return;\n'
        '        int mid = left + (right - left) / 2;\n'
        '        mergeSort(left, mid);\n'
        '        mergeSort(mid + 1, right);\n'
        '        int i = left, j = mid + 1, k = 0;\n'
        '        while (i &lt;= mid && j &lt;= right) {\n'
        '            if (nums[i] &lt;= nums[j])\n'
        '                temp[k++] = nums[i++];\n'
        '            else\n'
        '                temp[k++] = nums[j++];\n'
        '        }\n'
        '        while (i &lt;= mid) temp[k++] = nums[i++];\n'
        '        while (j &lt;= right) temp[k++] = nums[j++];\n'
        '        for (i = left, k = 0; i &lt;= right; i++)\n'
        '            nums[i] = temp[k++];\n'
        '    }\n'
        '}'
    ))

# --- 冒泡排序 ---
add_cloze(d, '模板 | 手撕冒泡排序' + '<br><code>'
    + 'for(i=0; i&lt;len-1; i++){<br>'
    + '&nbsp;&nbsp;boolean flag=false;<br>'
    + '&nbsp;&nbsp;for(j=0; j&lt;{{c1::len-1-i}}; j++){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;if(nums[j] &gt; nums[j+1]){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;swap(nums,j,j+1); flag=true;<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;}<br>'
    + '&nbsp;&nbsp;}<br>'
    + '&nbsp;&nbsp;if(!flag) {{c2::break}};<br>}</code>',
    'flag 提前退出优化：若某一趟无交换，说明已有序')

add_basic(d, make_front('模板', '冒泡排序完整代码'),
    '双重循环 + flag 提前退出优化，O(n^2)，稳定。<br>'
    + code(
        'private int[] bubbleSort(int[] array) {\n'
        '    int temp;\n'
        '    for (int i = 0; i &lt; array.length - 1; i++) {\n'
        '        boolean Flag = false;\n'
        '        for (int j = 0; j &lt; array.length - 1 - i; j++) {\n'
        '            if (array[j] &gt; array[j + 1]) {\n'
        '                temp = array[j];\n'
        '                array[j] = array[j + 1];\n'
        '                array[j + 1] = temp;\n'
        '                Flag = true;\n'
        '            }\n'
        '        }\n'
        '        if (!Flag) break;\n'
        '    }\n'
        '    return array;\n'
        '}'
    ))

# --- 二叉树路径 ---
add_basic(d, '模板 | 二叉树路径问题分类',
    '自顶向下：从根到叶（或任意节点）的路径<br>'
    '- 找路径和==target：用 target-node.val 代替 curSum<br>'
    '- 二叉树一般不需回溯（每条路径唯一）<br>'
    '- 必须到叶节点才 return，任意节点则不 return<br>'
    '- 从任意节点开始需要双重递归<br><br>'
    '非自顶向下：任意节点到任意节点<br>'
    '- 辅助函数 maxPath(node) 求左侧/右侧最长路径<br>'
    '- 经过 node 的最长路径 = left + right<br>'
    '- 全局变量 res 初值：有负数用 INT_MIN，无负数用 0')

# --- DFS 注意事项 ---
add_basic(d, '模板 | DFS注意事项',
    '1. 路径和：用 target-node.val 差分，判断 target==0<br>'
    '2. 回溯：二叉树通常不需回溯（路径唯一），二维数组需回溯<br>'
    '3. 找到后是否 return：必须到叶→return；任意节点→不return继续<br>'
    '4. 双重递归：从根开始调dfs；从任意节点开始还需调pathSum(root.left/right)')

# --- 二分查找 ---
add_cloze(d, '模板 | 二分查找' + '<br><code>'
    + 'int left=0, right=nums.length-1;<br>'
    + 'while({{c1::left &lt;= right}}){<br>'
    + '&nbsp;&nbsp;int mid = left+(right-left)/2;<br>'
    + '&nbsp;&nbsp;if(nums[mid]==target) return mid;<br>'
    + '&nbsp;&nbsp;else if(nums[mid]&lt;target) left=mid+1;<br>'
    + '&nbsp;&nbsp;else right=mid-1;<br>}<br>return -1;</code>',
    '取等号可在while中直接return mid')

add_basic(d, make_front('模板', '二分查找完整代码(迭代)'),
    '标准 while(left &lt;= right) 写法，在循环中直接 return。<br>'
    + code(
        'class Solution {\n'
        '    public int search(int[] nums, int target) {\n'
        '        int left = 0, right = nums.length - 1;\n'
        '        while (left &lt;= right) {\n'
        '            int mid = (left + right) / 2;\n'
        '            if (target &lt; nums[mid])\n'
        '                right = mid - 1;\n'
        '            else if (target &gt; nums[mid])\n'
        '                left = mid + 1;\n'
        '            else\n'
        '                return mid;\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front('模板', '二分查找完整代码(递归)'),
    '递归二分查找，注意递归调用时缩小区间。<br>'
    + code(
        'public int search(int[] nums, int target) {\n'
        '    return recursion(nums, 0, nums.length - 1, target);\n'
        '}\n'
        '\n'
        'public int recursion(int[] nums, int left, int right, int target) {\n'
        '    int low = left;\n'
        '    int high = right;\n'
        '    int mid = (left + right) / 2;\n'
        '    if (left &gt; right) return -1;\n'
        '    if (nums[mid] == target) {\n'
        '        return mid;\n'
        '    } else if (nums[mid] &gt; target) {\n'
        '        high = mid - 1;\n'
        '        return recursion(nums, low, high, target);\n'
        '    } else {\n'
        '        low = mid + 1;\n'
        '        return recursion(nums, low, high, target);\n'
        '    }\n'
        '}'
    ))

# --- 滑动窗口模板 ---
add_cloze(d, '模板 | 滑动窗口' + '<br><code>'
    + 'int left=0, right=0;<br>'
    + 'while(right &lt; N){<br>'
    + '&nbsp;&nbsp;sums += nums[{{c1::right++}}];<br>'
    + '&nbsp;&nbsp;while(!isValid(sums,left,right)){<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;sums -= nums[{{c2::left++}}];<br>'
    + '&nbsp;&nbsp;}<br>'
    + '&nbsp;&nbsp;res = Math.max(res, right-left);<br>}</code>',
    'right扩张→while收缩left→更新结果。need数组：正=还需要，0=刚好，负=多余')

add_basic(d, make_front('模板', '滑动窗口完整模板'),
    '标准滑动窗口模板：right 扩张 + while 收缩 left + 更新结果。<br>'
    + code(
        'public int findSubArray(int[] nums) {\n'
        '    int N = nums.length;\n'
        '    int left = 0, right = 0;\n'
        '    int sums = 0;\n'
        '    int res = 0;\n'
        '\n'
        '    while (right &lt; N) {\n'
        '        sums += nums[right];\n'
        '        while (!isValid(sums, left, right, nums)) {\n'
        '            sums -= nums[left];\n'
        '            left++;\n'
        '        }\n'
        '        res = Math.max(res, right - left + 1);\n'
        '        right++;\n'
        '    }\n'
        '    return res;\n'
        '}\n'
        '\n'
        'private boolean isValid(int sums, int left, int right, int[] nums) {\n'
        '    return true;  // 根据具体题目实现\n'
        '}'
    ))

# --- 原地哈希 ---
add_basic(d, '模板 | 原地哈希',
    '适合：数组元素值在 [1, n] 或 [0, n] 范围内<br>'
    '核心：利用数组索引作为 hash key，通过标记（取反、加n）记录出现信息<br>'
    + img('image 1.png'))

# --- 递归与回溯 ---
add_basic(d, '模板 | 递归与回溯',
    '回溯三要素：<br>'
    '1. 选择列表：for 循环遍历可选项<br>'
    '2. 做选择+递归+撤销选择<br>'
    '3. 终止条件：满足条件时加入结果<br>'
    + img('image 2.png'))

# --- DFS ---
add_basic(d, '模板 | DFS',
    'DFS 网格模板：<br>'
    '1. 边界检查（越界/已访问/不满足条件）<br>'
    '2. 标记已访问<br>'
    '3. 递归四个方向<br><br>'
    'BFS 拓扑排序模板：<br>'
    '1. 建图+入度数组<br>'
    '2. 入度为0入队<br>'
    '3. BFS：出队→更新邻接节点入度→入度为0入队'
    + img('image 3.png') + img('image 4.png') + img('image 5.png'))

if __name__ == '__main__':
    print(build('../../牌组/算法模板.apkg'))

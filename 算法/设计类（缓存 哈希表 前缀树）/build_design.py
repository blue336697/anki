"""Build APKG for 设计类 (Design Problems). 7 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301700, '算法::设计类::原理通识')
add_basic(d0, '设计类核心数据结构',
    '设计类问题常用数据结构组合：<br>'
    '1. HashMap + DoublyLinkedList → O(1) 查找 + O(1) 插入/删除（LRU、LFU）<br>'
    '2. HashMap + ArrayList → O(1) 查找/插入 + O(1) 随机访问（RandomizedSet）<br>'
    '3. TrieNode[26] 前缀树 → 字符串前缀匹配（Trie）<br>'
    '4. Array + % 取模 → 循环队列（CircularQueue）<br>'
    '5. 数组分桶 + 除留余数法 → 哈希映射（HashMap）')
add_cloze(d0, 'LRU vs LFU 对比',
    'LRU：淘汰{{c1::最久未访问}}的数据，基于{{c2::访问时间}}<br>'
    'LFU：淘汰{{c3::访问频率最低}}的数据，基于{{c4::访问次数}}<br>'
    '共同点：都用 HashMap + DoublyLinkedList，查找 O(1)，插入/删除 O(1)')
add_basic(d0, 'Trie 前缀树结构',
    '每个节点包含：boolean isEnd 标记是否为一个完整单词的结尾 + TrieNode[26] children 指向子节点。<br>'
    '插入：逐字符遍历，节点不存在则创建，最后标记 isEnd=true。<br>'
    '搜索：逐字符遍历，若中途节点为 null 则返回 false，最后检查 isEnd。<br>'
    '前缀匹配：同搜索逻辑，但不检查 isEnd，遍历完所有字符即返回 true。')
add_cloze(d0, 'KMP 算法核心思想',
    '核心：构建 {{c1::next 数组}}（部分匹配表），避免匹配失败时的回退。<br>'
    'next[i] = 模式串[0..i] 的{{c2::最长相等前后缀}}长度。<br>'
    '时间复杂度：{{c3::O(m+n)}}，暴力法为 {{c4::O(m*n)}}。<br>'
    '匹配失败时：目标串指针不回溯，模式串跳转到 next[j] 继续匹配。')

# ============================================================
# 1. LRU缓存机制
# ============================================================
p = 'LRU缓存机制'
d = make_deck(1747301701, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '设计一个 LRU（最近最少使用）缓存数据结构。实现 LRUCache 类：<br>'
    'LRUCache(int capacity) 初始化，get(int key) 获取值（不存在返回-1），'
    'put(int key, int value) 插入或更新。<br>'
    '如果 key 已存在，变更其 value；key 不存在则插入。当缓存容量满时，淘汰最久未使用的 key。<br>'
    '要求：get 和 put 均为 O(1) 时间复杂度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：get — {{c1::O(1)}}，put — {{c2::O(1)}}<br>空间：{{c3::O(capacity)}}')

add_basic(d, make_front(p, '题解(DoubleList独立类)'),
    '自定义双向链表类 + 自定义节点 + HashMap 实现 LRU。<br>'
    + code("""\
class LRUCache {
    // 定义结点的内部类
    private class Node{
        Node pre,next;
        int key,value;

        private Node(){
            this.pre = this.next = null;
        }

        private Node(int k, int v){
            this.key = k;
            this.value = v;
            this.pre = this.next = null;
        }
    }

    // 定义双向列表的类
    private class DoubleList{
        Node head = new Node(0, 0);
        Node tail = new Node(0, 0);
        int size;

        private DoubleList(){
            head.next = tail;
            tail.pre = head;
            size = 0;
        }

        // 添加结点到队头
        private void addFirst(Node node){
            Node headNext = head.next;
            head.next = node;
            headNext.pre = node;
            node.pre = head;
            node.next = headNext;
            size++;
        }

        // 删除队尾的结点
        private Node rmLast(){
            Node last = tail.pre;
            rm(last);
            return last;
        }

        // 删除指定结点
        private void rm(Node node){
            node.next.pre = node.pre;
            node.pre.next = node.next;
            size--;
        }

        private int size() {
            return size;
        }
    }

    // key -> Node(key, val)
    private HashMap&lt;Integer, Node&gt; map;
    // Node(k1, v1) <-> Node(k2, v2)...
    private DoubleList cache;
    // 最大容量
    private int cap;

    public LRUCache(int capacity) {
        this.cap = capacity;
        cache = new DoubleList();
        map = new HashMap&lt;&gt;();
    }

    public int get(int key) {
        if(!map.containsKey(key))
            return -1;
        int value = map.get(key).value;
        // 调用put方法移动到队头
        put(key, value);
        return value;
    }

    public void put(int key, int value) {
        Node node = new Node(key, value);

        if(map.containsKey(key)){
            cache.rm(map.get(key));
            cache.addFirst(node);
            // 更新map中的value值
            map.put(key, node);
        }else {
            if(cap == cache.size()){
                Node last = cache.rmLast();
                map.remove(last.key);
            }
            cache.addFirst(node);
            map.put(key, node);
        }
    }
}"""))

add_basic(d, make_front(p, '题解(双向链表合并在Node中)'),
    '节点自带双向链表指针，虚拟头尾节点简化边界。<br>'
    + code("""\
public class LRUCache {

    /**
     * 容量
     */
    private int capacity;

    /**
     * 存储缓存
     */
    private Map&lt;Integer, Node&lt;Integer, Integer&gt;&gt; map;

    /**
     * 虚拟头结点
     */
    private Node&lt;Integer, Integer&gt; head;

    /**
     * 虚拟尾结点
     */
    private Node&lt;Integer, Integer&gt; tail;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        map = new HashMap&lt;&gt;((int)(capacity / 0.75 + 1), 0.75f);
        head = new Node&lt;&gt;();
        tail = new Node&lt;&gt;();
        head.next = tail;
        tail.pre = head;
    }

    public int get(int key) {
        Node&lt;Integer, Integer&gt; node = map.get(key);
        if (node == null) {
            return -1;
        }
        deleteNode(node);
        addToTail(node);
        return node.value;
    }

    public void put(int key, int value) {
        Node&lt;Integer, Integer&gt; node = map.get(key);
        if (node != null) {
            deleteNode(node);
        }
        node = new Node&lt;&gt;(key, value);
        addToTail(node);
        map.put(key, node);
        if (map.size() &gt; capacity) {
            removeHead();
        }
    }

    private void deleteNode(Node node) {
        node.pre.next = node.next;
        node.next.pre = node.pre;
    }

    private void addToTail(Node node) {
        node.next = tail;
        node.pre = tail.pre;
        tail.pre.next = node;
        tail.pre = node;
    }

    private void removeHead() {
        Node node = head.next;
        head.next = node.next;
        node.next.pre = head;
        map.remove(node.key);
    }

    private static class Node&lt;k, v&gt; {
        k key;
        v value;
        Node&lt;k, v&gt; next;
        Node&lt;k, v&gt; pre;

        public Node() {
        }

        public Node(k key, v value) {
            this.key = key;
            this.value = value;
            next = null;
            pre = null;
        }
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    '核心组合：HashMap 实现 O(1) 查找 + 双向链表实现 O(1) 插入/删除。<br>'
    '使用虚拟头尾节点（dummy head/tail）简化边界处理。<br>'
    'get 时先删除再插入头部 = 更新访问时间。<br>'
    'put 满时删除 tail.pre（尾部前一个节点），注意同时清理 HashMap 中的映射。')

# ============================================================
# 2. LFU缓存
# ============================================================
p = 'LFU缓存'
d = make_deck(1747301702, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '设计一个 LFU（最不经常使用）缓存数据结构。实现 LFUCache 类：<br>'
    'LFUCache(int capacity) 初始化，get(int key) 获取值，put(int key, int value) 插入或更新。<br>'
    '淘汰策略：当缓存满时，移除使用频率最低的 key；若频率相同，淘汰其中最久未使用的。<br>'
    '要求：get 和 put 均为 O(1) 时间复杂度。' + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：get — {{c1::O(1)}}，put — {{c2::O(1)}}<br>空间：{{c3::O(capacity)}}')

add_basic(d, make_front(p, '题解(频次双向链表链)'),
    'HashMap(key→Node) + 按频次串联的双向链表链，淘汰最小频次的最久未用节点。<br>'
    + code("""\
class LFUCache {
    private class Node{
        int key, value;
        Node pre;
        Node next;
        DoublyLinkedList doublyLinkedList;  // Node所在频次的双向链表

        private Node(int key, int value){}
        private Node(int key, int value){
            this.key = key;
            this.value = value;
        }
    }

    int capacity;
    Map&lt;Integer, Node&gt; cache;
    DoublyLinkedList firstLinkedList;
    // firstLinkedList.next 是频次最大的双向链表

    DoublyLinkedList lastLinkedList;
    // lastLinkedList.pre 是频次最小的双向链表，满了之后删除 lastLinkedList.pre.tail.pre 即为频次最小且访问最早的Node

    int size;

    public LFUCache(int capacity) {
        this.capacity = capacity;
        cache = new HashMap&lt;&gt;(capacity);
        firstLinkedList = new DoublyLinkedList();
        firstLinkedList.next = lastLinkedList;
        lastLinkedList = new DoublyLinkedList();
        lastLinkedList.pre = firstLinkedList;
    }

    public int get(int key) {
        Node node = cache.get(key);
        if(node == null)
            return -1;
        freqInc(node);
        return node.value;
    }

    public void put(int key, int value) {
        if(capacity == 0)
            return;

        Node node = cache.get(key);
        if(node != null){
            node.value = value;
            freqInc(node);
        }else{
            if(cache.size() == capacity){
                cache.remove(lastLinkedList.pre.tail.pre.key);

                lastLinkedList.removeNode(lastLinkedList.pre.tail.pre);

                size--;
                if(lastLinkedList.pre.head.post == lastLinkedList.pre.tail) {
                   removeDoublyLinkedList(lastLinkedList.pre);
                }
            }

            Node newNode = new Node(key, value);

            cache.put(key, newNode);

            if (lastLinkedList.pre.freq != 1) {

              DoublyLinkedList newDoublyLinedList = new DoublyLinkedList(1);

              addDoublyLinkedList(newDoublyLinedList, lastLinkedList.pre);

              newDoublyLinedList.addNode(newNode);

            } else {

              lastLinkedList.pre.addNode(newNode);

            }

            size++;
        }
    }

    public void freqInc(Node node){
        DoublyLinkedList linkedList = node.doublyLinkedList;

        DoublyLinkedList preLinkedList = linkedList.pre;

        linkedList.removeNode(node);

        if (linkedList.head.post == linkedList.tail) {

          removeDoublyLinkedList(linkedList);

        }

        node.freq++;

        if (preLinkedList.freq != node.freq) {

          DoublyLinkedList newDoublyLinedList = new DoublyLinkedList(node.freq);

          addDoublyLinkedList(newDoublyLinedList, preLinkedList);

          newDoublyLinedList.addNode(node);

        } else {

          preLinkedList.addNode(node);

        }
    }

    public void addDoublyLinkedList(DoublyLinkedList newDoublyLinedList, DoublyLinkedList preLinkedList) {

        newDoublyLinedList.post = preLinkedList.post;

        newDoublyLinedList.post.pre = newDoublyLinedList;

        newDoublyLinedList.pre = preLinkedList;

        preLinkedList.post = newDoublyLinedList;

    }

    public void removeDoublyLinkedList(DoublyLinkedList doublyLinkedList) {

        doublyLinkedList.pre.post = doublyLinkedList.post;

        doublyLinkedList.post.pre = doublyLinkedList.pre;

    }

}

class DoublyLinkedList {

  int freq; // 该双向链表表示的频次

  DoublyLinkedList pre;  // 该双向链表的前继链表（pre.freq &lt; this.freq）

  DoublyLinkedList next; // 该双向链表的后继链表 (next.freq &gt; this.freq)

  Node head; // 该双向链表的头节点，新节点从头部加入，表示最近访问

  Node tail; // 该双向链表的尾节点，删除节点从尾部删除，表示最久访问

  public DoublyLinkedList() {

    head = new Node();

    tail = new Node();

    head.next = tail;

    tail.pre = head;

  }

  public DoublyLinkedList(int freq) {

    head = new Node();

    tail = new Node();

    head.next = tail;

    tail.pre = head;

    this.freq = freq;

  }

  void removeNode(Node node) {

    node.pre.next = node.next;

    node.next.pre = node.pre;

  }

  void addNode(Node node) {

    node.next = head.next;

    head.next.pre = node;

    head.next = node;

    node.pre = head;

    node.doublyLinkedList = this;

  }

}"""))

add_basic(d, make_front(p, '关键技巧'),
    '数据结构：HashMap 存 key→Node + 按频次串联的多个双向链表。<br>'
    '频次链表链：firstLinkedList ↔ freq=3 ↔ freq=2 ↔ freq=1 ↔ lastLinkedList（最小频次靠近 last）。<br>'
    '淘汰时从 lastLinkedList.pre 的尾部移除（频率最低且最久未用）。<br>'
    '每个 Node 持有所在链表的引用（doublyLinkedList 字段），便于 O(1) 定位。')

# ============================================================
# 3. 实现 Trie (前缀树)
# ============================================================
p = '实现 Trie (前缀树)'
d = make_deck(1747301703, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '实现 Trie（前缀树）类：Trie() 初始化，insert(String word) 插入单词，'
    'search(String word) 查找单词是否存在，startsWith(String prefix) 检查是否有以此前缀开头的单词。'
    + img('image 1.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：insert/search/startsWith 均为 {{c1::O(L)}}（L 为单词长度）<br>'
    '空间：{{c2::O(26*N)}}（N 为总节点数，每个节点 26 个 child 指针）')

add_basic(d, make_front(p, '题解(TrieNode+数组)'),
    'TrieNode[26] 存储子节点，ch - \'a\' 映射到 0-25，isEnd 标记完整单词。<br>'
    + code("""\
class Trie {
    private class TrieNode{
        private boolean isEnd;
        private TrieNode[] next;

        public TrieNode() {
            isEnd  = false;
            // 除了根节点外每个节点有26个分支
            next = new TrieNode[26];
        }
    }
    // root是一个空节点
    private TrieNode root;
    public Trie() {
        root = new TrieNode();
    }

    public void insert(String word) {
        TrieNode cur = root;
        for(char ch : word.toCharArray()){
            if(cur.next[ch - 'a'] == null)
                cur.next[ch - 'a'] = new TrieNode();
            cur = cur.next[ch - 'a'];
        }
        // 循环后将结尾的结束标识设置为true
        cur.isEnd = true;
    }

    public boolean search(String word) {
        TrieNode cur = root;
        for(char ch : word.toCharArray()){
            cur = cur.next[ch - 'a'];
            if(cur == null)
                return false;
        }
        return cur.isEnd;
    }

    public boolean startsWith(String prefix) {
        TrieNode cur = root;
        for(char ch : prefix.toCharArray()){
            cur = cur.next[ch - 'a'];
            if(cur == null)
                return false;
        }
        return true;
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    'Trie 本质：用树形结构共享公共前缀，每个节点代表一个字符。<br>'
    'search 与 startsWith 的区别：search 检查 isEnd，startsWith 不检查。<br>'
    '注意：先插入 "apple" 后 search("app") 返回 false，因为 \'p\' 节点的 isEnd 没有被设置。<br>'
    '扩展：除了 26 个字母，也可用 HashMap 存储子节点以支持 Unicode。')

# ============================================================
# 4. 常数时间插入、删除和获取随机元素
# ============================================================
p = '常数时间插入、删除和获取随机元素'
d = make_deck(1747301704, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '实现 RandomizedSet 类：insert(int val) 插入（已存在返回 false），'
    'remove(int val) 删除（不存在返回 false），getRandom() 随机返回集合中的一个元素。<br>'
    '要求：所有操作平均 O(1) 时间复杂度，不允许重复元素。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：insert/remove/getRandom 均为 {{c1::O(1)}}<br>空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(HashMap+数组)'),
    'HashMap(val→index) + 数组存值，删除时用末尾元素覆盖要删除的位置。<br>'
    + code("""\
class RandomizedSet {
    static int[] nums;
    Random random;
    Map&lt;Integer, Integer&gt; map;
    int index;

    public RandomizedSet(){
        nums = new int[200010];
        random = new Random();
        map = new HashMap&lt;&gt;();
        index = -1;
    }

    public boolean insert(int val) {
        if (map.containsKey(val))
            return false;
        nums[++index] = val;
        map.put(val, index);
        return true;
    }

    public boolean remove(int val) {
        if (!map.containsKey(val))
            return false;
        // 返回删除元素对应索引位置
        int loc = map.remove(val);
        // 下面两步就是在修改映射关系和将被删除元素的值用后一个值给覆盖
        if (loc != index)
            map.put(nums[index], loc);
        nums[loc] = nums[index--];
        return true;
    }

    public int getRandom() {
        return nums[random.nextInt(index + 1)];
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    '核心：HashMap 存值→索引实现 O(1) 查找，ArrayList 存值实现 O(1) 随机访问。<br>'
    '删除技巧：先交换（用最后一个元素覆盖要删除的位置），再删除末尾。<br>'
    '注意：删除时要同时更新 map 中 lastVal 的索引映射。<br>'
    '不允许重复元素：插入前用 map.containsKey 检查。')

# ============================================================
# 5. 设计循环队列
# ============================================================
p = '设计循环队列'
d = make_deck(1747301705, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '设计一个循环队列实现 MyCircularQueue 类：MyCircularQueue(k) 初始化大小为 k，'
    'enQueue(value) 入队，deQueue() 出队，Front() 获取队首，Rear() 获取队尾，'
    'isEmpty() 判断空，isFull() 判断满。<br>'
    '要求：使用数组实现，利用取模运算实现循环。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：所有操作均为 {{c1::O(1)}}<br>空间：{{c2::O(k)}}（k 为队列容量）')

add_basic(d, make_front(p, '题解(数组实现)'),
    'front 是写入指针，rear 是读取指针，用 front%size 做索引映射。<br>'
    + code("""\
class MyCircularQueue {
    int[] items;
    int front;  // 前进指针
    int rear;   // 末端指针
    int size;   // 需要的数组长度

    public MyCircularQueue(int k) {
        items = new int[k];
        front = 0;
        rear = 0;
        size = k;
    }

    public boolean enQueue(int value) {
        if(front - rear == size)    // 如果前进指针到达最后一个位置，末尾指针还在起点就说明装满了
            return false;
        // 循环在数组中添加
        items[front % size] = value;
        front++;
        return true;
    }

    public boolean deQueue() {
        if(front == rear)   // 说明没有元素
            return false;
        rear++;
        return true;
    }

    public int Front() {
        // 注意这里返回是末端的指针，是因为数组的存放顺序是不满足队列的先进先出
        return front == rear ? -1 : items[rear % size];
    }

    public int Rear() {
        // 之所以-1，是因为最后添加成功front会+1
        if(front % size == 0)
            return front == rear ? -1 : items[size-1];
        return front == rear ? -1 : items[(front % size) - 1];
    }

    public boolean isEmpty() {
        return front == rear;
    }

    public boolean isFull() {
        return size == front - rear;
    }
}"""))

add_basic(d, make_front(p, '题解(链表实现)'),
    '头插法入队，尾部出队，count 计数判空/判满。<br>'
    + code("""\
class MyCircularQueue {
    private class Node{
        int val;
        Node next, prev;
        Node(){}
        Node(int val){
            this.val = val;
        }
        Node(int val, Node next, Node prev){
            this.val = val;
            this.next = next;
            this.prev = prev;
        }
    }

    Node head, tail;    // 头节点和尾节点
    int size, count;
    public MyCircularQueue(int k) {
        head = new Node();  // 头节点
        tail = new Node();
        head.next = tail;
        tail.prev = head;
        this.size = k;
        count = 0;
    }
    // 头插法
    public boolean enQueue(int value) {
        if(count == size)
            return false;
        Node node = new Node(value);
        Node temp = head.next;
        node.next = temp;
        head.next = node;
        temp.prev = node;
        node.prev = head;
        count++;
        return true;
    }
    // 我们采取将尾部的节点删除，也就是对头的节点
    public boolean deQueue() {
        if(count == 0)
            return false;
        tail.prev = tail.prev.prev;
        tail.prev.next = tail;
        count--;
        return true;
    }
    // 这里注意我们采用头插法，那么对头就是尾部的前一个
    public int Front() {
        return count == 0 ? -1 : tail.prev.val;
    }

    public int Rear() {
        return count == 0 ? -1 : head.next.val;
    }

    public boolean isEmpty() {
        return count == 0;
    }

    public boolean isFull() {
        return count == size;
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    '数组实现：front 累计写入次数，rear 累计读取次数，用 % size 做索引映射。<br>'
    '判空：front == rear（写入等于读取，无数据）。<br>'
    '判满：front - rear == size（写入领先读取一个完整周期）。<br>'
    '链表实现（另一种思路）：头插法入队，尾部出队，用 count 计数判空/判满，更直观但空间开销略大。')

# ============================================================
# 6. 设计哈希映射
# ============================================================
p = '设计哈希映射'
d = make_deck(1747301706, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '设计一个哈希映射 MyHashMap 类（不使用内置 HashMap）：MyHashMap() 初始化，'
    'put(int key, int value) 插入或更新，get(int key) 获取值，remove(int key) 删除映射。<br>'
    '要求：使用数组分桶 + 链表解决冲突。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：平均 {{c1::O(1)}}，最坏 {{c2::O(n)}}（所有 key 冲突在同一桶）<br>'
    '空间：{{c3::O(n + BASE)}}（n 个元素 + BASE 个桶）')

add_basic(d, make_front(p, '题解(数组分桶+链表)'),
    'BASE 取质数 769 用除留余数法，桶内用 LinkedList 处理冲突（链地址法）。<br>'
    + code("""\
class MyHashMap {
    private class Node{
        int val;
        int key;
        Node next;
        Node(int x, int y){
            val = y;
            key = x;
        }
    }

    private static final int BASE = 769;
    // 设置桶，根据key算出索引值
    LinkedList[] buckets;
    public MyHashMap() {
        buckets = new LinkedList[BASE];
        for(int i = 0; i &lt; BASE; i++){
            buckets[i] = new LinkedList&lt;Node&gt;();
        }
    }

    public void put(int key, int value) {
        int hash = hash(key);
        List&lt;Node&gt; nodes = buckets[hash];
        for(Node node : nodes){
            if(node.key == key){
                node.val = value;
                return;
            }
        }
        // 尾插法
        buckets[hash].offerLast(new Node(key, value));
    }

    public int get(int key) {
        int hash = hash(key);
        List&lt;Node&gt; nodes = buckets[hash];
        for(Node node : nodes){
            if(node.key == key){
                return node.val;
            }
        }
        return -1;
    }

    public void remove(int key) {
        int hash = hash(key);
        List&lt;Node&gt; nodes = buckets[hash];
        for(Node node : nodes){
            if(node.key == key){
                buckets[hash].remove(node);
                return;
            }
        }
    }

    public int hash(int key){
        // 这是哈希函数构造四种方法中的除留余数法
        return key % BASE;
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    '哈希函数设计：除留余数法 key % BASE，BASE 选质数（如 769）以减少冲突。<br>'
    '冲突解决：链地址法 — 每个桶是一个链表，冲突的 key 追加到链表末尾。<br>'
    '关键操作：遍历桶内链表时需同时检查 key 是否相等，相等则更新值或删除。<br>'
    '为什么 BASE 用质数：可减少因 key 分布规律引起的哈希冲突。')

# ============================================================
# 7. 实现 strStr()
# ============================================================
p = '实现 strStr()'
d = make_deck(1747301707, f'算法::设计类::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个字符串 haystack 和 needle，在 haystack 中找出 needle 出现的第一个位置（从 0 开始）。'
    '如果不存在，返回 -1。实现 KMP 算法达到 O(m+n) 时间复杂度。')
add_cloze(d, make_front(p, '复杂度'),
    'KMP：时间 {{c1::O(m+n)}}，空间 {{c2::O(m)}}（next 数组）<br>'
    '暴力法：时间 {{c3::O(m*n)}}，空间 {{c4::O(1)}}')

add_basic(d, make_front(p, '题解(暴力法)'),
    '逐位匹配，不匹配时回溯目标串指针。<br>'
    + code("""\
class Solution {
    public int strStr(String haystack, String needle) {
        if(needle == null)
            return 0;
        int n = haystack.length(), m = needle.length();
        char[] target = haystack.toCharArray(), pattern = needle.toCharArray();
        for(int i = 0; i &lt;= n - m; i++){
            // 前者就是目标串的指针，当前匹配逐个向后遍历，如果当前不匹配换出发点
            // 后者是模式串的指针，不匹配会被下一轮重置为0
            int begin = i, reStart = 0;
            while(reStart &lt; m && target[begin] == pattern[reStart]){
                begin++;
                reStart++;
            }
            // 如果能够完全匹配，返回原串的「发起点」下标
            if(reStart == m)
                return i;
        }
        return -1;
    }
}"""))

add_basic(d, make_front(p, '题解(KMP)'),
    '构建 next 数组实现 O(m+n)，失配时目标串指针不回溯，只回退模式串指针。<br>'
    + code("""\
class Solution {
    public int strStr(String target, String pattern) {
        if(pattern == null)
            return 0;
        int n = target.length(), m = pattern.length();

        // 原串和匹配串前面都加空格，使其下标从 1 开始
        target = " " + target;
        pattern = " " + pattern;
        char[] targets = target.toCharArray(), patterns = pattern.toCharArray();

        // 构建next数组，指明当前模式串与目标串不匹配，模式串回溯到哪个索引继续匹配
        int[] next = new int[m+1];
        // 构造过程 i = 2，j = 0 开始，i 小于等于匹配串长度 【构造 i 从 2 开始】
        for(int i = 2, j = 0; i &lt;= m; i++){
            // 匹配不成功的话，j = next(j)
            while (j &gt; 0 && patterns[i] != patterns[j + 1])
                j = next[j];
            // 匹配成功的话，先让 j++
            if (patterns[i] == patterns[j + 1])
                j++;
            // 更新 next[i]，结束本次循环，i++
            next[i] = j;
        }
        // 匹配过程，i = 1，j = 0 开始，i 小于等于原串长度 【匹配 i 从 1 开始】
        for(int i = 1, j = 0; i &lt;= n; i++){
            // 匹配不成功 j = next(j)
            while (j &gt; 0 && targets[i] != patterns[j + 1])
                j = next[j];
            // 匹配成功的话，先让 j++，结束本次循环后 i++
            if (targets[i] == patterns[j + 1])
                j++;
            // 整一段匹配成功，直接返回下标
            if (j == m)
                return i - m;
        }
        return -1;
    }
}"""))

add_basic(d, make_front(p, '关键技巧'),
    'KMP 核心：利用已匹配信息，匹配失败时不回溯目标串指针 i，只回退模式串指针 j。<br>'
    'next[i] 含义：pattern[0..i] 的最长相等前后缀长度，即失配时 j 应跳转到的位置。<br>'
    '技巧：字符串前加空格使下标从 1 开始，简化边界处理。<br>'
    '构建 next：i 从 2 开始（next[1]=0），匹配成功 j++，匹配失败 j=next[j]。')

if __name__ == '__main__':
    print(build('../../牌组/算法/设计类.apkg'))

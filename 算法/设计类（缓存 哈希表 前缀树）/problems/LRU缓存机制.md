# LRU缓存机制

## 题干
设计一个 LRU（最近最少使用）缓存数据结构。实现 LRUCache 类：
LRUCache(int capacity) 初始化，get(int key) 获取值（不存在返回-1），put(int key, int value) 插入或更新。
如果 key 已存在，变更其 value；key 不存在则插入。当缓存容量满时，淘汰最久未使用的 key。
要求：get 和 put 均为 O(1) 时间复杂度。

## 复杂度
时间：get — {{c1::O(1)}}，put — {{c1::O(1)}}
空间：{{c1::O(capacity)}}

## 关键技巧
核心组合：HashMap 实现 O(1) 查找 + 双向链表实现 O(1) 插入/删除。
使用虚拟头尾节点（dummy head/tail）简化边界处理。
get 时先删除再插入头部 = 更新访问时间。
put 满时删除 tail.pre（尾部前一个节点），注意同时清理 HashMap 中的映射。

## 题解(DoubleList独立类)
自定义双向链表类 + 自定义节点 + HashMap 实现 LRU。

```java
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
    private HashMap<Integer, Node> map;
    // Node(k1, v1) <-> Node(k2, v2)...
    private DoubleList cache;
    // 最大容量
    private int cap;

    public LRUCache(int capacity) {
        this.cap = capacity;
        cache = new DoubleList();
        map = new HashMap<>();
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
}
```

## 题解(双向链表合并在Node中)
节点自带双向链表指针，虚拟头尾节点简化边界。

```java
public class LRUCache {

    /**
     * 容量
     */
    private int capacity;

    /**
     * 存储缓存
     */
    private Map<Integer, Node<Integer, Integer>> map;

    /**
     * 虚拟头结点
     */
    private Node<Integer, Integer> head;

    /**
     * 虚拟尾结点
     */
    private Node<Integer, Integer> tail;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        map = new HashMap<>((int)(capacity / 0.75 + 1), 0.75f);
        head = new Node<>();
        tail = new Node<>();
        head.next = tail;
        tail.pre = head;
    }

    public int get(int key) {
        Node<Integer, Integer> node = map.get(key);
        if (node == null) {
            return -1;
        }
        deleteNode(node);
        addToTail(node);
        return node.value;
    }

    public void put(int key, int value) {
        Node<Integer, Integer> node = map.get(key);
        if (node != null) {
            deleteNode(node);
        }
        node = new Node<>(key, value);
        addToTail(node);
        map.put(key, node);
        if (map.size() > capacity) {
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

    private static class Node<k, v> {
        k key;
        v value;
        Node<k, v> next;
        Node<k, v> pre;

        public Node() {
        }

        public Node(k key, v value) {
            this.key = key;
            this.value = value;
            next = null;
            pre = null;
        }
    }
}
```

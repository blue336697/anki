# LFU缓存

## 题干
设计一个 LFU（最不经常使用）缓存数据结构。实现 LFUCache 类：
LFUCache(int capacity) 初始化，get(int key) 获取值，put(int key, int value) 插入或更新。
淘汰策略：当缓存满时，移除使用频率最低的 key；若频率相同，淘汰其中最久未使用的。
要求：get 和 put 均为 O(1) 时间复杂度。
![image.png](image.png)

## 复杂度
时间：get — {{c1::O(1)}}，put — {{c1::O(1)}}
空间：{{c1::O(capacity)}}

## 关键技巧
数据结构：HashMap 存 key→Node + 按频次串联的多个双向链表。
频次链表链：firstLinkedList ↔ freq=3 ↔ freq=2 ↔ freq=1 ↔ lastLinkedList（最小频次靠近 last）。
淘汰时从 lastLinkedList.pre 的尾部移除（频率最低且最久未用）。
每个 Node 持有所在链表的引用（doublyLinkedList 字段），便于 O(1) 定位。

## 题解(频次双向链表链)
HashMap(key→Node) + 按频次串联的双向链表链，淘汰最小频次的最久未用节点。

```java
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
    Map<Integer, Node> cache;
    DoublyLinkedList firstLinkedList;
    // firstLinkedList.next 是频次最大的双向链表

    DoublyLinkedList lastLinkedList;
    // lastLinkedList.pre 是频次最小的双向链表，满了之后删除 lastLinkedList.pre.tail.pre 即为频次最小且访问最早的Node

    int size;

    public LFUCache(int capacity) {
        this.capacity = capacity;
        cache = new HashMap<>(capacity);
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

  DoublyLinkedList pre;  // 该双向链表的前继链表（pre.freq < this.freq）

  DoublyLinkedList next; // 该双向链表的后继链表 (next.freq > this.freq)

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

}
```

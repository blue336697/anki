# 环形链表 II

## 题干
给定一个链表，返回链表开始入环的第一个节点。如果链表无环，则返回 null。

## 指针策略
1. 快慢指针相遇于环内某点
2. {{c1::头结点}}和{{c1::相遇点}}各放一个指针，每次各走一步
3. {{c1::再次相遇点}}即为环入口
数学证明：头到入口=a，入口到相遇=b，相遇到入口=c，则 a=c(mod n)

## 复杂度
时间：{{c1::O(n)}} — 两次遍历
空间：{{c1::O(1)}}

## 题解(快慢指针+数学)
相遇点+头结点各走一步，再次相遇即为环入口。数学原理：a = c (mod n)。
```java
public class Solution {
    public ListNode detectCycle(ListNode head) {
        if(head == null || head.next == null)
            return null;
        ListNode fast = head;
        ListNode slow = head;
        do{
            fast = fast.next.next;
            slow = slow.next;
            if(slow == fast){
                ListNode index1 = fast;
                ListNode index2 = head;
                while(index1 != index2){
                    index1 = index1.next;
                    index2 = index2.next;
                }
                return index1;
            }
        }while(fast != null && fast.next != null);
        return null;
    }
}
```

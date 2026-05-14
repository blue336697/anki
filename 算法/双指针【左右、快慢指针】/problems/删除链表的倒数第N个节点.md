# 删除链表的倒数第N个节点

## 题干
给定一个链表，删除链表的倒数第 n 个节点，并且返回链表的头结点。

## 指针策略

> 前后指针：preNode 先走 n 步，然后一起走直到 preNode.next == null。
preNode走n步后为null → 删除头结点。注意：提前一个结点结束（while条件为preNode.next != null），使resNode停在删除节点的前一个。

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(1)}}

## 题解(前后指针)
preNode先走n步，然后一起走，resNode.next = resNode.next.next 完成删除。
```java
class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode preNode = head, resNode = head;
        for(int i = 0; i < n; i++)
            preNode = preNode.next;
        if(preNode == null)
            return head.next;
        while(preNode.next != null){
            preNode = preNode.next;
            resNode = resNode.next;
        }
        resNode.next = resNode.next.next;
        return head;
    }
}
```

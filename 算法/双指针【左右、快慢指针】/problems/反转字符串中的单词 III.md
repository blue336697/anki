# 反转字符串中的单词 III

## 题干
给定一个字符串，你需要反转字符串中每个单词的字符顺序，同时仍保留空格和单词的初始顺序。

## 指针策略
start={{c1::每个单词的起始位置}}，end={{c1::前进指针找空格}}
end 找到空格后 → {{c1::reverse(s, start, end-1)}}
然后 {{c1::start = ++end}}，继续找下一个单词

## 复杂度
时间：{{c1::O(n)}} — 每个字符处理一次
空间：{{c1::O(1)}} — 原地操作

## 题解(双指针)
外层end找空格分割单词，内层对撞指针反转每个单词。
```java
class Solution {
    public String reverseWords(String str) {
        if(str == null)
            return "";
        char[] s = str.toCharArray();
        int start = 0, end = 0;
        while(end < s.length){
            while(end < s.length && s[end] != ' ')
                end++;
            reverse(s, start, end - 1);
            end++;
            start = end;
        }
        return new String(s);
    }

    public void reverse(char[] s, int i, int j){
        char temp;
        while(i < j){
            temp = s[i];
            s[i] = s[j];
            s[j] = temp;
            i++;
            j--;
        }
    }
}
```

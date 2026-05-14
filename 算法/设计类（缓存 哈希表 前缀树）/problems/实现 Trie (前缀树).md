# 实现 Trie (前缀树)

## 题干
实现 Trie（前缀树）类：Trie() 初始化，insert(String word) 插入单词，search(String word) 查找单词是否存在，startsWith(String prefix) 检查是否有以此前缀开头的单词。
![image 1.png](image%201.png)

## 复杂度
时间：insert/search/startsWith 均为 {{c1::O(L)}}（L 为单词长度）
空间：{{c1::O(26*N)}}（N 为总节点数，每个节点 26 个 child 指针）

## 关键技巧
Trie 本质：用树形结构共享公共前缀，每个节点代表一个字符。
search 与 startsWith 的区别：search 检查 isEnd，startsWith 不检查。
注意：先插入 "apple" 后 search("app") 返回 false，因为 'p' 节点的 isEnd 没有被设置。
扩展：除了 26 个字母，也可用 HashMap 存储子节点以支持 Unicode。

## 题解(TrieNode+数组)
TrieNode[26] 存储子节点，ch - 'a' 映射到 0-25，isEnd 标记完整单词。

```java
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
}
```

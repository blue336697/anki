# BufferedReader 用法详解

## 基本设置
{{c1::BufferedReader + InputStreamReader}} 是 ACM 中最推荐的通用输入方案：

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
```

## 核心方法
- `readLine()` — {{c1::读取一行，返回 String（不含换行符），读到 EOF 返回 null}}
- `read()` — 读取单个字符（返回 int，EOF 返回 -1），一般不直接用
- `ready()` — 判断流是否就绪可读

## 读一行多个整数（split 方式）
```java
String[] parts = br.readLine().split(" ");
int a = Integer.parseInt(parts[0]);
int b = Integer.parseInt(parts[1]);
```

## 读一行多个整数（StringTokenizer 更快）
```java
import java.util.StringTokenizer;
StringTokenizer st = new StringTokenizer(br.readLine());
int a = Integer.parseInt(st.nextToken());
int b = Integer.parseInt(st.nextToken());
```
{{c1::StringTokenizer 比 split 快}}，因为 split 使用正则表达式，有额外开销。

## 读取数组（一行一个元素 vs 一行所有元素）
一行一个元素：
```java
int n = Integer.parseInt(br.readLine());
int[] arr = new int[n];
for (int i = 0; i < n; i++) {
    arr[i] = Integer.parseInt(br.readLine());
}
```
一行所有元素（更常见）：
```java
String[] parts = br.readLine().split(" ");
int[] arr = new int[parts.length];
for (int i = 0; i < parts.length; i++) {
    arr[i] = Integer.parseInt(parts[i]);
}
```

## 读取到 EOF（不定组数据）
```java
String line;
while ((line = br.readLine()) != null) {
    if (line.isEmpty()) continue; // 跳过空行
    int n = Integer.parseInt(line.trim());
}
```
{{c1::readLine() 返回 null 表示 EOF}}，这是判断输入结束的标准方式。

## 完整的 ACM Main 模板
```java
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            System.out.println(a + b);
        }
    }
}
```

## BufferedReader vs Scanner 关键区别
| | Scanner | BufferedReader |
|------|---------|------|
| 读一行 | nextLine() | readLine() |
| 读整数 | nextInt() | Integer.parseInt(readLine()) |
| 判断EOF | hasNext()==false | readLine()==null |
| 换行符处理 | 需手动 consume | readLine() 自动去掉 |
| 异常声明 | 无需 throws | 需 throws IOException |

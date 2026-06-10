# Scanner 用法详解

## 基本读取方法
Scanner 是最简单的输入工具，包装 `System.in`：

```java
import java.util.Scanner;
Scanner sc = new Scanner(System.in);
```

核心读取方法：
- `nextInt()` — {{c1::读取下一个整数（int）}}
- `nextLong()` — {{c2::读取下一个长整数（long）}}
- `nextDouble()` — {{c3::读取下一个浮点数（double）}}
- `next()` — {{c4::读取下一个单词（遇到空格/换行停止）}}
- `nextLine()` — {{c5::读取整行（包含空格，到换行符为止）}}

## next() vs nextLine() 的经典陷阱
{{c1::nextInt()/next() 不消耗换行符}}，紧接着的 nextLine() 会读到空行！

**错误示例**：
```java
int n = sc.nextInt();
String s = sc.nextLine(); // 读到的是 n 后面的换行符，结果是空串！
```

**正确做法**：{{c2::在 nextInt() 后多加一个 sc.nextLine() 吃掉换行符}}
```java
int n = sc.nextInt();
sc.nextLine(); // 吃掉换行符
String s = sc.nextLine(); // 正确读到下一行
```

## 循环读取直到 EOF
{{c1::while(sc.hasNext())}} 或 {{c2::while(sc.hasNextInt())}} 读取到文件末尾：
```java
while (sc.hasNext()) {
    String word = sc.next();
}
while (sc.hasNextInt()) {
    int num = sc.nextInt();
}
```

## 多组测试用例 T
先读 T，然后循环 T 次：
```java
int T = sc.nextInt();
while (T-- > 0) {
    int n = sc.nextInt();
    // solve one case
}
```

## 易错场景：混合读取数字和字符串
```java
// 输入: 3（数字）然后 "hello world"（含空格的字符串）
int n = sc.nextInt();
sc.nextLine();             // 必须吃掉换行符!!
String s = sc.nextLine();  // "hello world"
```

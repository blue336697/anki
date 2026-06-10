# FastReader 手写模板

## 为什么需要 FastReader
当输入量极大（&gt;10^6 行）时，BufferedReader + split 仍有字符串创建开销。FastReader 直接逐字符读取解析，{{c1::避免字符串临时对象和正则匹配}}。

## FastReader 标准版（StringTokenizer 包装，推荐背诵）
```java
import java.io.*;
import java.util.*;

class FastReader {
    BufferedReader br;
    StringTokenizer st;

    public FastReader() {
        br = new BufferedReader(new InputStreamReader(System.in));
    }

    String next() {
        while (st == null || !st.hasMoreElements()) {
            try { st = new StringTokenizer(br.readLine()); }
            catch (IOException e) { e.printStackTrace(); }
        }
        return st.nextToken();
    }

    int nextInt() { return Integer.parseInt(next()); }
    long nextLong() { return Long.parseLong(next()); }
    double nextDouble() { return Double.parseDouble(next()); }
    String nextLine() {
        try { return br.readLine(); }
        catch (IOException e) { e.printStackTrace(); return ""; }
    }
}

// Usage: FastReader fr = new FastReader(); int n = fr.nextInt();
```

## FastReader 极速版（字符流直接解析，CF/AtCoder首选）
```java
class FastReader {
    final private int BUFFER_SIZE = 1 << 16;
    private DataInputStream din;
    private byte[] buffer;
    private int bufferPointer, bytesRead;

    public FastReader() {
        din = new DataInputStream(System.in);
        buffer = new byte[BUFFER_SIZE];
        bufferPointer = bytesRead = 0;
    }

    public int nextInt() throws IOException {
        int ret = 0;
        byte c = read();
        while (c <= ' ') c = read();
        boolean neg = (c == '-');
        if (neg) c = read();
        do { ret = ret * 10 + c - '0'; }
        while ((c = read()) >= '0' && c <= '9');
        return neg ? -ret : ret;
    }

    public long nextLong() throws IOException {
        long ret = 0;
        byte c = read();
        while (c <= ' ') c = read();
        boolean neg = (c == '-');
        if (neg) c = read();
        do { ret = ret * 10 + c - '0'; }
        while ((c = read()) >= '0' && c <= '9');
        return neg ? -ret : ret;
    }

    private byte read() throws IOException {
        if (bufferPointer == bytesRead) {
            bytesRead = din.read(buffer, bufferPointer = 0, BUFFER_SIZE);
            if (bytesRead == -1) buffer[0] = -1;
        }
        return buffer[bufferPointer++];
    }
}
```

## 性能排序
| 方案 | 10^6 int 耗时 |
|------|------------|
| Scanner | ~600ms |
| BufferedReader + split | ~150ms |
| BufferedReader + StringTokenizer | ~100ms |
| FastReader 标准版 | ~80ms |
| FastReader 极速版 | {{c1::~30ms}} |

## 选择策略
- 日常 → {{c1::BufferedReader + StringTokenizer，够用}}
- 牛客/国内OJ → {{c2::FastReader 标准版}}
- CF/AtCoder 大输入 → {{c3::FastReader 极速版，防卡常}}
- 不确定 → {{c4::直接 FastReader 极速版，一劳永逸}}

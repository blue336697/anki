"""Build APKG for ACM I/O patterns — complete reference deck."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    return f'<pre><code class="language-java">{java}</code></pre>'


# ============================================================
# Deck 0: 总览
# ============================================================
d0 = make_deck(1747302300, '算法::ACM模式::总览')
add_basic(d0, 'ACM 模式 Java I/O 全景',
    'ACM模式下Java输入输出核心三件套：<br>'
    '<b>输入</b>：Scanner（简单慢）/ BufferedReader（推荐）/ FastReader（极限性能）<br>'
    '<b>输出</b>：System.out（简单）/ StringBuilder（批量）/ PrintWriter（最快）<br>'
    '<b>关键原则</b>：System.in/out 不能关；Scanner包裹了System.in则close会连带关；printWriter必须flush()')
add_cloze(d0,
    'ACM I/O 选型速查：<br>'
    '数据量 &lt;10^4 → {{c1::Scanner}}<br>'
    '数据量 10^4~10^5 → {{c2::BufferedReader + split/StringTokenizer}}<br>'
    '数据量 &gt;10^5 → {{c3::FastReader 极速版}}<br>'
    '输出 &gt;1000 行 → {{c4::StringBuilder 或 PrintWriter}}',
    '根据数据规模选择合适的工具')
add_cloze(d0,
    '最容易犯的 3 个错误：<br>'
    '1. {{c1::nextInt() 后直接 nextLine() 读到空串}} — 多加一个 sc.nextLine()<br>'
    '2. {{c2::System.in 被 Scanner.close() 关掉}} — 其它读取全失效<br>'
    '3. {{c3::PrintWriter 忘记 flush()}} — 最后一块输出丢失',
    'ACM必知必会的三大陷阱')

# ============================================================
# Deck 1: 输入工具选择与对比
# ============================================================
d = make_deck(1747302301, '算法::ACM模式::输入工具选择与对比')
add_basic(d, '三种工具的适用场景',
    '<table>'
    '<tr><th>方案</th><th>性能</th><th>易用性</th><th>场景</th></tr>'
    '<tr><td>Scanner</td><td>最慢</td><td>最简单</td><td>数据量&lt;10^4</td></tr>'
    '<tr><td>BufferedReader+split</td><td>快</td><td>适中</td><td>绝大多数题</td></tr>'
    '<tr><td>BufferedReader+StringTokenizer</td><td>更快</td><td>稍复杂</td><td>大量整数</td></tr>'
    '<tr><td>FastReader手写</td><td>最快</td><td>需自定义</td><td>&gt;10^6大量输入</td></tr>'
    '</table>')
add_cloze(d,
    '选择决策树：<br>'
    '练习/验证 → {{c1::Scanner}}<br>'
    '正式比赛 10^4~10^5 → {{c2::BufferedReader + split}}<br>'
    '极大数据 &gt;10^6 → {{c3::FastReader}}<br>'
    '纯数字输入可选 {{c4::StringTokenizer}} 比 split 更快',
    '根据场景选择输入方案')
add_basic(d, '为什么 Scanner 慢而 BufferedReader 快',
    '<b>Scanner 慢的原因</b>：<br>'
    '1. 内部大量正则匹配和类型解析<br>'
    '2. nextInt() 做完整数字解析和格式校验<br>'
    '3. 缓冲区小（默认1024字符），频繁读取<br>'
    '<b>BufferedReader 快的原因</b>：<br>'
    '1. 直接读字符流，缓冲区大（默认8192字符）<br>'
    '2. readLine() 一次读整行，减少IO调用<br>'
    '3. 不自动做类型解析')

# ============================================================
# Deck 2: Scanner 用法详解
# ============================================================
d = make_deck(1747302302, '算法::ACM模式::Scanner用法详解')
add_cloze(d, 'Scanner 核心方法',
    '{{c1::nextInt()}} — 读取int<br>'
    '{{c2::nextLong()}} — 读取long<br>'
    '{{c3::nextDouble()}} — 读取double<br>'
    '{{c4::next()}} — 读单词（遇空格/换行停）<br>'
    '{{c5::nextLine()}} — 读整行（含空格）',
    '五大核心读取方法')
add_cloze(d, 'next() vs nextLine() 经典陷阱',
    '问题：{{c1::nextInt()/next() 不消耗换行符}}<br>'
    '后果：紧接着 nextLine() 读到空行<br>'
    '修复：{{c2::在 nextInt() 后多加一个 sc.nextLine() 吃掉换行符}}<br>'
    '代码：int n = sc.nextInt(); sc.nextLine(); // 关键!')
add_cloze(d, 'Scanner 读取到 EOF',
    '{{c1::while(sc.hasNext())}} — 读到文件末尾<br>'
    '{{c2::while(sc.hasNextInt())}} — 还有整数可读<br>'
    'hasNextLine() — 还有下一行<br>'
    '多组测试用例：{{c3::int T=sc.nextInt(); while(T-- > 0)}}')
add_basic(d, 'Scanner 完整 Demo',
    '读取 T 组测试用例，每组一行含空格字符串，解析求和。<br>'
    + code(
'''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();
        sc.nextLine(); // consume newline
        while (T-- > 0) {
            String line = sc.nextLine();
            String[] parts = line.split(" ");
            int a = Integer.parseInt(parts[0]);
            int b = Integer.parseInt(parts[1]);
            System.out.println(a + b);
        }
        sc.close();
    }
}'''))

# ============================================================
# Deck 3: BufferedReader 用法详解
# ============================================================
d = make_deck(1747302303, '算法::ACM模式::BufferedReader用法详解')
add_cloze(d, 'BufferedReader 基本设置',
    '构造：{{c1::new BufferedReader(new InputStreamReader(System.in))}}<br>'
    '读一行：{{c2::readLine()}} — 返回String不含换行，EOF返回null<br>'
    '判断EOF：{{c3::while((line = br.readLine()) != null)}}<br>'
    '异常：方法签名需要 {{c4::throws IOException}}')
add_cloze(d, 'parseInt + split vs StringTokenizer',
    'split方式：String[] parts = br.readLine().split(" "); int a = Integer.parseInt(parts[0]);<br>'
    'StringTokenizer：{{c1::比 split 快}}（不用正则）<br>'
    '用法：st = new StringTokenizer(br.readLine()); int a = Integer.parseInt(st.nextToken());')
add_basic(d, '完整的 ACM Main 模板',
    'BufferReader + StringTokenizer + while(null) EOF 模式。<br>'
    + code(
'''import java.io.*;
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
}'''))
add_basic(d, 'BufferedReader vs Scanner 对比',
    '<table>'
    '<tr><th></th><th>Scanner</th><th>BufferedReader</th></tr>'
    '<tr><td>读一行</td><td>nextLine()</td><td>readLine()</td></tr>'
    '<tr><td>读整数</td><td>nextInt()</td><td>Integer.parseInt(readLine())</td></tr>'
    '<tr><td>判断EOF</td><td>hasNext()==false</td><td>readLine()==null</td></tr>'
    '<tr><td>换行符</td><td>需手动consume</td><td>自动去掉</td></tr>'
    '<tr><td>异常</td><td>无需throws</td><td>需throws IOException</td></tr>'
    '</table>')

# ============================================================
# Deck 4: 常见输入格式模板
# ============================================================
d = make_deck(1747302304, '算法::ACM模式::常见输入格式模板')
add_cloze(d, '格式速查：判断方式',
    '固定 T 组 → {{c1::int T=read(); while(T-- > 0)}}<br>'
    '读到 EOF → {{c2::while((line=readLine()) != null)}}<br>'
    '单行不定长 → {{c3::split("\\\\\\\\s+") 或 StringTokenizer}}<br>'
    '数字+长字符串 → {{c4::split(" ", 2) 限制split次数}}<br>'
    '矩阵 → {{c5::双重循环 + StringTokenizer}}<br>'
    '图 → {{c6::读n,m → 循环m行 → 邻接表}}',
    '6种常见输入格式速查')
add_basic(d, '格式1-3：单行值 / EOF / T组固定结构',
    '<b>单行+数组</b>：int n=parseInt(readLine()); arr[i]=parseInt(parts[i])<br>'
    '<b>多组EOF</b>：while((line=readLine())!=null) { split + parse }<br>'
    '<b>T组固定</b>：int T=parseInt(readLine()); while(T-->0) { 读n; 循环n行 }')
add_basic(d, '格式4-6：T组多行 / 矩阵 / 图',
    '<b>T组每组两行</b>：每轮先读n,m → StringTokenizer解析 → 再读m个数<br>'
    '<b>矩阵</b>：读n,m → 双重循环 + StringTokenizer → matrix[i][j]<br>'
    '<b>图</b>：读n,m → List&lt;Integer&gt;[] graph = new ArrayList[n+1] → 循环m行建边<br>'
    '注意：图常用1-indexed，分配n+1空间')
add_basic(d, '格式7-9：字符串 / 混合类型 / 不定长',
    '<b>字符串数组</b>：for(i=0;i&lt;n;i++) strs[i] = readLine();<br>'
    '<b>数字+长字符串</b>：split(" ", 2) → parts[0]是数字, parts[1]是剩余字符串<br>'
    '<b>不定长一行</b>：split("\\\\s+")处理多空格，parts.length即元素数')
add_basic(d, '跳过空行与注释',
    '空行：if(line.isEmpty()) continue;<br>'
    'trim：防止首尾空格影响解析<br>'
    '注释行跳过：if(line.startsWith("#")) continue;<br>'
    '多空格统一：trim().split("\\\\s+")')

# ============================================================
# Deck 5: 输出与流关闭
# ============================================================
d = make_deck(1747302305, '算法::ACM模式::输出与流关闭')
add_cloze(d, '三种输出方式',
    '少量输出(&lt;100行) → {{c1::System.out.println()}}<br>'
    '中量输出(100~10000) → {{c2::StringBuilder + System.out.print}}<br>'
    '大量输出(&gt;10000) → {{c3::PrintWriter 缓冲输出 + flush()}}',
    '选择合适的输出方式')
add_cloze(d, '流关闭五大铁律',
    '1. {{c1::System.in 绝对不能 close()}} — 全局流<br>'
    '2. {{c2::System.out 绝对不能 close()}} — 全局流<br>'
    '3. {{c3::Scanner 包裹 System.in → close 会连带关闭 System.in}}<br>'
    '4. {{c4::PrintWriter 必须 flush() 再 close()}}<br>'
    '5. {{c5::BufferedReader 可以不关（JVM自动回收）}}',
    '必须记住的五条规则')
add_cloze(d, 'PrintWriter 用法',
    '构造：new PrintWriter(new OutputStreamWriter(System.out))<br>'
    '打印：pw.println(x)<br>'
    '关键：{{c1::最后必须 pw.flush()！}} 否则输出丢失<br>'
    '带大小：new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)), 65536)')
add_basic(d, 'try-with-resources 标准模板',
    '最优雅的关闭方式，自动管理资源。<br>'
    + code(
'''try (BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
     PrintWriter pw = new PrintWriter(new OutputStreamWriter(System.out))) {
    String line;
    while ((line = br.readLine()) != null) {
        pw.println(solve(Integer.parseInt(line.trim())));
    }
    pw.flush(); // MUST flush inside try block
} catch (IOException e) {
    e.printStackTrace();
}'''))
add_basic(d, '常见输出坑',
    '1. flush() 忘记 → 输出尾端截断<br>'
    '2. Scanner close → System.in 关 → 所有读取报 NoSuchElementException<br>'
    '3. try-with-resources 中 flush 写在 try 块末尾（不能在finally）<br>'
    '4. 同时用 System.out 和 PrintWriter → 输出顺序可能乱<br>'
    '5. StringBuilder 用 \\\\n 不用 System.lineSeparator() → OJ跨平台一致')

# ============================================================
# Deck 6: FastReader 手写模板
# ============================================================
d = make_deck(1747302306, '算法::ACM模式::FastReader手写模板')
add_cloze(d, 'FastReader 两个版本选择',
    '日常练习 + 国内OJ → {{c1::FastReader 标准版（StringTokenizer包装）}}<br>'
    'CF / AtCoder 大输入 → {{c2::FastReader 极速版（字符流直接解析）}}<br>'
    '核心优势：{{c3::避免字符串临时对象和正则匹配开销}}')
add_basic(d, 'FastReader 标准版 (StringTokenizer)',
    '最常用版本，比 BufferedReader 方便，比 Scanner 快得多。<br>'
    + code(
'''import java.io.*;
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
}'''))
add_basic(d, 'FastReader 极速版 (字符流, CF/AtCoder首选)',
    '直接逐字符读入解析，~30ms 处理 10^6 个 int。<br>'
    + code(
'''class FastReader {
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
}'''))
add_basic(d, '性能对比表',
    '<table>'
    '<tr><th>方案</th><th>10^6 int 耗时</th></tr>'
    '<tr><td>Scanner</td><td>~600ms</td></tr>'
    '<tr><td>BufferedReader + split</td><td>~150ms</td></tr>'
    '<tr><td>BufferedReader + StringTokenizer</td><td>~100ms</td></tr>'
    '<tr><td>FastReader 标准版</td><td>~80ms</td></tr>'
    '<tr><td>FastReader 极速版</td><td>~30ms</td></tr>'
    '</table><br>'
    '建议：日常用 BufferedReader+StringTokenizer，大赛直接 FastReader 极速版。')

if __name__ == '__main__':
    print(build('../../牌组/算法/ACM模式.apkg'))

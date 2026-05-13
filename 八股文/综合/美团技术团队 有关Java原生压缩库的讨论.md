# 美团技术团队 | 有关Java原生压缩库的讨论

type: Post
status: Published
date: 2023/11/30
summary: 有关Java原生压缩库的讨论
tags: Java
category: 技术分享

# **有关Java原生压缩库的讨论**

### **1.压缩历史的发展**

- 上个世纪50～80年代，香农创立信息论为以后压缩技术打下基础，并出现以哈夫曼算法、LZ算法等
- 90年代公开数据压缩算法**deflate**（Huffman 与 LZ77 的组合算法）的所有技术参数。随后公开基于**deflate算法**而来的压缩格式zip和unzip。有过两年后推送解压缩工具gzip(GUN zip)

> 通常 gzip 会与归档工具 tar 结合使用来生成压缩的归档格式，文件扩展名为 .tar.gz。
> 
- 在90年代中期推出压缩库：zlib，此后随着 zip、gzip 工具及 zlib 库的广泛应用，DEFLATE 成为互联网时代数据压缩格式的事实标准。

![](https://p0.meituan.net/travelcube/03c34b25d5d6f954acb518a6b7bc7ccb202011.png)

- 时至今日，各大互联网公司推出自己的算法及实现，例如google的snappy，有压缩率低，压缩速度快的特点

### **2.Java原生压缩库与第三方库的使用区别**

如下图可以看到调用链中都有JNI（Java Native Interface）的出现，即调用非Java代码编写的一些函数，然后是调用各自的库函数进行解压缩。

![](https://p0.meituan.net/travelcube/56a7f72f3799cb5491e64fb310fc64bf393268.png)

在Java中可以使用zip或者gzip来解压缩，下面给出zip的示例，而gzip则是接收文件流时声明的对象为GZIPOutputStream，其余则一致

**zip** 

```java
public class ZipUtil {
    //压缩
    public void compress(File file, File zipFile) {
        byte[] buffer = new byte[1024];
        try {
            InputStream     input  = new FileInputStream(file);
            ZipOutputStream zipOut = new ZipOutputStream(new FileOutputStream(zipFile));
            zipOut.putNextEntry(new ZipEntry(file.getName()));
            int length = 0;
            while ((length = input.read(buffer)) != -1) {
                zipOut.write(buffer, 0, length);
            }
            input.close();
            zipOut.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
 
  //解压缩
    public void uncompress(File file, File outFile) {
        byte[] buffer = new byte[1024];
        try {
            ZipInputStream input  = new ZipInputStream(new FileInputStream(file));
            OutputStream   output = new FileOutputStream(outFile);
            if (!outFile.getParentFile().exists()) {
                outFile.getParentFile().mkdir();
            }
            if (!outFile.exists()) {
                outFile.createNewFile();
            }
 
            int length = 0;
            while ((length = input.read(buffer)) != -1) {
                output.write(buffer, 0, length);
            }
            input.close();
            output.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

还可以使用第三方库例如Snappy

**Snappy** 

```java
public class SnappyDemo {
    public static void main(String[] args) {
        String input = "Hello snappy-java! Snappy-java is a JNI-based wrapper of "
                + "Snappy, a fast compresser/decompresser.";
        byte[] compressed = new byte[0];
        try {
            compressed = Snappy.compress(input.getBytes("UTF-8"));
            byte[] uncompressed = Snappy.uncompress(compressed);
            String result = new String(uncompressed, "UTF-8");
            System.out.println(result);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

总结：JDK默认使用的是zlib库，在使用解压缩时库与库的对应要遵循一致，尽管压缩格式和算法一样也有可能出现兼容性问题；其次由于JDK需要考虑向下兼容，在每次升级JDK时并没有考虑zlib这个已经很规范很通用的库的改造升级，所以在7、8版本中解压缩的速度和压缩比几乎一样

### **3.总结**

由于原声的zlib的效率其实比不上主流的压缩效率和压缩比，所以解决方案主要有两个

- 使用第三方库进行解压缩
- 在原生zlib的基础上进行优化改造，例如同样使用 deflate 算法的压缩库有[Intel ISA-L](https://github.com/intel/isa-l)、[Intel IPP](https://www.intel.com/content/www/us/en/developer/tools/oneapi/ipp.html)、[Zopfli](https://github.com/google/zopfli)，或者直接基于 zlib 源码优化的项目有 [zlib-cloudflare](https://aws.amazon.com/cn/blogs/opensource/improving-zlib-cloudflare-and-comparing-performance-with-other-zlib-forks/)；如果使用前者在处理流程中相当于把原先使用deflate的地方换成改造后的deflate方法

主流上评判解压缩效率的测试集合：[测试集](https://sun.aei.polsl.pl//~sdeor/index.php?page=silesia)

无损压缩：利用数据的统计冗余进行压缩，常见的无损压缩编码方法有 Huffman编码，算术编码，LZ 编码（字典压缩）等。数据统计冗余度的理论限制为2:1到5:1，所以无损压缩的压缩比一般比较低。这类方法广泛应用于文本数据、程序等需要精确存储数据的压缩

有损压缩：有损压缩：利用了人类视觉、听觉对图像、声音中的某些频率成分不敏感的特性，允许压缩的过程中损失一定的信息，以此换来更大的压缩比。广泛应用于语音、图像和视频数据的压缩。 -[4] zlib：zlib 是基于 DEFLATE 算法实现的，一套完全开源、通用的无损数据压缩库。也是目前应用最广泛的压缩库。在网络传输、操作系统、图像处理等领域均有大量使用。比如：

- [Linux kernel](https://zh.m.wikipedia.org/zh-hans/Linux%E6%A0%B8%E5%BF%83)：使用zlib以实作网路协定的压缩、[档案系统](https://zh.m.wikipedia.org/wiki/%E6%AA%94%E6%A1%88%E7%B3%BB%E7%B5%B1)的压缩以及开机时解压缩自身的核心。
- libpng—：用于[PNG](https://zh.m.wikipedia.org/wiki/PNG)图形格式的一个实现，对[bitmap](https://zh.m.wikipedia.org/wiki/Bitmap)数据规定了 DEFLATE 作为流压缩方法。
- HTTP协议：使用 zlib 对 HTTP 响应头数据进行压缩/解压缩。
- [OpenSSH](https://zh.m.wikipedia.org/wiki/OpenSSH)、[OpenSSL](https://zh.m.wikipedia.org/wiki/OpenSSL)：以 zlib 达到最佳化加密网路传输。
- [Subversion](https://zh.m.wikipedia.org/wiki/Subversion)、[Git](https://zh.m.wikipedia.org/wiki/Git) 和[CVS](https://zh.m.wikipedia.org/wiki/CVS) 等[版本控制系统](https://zh.m.wikipedia.org/wiki/%E7%89%88%E6%9C%AC%E6%8E%A7%E5%88%B6)，使用 zlib 来压缩和远端仓库的通讯流量。
- [dpkg](https://zh.m.wikipedia.org/wiki/Dpkg)和[RPM](https://zh.m.wikipedia.org/wiki/RPM)等包管理软件：以 zlib 解压缩 RPM 或者其他封包。
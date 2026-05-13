# 关于Maven依赖的一些问题

type: Post
status: Published
date: 2023/10/25
summary: 关于Maven依赖的一些问题
tags: Maven
category: 技术分享

### **若使用IDEA自带的maven，则安装路径为：D:\Program Files\JetBrains\IntelliJ IDEA 2024.2.2\plugins\maven\lib\maven3**

### **依赖版本的写法**

在 Maven 中，`<version>[2.6.0-SNAPSHOT,)</version>` 这样的写法表示依赖版本的范围。这个范围从 `2.6.0-SNAPSHOT`（包含）开始，到无穷大（不包含）。

具体来说：

- `[` 和 `]` 表示范围的边界是包含的（闭区间）。
- `(` 和 `)` 表示范围的边界是不包含的（开区间）。

所以，`[2.6.0-SNAPSHOT,)` 表示的版本范围包含 `2.6.0-SNAPSHOT` 及其以上的版本。

这种写法允许你在不知道具体版本号的情况下，指定一个版本范围。当 Maven 解析依赖时，它会选择符合这个范围的最新版本。这对于快速迭代的项目来说非常有用，因为你不需要每次发布新版本时都更新你的 `pom.xml` 文件。

### **<Optional>**

在Maven中，`<optional>true</optional>`表示这个依赖是可选的。这意味着，如果其他项目依赖于你的项目，那么这个可选的依赖并不会被传递给那些依赖你的项目。

举个例子，假设你有一个项目A，它有一个可选的依赖B。然后有另一个项目C，它依赖于项目A。在这种情况下，项目C不会自动继承项目A的依赖B，除非项目C明确地声明了对B的依赖。

在给出的例子中，`lombok`被标记为可选依赖，这意味着如果其他项目依赖于项目，那么`lombok`不会被传递给那些项目，除非他们明确地声明了对`lombok`的依赖。

```java
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
```

---

### **上传maven仓库后产生的.md5和.sha1文件**

上传到Maven仓库的每个文件都会有.md5和.sha1后缀的两个文件，这是因为Maven使用这两种哈希算法（MD5和SHA-1）来验证文件的完整性。

当你下载一个文件时，Maven会计算下载的文件的MD5和SHA-1哈希值，然后将这两个值与仓库中的.md5和.sha1文件中的值进行比较。如果这两个值匹配，那么说明文件没有在传输过程中被修改或损坏。如果这两个值不匹配，那么Maven会报错，因为这可能意味着文件在传输过程中被修改或损坏。

这种机制可以提高Maven的安全性，因为它可以防止你下载到被篡改的文件。同时，它也可以提高Maven的可靠性，因为它可以检测到文件在传输过程中的错误。

### **`<repository>`和`<snapshotRepository>`**

在Maven的pom.xml文件中，`<repository>`和`<snapshotRepository>`标签都用于指定远程仓库的位置，但它们的用途有所不同：

1. **`<repository>`标签**：这个标签用于指定一个远程仓库，Maven会从这个仓库下载项目的依赖。这个仓库可以包含稳定版本（release）和快照版本（snapshot）的依赖，具体取决于仓库的配置。
2. **`<snapshotRepository>`标签**：这个标签用于指定一个快照仓库，Maven会将项目的快照版本发布到这个仓库。这个标签通常在`<distributionManagement>`标签中使用，用于配置项目的发布管理。

简单来说，`<repository>`标签用于下载依赖，而`<snapshotRepository>`标签用于发布项目的快照版本。

### **SpringBoot与maven插件依赖问题**

这几天在拉取新项目的pom文件中一直会有报错，与之相关的都是spring的maven插件，如下图。每次都会报找不到的错误，如果这个不报错，下面的去除标签同样也会报错。解决方法很简单，给这个插件加上与主springboot版本号一直的版本号标识

```java
<!-- 打可运行jar直接使用 spring-boot-maven-plugin ，并打入resources文件 -->
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <version>xxx与你主版本号一致</version>
    <executions>
        <execution>
            <goals>
                <goal>repackage</goal>
            </goals>
        </execution>
    </executions>
<plugin>
```

---

## **如何上传自己的Jar包到nexus私服**

### **1、配置用户名**

```java
<distributionManagement>
    <repository>
        <id>100credit_release</id>
        <name>100credit Release Repository</name>
        <url>http://192.168.162.106:8081/nexus/content/repositories/releases/
        </url>
    </repository>
    <snapshotRepository>
        <id>100credit_snapshots</id>
        <name>100credit Snapshot Repository</name>
        <url>http://192.168.162.106:8081/nexus/content/repositories/snapshots/
        </url>
    </snapshotRepository>
</distributionManagement>
```

---

### **2、编写自己的Jar坐标和版本**

注意：这里version的后缀不加SNAPSHOT则会上传releases仓库，反之则上传snapshots仓库

```java
<groupId>com.br.kit</groupId>
<artifactId>br-kit-springboot3</artifactId>
<version>1.0.1-SNAPSHOT</version>
<name>brkit-springboot3</name>
<description>brkit-springboot3</description>
```

---

### **3、设置maven仓库的打包插件以及源码注释上传的选项**

```java

<build>
    <plugins>
        <!--maven命令工具-->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
            <configuration>
                <source>17</source>
                <target>17</target>
                <encoding>UTF-8</encoding>
            </configuration>
        </plugin>
        <!--源码注释上传配置-->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-source-plugin</artifactId>
            <version>3.3.1</version>
            <executions>
                <execution>
                    <id>attach-sources</id>
                    <goals>
                        <goal>jar</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
    <defaultGoal>compile</defaultGoal>
</build>
```

---

### **4、执行deploy命令**

若存在单元测试，且单元测试不通过，那么需要跳过测试，命令如下：

```java
// 跳过测试执行但编译测试代码：
mvn deploy -DskipTests
//完全跳过测试编译和执行：
mvn clean deploy -Dmaven.test.skip=true
```

---

### **Could not transfer artifact [com.br](http://com.br/).encrypt:br-encrypt-starter-jdk8:pom:1.0.0 from/to maven-default-http-blocker ([http://0.0.0.0/](http://0.0.0.0/)): Blocked mirror for repositories: [100credit ([http://192.168.162.106:8081/nexus/content/groups/public/](http://192.168.162.106:8081/nexus/content/groups/public/), default, releases+snapshots)]**

[参考链接](https://blog.csdn.net/loushuai/article/details/124182904)

使用其中的第三种解决方案

```java
<mirror>
    <mirrorOf>external:http:*</mirrorOf>
    <id>100credit</id>
    <url>http://192.168.162.106:8081/nexus/content/groups/public/</url>
    <blocked>false</blocked>
</mirror>
<mirror>
    <mirrorOf>external:http:*</mirrorOf>
    <id>nexus</id>
    <url>http://192.168.162.106:8081/nexus/content/groups/public</url>
    <blocked>false</blocked>
</mirror>
```

---

后续：亲测第四种更好用

在全局的settings.xml将以下这段注释掉

`D:\Program Files\JetBrains\IntelliJ IDEA 2024.2.2\plugins\maven\lib\maven3\conf`

---

![image.png](%E5%85%B3%E4%BA%8EMaven%E4%BE%9D%E8%B5%96%E7%9A%84%E4%B8%80%E4%BA%9B%E9%97%AE%E9%A2%98/image.png)

### **Maven 错误 :The POM for com.xxx:jar:0.0.1-SNAPSHOT is invalid, transitive dependencies (if any) will not be available**

当出现类似的这种错误时，直接把本地仓库全部删除即可，然后让IDEA自己再下载一遍，本质上就是JAR包的依赖错乱，如果不通过maven查错很难查出来问题，就算使用maven查询，也会耗费大量的时间

[查错示例](https://tencentcloud.csdn.net/6566a702b94a6948d006cbb0.html)

### **当出现导包完成，但是怎么也点不进去的时候可以点这个按钮加载下**

![image.png](%E5%85%B3%E4%BA%8EMaven%E4%BE%9D%E8%B5%96%E7%9A%84%E4%B8%80%E4%BA%9B%E9%97%AE%E9%A2%98/image%201.png)
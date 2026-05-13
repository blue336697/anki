# Java虚拟机|JVM知识点汇总及简述-＞StringTable篇（总结自尚硅谷JVM课程）

type: Post
status: Published
date: 2021/09/06
summary: String的基本特性
tags: JVM
category: 虚拟机

@[TOC]

# StringTable

## 一、String的基本特性

### 1.String的概述

- String声明为final的，不可被继承
- String实现了Serializable接口:表示字符串是支持序列化的。实现了Comparable接口:表示String可以比较大小
- String:代表不可变的字符序列。简称:不可变性。

```java
String s1 = "abc";//字面量定义的方式，"abc"存储在字符串常量池中
```

- String的String Pool是一个固定大小的Hashtable，**默认值大小长度是1009**。如果放进String Pool的String非常多，就会造成Hash冲突严重，从而导致链表会很长，而链表长了后直接会造成的影响就是当调用String.intern()时性能会大幅下降。
- 字符串常量池中不会存储相同的内容的字符串
- 使用-XX: StringTablesize可设置stringTable的长度
- Jdk8开始，StringTable的长度1009是可设置的**最小值**。

## 二、String的内存分配

> 注意：对于字符串常量池的位置变化原因，详情可见**4.3.2**
> 
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image.png)
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%201.png)
> 

## 三、String的基本操作

### 1.验证字符串常量池中不能重复加载相同字符

> 也是就是对于同一字符只指向通一个String实例
> 

```java
public static void main(string[] args) {
	System.out.println();//22
	System.out.println("1");//2229
	System.out.println("2");//2230
	System.out.println("3");
	System.out.println("4");
	System.out.println("5");
	System.out.println("6");
	System.out.println("7");
	System.out.println("8");
	System.out.println("9");
	System.out.println("10");//2238

	System.out.println("1");//2239
	System.out.println("2");//2239
	System.out.println("3")﹔
	System.out.println("4");
	System.out.println("5")
	System.out.println("6");
	System.out.println("7");
	//........
	System.out.println("10");//2239
}
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%202.png)

### 2.同理验证指向位置即常量池的位置变化

```java
public class Memory {
    public static void main(String[] args) {
        int i = 1;
        Object obj = new Object();
        Memory memory = new Memory();
        memory.foo(obj);
    }

    private void foo(Object param){
        String str = param.toString();
        System.out.println(str);
    }
}
```

- 内存结构图

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%203.png)

## 四、字符串拼接操作

### 1.操作概述及注意事项

1. 常量与常量的拼接结果在常量池，原理是编译期优化，即字面量定义都会直接在常量池中

```java
	@Test
    public void test01(){
        String s1 = "a"+"b"+"c";//编译期优化,等同于"abc"
        String s2 = "abc";//一定放在字符串常量池中，将地址赋值给s2

        System.out.println(s1 == s2);//true
        System.out.println(s1.equals(s2));//true
    }
```

1. **常量池中不会存在相同内容的常量。（底层是个HashTable）**
2. 拼接字符串时，**只要其中有一个是"变量"，结果就在堆中**。变量拼接的原理是StringBuilder

```java
public void test03(){
        String s1 = "a";
        String s2 = "b";
        String s3 = "ab";
        String s4 = s1 + s2;
        System.out.println(s4 == s3);//false
    }
```

> 如下的s1 + s2的执行细节:
**stringBuilder s = new stringBuilder();
s.append( "a")
s.append("b")
s.tostring()-->约等于new string( "ab")
补充:在jdk5.0之后使用的是stringBuilder,在jdk5.0之前使用的是stringBuffer**
> 

```java
public void test04(){
		//注意此时s1和s2就不是变量了，为字符串常量了，仍使用编译期优化，所以结果为true
        final String s1 = "a";
        final String s2 = "b";
        String s3 = "ab";
        String s4 = s1 + s2;
        System.out.println(s3 == s4);//true
    }
```

1. 如果拼接的结果调用intern()方法，则主动将常量池中还没有的字符串对象放入池中，并返回此对象地址。

```java
	@Test
    public void test02(){
        String s1 = "javaEE";
        String s2 = "hadoop";

        String s3 = "javaEEhadoop";
        String s4 = "javaEE" + "hadoop";//编译期优化
        String s5 = s1 + "hadoop";
        String s6 = "javaEE" + s2;
        String s7 = s1 + s2;

        System.out.println(s3 == s4);   //true
        System.out.println(s3 == s5);   //false
        System.out.println(s3 == s6);   //false
        System.out.println(s3 == s7);   //false
        System.out.println(s5 == s6);   //false
        System.out.println(s5 == s7);   //false
        System.out.println(s6 == s7);   //false
        //intern():判断字符串常量池中是否存在javaEEhadoop值，如果存在，则返回常量池中javaEEhadoop的地址;
		//如果字符串常量池中不存在javaEEhadoop，则在常量池中加载一份javaEEhadoop，并返回此对象的地址。
		String s8 = s6.intern();
        System.out.println(s3 ==s8);    //true
		}
```

1. **如果要进行多次字符串变量拼接操作，我们可以直接创建一个StringBuilder对象来进行拼接操作来节省资源及GC触发时间，如果每次都通过变量拼接，在底层每次都要创建一个StringBuilder对象和String（toString方法返回的）对象**，且创建StringBuilder对象时还可以调用指定长度的构造器来创建，以此来节省扩容的频率

## 五、intern()的使用

### 1.使用

> 以下两者是同理的
> 

```java
String s1 = "abc";
String s2 = new String("abc").intern();
```

### 2.相关面试题

1. new String("ab")会创建几个对象？

> 答案是两个，通过查看字节码就很清楚，
> 
> 
> **第一个对象是通过new关键字在堆空间中创建的，第二个对象是在字符串常量池中创建的"ab"**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%204.png)
> 
1. new String("a")+new String("b")会创建几个呢？

> 同样也是观察字节码，总共有五个对象被创建
但其实往深入里讲的话是
> 
> 
> **有六个对象**
> 
> **但注意此时常量池中并没有"ab"**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EStringTable%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%205.png)
> 
1. s.intern()

> 第一个判相等的false：以jdk7/8为例，new完String返回的是堆空间的对象地址，同时常量池上已经有了创建好的对象，然后调用intern来去检查常量池中是否有“1”，肯定是有的，**所以返回常量池中的对象地址，但此时没有用此返回值设置设置新的String对象**，所以s还是原来堆空间中的地址，而s2就更简单了，常量赋值地址就是常量池中的，两者肯定不相等所以false
> 

```java
public class StringIntern {
    public static void main(String[] args) {
        String s = new String("1");
        s.intern();
        String s2 = "1";
        System.out.println(s == s2);//jdk6:false    jdk7/8:false
        }
}
```

> **第二个判相等的true，是因为jdk6时字符串常量池还在方法区中，s3是通过new出来的对象，所以对象地址时堆空间的地址，同时字符串常量池中是存在“1”而不存在“11”。然后intern方法去检查常量池中是否有“11”，结果肯定是没有，所以在常量池中创建“11”对象，然后s4是常量赋值，即是字符串常量池中的intern生成的对象地址，所以以jdk6来看确实地址是不一样的（jdk6时的intern方法直接生成创建一个新对象）。但以jdk7/8来看，当检测常量池中没有“11”时，直接指向了new String("11")的这个堆中的对象地址，所以是true，目的就是节省空间**
> 

```java
		String s3 = new String("1") + new String("1");// == String s3 = new String("11");
        s3.intern();
        String s4 = "11";
        System.out.println(s3 == s4);//jdk6:false   jdk7/8:true
```

### 3.总结

- jdk6

> jdk1.6中，将这个字符串对象尝试放入串池。如果串池中有，则并不会放入。返回已有的串池中的对象的地址；如果没有，会把此对象复制一份，放入串池，并返回串池中的对象地址
> 
- jdk7/8

> **Jdk1.7起，将这个字符串对象尝试放入串池。如果串池中有，则并不会放入。返回已有的串池中的对象的地址；如果没有，则会把对象的引用地址复制一份，放入串池，并返回串池中的引用地址**，**即以后相同字符串在常量池中都不会在创建对象，而是直接用这个引用地址**
> 
- 在开发中，合理使用intern()方法可以做到节省空间，提高效率的效果
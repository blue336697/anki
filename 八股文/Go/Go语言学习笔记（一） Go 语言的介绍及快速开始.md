# Go语言学习笔记（一）| Go 语言的介绍及快速开始

type: Post
status: Published
date: 2022/10/12
summary:  Go 语言的介绍及快速开始
tags: Go
category: 技术栈

# Go 语言的介绍

## 1.用 Go 解决现代编程难题

- 概述

> C 和 C++这类语言提供了很快的执行速度，而 Ruby 和 Python 这类语言则擅长快速开发。**Go 语言在这两者间架起了桥梁，不仅提供了高性能的语言，同时也让开发更快速。**
> 
- 特性简述

> • Go 语言的语法简洁到只有几个关键字，便于记忆。
• Go 语言的编译器速度非常快，有时甚至会让人感觉不到在编译。所以，Go 开发者能显著减少等待项目构建的时间。
• 因为 Go 语言内置并发机制，所以不用被迫使用特定的线程库，就能让软件扩展，使用更多的资源。
• Go 语言的类型系统简单且高效，不需要为面向对象开发付出额外的心智，让开发者能专注于代码复用。
• Go 语言还自带垃圾回收器，不需要用户自己管理内存。
> 

### 1.1 开发速度

- C&C++的编译速度

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image.png)

- Go的编译速度

> 主要就是解决了依赖的算法，使之加载进去的依赖库更少了，**而不是像 Java、C 和 C++那样，要遍历依赖链中所有依赖的库**。在现代硬件上，编译整个 Go语言的源码树只需要 20 秒。因为没有从编译代码到执行代码的中间过程，用动态语言编写应用程序可以快速看到输出。**代价是，动态语言不提供静态语言提供的类型安全特性，不得不经常用大量的测试套件来避免在运行的时候出现类型错误这类 bug**。
> 

==类型安全==

- 什么是类型安全

> 类型安全简单来说就是访问可以被授权访问的内存位置，类型安全的代码不会试图访问自己未被授权的内存区域。一方面，类型安全被用来形容编程语言，主要根据这门编程语言是否提供类型安全的保障机制；另一方面，类型安全也可以用来形容程序，根据这个程序是否隐含类型错误。类型安全的语言和程序之前，其实没有必然的联系。类型安全的语言，使用不当，也可能写出来类型不安全的程序；类型不安全的语言，使用得当，也可以写出非常安全的程序。
> 
- C的类型安全

> C语言不是类型安全的语言，原因如下：
> 
> - 很多情况下，会存在类型隐式转换，比如bool自动转成int类型；
> - malloc函数返回的是void *的空类型指针，通常需要这样的显示类型转换`char* pStr=(char*)malloc(100*sizeof(char))`，类型匹配没有问题。但如果出现`int* pInt=(int*)malloc(100*sizeof(char))`这样的转换，可能会带来一些问题，但C并不会提示。

> 当然，在有些情况下表现还是类型安全的，当从一个结构体指针转换成另一个结构体指针时，编译器会报错，除非显式转换。
> 
- C++的类型安全

> C++也不是类型安全的语言，但远比C更具类型安全。相比于C，提供了一些安全保障机制：
> 
> - 用操作符new来申请内存，严格与对象类型匹配，而malloc是`void *`；
> - 函数参数为`void *`的可以改写成模板，模板支持运行时检查参数类型；
> - 使用const代替define来定义常量，具有类型、作用域，而不是简单的文本替换；
> - 使用inline代替define来定义函数，结合函数的重载，在类型安全的前提下可以支持多种类型，如果改写成模板，会更安全；
> - 提供dynamic_cast使得转换过程更安全。

> 尽管如此，但如果使用空类型指针或者在两个不同类型指针间做强制转换，很可能引发类型不安全的问题。
> 
- Java的类型安全

> 对于Java来说是静态语言，那么显然就是类型安全的，是强类型的语言
> 
> - **Java是在编译时期确定的变量类型且在运行时期不能改变，在类型转换方面也是强制的，例如大范围整数类型转换为小范围整数类型时必须要强转，如int必须强制转换才能得到小范围类型byte**

### 1.2 并发

- 概述

> Go 语言对并发的支持是这门语言最重要的特性之一，就是用goroutine运行所有的一切，包括main入口函数，**goroutine 很像线程，但是它占用的内存远少于线程，使用它需要的代码更少。通道（channel）是一种内置的数据结构，可以让用户在不同的 goroutine 之间同步发送具有类型的消息**。这让编程模型更倾向于在 goroutine之间发送消息，而不是让多个 goroutine 争夺同一个数据的使用权。
> 

==goroutine==

> 在web开发中，以往的Java等编程语言来同时处理不同的web请求会使得代码量增加在使用线程上，而在go中每个线程可以执行多个goroutine，这些goroutine可以并行执行的函数，所以go中的网络库可以直接使用goroutine，每个请求对应一个
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image%201.png)

- 例子

> 关键字 go 是唯一需要去编写的代码，调度 log 函数作为独立的 goroutine 去运行，以便与其他 goroutine 并行执行。这意味着应用程序的其余部分会与记录日志并行执行
> 

```go
func log(msg string) {
..．这里是一些记录日志的代码
}
// 代码里有些地方检测到了错误
go log("发生了可怕的事情")
```

==通道==

> **通道是一种数据结构，可以让 goroutine 之间进行安全的数据通信**。通道可以帮用户避免其他语言里常见的共享内存访问的问题。即最难也就是数据的同步性了，当不同的线程在没有同步保护的情况下修改同一个数据时，总会发生不同步的现象，这个时候其他语言就会用复杂的锁规则来控制资源的访问
> 

> 通道这一模式保证同一时刻只会有一个 goroutine 修改数据。通道用于在几个运行的 goroutine 之间发送数据。在下图可以看到数据是如何流动的示例。想象一个应用程序，有多个进程需要顺序读取或者修改某个数据，使用 goroutine 和通道，可以为这个过程建立安全的模型。**第一个goroutine处理完数据就传递给正在等待（同步的）的第二个goroutine，然后依次传递，整个过程不需要锁或同步机制**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image%202.png)

- 注意

> **需要强调的是，通道并不提供跨 goroutine 的数据访问保护机制。如果通过通道传输数据的一份副本，那么每个 goroutine 都持有一份副本，各自对自己的副本做修改是安全的。当传输的是指向数据的指针时，如果读和写是由不同的 goroutine 完成的，每个 goroutine 依旧需要额外的同步动作**。
> 

### 1.3 Go 语言的类型系统

- 概述

> • Go 语言提供了灵活的、无继承的类型系统，无需降低运行性能就能最大程度上复用代码。这个类型系统依然支持面向对象开发，但避免了传统面向对象的问题（抽象类与接口）。
• Go 开发者使用组合（composition）设计模式（树结构），只需简单地将一个类型嵌入到另一个类型，就能复用所有的功能。
• Go中不需要声明某个类型实现了某个接口，编译器会判断一个类型的实例是否符合正在使用的接口。Go 标准库里的很多接口都非常简单，只开放几个函数。
> 

==类型简单==

> • 内置类型：int、string
• 用户自定义类型：用户定义的类型通常包含一组带类型的字段，用于存储数据。
> 
- 类型简单体现在组合模式上

> • 传统语言使用继承来扩展结构——`Client` 继承自 `User`，`User` 继承自 `Entity`
• Go 语言与此不同，Go 开发者构建更小的类型——`Customer 和 Admin`，然后把这些小类型组合成更大的类型。
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image%203.png)

==Go接口对一组行为建模==

> 这就是上图的右边的描述，一个类型实现了一个接口，意味着这个实例可以执行一组特定的行为。你甚至不需要去声明这个实例实现某个接口，只需要实现这组行为就好
> 

> 其他的语言把这个特性叫作`鸭子类型`——如果它叫起来像鸭子，那它就可能是只鸭子。**Go 语言的接口也是这么做的。在 Go 语言中，如果一个类型实现了一个接口的所有方法，那么这个类型的实例就可以存储在这个接口类型的实例中，不需要额外声明。**
> 
- 具体与Java的区别

> Java中你要实现这个接口就要实现全部方法
> 

```java
interface User {
	public void login();
	public void logout();
}
```

> 在go中接口一般只会描述一个单一的动作。Go 语言的接口更小，只倾向于定义一个单一的动作。实际使用中，这更有利于使用组合来复用代码。**例如go中整个网络库都实现了这个接口，文件、缓冲区、套接字以及其他的数据源都实现了 `io.Reader` 接口。使用同一个接口，可以高效地操作数据，而不用考虑到底数据来自哪里**。
> 

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
```

## 2.你好，Go

```go
package main	//Go 程序都组织成包。

import "fmt" //import 语句用于导入外部代码。标准库中的 fmt 包用于格式化并输出数据。

func main() { 	//像 C 语言一样，main 函数是程序执行的入口。
	fmt.Println("Hello world!")
}
```

# 快速开始一个Go程序（就是介绍包结构）

## 0.相关表达式与语法

> 这些相关的用法注意事项会通过第三方包的分析全部指出
> 
- 表达式

```go
if y > 0 {

} else if y < 0 {

} else {

}

switch {
case y > 0:
case y < 0:
default:
}

for i := 0; i < 5; i++ {}

arr := []int{100, 12, 33}
for i, i2 := range arr { //前者是索引后面是元素值
	println(i, i2)
}
for x < 5 { //相当于while(x < 5)
}
for { //相当于while(true)
	break
}
```

- 函数

```go
//函数可定义多个返回值,甚至对其命名。
func div(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("除数不能为0")
	}
	return a / b, nil
}

//函数是第一类型,可作为参数或返回值。
func test01(x int) func {
	return func() {
		println(x)
	}
}

//用 defer定义延迟调用,无论函数是否出错，它都确保结束前被调用。
func test02(a,b int) {
	//常用来释放资源、解除锁定，或执行一些清理操作
	//可定义多个defer按FILO顺序执行
	defer println("dispose...")
	println(a / b)
}

func main() {
	a, b := 10, 2
	res, err := div(a, b)
	fmt.Println(res, err)

	x := 100
	f := test01(x)
	f()

	test02(10, 0)
}
```

- 数据

```go
//切片（slice）可实现类似动态数组的功能。
func main() {
	//创建容量为5的切片
	x := make([]int, 0, 5)
	for i := 0; i < 100; i++ {
		//如果容量不够，会自动分配更大的存储空间
		x = append(x, i)
	}
	fmt.Println(x)
}

//map类型对象
func main() {
	//键的类型是[]里的，值的类型是后面
	m := make(map[string]int) //创建字典类型对象
	m["a"] = 1                //添加键值对

	x, ok := m["b"] //使用 ok-idiomi 获取值,可知道key/value是否存在
	fmt.Println(x, ok)
	delete(m, "a")	//删除键值对
}
```

- 方法

> 可以为当前包内的任意类型定义方法
> 

```go
type X int
func (x *X) inc() {//名称前的参数称作 receiver，作用类似 python self
	*x++
}
func main(){
	var y X
	y.inc()
	println(y)
}

//匿名字段的方式，实现类似于继承的功能
type user struct {
	name string
	age  byte
}

type manager struct {
	user  //没标类型默认就是你的结构体
	title string
}

//括号代表调用的对象，后面代表返回值
func (u user) ToString() string {
	return fmt.Sprintf("%+v", u)
}

func main(){
	var u manager
	u.name = "Tom"
	u.age = 29
	println(u.ToString())
}
```

- 接口

> **接口采用了duck type方式，也就是说无须在实现类型上添加显式声明**。另有空接口类型 `interface{}`，用途类似OOP里的`system.Object`，可接收任意类型对象。
> 

```go
type printer interface {
	print()
}

func (u user) print() {
	fmt.Printf("%+v\\n", u)
}

type user struct {
	name string
	age  byte
}

func main(){
	var user user
	user.name = "tom"
	user.age = 29

	var p printer = user
	p.print()
}
```

- 并发

> 这里主要就是goroutine和channel的配合使用了
> 

```go
import (
	"fmt"
	"time"
)

//并发

func task(id int) {
	for i := 0; i < 5; i++ {
		fmt.Printf("%d: %d\\n", id, i)
		time.Sleep(time.Second)
	}
}
func main(){
	go task(1)
	go task(2)

	time.Sleep(time.Second * 6)
}

//goroutine+channel
/*
*
这个接收参数：1.接收传输int类型的通道

	2.接收传出boolean类型的通道

		接收者<-发送的数据
*/
func consumer(data chan int, done chan bool) {
	for x := range data {
		println("recv:", x) //接收消息，直到通道被关闭
	}

	done <- true //通知main，消费结束
}

func producer(data chan int) {
	for i := 0; i < 4; i++ {
		data <- i //发送数据
	}
	close(data) //生产结束，关闭通道
}

func main(){
	done := make(chan bool) //用于接收boolean类型的通道
	data := make(chan int)  //用于接收int数据的通道

	go consumer(data, done) //启动消费者
	go producer(data)       //启动生产者

	<-done //阻塞，直到消费者发回结束信号
}
```

## 1.程序框架

- 概述

> 这个程序分成多个不同步骤，在多个不同的`goroutine`里运行。我们会根据流程展示代码，从主 `goroutine` 开始，一直到执行搜索的 `goroutine` 和跟踪结果的 `goroutine`，最后回到主 `goroutine`。
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image%204.png)

- 拿一个第三方包举例

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%80%EF%BC%89%20Go%20%E8%AF%AD%E8%A8%80%E7%9A%84%E4%BB%8B%E7%BB%8D%E5%8F%8A%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B/image%205.png)

```go
- sample
	- data
		 data.json -- 包含一组数据源
 	- matchers
 		rss.go -- 搜索 rss 源的匹配器
 	- search
		default.go -- 搜索数据用的默认匹配器
		feed.go -- 用于读取 json 数据文件
		match.go -- 用于支持不同匹配器的接口
		search.go -- 执行搜索的主控制逻辑
	main.go -- 程序的入口
```

## 2.main包

- 概述

> 我们继续以上面的main入口为例：列举出注意事项
> 

```go
package main

import (
	"log"
	"os"

	_ "github.com/goinaction/code/chapter2/sample/matchers"
	"github.com/goinaction/code/chapter2/sample/search"
)

// init 在 main 之前调用
func init() {
	// 将日志输出到标准输出
	log.SetOutput(os.Stdout)
}

 // main 是整个程序的入口
func main() {
	// 使用特定的项做搜索
	search.Run("president")
}
```

- 注意事项

> • **main 函数保存在名为 main 的包里。如果 main 函数不在 main 包里，构建工具就不会生成可执行的文件。**
• 每个代码文件都属于一个包，**一个包下只能有一个main函数**，一个包定义一组编译过的代码，包的名字类似命名空间，可以用来间接访问包内声明的标识符。这个特性可以把不同包中定义的同名标识符区别开。
• 导包语句对应的API没有用到就会用`_`开头，来标志没用到；为了让程序的可读性更强，Go 编译器不允许声明导入某个包却不使用。所以加入这个下划线来表明
• init函数都会在 main 函数执行前调用。
> 

## 3.search包

- 匹配器

> 这个程序里的匹配器，是指包含特定信息、用于处理某类数据源的实例。**框架本身实现了一个无法获取任何信息的默认匹配器**，而在 matchers 包里实现了 RSS 匹配器。RSS匹配器知道如何获取、读入并查找 RSS 数据源。随后我们会扩展这个程序，加入能读取 JSON文档或 CSV 文件的匹配器。
> 

### 3.1 search.go

- 代码

```go
package search

import (
	"log"
	"sync"
)

// 注册用于搜索的匹配器的映射
var matchers = make(map[string]Matcher)

// Run 执行搜索逻辑
func Run(searchTerm string) {
	// 获取需要搜索的数据源列表
	feeds, err := RetrieveFeeds()
	if err != nil {
		log.Fatal(err)
	}

	// 创建一个无缓冲的通道，接收匹配后的结果
	results := make(chan *Result)

	// 构造一个 waitGroup，以便处理所有的数据源
	var waitGroup sync.WaitGroup

	// 设置需要等待处理
	// 每个数据源的 goroutine 的数量
	waitGroup.Add(len(feeds))

	// 为每个数据源启动一个 goroutine 来查找结果
	for _, feed := range feeds {
		// 获取一个匹配器用于查找
		matcher, exists := matchers[feed.Type]
		if !exists {
			matcher = matchers["default"]
		}

		// 启动一个 goroutine 来执行搜索
		go func(matcher Matcher, feed *Feed) {
			Match(matcher, feed, searchTerm, results)
			waitGroup.Done()
		}(matcher, feed)
	}

	// 启动一个 goroutine 来监控是否所有的工作都做完了
	go func() {
		// 等候所有任务完成
		waitGroup.Wait()

		// 用关闭通道的方式，通知 Display 函数可以退出程序了
		close(results)
	}()

	// 启动函数，显示返回的结果，并且在最后一个结果显示完后返回
	Display(results)
}

// Register is called to register a matcher for use by the program.
func Register(feedType string, matcher Matcher) {
	if _, exists := matchers[feedType]; exists {
		log.Fatalln(feedType, "Matcher already registered")
	}

	log.Println("Register", feedType, "matcher")
	matchers[feedType] = matcher
}
```

- 注意事项

> 
> 
> - `查找包`：与第三方包不同，从标准库中导入代码时，只需要给出要导入的包名。编译器查找包的时候，总是会到 GOROOT 和 GOPATH 环境变量引用的位置去查找。
> - `变量作用域`：没有定义任何作用域的变量默认作为包级变量
> - **程序可以直接访问这个包中任意一个公开的标识符。这些标识符以大写字母开头。以小写字母开头的标识符是不公开的，不能被其他包中的代码直接访问**。但是，其他包可以间接访问不公开的标识符。例如，一个函数可以返回一个未公开类型的值，那么这个函数的任何调用者，哪怕调用者不是在这个包里声明的，都可以访问这个值。
> - `make关键字`：先用make来构造引用类型，然后在赋值给变量，若没有则会被赋值为零值（null）
> - `类型默认值`：**对于数值类型零值为0；字符串类型为空字符串；布尔类型为false；指针为null；对于引用类型来说，所引用的底层数据结构会被初始化为对应的零值。但是被声明为其零值的引用类型的变量，会返回 nil 作为其值。**
> - `函数返回值`：函数能返回多个值，一般都是需要的值和发生错误值，如果发生错误就要忽略需要的值
> - `简化书写`：简化变量声明运算符`（:=）`。这个运算符用于声明一个变量，同时给这个变量赋予初始值。编译器使用函数返回值的类型来确定每个变量的类型。
> - **如果需要声明初始值为零值的变量，应该使用 var 关键字声明变量；如果提供确切的非零值初始化变量或者使用函数返回值创建变量，应该使用简化变量声明运算符**。
> - `通道（channel）和映射（map）与切片（slice）`一样，也是引用类型，不过通道本身实现的是一组带类型的值，这组值用于在 goroutine 之间传递数据。通道内置同步机制，从而保证通信安全。
> - `书写建议`：写并发程序的时候，最佳做法是，在 main 函数返回前，清理并终止所有之前启动的 goroutine。编写启动和终止时的状态都很清晰的程序，有助减少 bug，防止资源异常。
> - `waitGroup`：推荐使用 WaitGroup 来跟踪 goroutine 的工作是否完成。WaitGroup 是一个计数信号量，我们可以利用它来统计所有的goroutine 是不是都完成了工作。
> - **下划线的另一个作用**：上面说过下划线是导入包时如果没有使用到相关API就会标注，这里在有个for循环中只用在了for后面，这次，下划线标识符的作用是占位符，占据了保存 range 调用返回的索引值的变量的位置。如果要调用的函数返回多个值，而又不需要其中的某个值，就可以使用下划线标识符将其忽略。在我们的例子里，我们不需要使用返回的索引值，所以就使用下划线标识符把它忽略掉。
> - `返回值的处理——ok-idiom模式`：**是指在多返回值中用一个名为 xx的布尔值来标示操作是否成功。因为很多操作默认返回零值,所以须额外说明。查找 map 里的键时，有两个选择。要么赋值给一个变量，要么为了精确查找，赋值给两个变量（第二个变量就是你要查找的键的boolean）。**
> - `go关键字之匿名函数`：一个 goroutine 是一个独立于其他函数运行的函数。使用关键字 go 启动一个 goroutine，并对这个 goroutine 做并发调度。在代码中我们使用关键字 go 启动了一个匿名函数作为 goroutine。匿名函数是指没有明确声明名字的函数。在 for range 循环里，我们为每个数据源，以 goroutine 的方式启动了一个匿名函数。这样可以并发地独立处理每个数据源的数据。你可以指定这个匿名函数接收几个参数
> - `变量传递`：在 Go 语言中，所有的变量都以值的方式传递。因为指针变量的值是所指向的内存地址，在函数间传递指针变量，是在传递这个地址值，所以依旧被看作以值的方式在传递。
> - **编译器将未使用的局部变量定义当作错误**。

# 关于Go的RPC&Threads

## Threads

- 语言线程与OS线程

> 对于某个语言的线程来说最终肯定要使用OS的线程去运行，例如GO的多线程goroutine会复用OS的线程以节省系统开销；当进行上下文切换时，OS会根据一定的策略选择某个某个OS线程去执行任务，而这个OS线程也会根据策略选择某个goroutine去执行
> 
- 多线程与其对立面

> IO并行化——多线程
异步编程——事件驱动型编程：对于异步编程来说我们主要强调的是处理的方式即单一循环处理一个大任务分成的很多小任务，这种模型好处就是在单体服务器上可以有很好的性能表现，不存在切换线程，线程栈之类的消耗；对于异步+单线程的结合典型的就是JS这门语言，津津乐道的AJAX请求也应运而生；
> 
> - 那么对于单线程来说执行的方式就是单一循环执行；
> - 而对于多线程则是每个线程对应不同的任务，对应还是在单一循环中；对于每个线程我们可以优化成精简的事件驱动循环，每个线程负责单一的事件，每个线程执行还都是异步的，让整体的性能提高很多很多，其实此时就可以看成一个并行化处理了
- go中的锁

> go中的锁是不能重入的，而且go中的锁不强调是谁声明的锁，谁调用的锁，它仅仅就是防止竞争，那么既然不能重入，这个锁的范围难道是当前调用栈的全局代码？
>
# Go语言学习笔记（四）| 并发（goroutine）及并发模式

type: Post
status: Published
date: 2022/10/19
summary: 并发（goroutine）及并发模式
tags: Go
category: 技术栈

# 并发

## 1.并发的含义

### 1.1 并发与并行

- 概述

> 在开始本章之前,需要了解并发`(concurrency)`和并行`(parallesim)`的区别。
> 
> - 并发：逻辑上具备同时处理多个任务的能力。
> - 并行：物理上在同一时刻执行多个并发任务。
> 
> ![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image.png)
> 

我们通常会说程序是并发设计的，也就是说它允许多个任务同时执行，但实际上并不一定真在同一时刻发生。在单核处理器上，它们能以间隔方式切换执行。而并行则依赖多核处理器等物理设备，让多个任务真正在同一时刻执行，它代表了当前程序运行状态。简单点说，并行是并发设计的理想执行模式。

- 进程与线程

> **当运行一个应用程序（如一个 IDE 或者编辑器）的时候，操作系统会为这个应用程序启动一个进程。可以将这个进程看作一个包含了应用程序在运行中需要用到和维护的各种资源的容器。下图展示了一个包含所有可能分配的常用资源的进程。这些资源包括但不限于内存地址空间、文件和设备的句柄以及线程。一个线程是一个执行空间，这个空间会被操作系统调度来运行函数中所写的代码。每个进程至少包含一个线程，每个进程的初始线程被称作主线程。因为执行这个线程的空间是应用程序的本身的空间，所以当主线程终止时，应用程序也会终止。操作系统将线程调度到某个处理器上运行，这个处理器并不一定是进程所在的处理器。不同操作系统使用的线程调度算法一般都不一样，但是这种不同会被操作系统屏蔽，并不会展示给程序员**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%201.png)

- 协程

> **多线程或多进程是并行的基本条件，但单线程也可用协程`（goroutine）`做到并发。尽管协程在单个线程上通过主动切换来实现多任务并发，但它也有自己的优势。除了将因阻塞而浪费的时间找回来外，还免去了线程切换开销，有着不错的执行效率。协程上运行的多个任务本质上是依旧串行的，加上可控自主调度，所以并不需要做同步处理**。
> 

> **Go 语言的运行时会在逻辑处理器上调度goroutine来运行。每个逻辑处理器都分别绑定到单个操作系统线程。在 1.5 版本以上，Go语言的运行时默认会为每个可用的物理处理器分配一个逻辑处理器，那么我们如果要实现类似于并行的效果就要多个逻辑处理器**。
> 
> - 在 1.5 版本之前的版本中，默认给整个应用程序只分配一个逻辑处理器。这些逻辑处理器会用于执行所有被创建的goroutine。即便只有一个逻辑处理器，Go也可以以神奇的效率和性能，并发调度无数个goroutine。
- `go`调度器如何管理`goroutine`

> 可以看到操作系统线程、逻辑处理器和本地运行队列之间的关系。如果创建一个 goroutine 并准备运行，这个 goroutine 就会被放到调度器的**全局运行队列**中。之后，调度器就将这些队列中的 goroutine 分配给一个逻辑处理器，并放到这个逻辑处理器对应的**本地运行队列**
> 

==出现系统调用时对应线程处理==

> 有时，正在运行的 goroutine 需要执行一个阻塞的系统调用：
> 
> - 如打开一个文件。当这类调用发生时，**线程和 goroutine 会从逻辑处理器上分离，该线程会继续阻塞，等待系统调用的返回。与此同时，这个逻辑处理器就失去了用来运行的线程。所以，调度器会创建一个新线程，并将其绑定到该逻辑处理器上。之后，调度器会从本地运行队列里选择另一个 goroutine 来运行。一旦被阻塞的系统调用执行完成并返回，对应的 goroutine 会放回到本地运行队列，而之前的线程会保存好，以便之后可以继续使用**。
> 
> ![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%202.png)
> 
> - 在网络IO调用时，会有些许不同，发生调用时正在处理的goroutine也会与逻辑处理器分离，但是会移动到网络轮询器，相当于一个selector去轮询的检查每个操作的准备情况，如果某个操作准备完成那么对应的goroutine就会被重新分配到逻辑处理器完成操作
- 逻辑处理器的限制

> 调度器对可以创建的逻辑处理器的数量没有限制，但语言运行时默认限制每个程序最多创建 `10 000` 个线程。这个限制值可以通过调用 `runtime/debug` 包的 `SetMaxThreads` 方法来更改。如果程序试图使用更多的线程，就会崩溃。
> 

## 2.goroutine

- 概述

> 只须在函数调用前添加go关键字即可创建并发任务。关键字go并非执行并发操作，而是创建一个并发任务单元。新建任务被放置在系统队列中，等待调度器安排合适系统线程去获取执行权。当前流程不会阻塞，不会等待该任务启动，且运行时也不保证并发任务的执行次序。
> 
- go任务信息

> **每个任务单元除保存函数指针、调用参数外，还会分配执行所需的栈内存空间。相比系统默认MB级别的线程栈，goroutine自定义栈初始仅须2KB（1.6版本），所以才能创建成千上万的并发任务。自定义栈采取按需分配策略，在需要时进行扩容，最大能到GB规模**。
> 
- 代码解读以及相关方法

`runtime.GOMAXPROCS()`：**调用了 runtime 包的 GOMAXPROCS 函数。这个函数允许程序更改调度器可以使用的逻辑处理器的数量。如果不想在代码里做这个调用，也可以通过修改和这个函数名字一样的环境变量的值来更改逻辑处理器的数量**。

- **给这个函数传入 1，是通知调度器只能为该程序使用一个逻辑处理器**
- **如参数小于1，GOMAXPROCS仅返回当前设置值，不做任何调整**
- **可以给每个可用的物理处理器在运行的时候分配一个逻辑处理器。让 goroutine 真正并行运行，其实默认你不设置就是跟物理核心数量是相等的**。

```go
import "runtime"
// 给每个可用的核心分配一个逻辑处理器
runtime.GOMAXPROCS(runtime.NumCPU())
```

`WaitGroup`：是一个计数信号量，可以用来记录并维护运行的 goroutine。如果 WaitGroup的值大于 0，Wait 方法就会阻塞。为了减小WaitGroup 的值并最终释放 main 函数，使用 defer 声明在函数退出时调用 Done 方法。**建议在goroutine任务外面进行累加操作，否则可能会导致主线程执行的快直接结束主任务**

- 也可以使用通道进行阻塞，然后发出退出信号

```go
func main(){
	exit := make(chan struct{}) //创建一个空的结构体的通道

	go func() {
		time.Sleep(time.Second)
		println("执行完成")
		close(exit) //关闭通道，发出信号
	}()

	println("主函数等待goroutine")
	<-exit //接收消息
	println("goroutine执行完，主函数结束")
}
```

`wait()`：这个方法就是阻塞当前线程获goroutine直到WaitGroup的计数为归零

> 例子：完成大写小字母表的打印
> 

```go
func main() {
	//分配一个逻辑处理器给调度器
	runtime.GOMAXPROCS(1)

	//WaitGroup用来等待程序完成
	//计数加2，表示要等待两个go协程
	var wg sync.WaitGroup
	wg.Add(2)

	fmt.Println("开始并发任务")

	go func() {
		// 在函数退出时调用 Done 来通知 main 函数工作已经完成
		defer wg.Done()
		//显示26字母三次
		for count := 0; count < 3; count++ {
			for char := 'a'; char < 'a'+26; char++ {
				fmt.Printf("%c", char)
			}
			println()
		}
	}()

	go func() {
		// 在函数退出时调用 Done 来通知 main 函数工作已经完成
		defer wg.Done()
		//显示大写26字母三次
		for count := 0; count < 3; count++ {
			for char := 'A'; char < 'A'+26; char++ {
				fmt.Printf("%c", char)
			}
			println()
		}
	}()

	fmt.Println("等待go协程执行完成")
	wg.Wait()

	fmt.Println("执行结束")
}
```

> **第一个 goroutine 完成所有显示需要花时间太短了，以至于在调度器切换到第二个 goroutine之前，就完成了所有任务。这也是为什么会看到先输出了所有的大写字母，之后才输出小写字母**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%203.png)

==上面例子从逻辑处理器的角度分析==

基于调度器的内部算法，一个正运行的 goroutine 在工作结束前，可以被停止并重新调度。调度器这样做的目的是防止某个 goroutine 长时间占用逻辑处理器。当 goroutine 占用时间过长时，调度器会停止当前正运行的 goroutine，并给其他可运行的 goroutine 运行的机会。可以看到是抢占式的方式去管理调度的

我们具体分析以下上面两个goroutine的执行过程：从逻辑处理器的角度展示了这一场景。在第 1 步，调度器开始运行goroutine A，而goroutine B 在运行队列里等待调度。之后，在第 2 步，调度器交换了 goroutine A 和 goroutine B。由于 goroutine A 并没有完成工作，因此被放回到运行队列。之后，在第 3 步，goroutine B 完成了它的工作并被系统销毁。这也让 goroutine A 继续之前的工作

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%204.png)

- 改变代码让其执行长任务后的行为改变

> 在长任务与一个逻辑处理器下，对于A来说就不会出现那么快的执行完任务切换到B了，对于A会出现时间片用完也没执行完而被迫切换到B，然后B开始执行，提前或被迫也是看任务的大小决定，最后在切换会A继续完成剩下的任务
> 
- 其他的一些方法或结构实现

==Local Storage==

> 与线程不同，`goroutine`任务无法设置优先级，无法获取编号，没有局部存储`(TLS)`，甚至连返回值都会被抛弃。但除优先级外，其他功能都很容易实现,
> 

```go
func main() {
	runtime.GOMAXPROCS(1)

	var wg sync.WaitGroup

	var gs [5]struct { //用于实现TLS的功能
		id     int //编号
		result int //执行结果返回值
	}
	for i := 0; i < len(gs); i++ {
		wg.Add(1)

		go func(id int) { //使用参数避免闭包延迟求值
			defer wg.Done()

			gs[id].id = id
			gs[id].result = (id + 1) * 100
		}(i)
	}
	wg.Wait()
	//[{id:0 result:100} {id:1 result:200} {id:2 result:300} {id:3 result:400} {id:4 result:500}]
	fmt.Printf("%+v\\n", gs)
}
```

==Gosched==

> 暂停，释放线程去执行其他任务。当前任务被放回队列，等待下次调度时恢复执行。**该函数很少被使用，因为运行时会主动向长时间运行`(10ms)`的任务发出抢占调度**。只是当前版本实现的算法稍显粗糙，不能保证调度总能成功，所以主动切换还有适用场合。
> 

> 这里有一个疑问，如果分配了两个逻辑处理器，每个逻辑处理器是有自己的任务队列的，两个goroutine任务分别给两个逻辑处理器执行，如果此时调用Gosched，某个任务被放到队列，那么这个逻辑处理器也没有别的任务执行了啊，它又会去执行队列里的那个任务？那不就表示这个方法根本没用吗.....
> 

==Goexit==

> Goexit立即终止当前任务（注意最外层的goroutine也属于当前任务），运行时确保所有已注册延迟调用被执行。该函数不会影响其他并发任务，不会引发异常，自然也就无法捕获。**如果在 main.main里调用Goexit，它会等待其他任务结束，然后让进程直接崩溃**。
> 

```go
func main() {
	exit := make(chan struct{})
	go func() {
		defer close(exit)
		defer println("a开始")

		func() {
			defer func() {
				//看有没有捕获到异常
				println("b开始，异常", recover() == nil)
			}()

			func() {
				println("c开始")
				runtime.Goexit() //立即终止整个调用堆栈
				println("c结束")   //不会执行
			}()
			println("b结束") //不会执行
		}()
		println("a结束") //不会执行
	}()

	<-exit
	println("main结束")
}
```

- 注意

> 无论身处哪一层，**Goexit都能立即终止整个调用堆栈**，这与return仅退出当前函数不同。标准库函数`os.Exit`可终止进程，但不会执行延迟调用。
> 
- 简单例子：创建了两个 `goroutine`，分别打印 `1~5000` 内的素数

```go
var wg sync.WaitGroup

func main() {
	//使用一个逻辑处理器
	runtime.GOMAXPROCS(1)
	//表示等待两个协程
	wg.Add(2)
	go printPrime("A")
	go printPrime("B")

	fmt.Println("开始执行")
	wg.Wait()
	fmt.Println("等待执行结束")

	fmt.Println("结束")
}

// printPrime 显示 5000 以内的素数值
func printPrime(gId string) {
	defer wg.Done()
next:
	for outer := 2; outer < 5000; outer++ {
		for inner := 2; inner < outer; inner++ {
			if outer%inner == 0 {
				continue next
			}
		}
		fmt.Printf("%s:%d\\n", gId, outer)
	}
	fmt.Println("完成", gId)
}
```

## 3.竞争状态

- 概述

> **如果两个或者多个 `goroutine` 在没有互相同步的情况下，访问某个共享的资源，并试图同时读和写这个资源**，就处于相互竞争的状态，这种情况被称作竞争状态`（race candition）`。
> 

> 竞争状态的存在是让并发程序变得复杂的地方，十分容易引起潜在问题。**对一个共享资源的读和写操作必须是原子化的**，换句话说，同一时刻只能有一个 `goroutine` 对共享资源进行读和写操作
> 
- 未加锁的数据不同步例子

> 这个最终的输出值为2或者4，虽然4是正确结果但是非常看两个goroutine的配合执行时间，但是一旦两个配合的并不是很好，那么未同步的共享变量会有一定概率发生修改值错误，比如下面如图的执行顺序
> 

```go
var (
	counter int //用来让goroutine访问的共享变量
	wg      sync.WaitGroup
)

func main() {
	wg.Add(2)
	go incCounter(1)
	go incCounter(2)

	wg.Wait()
	fmt.Println("最后的值为：", counter)
}

// 访问共享变量的函数
func incCounter(id int) {
	//修改完通知主线程
	defer wg.Done()

	for count := 0; count < 2; count++ {
		//捕获counter的值
		value := counter
		//当前goroutine放弃CPU执行权
		runtime.Gosched()
		//增加局部变量
		value++
		//修改共享变量
		counter = value
	}
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%205.png)

- race工具

> 根据我们上一章所提到的一个竞争检测器，就可以看到具体那些代码发生了冲突
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%206.png)

## 4.锁住共享资源

- 概述

> Go 语言提供了传统的同步 goroutine 的机制，就是对共享资源加锁。如果需要顺序访问一个整型变量或者一段代码，`atomic 和 sync` 包里的函数提供了很好的解决方案。下面我们了解一下 `atomic` 包里的几个函数以及 `sync` 包里的 `mutex` 类型。
> 

### 4.1 原子函数

- 概述

> 原子函数能够以很底层的加锁机制来同步访问整型变量和指针。我们可以用原子函数来修正竞争状态，
> 

==AddInt32(64)==

> 我们就拿上面的例子来修改成同步的，修改成下面这样无论怎么样都没有同步的问题了
> 

```go
// 访问共享变量的函数
func incCounter(id int) {
	//修改完通知主线程
	defer wg.Done()

	for count := 0; count < 2; count++ {
		// 安全地对 counter 加 1
		atomic.AddInt32(&counter, 1)
		runtime.Gosched()
	}
}
```

==LoadInt64&StoreInt64==

> 这两个函数提供了一种安全地读和写一个整型值的方式。下面的示例程序使用 `LoadInt64 和 StoreInt64` 来创建一个同步标志，这个标志可以向程序里多个 goroutine 通知某个特殊状态
> 

```go
var (
	shutdown int64 //shutdown 是通知正在执行的 goroutine 停止工作的标志
	wg       sync.WaitGroup
)

func main() {
	wg.Add(2)
	go doWork("A")
	go doWork("B")
	//让两个goroutine执行
	time.Sleep(1 * time.Second)

	//此时如果goroutine没有执行完也应该停止工作了
	fmt.Println("现在下班！！！")
	atomic.StoreInt64(&shutdown, 1)
	//等待收尾工作一起结束
	wg.Wait()
}

// doWork 用来模拟执行工作的 goroutine，检测之前的 shutdown 标志来决定是否提前终止
func doWork(name string) {
	defer wg.Done()

	for {
		fmt.Printf("正在做 %s 工作\\n", name)
		time.Sleep(250 * time.Microsecond)

		//检测标志位是否停止工作
		if atomic.LoadInt64(&shutdown) == 1 {
			fmt.Printf("正在停止 %s 工作", name)
			break
		}
	}
}
```

### 4.2 互斥锁

- 概述

> 另一种同步访问共享资源的方式是使用互斥锁（mutex）。互斥锁这个名字来自互斥（mutual exclusion）的概念。互斥锁用于在代码上创建一个临界区，保证同一时间只有一个 goroutine 可以执行这个临界区代码。
> 
- 代码

> 我们改造上面`AddInt32`的那个例子
> 

```go
// 访问共享变量的函数
func incCounter(id int) {
	//修改完通知主线程
	defer wg.Done()

	for count := 0; count < 2; count++ {
		lock.Lock()
		{ //注意代码块的左括号要另起一行
			//捕获counter的值
			value := counter
			//当前goroutine放弃CPU执行权
			runtime.Gosched()
			//增加局部变量
			value++
			//修改共享变量
			counter = value
		}
		lock.Unlock()
	}
}
```

- 相关使用注意事项

> • **将 Mutex作为匿名字段时，相关方法必须实现为 `pointer-receiver`即引用的类型必须是指针指针类型，否则会因复制导致锁机制失效。也可用嵌入 `*Mutex`来避免复制问题，但那需要专门初始化。**
> 

```go
type data struct {
	sync.Mutex
}
//就是这里如果不设置成指针类型那么就会发现锁根本没生效
func (d *data) test(s string) {
	d.Lock()
	defer d.Unlock()
	for i := 0; i < 5; i++ {
		println(i, s)
		time.Sleep(time.Second)
	}
}

func main() {
	wg.Add(2)
	var d data
	go func() {
		defer wg.Done()
		d.test("read")
	}()
	go func() {
		defer wg.Done()
		d.test("write")
	}()

	wg.Wait()
}
```

> 应将锁的粒度控制在最小范围内，尽早释放
> 

```go
func doSomething() {
	lock.Lock()
	url := cache["key"]
	http.Get(url)
	lock.Unlock()
}
//优化
func doSomething() {
	lock.Lock()
	url := cache["key"]
	lock.Unlock()	//这里切记不能写成defer，要不然get还是在里面
	http.Get(url)
}
```

- **Mutex不支持递归锁（不可重入锁），即便在同一goroutine下也会导致死锁**！！！！！！！！！！！！！同一个方法内重复获取，或者方法内递归调用自身（其他方法）重复获取都不行
- 对性能要求较高时，应避免使用`defer Unlock` 。
- 读写并发时，用`RWMutex`性能会更好一些。
- 对单个数据读写保护，可尝试用原子操作。
- 执行严格测试，尽可能打开数据竞争检查。

## 5.通道

- 概述

> 通道并非用来取代锁的，它们有各自不同的使用场景。**通道倾向于解决逻辑层次的并发处理架构并且简单不容易出错，而锁则用来保护局部范围内的数据安全**。
> 

> 当一个资源需要在`goroutine`之间共享时，通道在`goroutine`之间架起了一个管道，并提供了确保同步交换数据的机制。声明通道时，需要指定将要被共享的数据的类型。**可以通过通道共享内置类型、命名类型、结构类型和引用类型的值或者指针**。
> 
- 两种消息模型

> **Go官方更加推荐使用GSP通道以通信来替代内存共享，实现并发安全**
> 
> - `GSP(Communicating Sequential Process)`：作为CSP核心，通道（channel ）是显式的，要求操作双方必须知道数据类型和具体通道，并不关心另一端操作者身份和数量。可如果另一端未准备妥当，或消息未能及时处理时，会阻塞当前端。
> - actor模型：相比起来，Actor是透明的，它不在乎数据类型及通道，只要知道接收者信箱（缓冲区）即可。默认就是异步方式，发送方对消息是否被接收和处理并不关心。
> 
> ![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%207.png)
> 

==两者的对比==

> 
> 
> - csp 和actor 最大的不同是actor需要知道接收方的地址，需要知道将消息传递给谁，而channel不关心接收方和发送方是谁，只关心传递介质，相当于CSP把发送方和接收方给解耦了。
> - csp 是同步虽然buffer 支持有限量的异步，而且它关心接收者是否处理信息，没有处理就阻塞
> - actor 是异步的，只关心发给谁，不关心消息是否处理和传递通道，发送者不能假定发送的消息一定被收到和处理。Actor模型必须支持强大的模式匹配机制，因为无论什么类型的消息都会通过同一个通道发送过来，需要通过模式匹配机制做分发
> - 还有一个极好的特性，可以轻松地允许actor在其网络上的不同计算机上存储，实现分布式。消息分组和路由是自动处理的。
- go通道的底层实现

> 从底层实现上就是一个队列，主要就看采用同步还是异步，那么发送端和接收端就会有不同的行为，下面会细讲两类通道
> 
> - `同步模式（无缓冲的通道）`：同步模式下，发送和接收双方配对，然后直接复制数据给对方。如配对失败，则置入等待队列，直到另一方出现后才被唤醒。
> - `异步模式（有缓冲的通道）`：抢夺的则是数据缓冲槽。发送方要求有空槽可供写人,而接收方则要求有缓冲数据可读。需求不符时,同样加入等待队列,直到有另一方写入数据或腾出空槽后被唤醒。
- go通道的相关操作

> **使用make创建通道**
> 

```go
// 无缓冲的整型通道
unbuffered := make(chan int)
// 有缓冲的字符串通道
buffered := make(chan string, 10)
```

> **向通道发送值：向通道发送值或者指针需要用到`<-`操作符**
> 

```go
// 有缓冲的字符串通道
buffered := make(chan string, 10)
// 通过通道发送一个字符串
buffered <- "Gopher"
```

> **从通道里接收值：为了让另一个 goroutine 可以从该通道里接收到这个字符串，我们依旧使用`<-`操作符，但这次是一元运算符，当从通道里接收一个值或者指针时，`<-`运算符在要操作的通道变量的左侧**
> 

```go
// 从通道接收一个字符串
value := <-buffered
```

### 5.1 无缓冲的通道

- 概述

> **无缓冲的通道`（unbuffered channel）`是指在接收前没有能力保存任何值的通道。这种类型的通道要求发送 goroutine 和接收 goroutine 同时准备好，才能完成发送和接收操作。如果两个 goroutine没有同时准备好，通道会导致先执行发送或接收操作的 goroutine 阻塞等待。这种对通道进行发送和接收的交互行为本身就是同步的。其中任意一个操作都无法离开另一个操作单独存在**。
> 

生动的图示

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%208.png)

- 示例

> 在网球比赛中，两位选手会把球在两个人之间来回传递。选手总是处在以下两种状态之一：**要么在等待接球，要么将球打向对方。可以使用两个 goroutine 来模拟网球比赛，并使用无缓冲的通道来模拟球的来回**
> 
> - 首先我们建立一个无缓冲的通道，然后模拟发球，那个goroutine快就消费这个发球信息，就相当于谁发球了
> - 此时没有发球的就会被阻塞等待接球
> - 发球方消费后又将球击出然后被阻塞等待接球
> - 没有发球的就会检查通道里面的消息，如果对面接球失败的信息会在这里显示，同时尝试击球，如果击球成功继续这个循环

```go
// wg 用来等待程序结束
var wg sync.WaitGroup

func init() {
	rand.Seed(time.Now().UnixNano())
}
func main() {
	//创建一个无缓冲的通道模拟球场
	court := make(chan int)
	wg.Add(2) //两个goroutine即球场的两个人

	go play("LHJ", court)
	go play("PY", court)
	//发球
	court <- 1
	wg.Wait()
}

// 模拟人的击球动作
func play(name string, court chan int) {
	defer wg.Done()

	for {
		//对手接球是否成功，使用ok-idom模式处理数据
		ball, ok := <-court
		if !ok { //对面接球失败
			//我们赢了
			fmt.Printf("玩家 %s 胜利\\n", name)
			return
		}
		//随机一个数，来判断我们是否丢球
		n := rand.Intn(100)
		if n%13 == 0 { //如果不是13的倍数就代表我们接球失败
			fmt.Printf("玩家 %s 接球失败\\n", name)

			close(court)
			return
		}
		//如果双方都没有失误，那就进行继续游戏
		fmt.Printf("玩家 %s 击球 %d\\n", name, ball)
		ball++
		//击球
		court <- ball
	}
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%209.png)

- 上面代码的扩展点

> • **处理使用简单的收发、ok-idom模式，我们还可以使用range来收发消息**
• 及时用 close函数关闭通道引发结束通知，否则可能会导致死锁
> 

```go
func main(){
	done := make (chan struct {})
	c := make (chan int)
	go func() {
		defer close (done)
		for x := range c{	//循环获取消息，直到通道被关
			println(x)
		}
	}()
	c<-1
	c<-2
	c<-3
	close (c)
	<-done
}
```

> **通知可以是群体性的。也未必就是通知结束（就如下面有可能是通道被关闭了），可以是任何需要表达的事件。一次性事件用`close`效率更好，没有多余开销。连续或多样性事件，可传递不同数据标志实现。还可使用 `sync.Cond`实现单播或广播事件**。
> 

```go
func main() {
	ready := make(chan struct{})
	for i := 0; i < 3; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			println(id, "开始")
			//尝试从通道里获取信息，没有就阻塞，结束不阻塞可能是接收到消息或者通道被关闭
			<-ready
			println(id, "结束")
		}(i)
	}
	time.Sleep(time.Second)
	println("接受中~~~~")
	close(ready)
	wg.Wait()
}
```

### 5.2 有缓冲的通道

- 概述

> 有缓冲的通道`（buffered channel）`是一种在被接收前能存储一个或者多个值的通道。这种类型的通道并不强制要求 goroutine 之间必须同时完成发送和接收。通道会阻塞发送和接收动作的条件也会不同。**只有在通道中没有要接收的值时，接收动作才会阻塞。只有在通道没有可用缓冲区容纳被发送的值时，发送动作才会阻塞。这导致有缓冲的通道和无缓冲的通道之间的一个很大的不同：无缓冲的通道保证进行发送和接收的 goroutine 会在同一时间进行数据交换；有缓冲的通道没有这种保证**。
> 
- 生动图示

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%2010.png)

- 代码示例

> 让我们看一个使用有缓冲的通道的例子，这个例子管理一组`goroutine`来接收并完成工作。有缓冲的通道提供了一种清晰而直观的方式来实现这个功能
> 

```go
const (
	numberGoroutines = 4  // 要使用的 goroutine 的数量
	taskLoad         = 10 // 要处理的工作的数量
)
// wg 用来等待程序完成
var wg sync.WaitGroup

// init 初始化包，Go 语言运行时会在其他代码执行之前优先执行这个函数
func init() {
	rand.Seed(time.Now().Unix())
}

func main() {
	//创建一个缓冲容量为10的通道
	tasks := make(chan string, taskLoad)
	wg.Add(numberGoroutines)

	for i := 1; i <= numberGoroutines; i++ {
		go work(tasks, i)
	}

	//开始布置任务
	for task := 1; task <= taskLoad; task++ {
		tasks <- fmt.Sprintf("Task : %d", task)
	}
	//关闭通道
	close(tasks)
	wg.Wait()
}

// 模拟工人工作
func work(tasks chan string, worker int) {
	defer wg.Done()

	for {
		task, ok := <-tasks
		if !ok {
			//如果当前工人的全部任务完成了，也就是没有工作了通道被关闭就返回
			fmt.Printf("工人: %d : 完成了全部任务\\n", worker)
			return
		}

		fmt.Printf("工人: %d : 开始工作 %s\\n", worker, task)
		// 随机等一段时间来模拟工作
		sleep := rand.Int63n(100)
		time.Sleep(time.Duration(sleep) * time.Millisecond)
		// 显示我们完成了工作
		fmt.Printf("工人: %d : 完成 %s\\n", worker, task)
	}
}
```

### 5.3 两种通道的相关注意事项

- 通道的类型以及大小

> 缓冲区大小仅是内部属性，不属于类型组成部分。另外通道变量本身就是指针，可用等操作符判断是否为同一对象或`nil`。**虽然可传递指针来避免数据复制,但须额外注意数据并发安全**。
> 

```go
func main(){
	var a,b chan int = make (chan int,3),make (chan int)
	var c chan bool

	println(a == b)	//false
	println(c == nil)	//true

	fmt.Printf(%p, %d\\n",a,unsafe.sizeof (a))	//xxx 8
}
```

> **内置函数`cap和 len`返回缓冲区大小和当前已缓冲数量；而对于同步通道则都返回0，据此可判断通道是同步还是异步**。
> 

```go
func main({
	a, b:=make (chan int) , make (chan int,3)
	b<-1
	b<-2
	println("a: ", len(a), cap(a))//a:0 0
	println("b: ", len(b), cap(b))//b:2 3
}
```

==对于closed 或nil通道，发送和接收操作都有相应规则:==

> • 向已关闭通道发送数据，引发panic。
• 从已关闭接收数据，返回**已缓冲数据**或零值。
• 无论收发，nil通道都会阻塞。
> 

==单向==

> 通道默认是双向的，并不区分发送和接收端。但某些时候，我们可限制收发操作的方向来获得更严谨的操作逻辑。尽管可用make创建单向通道，但那没有任何意义。**通常使用类型转换来获取单向通道，并分别赋予操作双方**。
> 

```go
func main() {
	wg.Add(2)
	c := make(chan int)
	//单向发送通道
	var send chan<- int = c
	//单向接收通道
	var recv <-chan int = c

	go func() {
		defer wg.Done()

		for x := range recv {
			println(x)
		}
	}()

	go func() {
		defer wg.Done()
		defer close(c)
		for i := 0; i < 3; i++ {
			send <- i
		}
	}()
	wg.Wait()
}
```

- 注意事项

> • 不能在单向通道上做逆向操作，不能让发送去接收，反之亦然
• close不能用于接收端。
• 无法将单向通道重新转换回去，转换过程不可逆
> 

==选择==

> 如要同时处理多个通道，可选用`select`语句。它会随机选择一个可用通道做收发操作。
> 

```go
select{		//随机选择发送channel
case a <- i:
case b <- i*10:
}
//后续处理ok就会出现任一通道关闭，直接全部关不停止接收消息
select {	//随机选择可用 channel接收数据
case x, ok = <-a:
	name= "a"
case x, ok = <-b:
	name ="b"
}

if !ok{	//任一通道关闭直接停止接收
	return
}
```

> 如要等全部通道消息处理结束（ closed )，可将已完成通道设置为nil。这样它就会被阻塞，不再被select选中。
> 

```go
select {
case x,ok := <-a:
	if !ok{	//如果通道关闭，则设置为nil，阻塞
		a= nil
		break
	}
	println ("a"，x)
case x,ok := <-b:
	if!ok{
		b= nil
		break
	}
	println ("b",x)
}

if a== nil && b== nil{	//全部结束,退出循环
	return
}
```

> 即便是同一通道，也会随机选择case执行。
> 

```go
select{
case v,ok := <-C:
	println("a1;",v)
case V,ok := <-C:
	println("a2:",v)
}
```

> **当所有通道都不可用时，select 会执行 default 语句。如此可避开select阻塞，但须注意处理外层循环，以免陷入空耗。也可用 default处理一些默认逻辑**。
> 

```go
func main() {
	done := make(chan struct{})
	data := []chan int{ //数据缓冲区
		make(chan int, 3),
	}

	go func() {
		defer close(done)
		for i := 0; i < 10; i++ {
			select {
			case data[len(data)-1] <- i: //生产数据
			default: //当前通道已满，生成新的缓冲通道
				data = append(data, make(chan int, 3))
			}
		}
	}()
	//阻塞直到done中有数据
	<-done
	for i := 0; i < len(data); i++ {
		c := data[i]
		close(c) //接收到某个通道先关闭，因为通道缓冲区里肯定有东西，我们是等到done中有数据才进行的
		for x := range c {
			println(x)
		}
	}
}
```

==模式==

> 通常使用工厂方法将`goroutine`和通道绑定。
> 

```go
type receiver struct {
	sync.WaitGroup
	data chan int
}

func newReceiver() *receiver {
	r := &receiver{
		data: make(chan int),
	}
	r.Add(1)
	go func() {
		defer r.Done()
		for i := range r.data {
			println("收到：", i)
		}
	}()
	return r
}
func main() {
	r := newReceiver()
	r.data <- 1
	r.data <- 2

	close(r.data)
	r.Wait()
}
```

> • 鉴于通道本身就是一个并发安全的队列，可用作`ID generator 、Pool`等用途。
• 用通道实现信号量`（semaphore)`。下面的由于缓冲区的设置，那么速度快的两个任务会先输出，输出是成对的，两个满了后面的就会在获取信号哪里被阻塞
> 

```go
func main() {
	//设置四个逻辑处理器
	runtime.GOMAXPROCS(4)
	var wg sync.WaitGroup
	//最多允许两个并发同时执行
	sem := make(chan struct{}, 2)
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			sem <- struct{}{}        //获取信号
			defer func() { <-sem }() //最后释放信号

			time.Sleep(time.Second * 2)
			fmt.Println(id, time.Now())
		}(i)
	}
	wg.Wait()
}
```

> 标准库 time提供了 `timeout 和 tick channel`实现。
> 

```go
func main() {
	go func() {
		for {
			select {
			//这个case5秒以后才能进入
			case <-time.After(time.Second * 5):
				fmt.Println("timeout ...")
				os.Exit(0)
			}
		}
	}()

	go func() {
		//使用每秒一拍的节拍器通道，每秒从通道输出
		tick := time.Tick(time.Second)
		for {
			select {
			case <-tick:
				fmt.Println(time.Now())
			}
		}
	}()
	//使用空通道阻塞进程
	<-(chan struct{})(nil)
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%2011.png)

> 捕获`INT、TERM`信号，顺便实现一个简易的`atexit` 函数。这个函数类似于defer关键字，不过函数所做的工作时机是main函数结束之后
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E5%9B%9B%EF%BC%89%20%E5%B9%B6%E5%8F%91%EF%BC%88goroutine%EF%BC%89%E5%8F%8A%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%BC%8F/image%2012.png)

```go
var exits = &struct {
	sync.RWMutex //读写锁
	funcs        []func()
	signals      chan os.Signal //通知通道
}{}

func atexit(f func()) {
	exits.Lock()
	defer exits.Unlock()
	exits.funcs = append(exits.funcs, f)
}

func waitExit() {
	if exits.signals == nil {
		//初始化通道
		exits.signals = make(chan os.Signal)
		//就相当于通知了那个通道
		signal.Notify(exits.signals, syscall.SIGINT, syscall.SIGTERM)
	}
	exits.RLock()
	for _, f := range exits.funcs {
		defer f() //即便某些函数 panic，延迟调用也能确保后续函数执行，延迟调用按FILO顺序执行
	}
	exits.RUnlock()

	<-exits.signals
}

func main() {
	atexit(func() {
		println("exit1")
	})
	atexit(func() {
		println("exit2")
	})
	//
	waitExit()
}
```

==性能==

> **将发往通道的数据打包，减少传输次数，可有效提升性能。从实现上来说，通道队列依旧使用锁同步机制，单次获取更多数据（批处理)，可改善因频繁加锁造成的性能问题。虽然单次消耗更多内存，但性能提升非常明显。如将数组改成切片会造成更多内存分配次数**。
> 

==资源泄漏==

> **通道可能会引发 `goroutine leak`，确切地说，是指 goroutine处于发送或接收阻塞状态，但一直未被唤醒。垃圾回收器并不收集此类资源，导致它们会在等待队列里长久休眠，形成资源泄漏**。
> 

```go
main(){
	test()

	for {
		time.Sleep(time.Second)
		runtime.GC() //自己调用GC，也不会回收goroutine
	}
}

func test() {
	c := make(chan int)
	for i := 0; i < 10; i++ {
		go func() {
			<-c
		}()
	}
}
```

# 并发模式

- 概述

> **我们会学习 3 个可以在实际工程里使用的包，这3 个包分别实现了不同的并发模式。每个包从一个实用的视角来讲解如何使用并发和通道。我们会学习如何用这个包简化并发程序的编写，以及为什么能简化的原因**。
> 

## 1.runner

- 概述

> **`runner` 包用于展示如何使用通道来监视程序的执行时间，如果程序运行时间太长，也可以用 `runner` 包来终止程序。当开发需要调度后台处理任务的程序的时候，这种模式会很有用**
> 

```go
const timeout = 3 * time.Second

func main() {
	log.Println("进程开始")
	// 为本次执行分配超时时间
	r := runner.New(timeout)
	// 加入要执行的任务
	r.Add(createTask(), createTask(), createTask())
	//执行任务处理结果
	if err := r.Start(); err != nil {
		switch err {
		//如果执行超时，程序就会用错误码 1 终止。
		//如果接收到中断信号，程序就会用错误码 2 终止。
		case runner.ErrTimeout:
			log.Println("因超时而终止.")
			os.Exit(1)
		case runner.ErrInterrupt:
			log.Println("由于中断而终止.")
			os.Exit(2)
		}
	}
	log.Println("进程结束.")
}

// createTask 返回一个根据 id休眠指定秒数的示例任务
func createTask() func(int) {
	return func(id int) {
		log.Printf("处理 - 任务 #%d.", id)
		time.Sleep(time.Duration(id) * time.Second)
	}
}
```

- 分析以下里面涉及到的方法

==runner.struct==

> 这个runner包调用就会初始化这个结构体里面有四个字段：
> 
> 1. `interrupt chan os.Signal`：interrupt 通道收发 os.Signal 接口类型的值，用来从主机操作系统接收中断事件。
> 2. `complete chan error`：收发 error 接口类型值的通道。这个通道被命名为 complete，因为它被执行任务的 goroutine 用来发送任务已经完成的信号。如果执行任务时发生了错误，会通过这个通道发回一个 error 接口类型的值。如果没有发生错误，会通过这个通道发回一个 nil 值作为 error 接口值。
> 3. `timeout <-chan time.Time`：这个通道用来管理执行任务的时间。如果从这个通道接收到一个 time.Time 的值，这个程序就会试图清理状态并停止工作。
> 4. `tasks []func(int)`：最后一个字段被命名为 tasks，是一个函数值的切片。这些函数值代表一个接一个顺序执行的函数。会有一个与 main 函数分离的 goroutine 来执行这些函数。

==ErrTimeout&ErrInterrupt==

> 这两个runner包的成员变量就会读取complete里面的错误信息然后进行分类处理和显示
> 

==runner.New()==

> New 的工厂函数。这个函数接收一个 time.Duration 类型的值，并返回 Runner 类型的指针。这个函数会创建一个 Runner 类型的值，并初始化每个通道字段（结构体中的那些）。因为 task 字段的零值是 nil，已经满足初始化的要求，所以没有被明确初始化。每个通道字段都有独立的初始化过程
> 

```go
func New(d time.Duration) *Runner {
	return &Runner{
		interrupt: make(chan os.Signal, 1),
		complete:  make(chan error),
		timeout:   time.After(d),
	}
}
```

`interrupt的初始化`

> 通道 interrupt 被初始化为缓冲区容量为 `1` 的通道。这可以保证通道至少能接收一个来自语言运行时的 `os.Signal` 值，确保语言运行时发送这个事件的时候不会被阻塞。如果 goroutine没有准备好接收这个值，这个值就会被丢弃。**例如，如果用户反复敲 Ctrl+C 组合键，程序只会在这个通道的缓冲区可用的时候接收事件，其余的所有事件都会被丢弃。**
> 

`complete的初始化`

> 通道 complete 被初始化为无缓冲的通道。当执行任务的 goroutine 完成时，会向这个通道发送一个 error 类型的值或者 nil 值。之后就会等待 main 函数接收这个值。一旦 main 接收了这个 error 值，goroutine 就可以安全地终止了。
> 

`timeout的初始化`

> 最后一个通道 timeout 是用 time 包的 After 函数初始化的。After 函数返回一个time.Time 类型的通道。**语言运行时会在指定的 duration 时间到期之后，向这个通道发送一个 time.Time 的值**。
> 

==Add()&start()==

> 这两个方法：
> 
> - 前者就是添加任务到结构体的那个task切片数组中，
> - **后者就是调用run方法取这个数组里面任务声明单独的goroutine执行，创建 goroutine 后，Start 进入一个 select 语句，阻塞等待两个事件中的任意一个**。

==Duration==

> **是标准库的 time 包里的一个类型的声明。Duration 是一种描述时间间隔的类型，单位是纳秒（ns）。这个类型使用内置的 int64 类型作为其表示。在 Duration类型的声明中，我们把 int64 类型叫作 Duration 的基础类型。不过，虽然 int64 是基础类型，Go 并不认为 Duration 和 int64 是同一种类型。这两个类型是完全不同的有区别的类型**。
> 

## 2.pool

- 概述

> 这个包用于展示如何使用有缓冲的通道实现资源池，来管理可以在任意数量的goroutine之间共享及独立使用的资源。**这种模式在需要共享一组静态资源的情况（如共享数据库连接或者内存缓冲区）下非常有用。如果goroutine需要从池里得到这些资源中的一个，它可以从池里申请，使用完后归还到资源池里**。
> 
> - 本次介绍的是pool/pool.go，但在 Go 1.6 及之后的版本中，标准库里自带了资源池的实现`（sync.Pool）`。推荐使用
- 使用示例

> 代码使用 pool 包来管理一组模拟数据库连接的连接池。
> 

```go
const (
	maxGoroutines   = 25 // 要使用的 goroutine 的数量
	pooledResources = 2  // 池中的资源的数量
)

type dbConnection struct {
	ID int32
}

// Close 实现了 io.Closer 接口，以便 dbConnection可以被池管理。Close 用来完成任意资源的释放管理
func (dbConn *dbConnection) Close() error {
	log.Println("关闭: 连接", dbConn.ID)
	return nil
}

// idCounter 用来给每个连接分配一个独一无二的 id
var idCounter int32

// createConnection 是一个工厂函数，当需要一个新连接时，资源池会调用这个函数
func createConnection() (io.Closer, error) {
	//连接的id必须是并发安全的
	id := atomic.AddInt32(&idCounter, 1)
	log.Println("创建: 新链接", id)
	return &dbConnection{id}, nil
}
func main() {
	var wg sync.WaitGroup
	wg.Add(maxGoroutines)
	//这里直接传入函数名就好了，因为New里面的传入参数有函数的括号
	p, err := pool.New(createConnection, pooledResources)
	if err != nil {
		log.Println(err)
	}
	//用连接池中的连接完成查询
	for query := 0; query < maxGoroutines; query++ {
		// 每个 goroutine 需要自己复制一份要查询值的副本，不然所有的查询会共享同一个查询变量
		go func(q int) {
			performQueries(q, p)
			wg.Done()
		}(query)
	}

	wg.Wait()

	log.Println("连接池关闭")
	p.Close()
}

// performQueries 用来测试连接的资源池
func performQueries(query int, p *pool.Pool) {
	conn, err := p.Acquire()
	if err != nil {
		log.Println(err)
		return
	}
	//释放连接
	defer p.Release(conn)
	//随机睡眠个0~1s
	time.Sleep(time.Duration(rand.Intn(1000)) * time.Microsecond)
	log.Printf("查询ID[%d] 连接ID[%d]\\n", query, conn.(*dbConnection).ID)
}
```

## 3.work

- 概述

> **work 包的目的是展示如何使用无缓冲的通道来创建一个 goroutine 池，这些 goroutine 执行并控制一组工作，让其并发执行。在这种情况下，使用无缓冲的通道要比随意指定一个缓冲区大小的有缓冲的通道好，因为这个情况下既不需要一个工作队列，也不需要一组 goroutine 配合执行。无缓冲的通道保证两个 goroutine 之间的数据交换。这种使用无缓冲的通道的方法允许使用者知道什么时候 goroutine 池正在执行工作，而且如果池里的所有 goroutine 都忙，无法接受新的工作的时候，也能及时通过通道来通知调用者。使用无缓冲的通道不会有工作在队列里丢失或者卡住，所有工作都会被处理。**
> 
- 示例

> 使用 work 包来完成名字显示工作的测试程序。根据输出的值你可以看到每个无缓冲池中goroutine都是成对的完成通信，每秒一对的去显示输出
> 

```go
var names = []string{
	"A", "B", "C", "D", "E",
}

type namePrinter struct {
	name string
}

// Task 实现 Worker 接口
func (m *namePrinter) Task() {
	log.Println(m.name)
	time.Sleep(time.Second)
}

func main() {
	// 使用两个 goroutine 来创建工作池
	p := work.New(2)

	var wg sync.WaitGroup
	wg.Add(100 * len(names))

	for i := 0; i < 100; i++ {
		for _, name := range names {
			np := namePrinter{
				name: name,
			}

			go func() {
				// 将任务提交执行。当 Run 返回时任务就成功了
				p.Run(&np)
				wg.Done()
			}()
		}
	}

	wg.Wait()
	// 让工作池停止工作，等待所有现有的工作完成
	p.Shutdown()
}
```

- work源码

> 可以看到很清晰：
> 
> - 首先你要实现Task方法，因为goroutine的任务就是有这个决定的
> - 内部同样使用通道实现了任务之间的完成结束的过程传递，通过无缓冲的通道
> - 然后对于每一个任务都会有专门的range循环去阻塞直到Task任务被完成

```go
// Worker must be implemented by types that want to use
// the work pool.
type Worker interface {
	Task()
}

// Pool provides a pool of goroutines that can execute any Worker
// tasks that are submitted.
type Pool struct {
	work chan Worker
	wg   sync.WaitGroup
}

// New creates a new work pool.
func New(maxGoroutines int) *Pool {
	p := Pool{
		work: make(chan Worker),
	}

	p.wg.Add(maxGoroutines)
	for i := 0; i < maxGoroutines; i++ {
		go func() {
			for w := range p.work {
				w.Task()
			}
			p.wg.Done()
		}()
	}

	return &p
}

// Run submits work to the pool.
func (p *Pool) Run(w Worker) {
	p.work <- w
}

// Shutdown waits for all the goroutines to shutdown.
func (p *Pool) Shutdown() {
	close(p.work)
	p.wg.Wait()
}
```

## 4.总结

- 可以使用通道来控制程序的生命周期。
- 带 default 分支的 select 语句可以用来尝试向通道发送或者接收数据，而不会阻塞。
- 有缓冲的通道可以用来管理一组可复用的资源。
- 语言运行时会处理好通道的协作和同步。
- 使用无缓冲的通道来创建完成工作的 goroutine 池。
- 任何时间都可以用无缓冲的通道来让两个 goroutine 交换数据，在通道操作完成时一定保证对方接收到了数据。
# Go语言学习笔记（二）| Go语言的类型系统

type: Post
status: Published
date: 2022/10/15
summary: Go语言的类型系统
tags: Go
category: 技术栈

# 类型

## 1.变量

- 概述

> 作为静态类型语言，Go变量总是有固定的数据类型，类型决定了变量内存的长度和存储格式。我们只能修改变量值,无法改变类型。通过类型转换或指针操作，我们可用不同方式修改变量值，但这并不意味着改变了变量类型。
> 

==定义==

> 关键字 var用于定义变量，和C不同，类型被放在变量名后。**另外，运行时内存分配操作会确保变量自动初始化为二进制零值（zero value )，避免出现不可预测行为。如显式提供初始化值，可省略变量类型，由编译器推断**。
> 

`简短模式需要注意的地方`，注意与全局变量的使用区别哦；

> • 定义变量，同时显式初始化。
• 不能提供数据类型。
• 只能用在函数内部。
• 如果是对某个值的仅赋值更新，那么必须要有一个新变量被定义并且要在同一个作用域，不同就会变成新变量定义
> 

`简短模式的好处`

> • **简短定义在函数多返回值，以及 if/for/switch等语句中定义局部变量非常方便**。
• **在处理函数错误返回值时，退化赋值允许我们重复使用err变量,这是相当有益的**。
> 

```go
package main

func main() {
	var x int             //自动初始化为0
	var y = false         //自动识别类型
	var z, n int          //相同类型的多个变量
	var a, s = 100, "abc" //不同类型赋值

	var ( //以组的方式整理赋值多行
		b, c int
		d, e = 100, "bcd"
	)

	//简短模式
	f := 100
	g, h := 1, "cde"
	//简短模式并不总是重新定义变量,也可能是部分退化的赋值操作。注意i是新变量
	f, i := 200, 2

	i, err := os.Open("/dev/random")
	buf := make([]byte, 1024)
	j, err := i.Read(buf) //err退化赋值，j新定义

	//赋值操作必须保证左右值类型相同
	x, y := 1, 2
	x, y = y+3, x+2	//先计算出右值y+3、×+2，然后再对x、y变量赋值
	println(x, y)
}
```

- 未使用错误

> 编译器将未使用局部变量当做错误
> 

## 2.命名

规则

> 
> 
> - 以字母或下画线开始，由多个字母、数字和下画线组合而成。
> - 区分大小写。
> - 使用驼峰（camel case）拼写格式。局部变量优先使用短名。
> - 不要使用保留关键字。
> - 不建议使用与预定义常量、类型、内置函数相同的名字。
> - 专有名词通常会全部大写,例如escapeHTML。
> - 尽管Go支持用汉字等Unicode字符命名，但从编程习惯上来说，这并不是好选

==空标识符==

> 和 Python类似，Go也有个名为`“_”`的特殊成员（ blank identifier )。
> 
> - **通常作为忽略占位符使用,可作表达式左值,无法读取内容**。
> - 空标识符可用来临时规避编译器对未使用变量和导人包的错误检查。但请注意，它是预置成员,不能重新定义。

```go
import "strconv"

func main() {
	x, _ := strconv.Atoi("12") //忽略atoi的错误返回值
	println(x)
}
```

## 3.常量

- 概述

> 常量表示运行时恒定不可改变的值，通常是一些字面量。使用常量就可用一个易于阅读理解的标识符号来代替`“魔法数字”`，也使得在调整常量值时，无须修改所有引用代码。
> 
- 使用示例

> 
> 
> - 常量值必须是编译期可确定的字符、字符串、数字或布尔值。可指定常量类型，或由编译器通过初始化值推断,不支持C/C++数字类型后缀。
> - 不同作用域可定义同名常量
> - 如果显式指定类型，必须确保常量左右值类型一致，需要时可做显式转换右值不能超出常量类型取值范围,否则会引发溢出错误。
> - 常量值也可以是某些编译器能计算出结果的表达式，如 `unsafe.Sizeof、len、cap`等。
> - 在常量组中如不指定类型和初始化值,则与上一行非空常量右值（表达式文本）相同。

```go
func main() {
	const x, y int = 123, 0x22
	const s = "hello, world"
	const c = '我'

	const (
		i, f = 1, 0.123 // int, float64(默认)
		b    = false
	)

	{
		const x = 234
	}

	const (
		x, y int  = 99, -999
		b    byte = byte(x)  //x为int 显式转化为byte
		n         = uint8(y) //报错
	)

	const (
		x uint16 = 120
		y
		s = "abc"
		z
	)
	fmt.Printf("%T, %v\\n", y, y) 	//uint16, 120
	fmt.Printf("%T, %v\\n", z, z)	//string, abc
}
```

==枚举==

> Go并没有明确意义上的enum定义，不过可借助 iota标识符实现一组自增常量值来实现枚举类型。
> 

使用以及注意事项

> 
> 
> - 自增作用范围为常量组。可在多常量定义中使用多个 iota，它们各自单独计数，只须确保组中每行常量的列数量相同即可。
> - 如中断iota自增，则必须显式恢复。且后续自增值按行序递增，而非C enum那般按上一取值递增。
> - 自增默认数据类型为int,可显式指定类型。

```go
	const (
		x = iota //0
		y        //1
		z        //2
	)

	const (
		_  = iota
		KB = 1 << (10 * iota) //1 << (10 * 1)
		MB = 1 << (10 * iota) //1 << (10 * 2)
		GB = 1 << (10 * iota) //1 << (10 * 3)
	)

	const (
		_, _ = iota, iota * 10 //0, 0 * 10
		a, b                   //1, 1 * 10
		c, d                   //2, 2 * 10
	)

	const (
		a = iota //0
		b        //1
		c = 100  //100
		d        //100
		e = iota //还想恢复自增，那么显式声明 值为4，包括cd
		f        //5
	)

	const (
		a         = iota //int
		b float32 = iota //float32
		c         = iota //int，不显式的=iota，那么c就为b的类型
	)
```

在实际编码中，建议用自定义类型实现用途明确的枚举类型。但这并不能将取值范围限定在预定义的枚举值内。

```go
type color byte

const (
	black color = iota
	red
	blue
)

func test(c color) {
	println(c)
}
func main() {
	test(red)
	test(100)

	x := 2
	test(x)	//错误:cannot use x(type int) as type color in argument to test
}
```

==展开——常量与变量的区别==

> 
> 
> - 不同于变量在运行期分配存储内存（非优化状态)，常量通常会被编译器在预处理阶段直接展开，作为指令数据使用。
> - 数字常量不会分配存储空间,无须像变量那样通过内存寻址来取值，**所以常量拿不到地址**

显示声明类型的常量与无类型声明的常量

```go
const x = 100		//无类型声明的常量
const y byte = x	//直接展开×，相当于 const y byte = 100

const a int =100	//显式指定常量类型,编译器会做强类型检查
const b byte =a	//错误:cannot use a (type int) as type byte in const initializer
```

## 4.类型的本质

- 概述

> 如果给这个类型增加或者删除某个值，是要创建一个新值，还是要更改当前的值？如果是要创建一个新值，该类型的方法就使用值接收者。如果是要修改当前值，就使用指针接收者。这个答案也会影响程序内部传递这个类型的值的方式：**是按值做传递，还是按指针做传递。保持传递的一致性很重要**。
> 
- 类型表格概述

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%BA%8C%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E7%B1%BB%E5%9E%8B%E7%B3%BB%E7%BB%9F/image.png)

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%BA%8C%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E7%B1%BB%E5%9E%8B%E7%B3%BB%E7%BB%9F/image%201.png)

### 4.1 内置类型

- 值传递

> 内置类型是由语言提供的一组类型。我们已经见过这些类型，分别是数值类型、字符串类型和布尔类型。这些类型本质上是原始的类型。**因此，当对这些值进行增加或者删除的时候，会创建一个新值。基于这个结论，当把这些类型的值传递给方法或者函数时，应该传递一个对应值的副本**。
> 
- 地址传递

> 在go中主要就体现在*号的使用上，使用指针来共享参数的值或者返回值
> 
- 类型演示

> 
> 
> - 支持八进制、十六进制以及科学记数法。标准库math定义了各数字类型的取值范围。
> - 标准库strconv可在不同进制(字符串）间转换。
> - 使用浮点数时,须注意小数位的有效精度
> - 别名类型无序转换，可直接复制：`byte alias for uint8，rune alias for int32`，注意这不代表底层拥有相同结构的类型就属于相同类型了

```go
func main() {
	a, b, c := 100, 0144, 0x64
	fmt.Println(a, b, c)                    //100 100 100
	fmt.Printf("0b%b, %#o, %#x\\n", a, a, a) //0b1100100, 0144, 0x64
	fmt.Println(math.MinInt8, math.MaxInt8)	//-128 127

	a, _ := strconv.ParseInt("1100100", 2, 32)
	b, _ := strconv.ParseInt("0144", 8, 32)
	c, _ := strconv.ParseInt("64", 16, 32)

	println(a, b, c) //100 100 100

	println("0b" + strconv.FormatInt(a, 2)) //0b1100100
	println("0" + strconv.FormatInt(a, 8))  //0144
	println("0x" + strconv.FormatInt(a, 16))	//0x64

	//默认浮点数的类型时float64
	var a float32 = 1.1234567899
	var b float32 = 1.12345678
	var c float32 = 1.123456781

	println(a, b, c)        //+1.123457e+000 +1.123457e+000 +1.123457e+000
	println(a == b, a == c) //true true
	fmt.Printf("%v,%v,%v", a, b, c)	//1.1234568,1.1234568,1.1234568
}
```

### 4.2 引用类型

- 概述

> 所谓引用类型主要指下面几类：`切片、映射、通道、接口和函数`类型，当声明上述类型的变量时，**创建的变量被称作标头（header）值**。从技术细节上说，字符串也是一种引用类型。每个引用类型创建的标头值是包含一个指向底层数据结构的指针。每个引用类型还包含一组独特的字段，用于管理底层数据结构。因为标头值是为复制而设计的，所以永远不需要共享一个引用类型的值。标头值里包含一个指针，**因此通过复制来传递一个引用类型的值的副本，本质上就是在共享底层数据结构**，大白话没有*也是值传递
> 
- 与基本类型的区别

> 相比数字、数组等类型,引用类型拥有更复杂的存储结构。除分配内存外它们还须初始化一系列属性，诸如指针、长度,甚至包括哈希分布、数据队列等。
> 
- new函数与make函数

> ==new==：**内置函数 new按指定类型长度分配零值内存，返回指针，并不关心类型内部构造和初始化方式**。当然，new函数也可为引用类型分配内存，但这是不完整创建。以字典( map)为例，它仅分配了字典类型本身（实际就是个指针包装）所需内存，并没有分配键值存储内存，也没有初始化散列桶等内部属性,因此它无法正常工作。
> 

```go
func main(){
	p := new(map[string]int)
	q := *p
	q["a"] = 1	//报错：panic: assignment to entry in nil map
	fmt.Println(q)
}
```

> ==make==：**而引用类型则必须使用make函数创建，编译器会将make转换为目标类型专用的创建函数（或指令)，以确保完成全部内存分配和相关属性初始化**
> 

```go
func main() {
	m := mkmap()
	println(m["a"])

	s := mkslice()
	println(s[0])
}

func mkslice() []int {
	s := make([]int, 0, 10)
	s = append(s, 100)
	return s
}

func mkmap() map[string]int {
	m := make(map[string]int)
	m["a"] = 1
	return m
}
```

### 4.3 结构类型（自定义类型）

- 概述

> • 使用关键字type定义用户自定义类型,包括基于现有基础类型创建，或者是结构体、函数类型等。
• 使用小括号，也可以多个type定义成一个组
> 

```go
type flags byte

const (
	read  flags = 1 << iota //1
	write                   //2
	exec                    //4
)

func main() {
	f := read | exec
	fmt.Printf("%b\\n", f)		//5 0101
}

//类型分组
func main() {
	type ( //类型组
		user struct {
			name string
			age  uint8
		}

		event func(string) bool //函数类型
	)

	u := user{"Tom", 20}
	fmt.Println(u)

	var f event = func(s string) bool {
		println(s)
		return s != ""
	}

	println(f("abc")) //true

}
```

> 即便指定了基础类型,也只表明它们有相同底层数据结构，两者间不存在任何关系，属完全不同的两种类型。除操作符外，自定义类型不会继承基础类型的其他信息（包括方法)。不能视作别名,不能隐式转换,不能直接用于比较表达式。
> 

```go
func main() {
	type data int
	var d data = 10

	var x int = d //报错，即使底层类型一样，声明出来也不一样
	println(x)
	println(x == d) //不能隐式转换也能表达式
}
```

==未命名类型==

- 概述

> • 与有明确标识符的 bool、int、string等类型相比，数组、切片、字典、通道等类型与具体元素类型或长度等属性有关，**故称作未命名类型（unnamed type )**。
• 当然，可用 type为其提供具体名称,**将其改变为命名类型（named type )**。
> 
- 被视为同一类型的相同声明未命名类型

> 
> 
> - 具有相同基类型的指针。
> - 具有相同元素类型和长度的数组（array)。
> - 具有相同元素类型的切片（slice）。
> - 具有相同键值类型的字典（map)。
> - 具有相同数据类型及操作方向的通道（channel)。
> - 具有相同字段序列(字段名、字段类型、标签,以及字段顺序）的结构体( struct） 。
> - 具有相同签名（参数和返回值列表,不包括参数名）的函数（func) 。
> - 具有相同方法集（方法名、方法签名,不包括顺序）的接口（ interface )
- 不被视为相同类型进行相互转换

> 容易被忽视的是struct tag，它也属于类型组成部分,而不仅仅是元数据描
> 

```go
func main() {
	var a struct { //匿名结构类型，就是用struct tag去描述这个元数据
		x int    `x`
		s string `s`
	}

	var b struct {
		x int
		s string
	}

	b = a	//报错，两者不能相互赋值

	fmt.Printf(b)
}
```

> 同样，函数的参数顺序也属签名组成部分。
> 

```go
func main() {
	var a func(int, string)
	var b func(string, int)

	a = b	//报错
}
```

- 未命名相互转换的规则

> 
> 
> - 所属类型相同。
> - 基础类型相同，且其中一个是未命名类型。
> - 数据类型相同，将双向通道赋值给单向通道，且其中一个为未命名类型
> - 将默认值nil赋值给切片、字典、通道、指针、函数或接口。
> - 对象实现了目标接口。

```go
func main() {
	type data [2]int
	var d data = [2]int{1, 2} //基础类型相同，右值为未命名类型

	fmt.Println(d)
	//接收者<-发送的数据
	a := make(chan int, 2)
	var b chan <- int = a //双向通道转单向通道，b为未命名类型
	b <- 2
}
```

## 5.函数

### 5.1 函数的定义

- 概述

> 函数是结构化编程的最小模块单元。它将复杂的算法过程分解为若干较小任务，隐藏相关细节，使得程序结构更加清晰，易于维护。函数被设计成相对独立，通过接收输入参数完成一段算法指令，输出或存储相关结果。因此，函数还是代码复用和测试的基本单元。
> 
- func函数限制与优点

> 
> 
> - 无须前置声明。
> - 不支持命名嵌套定义（nested ) 。
> - 不支持同名函数重载（overload）
> - 不支持默认参数。
> - 支持不定长变参。
> - 支持多返回值。
> - 支持命名返回值。
> - 支持匿名函数和闭包。
> - **左花括号不能另起一行**
- 相关演示

> 
> 
> - 函数属于第一类对象（`first-class object`：指可在运行期创建，可用作函数参数或返回值，可存入变量的实体。最常见的用法就是匿名函数），具备相同签名(**参数及返回值列表**）的视作同一类
> - 使用命名类型，会方便一点

```go
// 定义函数类型
type FormatFunc func(string, ...interface{}) (string, error)

// 如果不使用自定义命名类型，这个参数签名会很长
func format(f FormatFunc, s string, a ...interface{}) (string, error) {
	return f(s, a...)
}
```

> 函数只能判断其是否为nil，不支持其他操作
> 

```go
func main() {
	println(a == nil)
	println(a == b)		//无效操作
}

func a() {}
func b() {}
```

> 
> 
> - **从函数返回局部变量指针是安全的，编译器会通过逃逸分析（ escape analysis)来决定是否在堆上分配内存**。通过go tool分析看就可以了
> - **函数内联（inline）对内存分配有一定的影响。如果下例中允许内联，那么就会直接在栈上分配内存**。
> - `内联函数普通函数的区别`：：**在调用内联函数的调用点，直接将函数的代码展开，没有栈桢的开辟和回退过程。而当调用一个普通函数时，会为函数开辟栈桢，压参入栈，生成汇编语言的调用，执行return的过程，相比之下就增加了函数的开销**

```go
func main() {
	var a *int = test()
	println(a, *a)
}

func test() *int {
	a := 0x100
	return &a
}
```

- 注意

> 虽然go的执行栈上限是GB级别的，但是还是要注意拷贝栈的复制成本
> 

==建议函数命名规则==

> 
> 
> - 通常是动词和介词加上名词，例如scan Words。
> - 避免不必要的缩写，printError 要比printErr 更好一些。
> - 避免使用类型关键字，比如 buildUserStruct看上去会很别扭。
> - 避免歧义，不能有多种用途的解释造成误解。
> - 避免只能通过大小写区分的同名函数。
> - 避免与内置函数同名，这会导致误用。
> - 避免使用数字，除非是特定专有名词，例如UTF8。
> - 避免添加作用域提示前缀。
> - 统一使用camel/pascal case 拼写风格。
> - 使用相同术语，保持一致性。
> - 使用习惯用语，比如 init表示初始化，is/has返回布尔值结果。
> - 使用反义词组命名行为相反的函数，比如 get/set、min/max等。

### 5.2 参数

- 概述

> Go对参数的处理偏向保守，不支持有默认值的可选参数，不支持命名实参。调用时，必须按签名顺序传递指定类型和数量的实参，**就算以`“_”`命名的参数也不能忽略**。
> 
- 具体使用

> 
> 
> - 在参数列表中,相邻的同类型参数可合并。
> - 参数可视作函数局部变量（形参是指函数定义中的参数，实参则是函数调用时所传递的参数），因此不能在相同层次定义同名变量。
- go中全是值传递

> **不管是指针、引用类型,还是其他类型参数，都是值拷贝传递`(pass-by-value)`。区别无非是拷贝目标对象，还是拷贝指针而已。在函数调用前，会为形参和返回值分配内存空间,并将实参拷贝到形参内存**。
> 
> - 从输出结果可以看出，尽管实参和形参都指向同一目标，但传递指针时依然被复制。

```go
func main(){
	x := 0x100
	p = &x
	//自己的地址：0xc00000a028，指向的地址：0xc00001c0b0
	fmt.Printf("自己的地址：%p，指向的地址：%v\\n", &p, p)

	test02(p)
}

func test02(p *int) {
	//自己的地址：0xc00000a038，指向的地址：0xc00001c0b0
	fmt.Printf("自己的地址：%p，指向的地址：%v\\n", &p, p)
}
```

- 指针参数的性能缺点与适用

> **表面上看，指针参数的性能要更好一些,但实际上得具体分析。被复制的指针会延长目标对象生命周期，还可能会导致它被分配到堆上，那么其性能消耗就得加上堆内存分配和垃圾回收的成本。其实在栈上复制小对象只须很少的指令即可完成，远比运行时进行堆内存分配要快得多。另外，并发编程也提倡尽可能使用不可变对象（只读或复制)，这可消除数据同步等麻烦**。
> 

```go
func main(){
	x := 100
	y := &x
	test02(y)
}

func test02(p *int) {
	go func() { //延长p的生命周期
		println(p)
	}()
}
```

> 当然，如果复制成本很高，或需要修改原对象状态，自然使用指针更好。要实现传出参数（out)，通常建议使用返回值。当然，也可继续用二级指针。
> 

```go
func main() {
	var p *int //指针p
	test(&p)
	//因为时双层指针，那么我们就要传递指针自己的地址而不是指针本身，地址复制还是这个地址，
	//但是传入进去指针的话又会复制一个新的指针，因为我们要通过别的函数来改变当前域的p指针的指向，那么
	//就不能允许这个指针的复制，因为别的函数改变的根本就不是我们这个指针，所以要直接传递指针的地址过去

	println(*p) //输出100，因为双层指针本身是地址，那么对着地址再取一次*得到指向的具体值
}

// 两级地址说实话就是取指针本身的地址
func test(p **int) {
	x := 100
	*p = &x
}
```

> 如果函数参数过多，建议将其重构为一个复合结构类型，也算是变相实现可选参数和命名实参功能。
> 

```go
type serverObj struct {
	address string
	port    int
	path    string
	timeout time.Duration
	log     *log.Logger
}

func newObj() *serverObj {	//默认参数
	return &serverObj{
		address: "47.101.23.1",
		port:    8080,
		path:    "/var/test",
		timeout: time.Second * 5,
		log:     nil,
	}
}
func server(obj *serverObj) {}

func main() {
	obj := newObj()
	obj.port = 8081

	server(obj)
}
```

==变参==

> 变参本质上就是一个切片。只能接收一到多个同类型参数，且必须放在列表尾部。
> 

```go
func main(){
	test("aaa", 1, 2, 3, 4)
}
//[1 2 3 4]
func test(s string, a ...int) {
	fmt.Printf("%T, %v\\n", a, a) //类型和值
}
```

> 既然变参是切片（指向数组的指针），那么参数复制的仅是切片自身，并不包括底层数组，也因此可修改原数据。如果需要，可用内置函数copy 复制底层数据。
> 

### 5.3 返回值

- 注意事项以及演示

> 
> 
> - 有返回值的函数,必须有明确的return终止语句。
> - 除非有异常错误等，或者无 break的死循环，则无须return终止语句。
> - 借鉴自动态语言的多返回值模式，函数得以返回更多状态，尤其是error模式，多返回值列表必须使用括号，稍有不便的是没有元组（tuple）类型，也不能用数组、切片接收，但可用`“_”`忽略掉不想要的返回值。多返回值可用作其他函数调用实参，或当作结果直接返

==命名返回值==

> 对返回值命名和简短变量定义一样，优缺点共存。
> 
> - 从这个简单的示例可看出，命名返回值让函数声明更加清晰，同时也会改善帮助文档和代码编辑器提示。

```go
func paging(sql string, index int) (count int, pages int, err error) {}
```

> 命名返回值和参数一样,可当作函数局部变量使用，最后由return隐式返回
> 

```go
func div(x, y int) (z int, err error) {
	if y == 0 {
		err = errors.New("除数不能为0")
		return//相当于返回 z和err
	}
	z = x / y
	return	//相当于返回 z和err
}
```

> 这些特殊的“局部变量”会被不同层级的同名变量遮蔽。好在编译器能检查到此类状况，只要改为显式return返回即可。
> 

```go
func add(x, y int) (z int) {
	{
		z := x + y	//同名遮蔽了
		return //这里会报错，只需改成return z
	}
	return
}
```

> 
> 
> - 除遮蔽外，我们还必须对全部返回值命名，否则编译器会搞不清状况。显然编译器在处理return语句的时候，会跳过未命名返回值，无法准确匹配
> - 如果返回值类型能明确表明其含义，就尽量不要对其命名。

### 5.4 匿名函数

- 概述

> **匿名函数是指没有定义名字符号的函数。除没有名字外，匿名函数和普通函数完全相同。最大区别是，我们可在函数内部定义匿名函数，形成类似嵌套效果。匿名函数可直接调用，保存到变量，作为参数或返回值**。同样未使用的匿名函数会报错
> 
- 基本使用

> 不同地方的使用示例
> 

```go
func main() {
	//直接使用
	func(s string) {
		println(s)
	}("hello") //后面这个括号就是传入的参数

	//赋值给变量
	add := func(x, y int) int {
		return x + y
	}
	//作为参数
	println(add(1, 2))
	test(func() {
		println("world!")
	})

	//将匿名函数赋值给变量，与为普通函数提供名字标识符有着根本的区别。
	//当然编译器会为匿 名函数生成一个“随机”符号名。
	add01 := test02()
	println(add01(1, 2))
}

// 作为参数
func test(f func()) {
	f()
}
```

> 普通函数和匿名函数都可作为结构体字段，或经通道传递。
> 

```go
func testStruct() {
	type calc struct { //定义结构体类型
		mul func(x, y int) int //函数类型字段
	}

	x := calc{
		mul: func(x, y int) int {
			return x * y
		},
	}

	println(x.mul(2, 3))
}

func testChannel() {
	c := make(chan func(int, int) int, 2)
	//将右边函数输入到通道中
	c <- func(x, y int) int {
		return x + y
	}
	//通过通道将函数需要的值进行传递，并输出
	println((<-c)(1, 2))
}
```

- 总结

> 
> 
> - 除闭包因素外,匿名函数也是一种常见重构手段。可将大函数分解成多个相对独立的匿名函数块，然后用相对简洁的调用完成逻辑流程，以实现框架和细节分离。
> - 相比语句块，匿名函数的作用域被隔离（不使用闭包)，不会引发外部污染，更加灵活。没有定义顺序限制,必要时可抽离,便于实现干净、清晰的代码层次。

==闭包==

> 闭包 `（closure）`是在其词法上下文中引用了自由变量的函数，或者说是函数和其引用的环境的组合体。这种说明太学术范儿了，很难理解，**我们先看一个例子：就这段代码而言，test 返回的匿名函数会引用上下文环境变量x。当该函数在main中执行时，它依然可正确读取x的值,这种现象就称作`闭包`**。
> 

```go
func main() {
	f := test(111)
	f()
}

func test(x int) func() {
	return func() {
		println(x)
	}
}
```

- 底层如何实现？

> 通过输出指针，我们注意到闭包直接引用了原环境变量。分析汇编代码，你会看到返回的不仅仅是匿名函数，还包括所引用的环境变量指针。**所以说，闭包是函数和引用环境的组合体更加确切。在go中的官方定义上返回的是一个`funcval`结构**
> 
> 1. 进入test函数，获取环境变量x的地址
> 2. 继续执行，回到main函数
> 3. 将test的返回值（包含匿名函数和环境变量地址）保存到寄存器
> 4. 然后继续进入到匿名函数中
> 5. 通过寄存器读取环境变量地址

```go
func main(){
	f := test(0x111)
	f()
}
func test(x int) func() {
	println(&x)		  //0xc00004df68
	return func() {
		println(&x, x) //0xc00004df68 273
	}
}
```

- 闭包特性的应用

> **正因为闭包通过指针引用环境变量，那么可能会导致其生命周期延长，甚至被分配到`堆内存`。另外，还有所谓“延迟求值”的特性。底层go就会分析这个闭包使用的变量的作用范围来适当调整变量的作用域，宏观上来说就是内存逃逸**
> 

> 现在看下面代码的输出：**for 循环复用局部变量i，那么每次添加的匿名函数引用的自然是同一变量。添加操作仅仅是将匿名函数放入列表，并未执行。因此，当main执行这些函数时，它们读取的是环境变量i最后一次循环时的值。**`你如果不想要这样，那么可以在for循环中声明一个新的变量去接受i的值`
> 

> **同样可以看到使用goroutine结合闭包，这里使用闭包避免的go中for循环的变量是会发生变化的，那么我们就可以使用匿名函数的参数列表传入当前for的变量去复制一份，避免跟着主循环变量发送变化**
> 

```go
func main() {
	for _, f := range test() { //迭代执行匿名函数
		f()
	}
}

func test() []func() {
	var s []func()

	for i := 0; i < 2; i++ {
		s = append(s, func() { //将多个匿名函数添加到列表
			//0xc00001c040 2
			//0xc00001c040 2
			println(&i, i)
		})
	}
	return s
}

for _, u := range urls {
		done.Add(1)
		go func(u string) {
			defer done.Done()
			ConcurrentMutex(u, fetcher, f)
		}(u)
	}
```

> 多个匿名函数引用同一环境变量，任何的修改行为都会影响其他函数取值，在并发模式下可能需要做同步处理。
> 

```go
func main() {
	a, b := test(100)
	a() //100
	b() //110
}

func test(x int) (func(), func()) {
	//分属于两个函数中的x却是共享的
	return func() {
			println(x)
			x += 10
		}, func() {
			println(x)
		}
}
```

### 5.5 延迟调用

- 概述

> **语句`defer`向当前函数注册稍后执行的函数调用。这些调用被称作延迟调用，因为它们直到当前函数执行结束前才被执行，常用于资源释放、解除锁定，以及错误处理等操作**。多个延迟调用遵循`前进后出`
> 

```go
func main() {
	f, err := os.Open("./main.go")
	if err != nil {
		log.Fatalln(err)
	}

	defer f.Close() //仅仅就打上关闭标记，等到main退出才执行
}
```

> **注意，延迟调用注册的是调用，必须提供执行所需参数（哪怕为空)。参数值在注册时被复制并缓存起来。如对状态敏感，可改用指针或闭包。延迟调用可修改当前函数命名返回值，但其自身返回值被抛弃**。
> 

```go
func main() {
	x, y := 1, 2
	defer func(a int) {
		//defer x , y = 1 202，x是另外复制的
		println("defer x , y =", a, y)
	}(x)

	x += 100 //对x的修改不会影响延迟函数，因为上面是闭包引用会另外复制
	y += 200
	println(x, y)
}
```

> 编译器通过插入额外指令来实现延迟调用执行，而return和 异常语句都会终止当前函数流程，引发延迟调用。另外，return语句不是ret汇编指令，它会先更新返回值。
> 

```go
func main() {
	//test: 200
	println("test:", test())
}

func test() (z int) {
	defer func() {
		//defer: 100
		println("defer:", z)
		z += 100	//修改命名返回值
	}()
	return 100//实际执行次序:z=100, call defer, ret
}
```

==误用——延迟调用不能乱用==

> **千万记住，延迟调用在函数结束时才被执行。不合理的使用方式会浪费更多资源，甚至造成逻辑错误**。
> 
> - `案例`：**循环处理多个日志文件，不恰当的defer导致文件关闭时间延长，可以看到下面for循环中的文件关闭，因为这个文件关闭是在main函数结束后才会执行，那么每次循环都会延长f的生命周期导致占资源**

```go
func main() {
	for i := 0; i < 10000; i++ {
		path := fmt.Sprintf("./log/%d.txt", i)

		f, err := os.Open(path)
		if err != nil {
			log.Println(err)
			continue
		}

		defer f.Close()
	}
}
```

- 性能方面

> **相比直接用CALL汇编指令调用函数，延迟调用则须花费更大代价。这其中包括注册、调用等操作，还有额外的缓存开销**。我们简单写一个测试用例
> 

```go
var s sync.Mutex

func call() {
	s.Lock()
	s.Unlock()
}

func callByLazy() {
	s.Lock()
	defer s.Unlock()
}

// 这里别自己起名，压力测试必须以Benchmark开头
func BenchmarkCall(b *testing.B) {
	for i := 0; i < b.N; i++ {
		call()
	}
}

func BenchmarkLazy(b *testing.B) {
	for i := 0; i < b.N; i++ {
		callByLazy()
	}
}
```

`输出`

> 相差几倍的结果足以引起重视。尤其是那些性能要求高且压力大的算法，应避免使用延迟调用。
> 

```bash
BenchmarkCall-12        100000000               10.95 ns/op
BenchmarkLazy-12        86432913                13.61 ns/op
```

### 5.6 错误处理

- 概述

> 返古的错误处理方式，是Go被谈及最多的内容之一。有人戏称做`“Stuck in 70's”`，可见它与流行趋势背道而驰。
> 

==error==

> **官方非常推荐返回error状态，在标准库中将error定义为接口，可以向下增强自己的异常错误，提供相关的创建函数，方便我们创建简单错误问题的error对象，典型的就是`errors.New`方法，错误变量通常以err 作为前缀，且字符串内容全部小写，没有结束标点，以便于嵌入到其他格式化字符串中输出。全局错误变量并非没有问题，因为它们可被用户重新赋值，这就可能导致结果不匹配。不知道以后是否会出现只读变量功能，否则就只能依靠自觉了。与`errors.New`类似的还有`fmt.Errorf`，它返回一个格式化内容的错误对象**。
> 
- 自定义错误类型

> 这样我们就可以快速定位到哪里出错了
> 

```go
type DivError struct {
	x, y int
}

//自定义异常类型
func (DivError) Error() string {
	return "除数为0"
}

func div(x, y int) (int, error) {
	if y == 0 {
		//返回我们自定义异常，异常对象的参数记得指定
		return 0, DivError{x, y}
	}
	return x / y, nil
}

func main() {
	z, err := div(1, 0)
	if err != nil {
		switch e := err.(type) {
		case DivError:	//如果出现的异常使我们自定义的就走我们的逻辑
			fmt.Println(e, e.x, e.y)
		default:	//默认
			fmt.Println(e)
		}
		//日志打印
		log.Fatalln(err)
	}
	println(z)
}
```

- 注意

> 在正式代码中，我们不能忽略error返回值，应严格检查，否则可能会导致错误的逻辑状态。调用多返回值函数时，除 error外，其他返回值同样需要关注。（以`os.File.Read`方法为例,它会同时返回剩余内容和`EOF`）
> 
- 实际开发中异常处理的代码美观建议

> 大量函数和方法返回`error`，使得调用代码变得很难看，一堆堆的检查语句充斥在代码行间。解决思路有:
> 
> - 使用专门的检查函数处理错误逻辑（比如记录日志），简化检查代码。
> - 在不影响逻辑的情况下，使用defer延后处理错误状态（err退化赋值）。
> - 在不中断逻辑的情况下，将错误作为内部状态保存，等最终“提交”时再处理。

==panic/recover==

> 这个就很类似于Java中的`try/catch`的结构化异常处理，比较有趣的是，它们是内置函数而非语句。
> 
> - **panic会立即中断当前函数流程，执行延迟调用。**
> - **而在延迟调用函数中，recover可捕获并返回panic提交的错误对象。**

```go
func panic(v any)
func recover() any

func main() {
	defer func() {
		if err := recover(); err != nil {//捕获错误
			println("!!")
			log.Fatalln(err)

		}
	}()

	panic("dead")   //引发错误
	println("exit") //这个永远不会执行
}
```

> 异常传递，无论是否执行recover，所有延迟调用都会被执行。但中断性错误会沿调用堆栈向外传递，要么被外层捕获,要么导致进程崩溃。
> 

```go
func main() {
	defer func() {
		log.Println(recover())
	}()

	test()
}

func test() {
	//test.2
	//test.1
	//2022/09/29 22:50:16 dead
	defer println("test.1")
	defer println("test.2")

	panic("dead")
}
```

> 连续调用panic，仅最后一个会被recover捕获。
> 
> - 可以看到下面执行到最后一个panic后开始执行延迟函数，第一个被执行的是后面的延迟函数，里面又是新的异常，那么前一个异常就会顶掉；后续recover获取到也是新的panic

```go
//输出：
//2022/09/29 23:04:25 dead01
//2022/09/29 23:04:25 fatal

func main() {
	defer func() {
		for {
			if err := recover(); err != nil {
				log.Println(err)
			} else {
				log.Fatalln("fatal")
			}
		}

	}()

	defer func() {
		panic("dead01")	//重新抛出异常
	}()

	panic("dead02")
}
```

> **在延迟函数中 panic，不会影响后续延迟调用执行。而 recover 之后 panic可被再次捕获。另外`recover 必须在延迟调用函数中执行才能正常工作`**。
> 

```go
//2022/09/29 23:15:36 <nil>
//2022/09/29 23:15:36 catch: dead
func catch() {
	log.Println("catch:", recover())
}

func main() {
	defer catch()                //成功捕获
	defer log.Println(recover()) //同样没有捕获到
	defer recover()              //没有捕获到

	panic("dead")
}
```

> 考虑到recover 特性，如果要保护代码片段，那么只能将其重构为函数调用
> 

```go
func main() {
	test(0, 5)
}

func test(x, y int) {
	z := 0

	func() {	//利用匿名函数保护z=x/y
		defer func() {
			if recover() != nil {
				z = 0
			}
		}()
		z = x / y
	}()

	println("x / y :", z)
}
```

> 调试阶段，可使用`runtime/debug.PrintStack`函数输出完整调用堆栈信息
> 

```go
func main() {
	defer func() {
		if err := recover(); err != nil {
			debug.PrintStack()
		}
	}()
	test()
}

func test() {
	panic("dead")
}
```

- 总结

> • **建议：除非是不可恢复性、导致系统无法正常工作的错误，否则不建议使用panic。**
• **例如:文件系统没有操作权限，服务端口被占用，数据库未启动等情况。**
> 

## 6.方法

### 6.1 方法的定义

- 概述

> 方法是与对象实例绑定的特殊函数。
> 

> 方法是面向对象编程的基本概念，用于维护和展示对象的自身状态。对象是内敛的，每个实例都有各自不同的独立特征，以属性和方法来暴露对外通信接口。普通函数则专注于算法流程，通过接收参数来完成特定逻辑运算，并返回最终结果。换句话说，方法是有关联状态的,而函数通常没有。
> 
- 方法与函数的定义

> **方法和函数定义语法区别的在于前者有前置实例接收参数（ receiver 就是允许那个类型使用这个方法)，编译器以此确定方法所属类型。在某些语言里，尽管没有显式定义，但会在调用时隐式传递this实例参数**。
> 
> - 可以为当前包，以及除接口和指针以外的任何类型定义方法。
> - 方法同样不支持重载（overload )。receiver 参数名没有限制，按惯例会选用简短有意义的名称（不推荐使用this、self )。如方法内部并不引用实例，可省略参数名仅保留类型。

```go
type N int

func (N) test() {
	println("!!!")
}
```

> 方法可看作特殊的函数,那么receiver 的类型自然可以是基础类型或指针类型，这会关系到调用时对象实例是否被复制。
> 

```go
func (n N) value() {
	n++
	fmt.Printf("v:%p, %v\\n", &n, n) //v:0xc00001c0b0, 26	复制
}

func (n *N) pointer() {
	(*n)++
	fmt.Printf("p: %p, %v\\n", n, *n) //p:0xc00001c098, 26
}

func main() {
	var a N = 25

	a.value()
	a.pointer()

	fmt.Printf("a:%p, %v\\n", &a, a)	//a:0xc00001c098, 26
}
```

> 可使用实例值或指针调用方法，编译器会根据方法 receiver类型自动在基础类型和指针类型间转换
> 

```go
func main() {
	var a N = 25
	p := &a
	p2 := p&	//不可以这样多级赋值
	a.value()   //v:0xc00001c0b0, 26
	a.pointer() //p: 0xc00001c098, 26

	p.value()   //v:0xc00001c0e0, 27
	p.pointer() //p: 0xc00001c098, 27
}
```

> 指针类型的receiver必须是合法指针（包括nil)，或能获取实例地址。**将方法看作普通函数，就能很容易理解 receiver的传参方式**。
> 

```go
type X struct {
}

func (x *X) test() {
	println("hi", x)
}
func main() {
	var a *X
	a.test() //相当于test(nil)
	x{}.test() //报错
}
```

- receiver类型的选择

> 说了这么多receiver就是方法的调用者，也就是方法内的实例对象，方法的第一个括号里面所要表明的
> 
> - 要修改实例状态，用`T`。
> - 无须修改状态的小对象或固定值,建议用`T`。
> - 大对象建议用`T`，以减少复制成本。
> - 引用类型、字符串、函数等指针包装对象，直接用`T`。
> - 若包含Mutex等同步字段,用`T`，避免因复制造成锁操作无效。
> - 其他无法确定的情况，都用`T`。

### 6.2 匿名字段

- 概述

> 可以像访问匿名字段成员那样调用其方法，由编译器负责查找。
> 

```go
type data struct {
	sync.Mutex
	buf [1024]byte
}

func main() {
	d := data{} //相当于使用无参构造出一个结构体
	d.Lock()    //此时我们没有指出结构体中那个字段成员使用这个lock方法，编译器自己寻找
	defer d.Unlock()	//refer一定会在一个函数和方法全部执行完之后才会执行。可以理解成析构函数
}
```

> **方法名同名遮蔽，实现重写功能，可以看到结构体与结构体之间体现出一个父子继承的关系，那么对应的方法也好体现出重写的关系**，尽管能直接访问匿名字段的成员和方法,但它们依然不属于继承关系。
> 

```go
type user struct {
}

type manager struct {
	user
}

func (user) toString() string {
	return "user"
}

func (m manager) toString() string {
	return m.user.toString() + ";manager"
}

func main() {
	var m manager
	println(m.toString())
	println(m.user.toString())
}
```

### 6.3 方法集

- 概述

> 类型有一个与之相关的方法集`（method set)`，这决定了它是否实现某个接口，下面规定了一个类型与之相关的方法集判定方法
> 
> - 类型`T`方法集包含所有`receiver T`方法。
> - 类型`T`方法集包含所有`receiver T ＋*T`方法。
> - 匿名嵌入`S,T`方法集包含所有`receiver S`方法。
> - 匿名嵌入`S，T`方法集包含所有`receiverS +*S`方法。
> - 匿名嵌入`S或*S,*T`方法集包含所有`receiver S＋*S`方法。
- 使用反射测试

> 这里很怪，楼主使用1.19通过reflect.TypeOf(a)获取不到这些方法的信息，都为空；书上获取出来是这样的
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%BA%8C%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E7%B1%BB%E5%9E%8B%E7%B3%BB%E7%BB%9F/image%202.png)

```go
type S struct {
}

type T struct {
	S //匿名字段
}

func (S) sVal() {
}
func (*S) sPtr() {
}
func (T) tVal() {
}
func (*T) tPtr() {
}

func methodSet(a interface{}) {
	t := reflect.TypeOf(a)

	for i, n := 0, t.NumMethod(); i < n; i++ {
		m := t.Method(i)
		fmt.Println(m.Name, m.Type)
	}
}

func main() {
	var t T
	methodSet(t)
	println("----------")
	methodSet(&t)
}
```

- 总结

> 方法集仅影响接口实现和方法表达式转换，与通过实例或实例指针调用方法无关。实例并不使用方法集，而是直接调用(或通过隐式字段名)。很显然，匿名字段就是为方法集准备的。否则，完全没必要为少写个字段名而大费周章。
> 

> **面向对象的三大特征“封装”、“继承”和“多态”，Go 仅实现了部分特征它更倾向于“组合优于继承”这种思想。将模块分解成相互独立的更小单元，分别处理不同方面的需求，最后以匿名嵌入方式组合到一起，共同实现对外接口。而且其简短一致的调用方式，更是隐藏了内部实现细节**。
> 
- 组合模式的优点

> **组合没有父子依赖，不会破坏封装。且整体和局部松耦合，可任意增加来实现扩展。各单元持有单一职责，互无关联，实现和维护更加简单。尽管接口也是多态的一种实现形式，但我认为应该和基于继承体系的多态分离开来。**
> 

### 6.4 表达式

- 概述

> 方法和函数一样，除直接调用外，还可赋值给变量，或作为参数传递。依照具体引用方式的不同,可分为expression和 value 两种状态。
> 

==Method Expression==

> 通过类型引用的 `method expression`会被还原为普通函数样式，receiver是第一参数，调用时须显式传参。至于类型，可以是T或*T，只要目标方法存在于该类型方法集中即可。
> 
> - 尽管N方法集包装的test方法 receiver类型不同，但编译器会保证按原定义类型拷贝传值。

```go
type N int

func (n N) test() {
	fmt.Printf("test.n: %p, %d\\n", &n, n)
}

func main() {
	var n N = 25
	fmt.Printf("main.n: %p, %d\\n", &n, n)

	//实际上跟n.test()	一模一样
	f1 := N.test //把方法相当于实例成一个表达式，在通过传入参数（调用者就是参数）的形式调用方法
	f1(n)

	f2 := (*N).test
	f2(&n)

	//也可以直接表达式方法调用
	N.test(n)
	(*N).test(&n)
}
```

==Method Value==

> **基于实例或指针引用的method value**，参数签名不会改变，依旧按正常方式调用。**但当method value被赋值给变量或作为参数传递时，会立即计算并复制该方法执行所需的receiver对象，与其绑定，以便在稍后执行时,能隐式传入receiver参数**。
> 

```go
type N int

func (n N) test() {
	fmt.Printf("test.n: %p, %d\\n", &n, n)
}

func main() {
	var n N = 100
	p := &n

	n++
	//复制n的值
	f1 := n.test //把方法相当于实例成一个表达式，在通过传入参数（调用者就是参数）的形式调用方法

	n++
	//同理会复制n的值
	f2 := p.test

	n++
	fmt.Printf("main.n: %p, %d\\n", &n, n)

	f1()
	f2()
}
```

> 编译器会为method value 生成一个包装函数，实现间接调用。至于 receiver复制，和闭包（闭包就是能够读取其他函数内部变量的函数）的实现方法基本相同，打包成funcval，经由DX寄存器传递。
> 

> • 当`method value`作为参数时，会复制含调用参数在内的整个`method value`
• 如果目标方法的调用参数是指针那么复制的仅仅是指针
> 

```go
type N int

func (n N) test() {
	fmt.Printf("test.n: %p, %d\\n", &n, n)
}

func (n *N) test() {	//这里如果是指针那么全部的n都是103,而不是每个值都复制一份自己的
	fmt.Printf("test.n: %p, %d\\n", &n, n)
}
func call(m func()) {
	m()
}
func main() {
	var n N = 100
	p := &n

	fmt.Printf("main.n: %p, %d\\n", &n, n)
	n++
	call(n.test)

	n++
	call(p.test)
}
```

> 只要 receiver参数类型正确,使用nil同样可以执行。即带地址传递的那些才可以跟nil互动
> 

```go
type N int

func (N) value() {
}

func (*N) pointer() {

}

func main() {
	var p *N

	p.value()
	p.pointer()

	(*N)(nil).pointer()
	(*N).pointer(nil)
}
```

## 7.接口

### 7.1 定义

- 概述

> 接口代表一种调用契约，是多个方法声明的集合。在某些动态语言里，接口 `（ interface）`也被称作协议`（ protocol )`。**准备交互的双方，共同遵守事先约定的规则，使得在无须知道对方身份的情况下进行协作。接口要实现的是做什么,而不关心怎么做，谁来做。**
> 
- 接口的使用建议

> **接口解除了类型依赖，有助于减少用户可视方法，屏蔽内部结构和实现细节。似乎好处很多，但这并不意味着可以滥用接口，毕竟接口实现机制会有运行期开销。对于相同包，或者不会频繁变化的内部模块之间，并不需要抽象出接口来强行分离。`接口最常见的使用场景，是对包外提供访问，或预留扩展空间`**。
> 
- go中实现接口的方式

> **Go接口实现机制很简洁，只要目标类型方法集内包含接口声明的全部方法，就被视为实现了该接口，无须做显示声明。当然，目标类型可实现多个接口**。
> 
> 
> 换句话说，我们可以先实现类型，而后再抽象出所需接口。这种非侵入式设计有很多好处。举例来说：**在项目前期就设计出最合理接口并不容易，而在代码重构，模块分拆时再分离出接口，用以解耦就很常见。另外，在使用第三方库时，抽象出所需接口，即可屏蔽太多不需要关注的内容，也便于日后替换**。
> 
- 对接口做出的限制

> • 不能有字段。
• 不能定义自己的方法。
• 只能声明方法，不能实现。
• 可嵌入其他接口类型。
> 
- 命名建议

> 接口通常以er作为名称后缀，方法名是声明组成部分，但参数名可不同或省略。
> 

```go
type tester interface {
	test()
	string() string
}

func (*data) test() {}

func (data) string() string {
	return ""
}

type data struct{}

func main() {
	var d data
	//编译器根据方法集来判断是否实现了接口，data没有实现接口
	//显然在本例中只有*data才符合tester的要求。
	//var t tester = d	报错
	var t tester = &d
	t.test()
	println(t.string())
}
```

> 如果接口没有任何方法声明，那么就是一个空接口 `（interface{})`，它的用途类似面向对象里的根类型`Object`，可被赋值为任何类型的对象。
> 
> - 接口变量默认值是`nil`。如果实现接口的类型支持，可做相等运算。

```go
func main(){
	var i1, i2 interface{}
	println(i1 == nil, i1 == i2) //true true
	i1, i2 = 100, 100
	println(i2 == i1) //true
	//不能比较map，报错
	i1, i2 = map[string]int{}, map[string]int{}
	println(i1 == i2)
}
```

> 可以像匿名字段那样，嵌入其他接口。目标类型方法集中必须拥有包含嵌入接口方法在内的全部方法才算实现了该接口。
> 
> - 嵌入其他接口类型，相当于将其声明的方法集导入。这就要求不能有同名方法，因为不支持重载。还有，不能嵌入自身或循环嵌入，那会导致递归错误。

```go
type stringer interface {
	string() string
}

type tester interface {
	test()
	stringer //嵌入其他接口
}

func (*data) test() {}

func (data) string() string {
	return ""
}

type data struct{}

func main() {
	var d data

	var t tester = &d
	t.test()
	println(t.string())
}
```

> 超集接口变量可隐式转换为子集，反过来不行。
> 

```go
func pp(a stringer) {
	println(a.string())
}

func main() {
	var d data

	var t tester = &d
	pp(t)              //隐式转换为子集接口
	var s stringer = t //超集转化为子集接口
	println(s.string())
	var t2 tester = s //报错
}
```

> 支持匿名接口类型，可直接用于变量定义，或作为结构字段类型。
> 

```go
type node struct {
	data interface { //匿名接口类型
		string() string
	}
}
type data struct{}

func main() {
	var t interface { //定义匿名接口变量
		string() string
	} = data{}
	n := node{
		data: t,
	}
	println(n.data.string())
}
```

### 7.2 执行机制

- itab结构

> 接口使用一个名为`itab`的结构存储运行期所需的相关类型信息。很显然，相关类型信息里保存了接口和实际对象的元数据。同时，`itab`还用 `fun` 数组（不定长结构）保存了实际方法地址，从而实现在运行期对目标方法的动态调用。
> 

```go
type iface struct {
	tab *itab	//类型信息
	data unsafe.Pointer	// 实际对象指针
}

type itab struct {
	inter *interfacetype	//接口类型
	_type *_type	//实际对象类型
	fun [1]uintptr //实际对象方法地址
}
```

- 接口的另一大特征

> **除此之外，接口还有一个重要特征：将对象赋值给接口变量时，会复制该对象。我们甚至无法修改接口存储的复制品,因为它也是 `unaddressable`的。**
> 

```go
type data struct {
	x int
}

func main() {
	//用build工具看可以发现接口变量与局部变量地址显然不一样
	d := data{100}
	var t interface{} = d
	println(t.(data).x)

	//两个都报错
	p := &t.(data)
	t.(data).x = 200
}
```

> 即便将其复制出来，用本地变量修改后，依然无法对 `iface.data`赋值。**解决方法就是将对象指针赋值给接口，那么接口内存储的就是指针的复制品。**
> 

```go
type data struct {
	x int
}

func main() {
	d := data{100}
	var t interface{} = &d

	t.(*data).x = 200
	println(t.(*data).x)
}
```

> 只有当接口变量内部的两个指针（`itab, data`：数据与数据类型）都为nil时，接口才等于nil；
> 

```go
func main() {
	var a interface{} = nil //不为nil
	var b interface{} = (*int)(nil)	//为nil
}
```

> 那么我们在处理错误时如果里面有接口直接的就会造成很多错误，下面这个代码你仔细看其实是没有发生错误的，但是对于错误这个对象来说虽然没有数据但是有类型，所以不为`nil`，**此时我们能做的就是在分类讨论，没有出错（错误直接返回nil）和出错分别返回**
> 

```go
type TestError struct{}

// 这里就实现了错误接口中的方法
func (*TestError) Error() string {
	return "error"
}
func test(x int) (int, error) {
	var err *TestError

	if x < 0 {
		err = new(TestError)
		x = 0
	} else {
		x += 100
	}
	return x, err
}
func main() {
	x, err := test(100)
	if err != nil {
		log.Fatalln("有错误")
	}
	println(x)
}
```

### 7.3 类型转换

- 概述

> 类型推断可将接口变量还原为原始类型，或用来判断是否实现了某个更具体的接口类型。
> 

```go
func (d data) String() string {
	return fmt.Sprintf("data:%d", d)
}

type data int

func main() {
	var d data = 15
	var x interface{} = d

	//这里就是可以先对n初始化，然后判断ok是true还是false
	if n, ok := x.(fmt.Stringer); ok { //转换为更具体的接口类型
		fmt.Println(n)	//data:15
	}

	if d2, ok := x.(data); ok { //转换回原始类型
		fmt.Println(d2)	//data:15
	}
	e := x.(error) //出错，main.data is not error: missing method Error
	fmt.Println(e)
}
```

> **使用 `ok-idiom`（是指在多返回值中用一个名为ok的布尔值来标示操作是否成功。）模式，即便转换失败也不会引发 panic。还可用switch语句在多种类型间做出推断匹配,这样空接口就有更多发挥空间**。
> 

```go
func main() {
	var x interface{} = func(x int) string {
		return fmt.Sprintf("d:%d", x)
	}

	switch v := x.(type) { //局部变量v是类型转换后的结果
	case nil:
		println("nil")
	case *int:
		println(*v)
	case func(int) string:	//这种情况d:100
		println(v(100))
	case fmt.Stringer:
		fmt.Println(v)
	default:
		println("unknown")
	}
}
```

### 7.4 技巧

- 概述

> 让编译器检查，确保类型实现了指定接口。
> 

```go
type data int

// 包初始化函数
func init() {
	//报错：不能在变量声明中使用 data(0)（数据类型的常量 0）作为 fmt.Stringer 类型：数据没有实现 fmt.Stringer（缺少 String 方法）
	var _ fmt.Stringer = data(0)
}
```

> 定义函数类型，让相同签名的函数自动实现某个接口。
> 

```go
type FuncString func() string

func (f FuncString) String() string {
	return f()
}

func main() {
	//这里有点像函数式编程以及匿名函数的意思
	var t fmt.Stringer = FuncString(func() string {
		return "hello,world！"
	})
	fmt.Println(t)
}
```
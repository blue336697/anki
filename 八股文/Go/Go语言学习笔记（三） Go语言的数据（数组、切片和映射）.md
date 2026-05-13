# Go语言学习笔记（三）| Go语言的数据（数组、切片和映射）

type: Post
status: Published
date: 2022/10/18
summary: Go语言的数据（数组、切片和映射）
tags: Go
category: 技术栈

# 数据

- 概述

> 很难遇到要编写一个不需要存储和读取集合数据的程序的情况。如果使用数据库或者文件，或者访问网络，总需要一种方法来处理接收和发送的数据。**Go 语言有 3 种数据结构可以让用户管理集合数据：数组、切片和映射。其实更加宽泛的来讲字符串和自定义结构也是算的**，我们先从字符串开始讲
> 

## 1.字符串

- 概述

> **字符串是不可变字节系列，本身是一个复合结构，头部指针指向字节数组，但没有NULL 结尾**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image.png)

```go
type stringStruct struct {
	str unsafe.Pointer
	len int
}
func main(){
	s := "测试\\x61\\142\\u0041"
	//十进制输出：测试abA
	fmt.Printf("%s\\n", s)
	//十六进制输出：e6 b5 8b e8 af 95 61 62 41,len:9
	fmt.Printf("% x,len:%d\\n", s, len(s))
}
```

- 使用方式以及注意事项

> • 字符串默认不是`nil`，而是`""`
• **使`“`”`定义不做转义处理的原始字符串（raw string)，支持跨行。编译器不会解析原始字符串内的注释语句，且前置缩进空格也属字符串内容**
> 

```go
	s1 := `line1\\r\\n,
			line2`
	println(s1)
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%201.png)

> 
> 
> - 支持`“!=、==、<、>、+、+=”`操作符。跨行时，加法操作符必须在上一行结尾
> - 允许以索引号访问字节数组（非字符)，但不能获取元素地址。

```go
func main(){
	s2 := "abc"
	println(s2[0] == 'a')//true
	println(&s2[0])	//不能取地址
}
```

> **以切片语法（起始和结束索引号）返回子串时，其内部依旧指向原字节数组。**
> 

```go
func main() {
	s := "abcdefg"
	s1 := s[:3]
	s2 := s[1:4]
	s3 := s[2:]
	//abc bcd cdefg	左闭右开
	println(s1, s2, s3)
	//提示:
	// reflect.StringHeader 和string 头结构相同
	//unsafe.Pointer用于指针类型转换
	//&reflect.StringHeader{Data:0x1e95bc, Len:7}
	fmt.Printf("%#v\\n", (*reflect.StringHeader)(unsafe.Pointer(&s)))
	//&reflect.StringHeader{Data:0x1e95bc, Len:3}
	fmt.Printf("%#v\\n", (*reflect.StringHeader)(unsafe.Pointer(&s1)))
}
```

> 使用for遍历字符串时，分`byte`和 `rune` 两种方式。
> 

```go
func main() {
	s := "测试"
	for i := 0; i < len(s); i++ {
		fmt.Printf("%d,[%c]\\n", i, s[i])
	}

	for i, c := range s { //rune返回数组索引号以及utf字符
		fmt.Printf("%d,[%c]\\n", i, c)
	}
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%202.png)

==转换==

> 要修改字符串，须将其转换为可变类型`([ ]rune或[ ]byte )`，待完成后再转换回来。**但不管如何转换，都须重新分配内存，并复制数据。**
> 

```go
func main() {
	s := "hello world!"
	pp("s: %x\\n", &s) //s: 1da434
	bs := []byte(s)
	s2 := string(bs)

	pp("string to []byte, bs: %x\\n", &bs) // bs: c00001c0e0
	pp("[]byte to string, s2: %x\\n", &s2) // s2: c00001c0f0

	rs := []rune(s)
	s3 := string(rs)
	pp("string to []rune, rs: %x\\n", &rs) // rs: c00000e3c0
	pp("[]rune to string, s3: %x\\n", &s3) // s3: c00001c110
}

func pp(format string, ptr interface{}) {
	p := reflect.ValueOf(ptr).Pointer()
	h := (*uintptr)(unsafe.Pointer(p))
	fmt.Printf(format, *h)
}
```

> 某些时候，转换操作会拖累算法性能，可尝试用“非安全”方法进行改善，该方法利用了`[ ]byte`和`string`头结构“部分相同”，**以非安全的指针类型转换来实现类型“变更”，从而避免了底层数组复制。在很多 Web Framework中都能看到此类做法，在高并发压力下，此种做法能有效改善执行性能。只是使用unsafe存在一定的风险，须小心谨慎**
> 

```go
func main(){
	s4 := toString(bs)
	pp("bs: %x\\n", &bs) //bs: c00001c0e0
	pp("s4: %x\\n", &s4) //s4: c00001c0e0
}
func toString(bs []byte) string {
	return *(*string)(unsafe.Pointer(&bs))
}
```

> 用append 函数，可将string直接追加到[ ]byte内。
> 

```go
func main(){
	var bss []byte
	bss = append(bss, "abc"...)
	fmt.Println(bss)	//[97 98 99]
}
```

- 转化时复制与性能的平衡建议

> 考虑到字符串只读特征，转换时复制数据到新分配内存是可以理解的。当然，性能同样重要，**编译器会为某些场合进行专门优化，避免额外分配和复制操作**:
> 
> - 将`[ ]byte`转换为`string key`，去`map[string]`查询的时候。
> - 将`string`转换为`[ ]byte`，进行`for range`迭代时，直接取字节赋值给局部变量

==性能==

> 除类型转换外，动态构建字符串也容易造成性能问题。**用加法操作符**拼接字符串时，每次都须重新分配内存。如此，在构建“超大”字符串时，性能就显得极差。
> 
> - 改进思路是预分配足够的内存空间。常用方法是用`strings.Join` 函数，它会统计所有参数长度，并一次性完成内存分配操作。可以看到下面的提升非常大
> - 另外，`bytes.Buffer` 也能完成类似操作,且性能相当。

```go
func Join(elems []string, sep string) string {
	switch len(elems) {
	case 0:
		return ""
	case 1:
		return elems[0]
	}
	//统计分隔符长度
	n := len(sep) * (len(elems) - 1)
	//统计所有待拼接字符串长度
	for i := 0; i < len(elems); i++ {
		n += len(elems[i])
	}
	//一次分配所需长度的数组空间
	var b Builder
	b.Grow(n)
	//拷贝数据
	b.WriteString(elems[0])
	for _, s := range elems[1:] {
		b.WriteString(sep)
		b.WriteString(s)
	}
	return b.String()
}

// BenchmarkTest-12             116           8934122 ns/op
func test01() string {
	var s string
	for i := 0; i < 10000; i++ {
		s += "a"
	}
	return s
}

//BenchmarkTest-12          158593              6826 ns/op
func test02() string {
	s := make([]string, 1000) //预分配内存，在join方法中直接拼装
	for i := 0; i < 1000; i++ {
		s[i] = "a"
	}
	return strings.Join(s, "")
}

//BenchmarkTest-12          220069              4607 ns/op
func test03() string {
	var b bytes.Buffer
	b.Grow(1000) //预分配内存，避免中途扩张
	for i := 0; i < 1000; i++ {
		b.WriteString("a")
	}
	return b.String()
}
```

- 性能总结

> **字符串操作通常在堆上分配内存，这会对Web等高并发应用会造成较大影响，会有大量字符串对象要做垃圾回收。建议使用`[]byte`缓存池，或在栈上自行拼装等方式来实现`zero-garbage`.**
> 

==Unicode==

> 类型rune专门用来存储Unicode码点(code point)，它是 int32的别名相当于`UCS-4/UTF-32`编码格式。使用单引号的字面量，其默认类型就是rune
> 
> - 除`[]rune`外,还可直接在 `rune、byte、string`间进行转换。

```go
func main(){
	r:='我'

	s:=string(c)	//rune to string
	b:= byte(r)	//rune to byte

	s2:=string(b)	// byte to string
	r2:=rune(b)	//byte to rune
	fmt .Println(s,b, s2, r2)
}
```

> 要知道字符串存储的字节数组，不一定就是合法的`UTF-8`文本。
> 

```go
func main() {
	s := "测试"
	s = string(s[0:1] + s[3:4])	//截取拼接一个不合法的字符串
	//�� false
	fmt.Println(s, utf8.ValidString(s))
}
```

> 标准库 unicode里提供了丰富的操作函数。除验证函数外，还可用`RuneCountInString`代替`len`返回准确的`Unicode`字符数量。
> 

```go
func main() {
	s := "测.试"
	//7 3
	fmt.Println(len(s), utf8.RuneCountInString(s))
}
```

## 2.数组

- 概述

> **定义数组类型时，数组长度必须是非负整型常量表达式，长度是类型组成部分。也就是说，元素类型相同，但长度不同的数组不属于同一类型**。只有这两部分都相同的数组，才是类型相同的数组，才能互相赋值
> 

```go
func main()[
	var d1 [3]int
	var d2 [2]int
	d1 = d2//错误:cannot use d2 (type [2]int) as type [3]int inassignment
}
```

- 声明方式以及注意事项

> 灵活的初始化方式
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%203.png)

```go
func main() {
	var a [4]int	//元素自动初始化为零	[0 0 0 0]
	b := [4]int{2,5}	//未提供初始值的元素自动初始化为0 [2 5 0 0]

	C = [4]int{5,3:10}//可指定索引位置初始化 [5 0 0 10]

	d := [...]int{1,2,3}//编译器按初始化值数量确定数组长度 [1 2 3]
	//[10 0 0 100]
	e := [...]int{10,3:100}//支持索引初始化，但注意数组长度与此有关

	fmt. Println(a,b,c,d, e)
}
```

> 对于结构等复合类型,可省略元素初始化类型标签。
> 

```go
func main() {
	type user struct {
		name string
		age  byte
	}

	d := [...]user{
		{"Tom", 20}, //省略了类型标签
		{"LHJ", 22},
	}
	fmt.Printf("%#v\\n", d)
}
```

> **在定义多维数组时，仅第一维度允许使用`“...”`。内置函数`len和 cap`都返回第一维度长度。内置函数 cap 只能用于切片**。
> 

```go
func main() {
	a := [2][2]int{
		{1, 2},
		{3, 4},
	}

	b := [...][3]int{
		{10, 20, 50},
		{30, 40, 60},
	}
	c := [...][2][2]int{
		{
			{1, 2},
			{3, 4},
		},
		{
			{10, 20},
			{30, 40},
		},
	}
	println(len(a), cap(a))	//2 2
	println(len(b), cap(b)) //2 2
	println(len(c), cap(c)) //2 2
	println(len(c[1]), cap(c[1])) //2 2

	//算法题中的初始化
	d := [][]int{}
	e := make([][]int, 0)
}
```

> 如元素类型支持`“==、!=”`操作符,那么数组也支持此操作。
> 

==指针==

> 要分清指针数组和数组指针的区别：
> 
> - 指针数组是指元素为指针类型的数组
> - 数组指针是获取数组变量的地址，数组指针可直接用来操作元素。

```go
func main() {
	x, y := 20, 30
	a := [...]*int{&x, &y} //元素为指针的数组
	p := &a                //存储数组的指针
	//[2]*int, [0xc00001c098 0xc00001c0b0]
	fmt.Printf("%T, %v\\n", a, a)
	//*[2]*int, &[0xc00001c098 0xc00001c0b0]
	fmt.Printf("%T, %v\\n", p, p)

	b := [...]int{1, 2}
	//数组地址，元素1地址，元素2地址
	println(&b,&b[0],&b[1])

	pp := &b
	pp[1] += 10
	println(pp[1]) //12
}
```

==复制==

> 与C数组变量隐式作为指针使用不同，**Go数组是值类型，赋值和传参操作都会复制整个数组数据。不管有多长，都会完整复制，并传递给函数**
> 
> - 如果需要，可改用指针或切片，以此避免数据复制。现在将数组的地址传入函数，只需要在栈上分配内存给指针就可以。

```go
func main(){
	c := [2]int{10, 20}
	test(&c)
	//c:0xc00001c0e0, [10 120]
	fmt.Printf("c:%p, %v\\n", &c, c)
}

func test(x *[2]int) {
	//x:0xc00001c0e0, [10 20]
	fmt.Printf("x:%p, %v\\n", x, *x)
	x[1] += 100
}
```

## 3.切片

- 概述及结构

> **切片`(slice)`本身并非动态数组或数组指针。它内部通过指针引用底层数组，设定相关属性将数据读写操作限定在指定区域内。切片本身是个只读对象，其工作机制类似数组指针的一种包装。可以按需自动增长和缩小。切片的动态增长是通过内置函数 `append` 来实现的。这个函数可以快速且高效地增长切片。还可以通过对切片再次切片来缩小一个切片的大小。因为切片的底层内存也是在连续块中分配的，所以切片还能获得索引、迭代以及为垃圾回收优化的好处。**
> 

==内部实现==

> 切片是一个很小的对象，对底层数组进行了抽象，并提供相关的操作方法。切片有 3 个字段的数据结构，这些数据结构包含 Go 语言需要操作底层数组的元数据，**这 3 个字段分别是指向底层数组的指针、切片访问的元素的个数（即长度）和切片允许增长到的元素个数（即容量，未指定就是左区间到结束）。数组必须`addressable`，否则会引发错误**。
> 

```go
//在runtime包中
type slice struct {
	array unsafe.Pointer
	len   int	//len用于限定可读的写元素数量
	cap   int	//属性cap表示切片所引用数组片段的真实长度
}

func main() {
	m := map[string][2]int{
		"a": {1, 2},
	}

	s := m["a"][:]	//Cannot slice 'm["a"]' (type '[2]int')
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%204.png)

- 一个具体的例子

> 可基于数组或数组指针创建切片，以开始和结束索引位置确定所引用的数组片段。**不支持反向索引，实际范围是一个右半开区间**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%205.png)

> 实际分析以下第三个，**指定了左索引开始，右索引结束以及容量**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%206.png)

==使用、创建以及注意事项==

> 和数组一样，切片同样使用索引号访问元素内容。起始索引为0，而非对应的底层数组真实索引位置。
> 

```go
func main() {
	x := [...]int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
	s := x[2:5]
	for i := 0; i < len(s); i++ {
		//2 3 4
		println(s[i])
	}
}
```

- 创建

> **可直接创建切片对象，无须预先准备数组。因为是引用类型，须使用make函数或显式初始化语句，它会自动完成底层数组内存分配**。
> 

```go
func main() {
	s1 := make([]int, 3, 5)    //指定len、cap，底层数组初始化为零值
	s2 := make([]int, 3)       //省略cap，和 len相等
	s3 := []int{10, 20, 5: 30} //按初始化元素分配底层数组,并设置len cap
	fmt.Println(s2, len(s2), cap(s2))	//[0 0 0] 3 3
	fmt.Println(s1, len(s1), cap(s1))	//[0 0 0] 3 5
	fmt.Println(s3, len(s3), cap(s3))	//[10 20 0 0 0 30] 6 6
}
```

> **注意下面两种定义方式的区别。前者仅定义了一个[ ]int类型变量，并未执行初始化操作，而后者则用初始化表达式完成了全部创建过程。变量b的内部指针被赋值，尽管它指向`runtime.zerobase`，但它依然完成了初始化操作。另外，`a == nil`，仅表示它是个未初始化的切片对象，切片本身依然会分配所需内存。可以直接对nil切片执行`slice[:]`操作，同样返回`nil`**。
> 

```go
func main() {
	var a []int
	b := []int{}
	println(a == nil, b == nil) //true false
	//a: &reflect.SliceHeader{Data:0x0, Len:0, Cap:0}
	fmt.Printf("a: %#v\\n", (*reflect.SliceHeader)(unsafe.Pointer(&a)))
	//b: &reflect.SliceHeader{Data:0x469560, Len:0, Cap:0}
	fmt.Printf("b: %#v\\n", (*reflect.SliceHeader)(unsafe.Pointer(&b)))
	//a size: 24
	fmt.Printf("a size: %d\\n", unsafe.Sizeof(a))
}
```

- 使用注意

> • 不支持比较操作，就算元素类型支持也不行，仅能判断是否为`nil`
• 可获取元素地址，但不能向数组那样直接用指针访问元素内容
> 

```go
func main() {
	s := []int{0, 1, 2, 3, 4}

	p := &s     //header的地址
	p1 := &s[0] //取s[0]地址
	p2 := &s[1]
	//0xc0000c7f58 0xc0000c8030 0xc0000c8038
	println(p, p1, p2)

	(*p)[0] += 100 //*[]int不支持索引的操作，那么就要先取到数组在进行操作
	*p1 += 100     //直接用单个元素的索引进行操作

	fmt.Println(s)	//[200 1 2 3 4]
}
```

> • 如果元素类型也是切片，那么就可实现类似交错数组`（ jagged array）`功能。
> 

```go
func main() {
	s := [][]int{
		{1, 2},
		{10, 20, 30},
		{100},
	}

	fmt.Println(s[1]) //[10 20 30]
	s[2] = append(s[2], 200, 300)
	fmt.Println(s[2])	//[100 200 300]
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%207.png)

> 很显然，切片只是很小的结构体对象，用来代替数组传参可避免复制开销。还有，make函数允许在运行期动态指定数组长度，绕开了数组类型必须使用编译期常量的限制。**并非所有时候都适合用切片代替数组，因为切片底层数组可能会在堆上分配内存。而且小数组在栈上拷贝的消耗也未必就比 `make`代价大**。
> 

==reslice==

> **将切片视作`[cap]slice`数据源，据此创建新切片对象。不能超出 `cap`，但不受`len` 限制**
> 
> 
> ![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%208.png)
> 

> 新建切片对象依旧指向原底层数组（切片本身的地址是新的，但储存的就是你指向的那些数组），也就是说修改对所有关联切片可见。
> 

```go
func main() {
	d := [...]int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
	s1 := d[3:7]
	s2 := s1[1:3]

	for i := range s2 {
		s2[i] += 100
	}
	fmt.Println(d)
	fmt.Println(s1)
	fmt.Println(s2)
}
```

> 利用`reslice`操作，很容易就能实现一个栈式数据结构。
> 

```go
func main() {
	//容量为5的栈
	stack := make([]int, 0, 5)
	//入栈
	push := func(x int) error {
		n := len(stack)
		if n == cap(stack) {
			return errors.New("栈满了")
		}
		stack = stack[:n+1]
		stack[n] = x

		return nil
	}
	//出栈
	pop := func() (int, error) {
		n := len(stack)
		if n == 0 {
			return -1, errors.New("栈为空")
		}
		x := stack[n-1]
		stack = stack[:n-1]
		return x, nil
	}

	//入栈测试
	for i := 0; i < 7; i++ {
		fmt.Printf("入栈 %d: %v, %v\\n", i, push(i), stack)
	}

	//出栈测试
	for i := 0; i < 7; i++ {
		x, err := pop()
		fmt.Printf("出栈：%d, %v, %v\\n", x, err, stack)
	}
}
```

==append==

> 向切片尾部`（slice[len]）`添加数据，返回新的切片对象。不会修改原`slice`属性，数据被追加到原底层数组（但是每个切片都是独立输出各自范围的数据的，虽然底层数据在容量未超过的情况下都是一样的）。如超出cap限制，则为新切片对象重新分配新的底层数组。
> 
- 注意

> • 是超出切片cap限制,而非底层数组长度限制，因为cap可小于数组长度。
• 新分配数组长度是原cap的2倍,而非原数组的2倍。并非总是2倍，对于较大的切片，会尝试扩容1/4，以节约内存。
> 

```go
func main() {
	s := make([]int, 0, 5)
	s1 := append(s, 10)
	s2 := append(s1, 20, 30)
	fmt.Printf("s1: %p: %v\\n", &s1[0], s1) //s1: 0xc00000e3c0: [10]
	fmt.Printf("s2: %p: %v\\n", &s2[0], s2) //s2: 0xc00000e3c0: [10 20 30]

	a := make([]int, 0, 100)
	a1 := a[:2:4]
	a2 := append(a1, 1, 2, 3, 4, 5, 6)     //超出4的cap限制，重新分配底层数组
	fmt.Printf("a1: %p: %v\\n", &a1[0], a1) //a1: 0xc00010e000: [0 0]
	fmt.Printf("a2: %p: %v\\n", &a2[0], a2) //a2: 0xc00001a3c0: [0 0 1 2 3 4 5 6]
	fmt.Printf("a data: %v\\n", a[:20])     //a data: [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
	fmt.Printf("a1 cap: %d, a2 cap: %d\\n", cap(a1), cap(a2))	//a1 cap: 4, a2 cap: 8
}
```

> 向`nil`切片追加数据时，会为其分配底层数组内存。不管是使用 nil 切片还是空切片，对其调用内置函数 append、len 和 cap 的效果都是一样的。
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%209.png)

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%2010.png)

> 正因为存在重新分配底层数组的缘故,在某些场合建议预留足够多的空间，避免中途内存分配和数据复制开销。
> 

==copy==

> **在两个切片对象间复制数据，允许指向同一底层数组，允许目标区间重叠。最终所复制长度以较短的切片长度（len）为准。返回的是复制成功的元素数量，还可直接从字符串中复制数据到`[]byte`。**
> 

```go
func main() {
	s := []int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
	s1 := s[5:8]          //三个元素[5,6,7]
	s2 := copy(s[4:], s1) //将s1copy到s中
	fmt.Println(s2, s)    //3 [0 1 2 3 5 6 7 7 8 9]

	s3 := make([]int, 6) //容量为6的数组
	s2 = copy(s3, s)     //将s复制到s3中，容量不够，按小的来
	fmt.Println(s2, s3)	//6 [0 1 2 3 5 6]
}
```

- 建议

> **如果切片长时间引用大数组中很小的片段，那么建议新建独立切片，复制出所需数据,以便原数组内存可被及时回收**。
> 

## 4.字典（映射）

- 概述

> 映射是一种数据结构，用于存储一系列无序的键值对。映射里基于键来存储值。下图通过一个例子展示了映射里键值对是如何存储的。映射功能强大的地方是，能够基于键快速检索数据。键就像索引一样，指向与该键关联的值。
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%2011.png)

- 注意

> **作为无序键值对集合，字典要求key 必须是支持相等运算符`（==、!=）`的数据类型，比如：数字、字符串、指针、数组、结构体以及对应接口类型。但是切片不能用作映射的键**。
> 
- 内部结构

> 如果再仔细看看图，就能看出桶的内部实现。映射使用两个数据结构来存储数据。
> 
> 
> **第一个数据结构是一个数组，内部存储的是用于选择桶的散列键的高八位值。这个数组用于区分每个键值对要存在哪个桶里。第二个数据结构是一个字节数组，用于存储键值对。该字节数组先依次存储了这个桶里所有的键，之后依次存储了这个桶里所有的值。实现这种键值对的存储方式目的在于减少每个桶所需的内存**
> 

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%2012.png)

- 使用以及声明

> 字典是引用类型，使用`make`函数或初始化表达语句来创建。
> 
> - **访问不存在的键值，默认返回零值，不会引发错误。但推荐使用ok-idiom模式，毕竟通过零值无法判断键值是否存在,或许存储的value本就是零**。

```go
func main() {
	m := make(map[string]int)
	m["a"] = 1
	m["b"] = 2

	m1 := map[int]struct {	//使用匿名结构类型
		name string
		age  int
	}{
		1: {"LHJ", 20},
	}
	//map[a:1 b:2]   {LHJ 20}
	fmt.Println(m, m1[1])

	//使用ok-idiom判断key是否存在
	if v, ok := m["a"]; ok {
		println(v)
	}
	//删除键值对，不存在不会报错
	delete(m, "c")
}
```

> 迭代，每次迭代出来的顺序与添加顺序是不一致的
> 

```go
func main() {
	m := make(map[string]int)
	for i := 0; i < 10; i++ {
		m[string('a'+i)] = i
	}

	for k, v := range m {
		println("key:", k, "value:", v)
	}
}
```

> **函数len返回当前键值对数量，cap不接受字典类型。另外，因内存访问安全和哈希算法等缘故，字典被设计成`“not addressable”`，故不能直接修改
`value`成员`（结构或数组)`。正确做法是返回整个value，待修改后再设置字典键值,或直接用指针类型**。
> 

```go
type user struct {
	name string
	age  byte
}

func main() {
	m := map[int]user{
		1: {"LHJ", 22},
	}

	u := m[1]
	u.age += 1
	m[1] = u //整体赋值

	m2 := map[int]*user{
		1: &user{"LHJ", 22},
	}

	m2[1].age++ //使用指针的方式修改目标对象
}
```

> • 不能对nil字典（未初始化）进行写操作，但却能读。注意：内容为空的字典（已经初始化），与nil是不同的。
> 

```go
var m3 map[string]int //没有初始化
m4 := map[string]int{} //初始化了
m5 := make(map[string]int)	//初始化了
```

==线程安全==

> 在迭代期间删除或新增键值是安全的。运行时会对字典并发操作做出检测。如果某个任务正在对字典进行写操作，那么其他任务就不能对该字典执行并发操作（**读、写、删除**)，否则会导致进程崩溃。可启用数据竞争`（data race）`检查此类问题，它会输出详细检测信息。
> 

```bash
$go run -race ./xxx.go
```

```go
// 报错fatal error: concurrent map read and map write
func main() {
	m := make(map[string]int)

	go func() {
		for {
			m["a"] += 1 //写操作
			time.Sleep(time.Microsecond)
		}
	}()

	go func() {
		for {
			_ = m["b"] //读操作
			time.Sleep(time.Microsecond)
		}
	}()
	select { //让进程一直存在
	}
}
```

> 可用`sync.RWMutex`实现同步，避免读写操作同时进行。
> 

```go
func main() {
	m := make(map[string]int)
	var lock sync.Mutex //声明互斥锁
	go func() {
		for {
			lock.Lock()   //注意锁的粒度
			m["a"] += 1   //写操作
			lock.Unlock() //这里不能使用defer，因为单次循环不执行
			time.Sleep(time.Microsecond)
		}
	}()

	go func() {
		for {
			lock.Lock()
			_ = m["b"] //读操作
			lock.Unlock()
			time.Sleep(time.Microsecond)
		}
	}()
	select { //让进程一直存在
	}
}
```

==性能==

> • 字典对象本身就是指针包装，传参时无须再次取地址。**在函数间传递映射并不会制造出该映射的一个副本。实际上，当传递映射给一个函数，并对这个映射做了修改时，所有对这个映射的引用都会察觉到这个修改**
• 在创建时预先准备足够空间有助于提升性能，减少扩张时的内存分配和重新哈希操作。
• **对于海量小对象，应直接用字典存储键值数据拷贝，而非指针（将切片或者映射传递给函数成本很小，并且不会复制底层的数据结构）。这有助于减少需要扫描的对象数量，大幅缩短垃圾回收时间。另外，字典不会收缩内存，所以适当替换成新对象是必要的**。
> 

## 5.自定义结构

- 概述

> 结构体`（struct）`将多个不同类型命名字段`（field）`序列打包成一个复合类型。**字段名必须唯一，可用`“_”`补位，支持使用自身指针类型成员。字段名、排列顺序属类型组成部分。除对齐处理外，编译器不会优化、调整内存布局。**
> 

```go
type node struct {
	_   int
	val int
	pre *node
}

func main() {
	head := node{
		val: 0,
	}

	n1 := node{
		val: 1,
		pre: &head,
	}

	n2 := node{
		val: 2,
		pre: &n1,
	}
	println(&head, &n1, &n2) //0xc000008078 0xc000008090 0xc000109ee0
	fmt.Println(head, n1, n2)	//{0 0 <nil>} {0 1 0xc000008078} {0 2 0xc000008090}
}
```

- 字段类型与初始化

> • 可按顺序初始化全部字段，或使用命名方式初始化指定字段。上面就是指定的方式，推荐用命名初始化。这样在扩充结构字段或调整字段顺序时，不会导致初始化语句出错
• 可直接定义匿名结构类型变量，或用作字段类型。但因其缺少类型标识，在作为字段类型时无法直接初始化,稍显麻烦。
> 

```go
func main() {
	u := struct { //直接定义匿名结构变量
		name string
		age  byte
	}{
		name: "Tom", age: 12,
	}
	type file struct {
		name string
		attr struct { //定义匿名结构类型字段
			owner int
			perm  int
		}
	}
	f := file{
		name: "test.dat",
		//attr: {	//复合文字中缺少类型
		//	owner: 1,
		//	perm: 0755,
		//},
	}
	f.attr.owner = 1	//正确方式
	f.attr.perm = 0755

	fmt.Println(u, f)
}
```

> • 只有在所有字段类型全部支持时，才可做相等操作。就比如你类型中有一个map类型，结构就不能进行相等操作了
• 可使用指针直接操作结构字段，但不能是多级指针。
> 

```go
type user struct {
	name string
	age  int
}

func main() {
	p := &user{
		name: "Tom",
		age:  22,
	}
	p.name = "LHJ"
	p.age++
	fmt.Println(p)

	p1 := &p
	*p1.name = "Jack" //报错，多级指针
}
```

==空结构==

> 空结构`（struct{}）`是指没有字段的结构类型。
> 
> - 它比较特殊，因为无论是其自身，还是作为数组元素类型，其长度都为零
> - 尽管没有分配数组内存，但依然可以操作元素，对应切片`len、cap`属性也正常。
> - 实际上，这类“长度”为零的对象通常都指向`runtime.zerobase`变量。

```go
func main() {
	var a struct{}
	var b [100]struct{}

	println(unsafe.Sizeof(a), unsafe.Sizeof(b)) //0 0

	s := b[:]
	b[1] = struct{}{}
	s[2] = struct{}{}
	fmt.Println(s[3], len(s), cap(s))	//{} 100 100

	fmt.Printf("%p,%p,%p", s, &b, &a)	//0x509540,0x509540,0x509540
}
```

> 空结构可作为通道元素类型，用于事件通知。
> 

```go
func main() {
	exit := make(chan struct{})

	go func() {
		println("hello")
		exit <- struct{}{}
	}()

	<-exit	//信道里面有信息了就会输出，没有就会阻塞在这里
	println("end.")
}
```

==匿名字段==

> **所谓匿名字段`（anonymous field)`，是指没有名字，仅有类型的字段，也被称作嵌入字段或嵌入类型。如嵌入其他包中的类型,则隐式字段名字不包括包名。不仅仅是结构体，除接口指针和多级指针以外的任何命名类型（未命名类型如果字段没有名字又不能通过字段类型找到那当然未命名类型不能作为匿名字段了）都可作为匿名字段**。
> 
> - 隐式名字：可通过字段的类型名int、string之类的作为字段名去初始化

```go
type user struct {
	name string
	age  int
}

type people struct {
	id   int
	user //仅有类型名
}

func main() {
	p := people{
		1, user{ //显示初始化匿名字段
			"LHJ",
			20,
		},
	}

	p.name = "LLL"  //直接设置匿名字段成员
	println(p.name) //直接读取匿名字段成员

	type a *int
	type b **int
	type c interface {
	}
	//这三个都错
	type d struct {
		*a
		b
		*c
	}
}
```

> • 不能将基础类型和其对应指针类型同时嵌入，因为两者隐式名字相同
• **虽然可以像普通字段那样访问匿名字段成员，但会存在重名问题默认情况下，编译器从当前显式命名字段开始，逐步向内查找匿名字段成员。如匿名字段成员被外层同名字段遮蔽，那么必须使用显式字段名。如果多个相同层级的匿名字段成员重名，也只能使用显式字段名访问，因为编译器无法确定目标。**
> 

```go
type user struct {
	name string
	age  int
}

type people struct {
	age int //与匿名字段user的age同名
	user
}

func main() {
	p := people{
		1, user{ //显示初始化匿名字段
			"LHJ",
			20,
		},
	}
	println(p.age, p.user.age)
	p.age = 21                 //访问people的age
	p.user.age = 22            //user里面的age必须显式字段名访问
	println(p.age, p.user.age)
}
```

- 匿名字段总结

> 严格来说，Go并不是传统意义上的面向对象编程语言，或者说仅实现了最小面向对象机制。匿名嵌入不是继承，无法实现多态处理。虽然配合方法集，可用接口来实现一些类似操作，但其本质是完全不同的。
> 

==字段标签==

> **字段标签`（tag）`并不是注释，而是用来对字段进行描述的元数据尽管它不属于数据成员，但却是类型的组成部分。在运行期，可用反射获取标签信息。它常被用作格式校验，数据库关系映射等**。
> 

```go
type user struct {
	name string `姓名`
	age  int    `年龄`
}

func main() {
	u := user{"LHJ", 1}
	v := reflect.ValueOf(u)
	t := v.Type()

	for i, n := 0, t.NumField(); i < n; i++ {
		fmt.Printf("%s: %v\\n", t.Field(i).Tag, v.Field(i))
	}
}
```

==内存布局==

> **不管结构体包含多少字段,其内存总是一次性分配的，各字段在相邻的地址空间按定义顺序排列**。当然，对于引用类型、字符串和指针，结构内存中只包含其基本（头部）数据。还有，所有匿名字段成员也被包含在内。借助`unsafe`包中的相关函数，可输出所有字段的偏移量和长度。
> 
> - 在分配内存时，字段须做对齐处理，通常以所有字段中最长的基础类型宽度为标准。
> - 比较特殊的是空结构类型字段。如果它是最后一个字段，那么编译器将其当作长度为1的类型做对齐处理，以便其地址不会越界，避免引发垃圾回收错误。
> - 如果仅有一个空结构字段，那么同样按1对齐，只不过长度为0，且指向`runtime.zerobase`变量。

```go
type user struct {
	x, y int
}

type people struct {
	id   int     //基本类型
	name string  //字符串
	data []byte  //引用类型
	next *people //指针类型
	user         //匿名字段
}

func main() {
	v := people{
		id:   1,
		name: "test",
		data: []byte{1, 2, 3, 4},
		user: user{1, 2},
	}
	s := `
		v: %p ~ %x,size: %d, align: %d
		field	address		  offset size
		------+-----------------+--------+--------
		id      %p	 %d	   %d
		name	%p	 %d	   %d
		data	%p	 %d	   %d
		next	%p	 %d	   %d
		x       %p	 %d	   %d
		y       %p	 %d	   %d
	`

	fmt.Printf(s,
		&v, uintptr(unsafe.Pointer(&v))+unsafe.Sizeof(v), unsafe.Sizeof(v), unsafe.Alignof(v),
		&v.id, unsafe.Offsetof(v.id), unsafe.Sizeof(v.id),
		&v.name, unsafe.Offsetof(v.name), unsafe.Sizeof(v.name),
		&v.data, unsafe.Offsetof(v.data), unsafe.Sizeof(v.data),
		&v.next, unsafe.Offsetof(v.next), unsafe.Sizeof(v.next),
		&v.x, unsafe.Offsetof(v.x), unsafe.Sizeof(v.x),
		&v.y, unsafe.Offsetof(v.y), unsafe.Sizeof(v.y))
}
```

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%2013.png)

![image.png](Go%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%88%E4%B8%89%EF%BC%89%20Go%E8%AF%AD%E8%A8%80%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%95%B0%E7%BB%84%E3%80%81%E5%88%87%E7%89%87%E5%92%8C%E6%98%A0%E5%B0%84%EF%BC%89/image%2014.png)

- 相关的三个方法

> • `unsafe.Sizeof()`：得到指定字段的占用大小
• `unsafe.Alignof()`：这一整个结构初始化采用几字节的大小对齐内存
• `unsafe.Offsetof()`：得到指定字段的起始地址
> 
- 为什么要对齐

> 对齐的原因与硬件平台，以及访问效率有关。某些平台只能访问特点地址，比如只能是偶数地址，而另一方面，CPU 访问自然对齐的数据所需的的读周期最少，还可避免拼接数据。
>
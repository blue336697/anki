# Go语言学习笔记（五）| 反射

type: Post
status: Published
date: 2022/10/22
summary: 反射
tags: Go
category: 技术栈

# 反射

## 1.类型

- 概述

> 反射`（reflect）`让我们能在运行期探知对象的类型信息和内存结构，这从一定程度上弥补了静态语言在动态行为上的不足。同时，反射还是实现元编程的重要手段。
> 
- 结构

> **和C数据结构一样，Go对象头部并没有`类型指针`，通过其自身是无法在运行期获知任何类型相关信息的。反射操作所需的全部信息都源自接口变量。接口变量除存储自身类型外，还会保存实际对象的类型数据**。
> 

```go
//这两个反射入口函数,会将任何传入的对象转换为接口类型。
func TypeOf(i interface{}) Type
func ValueOf(i interface{}) Value
```

- 反射的作用

==获取数据类型==

> **在面对类型时，需要区分`Type和Kind`。所以在类型判断上，须选择正确的方式，可以看到默认只输出转换后的结构显示的真实静态类型**。
> 
> - 前者表示真实类型（静态类型)
> - 后者表示其基础结构(底层类型)类别。

```go
type X int

func main() {
	var a X = 100
	t := reflect.TypeOf(a)
	fmt.Println(t, t.Name(), t.Kind()) //main.X X int
}
```

==构造基本类型==

> 除通过实际对象获取类型外，也可直接构造一些基础复合类型。
> 

```go
func main() {
	a := reflect.ArrayOf(0, reflect.TypeOf(0))
	m := reflect.MapOf(reflect.TypeOf(""), reflect.TypeOf(0))
	//[0]int map[string]int
	fmt.Println(a, m)
}
```

==区分类型==

> 传入对象应区分基类型和指针类型，因为它们并不属于同一类型
> 
> - **方法Elem返回指针、数组、切片、字典（值）或通道的基类型，进一步的说跟直接输出TypeOf后的变量是一致的，如果类型的 Kind 不是 指针、数组、切片、字典（值）或通道，它会发生异常**

```go
type X int

func main() {
	x := 100
	tx, tp := reflect.TypeOf(x), reflect.TypeOf(&x)
	fmt.Println(tx, tp, tx == tp)     //int *int false
	fmt.Println(tx.Name(), tp.Name()) //int 指针没有静态类型
	fmt.Println(tx.Kind(), tp.Kind()) //int ptr
	fmt.Println(tx == tp.Elem())      //true
	fmt.Println(tp.Elem())            //int

	var a X = 100
	t := reflect.TypeOf(a)
	t1 := reflect.TypeOf(&a)
	fmt.Println(t, t1.Elem()) //main.X main.X
}
```

==遍历结构体==

> 只有在获取结构体指针的基类型后，才能遍历它的字段。
> 

```go
type user struct {
	name string
	age  int
}
type manager struct {
	user
	title string
}

func main() {
	var m manager
	t := reflect.TypeOf(&m)
	if t.Kind() == reflect.Ptr { //获取指针的基类型
		t = t.Elem()
	}
	for i := 0; i < t.NumField(); i++ {
		f := t.Field(i)
		//user main.user 0
		//title string 24
		fmt.Println(f.Name, f.Type, f.Offset)
		//如果f的字段是另一个结构体，那么就输出匿名字段结构体的结构
		if f.Anonymous {
			for i := 0; i < f.Type.NumField(); i++ {
				af := f.Type.Field(i)
				//  name string
				//  age int
				fmt.Println(" ", af.Name, af.Type)
			}
		}
	}
}
```

==匿名字段直接访问==

> 对于匿名字段，可用多级索引(按定义顺序）直接访间。
> 
> - `FieldByName`：不支持多级名称，如有同名遮蔽，须通过匿名字段二次获
> - **`FieldByIndex`：返回与索引序列对应的嵌套字段。相当于对每个索引依次调用 Field。如果类型的 Kind 不是 Struct，它会发生异常**。

```go
type user struct {
	name string
	age  int
}
type manager struct {
	user
	title string
}

func main() {
	var m manager
	t := reflect.TypeOf(m)
	name, _ := t.FieldByName("name")   //按名称查找
	fmt.Println(name.Name, name.Type)  //name string
	age := t.FieldByIndex([]int{0, 1}) //按多级索引查找
	fmt.Println(age.Name, age.Type)    //age int
}
```

==结果集的类型==

> 同样地，输出方法集时，一样区分基类型和指针类型。
> 

==包结构==

> **有一点和想象的不同，反射能探知当前包或外包的非导出结构成员。相对reflect而言，当前包和外包都是“外包”。**
> 

==结构tag==

> **可用反射提取struct tag，还能自动分解。其常用于ORM映射，或数据格式验证**。
> 

```go
type user struct {
	name string `field:"name" type:"varchar(50)"`
	age  int    `field:"age" type:"int"`
}

func main() {
	var u user
	t := reflect.TypeOf(u)
	for i := 0; i < t.NumField(); i++ {
		f := t.Field(i)
		//name:name varchar(50)
		//age:age int
		fmt.Printf("%s:%s %s\\n", f.Name, f.Tag.Get("field"), f.Tag.Get("type"))
	}
}
```

==其他辅助方法==

> 辅助判断方法`Implements、ConvertibleTo、AssignableTo`都是运行期进行动态调用和赋值所必需的。
> 
> - `ConvertibleTo`：报告类型的值是否可转换为传入的类型。即使结果返回 true，转换仍可能出现异常。例如，`[]T` 类型的切片可转换为 `[N]T`，但如果其长度小于 N，则转换将出现异常。
> - `AssignableTo`：报告该类型的值是否可赋值给传入的类型

```go
type X int

func (X) String() string {
	return ""
}
func main() {
	var a X
	t := reflect.TypeOf(a)

	// Implements 不能直接使用类型作为参数，导致这种用法非常别扭
	st := reflect.TypeOf((*fmt.Stringer)(nil)).Elem()
	fmt.Println(t.Implements(st)) //true

	it := reflect.TypeOf(0)
	fmt.Println(t.ConvertibleTo(it)) //true

	fmt.Println(t.AssignableTo(st), t.AssignableTo(it))//true false
}
```

## 2.值（权限访问）

- 概述

> **和 Type获取类型信息不同，Value专注于对象实例数据读写。在前面章节曾提到过，接口变量会复制对象，且是`unaddressable`的，所以要想修改目标对象，就必须使用指针**。
> 
- 简单使用

> **同样我们刚才提到`valueOf`会将任何传入的对象转换为接口类型。就算传入指针，一样需要通过 Elem获取目标对象。因为被接口存储的指针本身是不能寻址和进行设置操作的**。
> 

```go
func main() {
	a := 100
	va, vp := reflect.ValueOf(a), reflect.ValueOf(&a).Elem()
	println(va.CanAddr(), va.CanSet())	//false false
	println(vp.CanAddr(), vp.CanSet())	//true true
}
```

- 权限访问——变量

> **程序可以直接访问这个包中任意一个公开的标识符。这些标识符以大写字母开头。以小写字母开头的标识符是不公开的，不能被其他包中的代码直接访问。但是，其他包可以间接访问不公开的标识符。例如，一个函数可以返回一个未公开类型的值，那么这个函数的任何调用者，哪怕调用者不是在这个包里声明的，都可以访问这个值**。
> 
> - ==小写称为非导出字段==：**非大写开头就只能在包内使用（变量或常量也可以下划线开头）**
> - ==大写称为小写字段==：**能被其它包访问或调用（相当于public）**

> **注意，不能对非导出字段直接进行设置操作，无论是当前包还是外包。**
> 

```go
type User struct {
	Name string
	code int
}

func main() {
	p := new(User) //以new关键字的就是引用的指针类型了
	v := reflect.ValueOf(p).Elem()

	name := v.FieldByName("Name")
	code := v.FieldByName("code")
	//name,addr: true, set: true
	//code,addr: true, set: false
	fmt.Printf("name,addr: %v, set: %v\\n", name.CanAddr(), name.CanSet())
	fmt.Printf("code,addr: %v, set: %v\\n", code.CanAddr(), code.CanSet())

	if name.CanSet() {
		name.SetString("TOM")
	}
	//我们直接通过非安全指针的方式进行修改
	if code.CanAddr() {
		//这里两次的转型+取值修改看下面的解释
		*(*int)(unsafe.Pointer(code.UnsafeAddr())) = 100
	}
	//因为p本来就是引用指针，那么取值就要再取一次指针
	fmt.Printf("%+v\\n", *p)
	fmt.Println(*p)
}
```

`Value.Pointer&Value.Int`

> `Value.Pointer和 Value.Int`等方法类似，将`Value.data`存储的数据转换为指针，目标必须是指针类型。而`UnsafeAddr`返回任何`CanAddr Value.data`地址（相当于&取地址操作），比如`Elem`后的`Value`，以及字段成员地址。
> 

> **以结构体里的指针类型字段为例，`Pointer` 返回该字段所保存的地址，而 `UnsafeAddr` 返回该字段自身的地址(结构对象地址+偏移量）**。
> 
- 接口类型推断和转换

> 可通过Interface方法进行类型推断和转换。
> 

```go
func main() {
	u := user{
		"LHJ",
		22,
	}

	v := reflect.ValueOf(&u)

	if !v.CanInterface() {
		println("不能通过接口")
		return
	}

	p, ok := v.Interface().(*user)

	if !ok {
		println("不能通过接口")
		return
	}
	p.Age++
	fmt.Println(u)	//{LHJ 23}
}
```

> 接口有两种nil状态（普通与指针），这一直是个潜在麻烦。解决方法是用`IsNil`判断值是否为`nil`。
> 

```go
func main() {
	var a interface{} = nil
	var b interface{} = (*int)(nil)
	fmt.Println(a == nil)                             //true
	fmt.Println(b == nil, reflect.ValueOf(b).IsNil()) //false true
}
```

> 也可用`unsafe`转换后直接判断`iface.data`是否为零值。
> 

```go
func main() {
	var b interface{} = (*int)(nil)
	iface := (*[2]uintptr)(unsafe.Pointer(&b))
	fmt.Println(iface, iface[1] == 0)	//&[12008288 0] true
}
```

- 其他转换

> 也可直接使用 `Value.Int、Bool`等方法进行类型转换，但失败时会引发 panic，且不支持`ok-idiom`。
> 

```go
func main() {
	c := make(chan int, 4)
	v := reflect.ValueOf(c)
	if v.TrySend(reflect.ValueOf(100)) {
		fmt.Println(v.TryRecv())	//100 true
	}
}
```

> **让人很无奈的是，Value里的某些方法并未实现ok-idom或返回error**，所以得自行判断返回的是否为Zero Value。
> 

```go
func main() {
	v := reflect.ValueOf(struct{ name string }{})
	println(v.FieldByName("name").IsValid())	//true
	println(v.FieldByName("xxx").IsValid())	//false
}
```

## 3.方法

- 动态调用方法

> **无法调用非导出方法，甚至无法获取有效地址。**`不可变参（固定参数）`
动态调用方法，谈不上有多麻烦。只须按In列表准备好所需参数即可。
> 

```go
type X struct{}

func (X) Add(x, y int) (int, error) {
	return x + y, fmt.Errorf("err: %d", x+y)
}
func main() {
	var a X

	r := reflect.ValueOf(&a)
	m := r.MethodByName("Add")
	//相当于放方法的容器，里面设置传入的参数
	mBox := []reflect.Value{
		reflect.ValueOf(1),
		reflect.ValueOf(2),
	}

	getM := m.Call(mBox)     //执行方法
	for _, m := range getM { //得到结果
		fmt.Println(m)	//3 		err: 3
	}
}
```

`可变参数`

> 对于变参来说，用`CallSlice`要更方便—些。
> 

```go
type X struct{}

func (X) Format(s string, a ...interface{}) string {
	return fmt.Sprintf(s, a...)
}
func main() {
	var a X

	r := reflect.ValueOf(&a)
	m := r.MethodByName("Format")
	//相当于放方法的容器，里面设置传入的参数
	mBox := m.Call([]reflect.Value{
		reflect.ValueOf("%s = %d"),
		reflect.ValueOf("x"), //所有参数都要处理
		reflect.ValueOf(100),
	})
	fmt.Println(mBox) //[x = 100]

	mBox = m.CallSlice([]reflect.Value{
		reflect.ValueOf("%s = %d"),
		reflect.ValueOf([]interface{}{"x", 100}), //一个接口接收可变参就可以了
	})
	fmt.Println(mBox) //[x = 100]
}
```

## 4.构建

- 概述

> 反射库提供了内置函数`make和 new`的对应操作,其中最有意思的就是 `MakeFunc`。可用它实现通用模板，适应不同数据类型。如果语言支付泛型，自然不需要这么折腾。
> 
- 加法模板示例

```go
func add(args []reflect.Value) (results []reflect.Value) {
	if len(args) == 0 {
		return nil
	}

	var res reflect.Value

	switch args[0].Kind() {
	case reflect.Int:
		n := 0
		for _, a := range args {
			n += int(a.Int())
		}
		res = reflect.ValueOf(n)
	case reflect.String:
		sb := make([]string, 0, len(args))
		for _, s := range args {
			sb = append(sb, s.String())
		}
		res = reflect.ValueOf(strings.Join(sb, ""))
	}

	results = append(results, res)
	return
}

// 将函数指针参数指向通用算法函数
func makeAdd(fptr interface{}) {
	fn := reflect.ValueOf(fptr).Elem()
	v := reflect.MakeFunc(fn.Type(), add) //这是关键
	fn.Set(v)                             //指向通用算法函数
}

func main() {
	var intAdd func(x, y int) int
	var strAdd func(a, b string) string

	makeAdd(&intAdd)
	makeAdd(&strAdd)

	println(intAdd(20, 30))	//50
	println(strAdd("hello ", "how are you"))	//hello how are you
}
```

## 5.性能

- 概述

> 反射在带来“方便”的同时，也造成了很大的困扰。很多人对反射避之不及，因为它会造成很大的性能损失。但损失到底有多大?我们简单测试一下
> 

==直接赋值和反射赋值==

- 原始

> 可以看到性能差距非常大
> 

```go
// 普通赋值
func set(x int) {
	d.X = x
}

// 反射方式
func rset(x int) {
	v := reflect.ValueOf(d).Elem()
	f := v.FieldByName("X")
	f.Set(reflect.ValueOf(x))
}

// BenchmarkSet-12         1000000000               0.3205 ns/op
func BenchmarkSet(b *testing.B) {
	for i := 0; i < b.N; i++ {
		set(100)
	}
}
//BenchmarkRSet-12        13821270                82.50 ns/op
func BenchmarkRSet(b *testing.B) {
	for i := 0; i < b.N; i++ {
		rset(100)
	}
}
```

- 如果给反射的数据加上“缓冲”

> 可以看到是有改善的
> 

```go
var v = reflect.ValueOf(d).Elem()
var f = v.FieldByName("X")
// 反射方式
func rset(x int) {
	f.Set(reflect.ValueOf(x))
}

// BenchmarkRSet-12        80437580                13.89 ns/op
func BenchmarkRSet(b *testing.B) {
	for i := 0; i < b.N; i++ {
		rset(100)
	}
}
```

==直接调用和反射调用==

> 可以看到性能也很低
> 

```go
// BenchmarkCall01-12      896067384                1.320 ns/op
func BenchmarkCall(b *testing.B) {
	for i := 0; i < b.N; i++ {
		call()
	}
}

// BenchmarkRCall-12        6757962               167.5 ns/op
func BenchmarkRCall(b *testing.B) {
	for i := 0; i < b.N; i++ {
		rCall()
	}
}

type Data struct {
	X int
}

func (x *Data) Inc() {
	x.X++
}

var d = new(Data)
var v = reflect.ValueOf(d)
var m = v.MethodByName("Inc")

// 普通赋值
func call() {
	d.Inc()
}

// 反射方式
func rCall() {
	m.Call(nil)
}
func main() {

}
```
# MIT6.824分布式 | Lab1（MapReduce）

type: Post
status: Published
date: 2023/04/01
summary: MapReduce
tags: 实践
category: 分布式

# 整个lab的结构——架构层次

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab1%EF%BC%88MapReduce%EF%BC%89/image.png)

# MapReduce

**`对于整个视频课程的中文翻译我推荐这个网址`**[MIT6.824课程翻译](https://mit-public-courses-cn-translatio.gitbook.io/mit6-824/)**`课程的相关资料全在官网课程计划那里`**[MIT6.824计划表](https://pdos.csail.mit.edu/6.824/schedule.html)

## 1.MapReduce的编程模型结构

- 概述

> 计算通过输入一系列键值对，然后生成一些列键值对。MapReduce库的使用者将计算的表示为2种函数：Map和Reduce。
> 
> - `Map函数`：由用户编写通过输入的键值对来生成新的一系列中间键值对。MapReduce库会将有相同中间Key，key的中间value全部都分组在一起，并将它们传递给Reduce函数。
> - `Reduce函数`：也是由用户编写。它接受一个中间Key，以及该key对应的一系列的的值。**它会合并这些值的集合并大可能生成更小的集合**。通常每次reduce调用后都只生成0个或者1个输出结果。这些中间值会通过迭代器提供给用户的reduce函数。这就可以使得我们处理那些太大而无法全部存储在内存中的值列表。
- 过程解构

> 我们用现实中的厨师做菜的例子，你通过下面的整个lab就可以十分生动的理解整个过程了
> 
> - 对于shuffle阶段我使用了更贴近lab中实际例子的命名sort
> 
> ![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab1%EF%BC%88MapReduce%EF%BC%89/image%201.png)
> 

### 1.1 使用示例

- 统计单次出现次数的过程图概述

> 我们使用一个统计文档中每个单词出现次数的伪代码
> 
> - map函数：就是每个字符的都统计一遍
> - reduce函数：就是将map统计出来的进行合并，key一样的将value进行相加

```go
map(String key,String value):
    // key: 文档名/行id等等每一种场景都有不同的含义
    // value: 文档内容
    for each word w in value:
    	//通过RPC发送到下个步骤
        EmitIntermediate(w,"1");

reduce(String key, Iterator values):
    // key: 一个单词
    // value: 计数值列表
    int result = 0;
    for each v in values:
        result += ParseInt(v);
	//通过RPC发送结果
    Emit(AsString(result));
```

- 用实际的lab例子——统计单次出现次数的过程图

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab1%EF%BC%88MapReduce%EF%BC%89/image%202.png)

- 倒排索引概述

> 倒排索引的map函数与reduce函数就是照葫芦画瓢
> 

```go
Map( string key, string value )
//key: 文档的id
//value: 文档的内容
	for each word in value:
		OutputTemp( word, key );

Reduce( string key, list valueList )
// key: 存放的具体值
//valueList: 值出现 在那些文档中的文档编号
	List sumList;
	for value in valueList:
		sumList.append(value);
	OutputFinal( key, sumList );
```

- 过程图示

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab1%EF%BC%88MapReduce%EF%BC%89/image%203.png)

### 1.2 类型

- 概述

> 即使前面的伪代码是用术语编写的字符串输入和输出，但从概念上讲，用户提供的`map和reduce`函数的有下面的类型关联：可以发现输入的k/v与输出的k/v完全不同了，而中间生成的k/v则是输出结构处于连贯的缔造顺序
> 

```go
map 	(k1,v1) 		→ list(k2,v2)
reduce 	(k2,list(v2)) 	→ list(v2)
```

### 1.3 更多例子

- 概述

> 我们还可以使用MapReduce完成更多的例子
> 
> - ==分布式的grep==：如果一行数据匹配所给定的模式map函数就会将更改行发出来，然后reduce函数是一个标识函数只负责将中间的数据拷贝到结果输出。
> - ==计算URL访问频率==：map函数处理web网页的请求日志并输出`{URL,1}`。然后reduce函数对一样的URL的值相加，并输出`{URL,总和}`的键值对。
> - ==反转Web链接图==：map函数将一个页面中所有能找到的叫source的链接和它的目标URL输出成`{target，source}`。然后reduce函数对相同target的source们聚合然后发出这个新的键值对`{target, list(source)}`。
> - ==每个主机的Term-向量==：【这里的term是搜索的概念，term就是一句话中的词组的意思】Term-向量是一个`{word, 频率}`键值对的一个列表，它总结了一个文档或者一组文档里面出现的最重要的单词。map函数对每个输入文档（其主机名是从文档的URL中抽取出来的）处理为`{hostname, term vector}`并发 出去。reduce函数传递一个主机所有文档的term-向量，然后将这些向量累加起来，丢弃不常用的term，最后发出`{hostname, term vector}`键值对。
> - ==倒排索引==：map函数解析每个文档，并发出一系列`{word, 文档ID}`的键值对，reduce函数会对一个给定的单词接受所有的键值对，然后对该单词的 文档ID进行排序并发出`{word, list(文档ID)}`的键值对。所有输出的键值对集合就形成了一个简单的倒排索引。通过增加这个计算来跟踪单词的位置是很容易的。
> - ==分布式排序==：map函数从每个记录中提取key，并发出`{key，记录}`这个键值对。 reduce函数会不做修改的发送所有的键值对。

## 2.实现

### 2.1 执行概述

- 概述

> 根据上面的模型我们可以直到
> 
> - map函数就是将一大推整体的数据进行解耦分解成一个个小的item，每个小item都会被一个个worker去并行处理，所以这里就体现出分布式的概念了，每个电脑就是一个或多个worker，很多电脑一起完成map函数的工作
> - 而reduce函数为了应对这么多的item同样也是分布式的，它通过一个分区函数（比如hash(key) mod R）将map中生成的临时key来分片为R个片段。分区数量（R）以及分区函数由用户来指定。
- **MapReduce的架构执行流程图示**

> 
> 
> 1. 根据用户设置（16~64M）的大小将输入的任务分成若干个块，然后用户程序的MapReduce会在一组计算机上fork很多当前程序的很多副本
> 2. 在fork的过程中会出现一个master（就是具体代码中的`Coordinator`）角色的程序，这与其他fork出来的worker是不同的，这个master就类似于Reactor模型里面的选择器了我觉得。将不同的map任务派发给这些worker，而worker又细分为map方的与reduce方的
> 3. worker接收任务读取数据解析成`k/v`结构然后传入给map函数生成缓存在内存的中间`k/v`，注意此时的`k/v`结构的key是没有合并的也就是说有很多key相同，value不同的结构
> 4. 将这些缓冲的数据周期性的进行持久化，持久化的磁盘被分为若干个区，通过分区函数将数据存放在不同的分区中，每个分区本质就是一个value构成的数组，数组的名字是key
> 5. master会持续的告诉reduce的worker这些数据的位置，然后reduce的worker使用RPC远程调用各个map的worker本地持久化数据，读取所有的中间值以后会通过key进行排序（相同key要进行合并），这里会像mysql一样先使用内存中的中间表，如果不够就会使用本地磁盘来进行排序
> 6. 排序合并完后，进行迭代遇到唯一的key就会将k/v这个结构传递给用户的Reduce函数。**Reduce函数的输出结果被附加到这部分reduce分区上的一个最终输出文件上去**。
> 7. 当完成所有的map、reduce任务后，master唤醒用户程序，此时，用户程序中的MapReduce调用会return返回到用户代码中。
> 8. 成功以后结果就在若干个输出文件中。通常，用户不需要将这若干个输出文件合并成一个文件，它们通常将这些文件作为输入传递给另一个MapReduce过程的调用，或者从另一个能够处理被分区为多个文件的来作为输入的分布式应用程序中使用它们。

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab1%EF%BC%88MapReduce%EF%BC%89/image%204.png)

> 对于图中标出的这个函数，是map函数或reduce函数的后置处理函数或是前置处理函数，例如统计单词出现的频率，这个map函数后的emit函数就可能负责是将计算出的数据持久化到磁盘中去。而reduce函数后面的这个emit函数则是负责将统一的结果输出到某个指定的位置去
> 
- 实际项目中我们需要完成的几个方面

> 
> 
> 1. 完成rpc通信的搭建
> 2. 协调器Coordinator负责整体任务产生、分配（RPC）和清点（宕机：work超10秒未完成任务，任务重新分配）
> 3. 工作器Worker负责申请任务（RPC）、完成任务
> 4. Worker超时未完成的话，Coordinator会把任务分配给其他worker，会产生两个Worker完成同一个任务，如果work直接将结果写入文件，会出现冲突。
- 注意

> 下面统一将`Coordinator称为master`，太长了不想打~~
> 

### 2.2 RPC的实现

- 概述

> 根据上面的执行图我们可以清晰的看到rpc负责是传递master与worker之间的信息，对于这个rpc文件我们主要编写这方面
> 
> - RPC结构体的定义，传递的结构体中有什么参数、字段信息。(这些结构体的名字都要大写因为声明外包调用在GO中方法名结构名要大写，也防止序列化找不到名字)
> - 输入的文件存放

### 2.3 Worker的实现

- 概述

> 上面说到worker会主动申请任务，可以看到原始代码中有一个worker申请任务并得到回复的例子，实际上就是完成了一个rpc调用
> 
> - 注意看第三个方法的的第一个参数，指定调用那个go文件的那个方法

```go
func Worker(mapf func(string, string) []KeyValue,
	reducef func(string, []string) string) {
	CallExample(...)
	...
}

func CallExample() {
	// 发送 RPC 请求，等待回复。 “Coordinator.Example”告诉接收服务器我们想调用struct Coordinator 的Example() 方法。
	ok := call("Coordinator.Example", &args, &reply)
	....
}

// 向协调器发送 RPC 请求，等待响应。通常返回真。如果出现问题，则返回 false。
func call(rpcname string, args interface{}, reply interface{}) bool {
	// c, err := rpc.DialHTTP("tcp", "127.0.0.1"+":1234")
	sockname := coordinatorSock()
	c, err := rpc.DialHTTP("unix", sockname)
	.....
}
```

- 功能完成

==worker向master循环发送心跳/请求rpc的方法——Worker==

> 此时可以看到我们没有完成reduce任务的申请的相关处理。**不断向Coordinator 发送心跳包，并根据返回结果来进行具体的操作，处理哪种任务，或者等待，或者结束。（需要提供心跳 RPC 以及完成任务的RPC）**
> 
> - 申请任务
> - 先判断任务的类型，如果是等待状态就需要当前map任务或者reduce任务全部结束才能进行接下来的流程
> - 执行任务，并向master汇报执行结果

```go
func Worker(mapf func(string, string) []KeyValue,
	reducef func(string, []string) string) {
	keepFlag := true
	for keepFlag {
		task := GetTaskFromMaster() //这个方法就是得到任务的方法
		switch task.TaskType {      //会根据任务得到不同的回应
		case MapTask:
			{
				DoMapTask(mapf, &task) //如果是map函数我们就执行并得出结果
				callDone(&task)
			}
		case ReduceTask:
			{
				DoReduceTask(reducef, &task) //如果是map函数我们就执行并得出结果
				callDone(&task)
			}
		case WaitingTask: //没任务了，自旋个一会等别的任务
			{
				fmt.Println("所有任务都在进行中，请稍候...")
				time.Sleep(time.Second)
			}
		case ExitTask:
			{
				fmt.Println("任务 :[", task.TaskId, "] 被终止...")
				keepFlag = false
			}
		}
	}
}
```

==发送rpc调用获取任务——GetTask==

> 这里会判断是否是map任务还是reduce任务，然后将空结构体传入进行远程调用并得到回应，正常返回任务
> 

```go
// GetTask 获取任务（需要知道是Map任务，还是Reduce）
func GetTaskFromMaster() Task {
	//通过call函数得到rpc调用的回应值并得到任务列表
	args := TaskArgs{}
	reply := Task{}
	ok := call("Coordinator.GetTask", &args, &reply)

	if ok {
		fmt.Println(reply)
	} else {
		fmt.Printf("向Master请求任务失败!\\n")
	}
	return reply
}
```

==如果获取的任务是map任务就开始执行——DoMapTask==

> 这个方法主要就是接收任务执行的工作，通过rpc传来的任务名与内容进行相应的分类，并且将处理的内容进行持久化到文件的操作，要将 JSON 格式的键/值对写入打开的文件：
> 
- 编码模板

```go
enc：= json.NewEncoder（file）
  for _, kv := ... {
    err := enc.Encode(&kv)
```

- 具体代码

```go
// DoMapTask 这个函数就会根据分发过来的任务，去具体执行。可以参考给定的wc.go、mrsequential.go的map方法
// 两个参数分别是任务名，以及任务的内容
func DoMapTask(mapf func(string, string) []KeyValue, t *Task) {
	fileName := t.FileInput[0]
	file, err := os.Open(fileName) //根据文件名打开文件
	if err != nil {
		log.Fatalf("不能打开 %v", fileName)
	}
	//通过io得到文件的内容
	fileContent, err := ioutil.ReadAll(file)
	if err != nil {
		log.Fatalf("不能读取 %v", fileName)
	}
	file.Close()
	tempKV := mapf(fileName, string(fileContent)) // map返回一组KV结构体数组
	buckets := t.ReducerNum                       //我们要将kv进行分类，查看分类的数量，放入指定的桶中

	// 创建一个长度为nReduce的二维切片
	HashedKV := make([][]KeyValue, buckets) //一维hash编号，二维具体kv结构
	for _, kv := range tempKV {             //按编号归位
		HashedKV[ihash(kv.Key)%buckets] = append(HashedKV[ihash(kv.Key)%buckets], kv)
	}

	for i := 0; i < buckets; i++ {
		//构造输出结果文件,文件个格式是json，名字格式：mr-tmp-x-y
		oname := "mr-tmp-" + strconv.Itoa(t.TaskId) + "-" + strconv.Itoa(i)
		ofile, _ := os.Create(oname)
		enc := json.NewEncoder(ofile) //通过json编码
		for _, kv := range HashedKV[i] {
			enc.Encode(kv)
		}
		ofile.Close()
	}
}
```

==如果获取的任务是reduce任务就开始执行——DoReduceTask&sortTask==

> **这个函数主要负责收到的reduce任务，那么我们需要将分配持久化好的每个桶（每个文件）进行集中输出，把key相同的输出到一个文件中，类似于排序并合并；在实际上每个worker都是不同的主机，所以存在很多网络传输，我们再单机就模拟一下**
> 
- 解码模板

> 因为在执行reduce函数时，需要将kv结构读出来那么就需要json的解码过程
> 

```go
dec := json.NewDecoder(file)
  for {
    var kv 键值
    if err := dec.Decode(&etc); err！= nil{
      breal
    }
    kvs = append（kvs, kv）
  }
```

- 实际代码

```go
// 我们在做reduce任务时，其实还要负责将这些kv结构把全部k相同的输出到一个文件中
func DoReduceTask(reducef func(string, []string) string, t *Task) {
	fileId := t.TaskId
	sortRes := sortTask(t.FileInput)
	dir, _ := os.Getwd()                              //读取全部路径
	tempFile, err := ioutil.TempFile(dir, "mr-tmp-*") //通过通配符的方式读取全部map生成的持久化文件
	if err != nil {
		log.Fatal("创建临时文件失败", err)
	}
	i := 0
	for i < len(sortRes) {
		j := i + 1
		//我们寻找不同key的分割线
		for j < len(sortRes) && sortRes[j].Key == sortRes[i].Key {
			j++
		}
		//然后找到分割线 ，将当前下key对应的所有的value进行合并
		var values []string
		for k := i; k < j; k++ {
			values = append(values, sortRes[k].Value)
		}
		//通过参数函数，将最后结果合并成一个文件
		mergeFile := reducef(sortRes[i].Key, values)
		fmt.Fprintf(tempFile, "%v %v\\n", sortRes[i].Key, mergeFile)
		i = j
	}
	tempFile.Close()
	//将旧文件用新文件进行覆盖
	fn := fmt.Sprintf("mr-out-%d", fileId)
	os.Rename(tempFile.Name(), fn)
}
```

- 其中负责排序解码的方法——`sortTask`

```go
// 根据map持久化的文件，进行排序根据key的字符进行字符集排序
func sortTask(files []string) []KeyValue {
	var kvs []KeyValue
	//遍历传过来的文件
	for _, fileName := range files {
		file, _ := os.Open(fileName)
		dec := json.NewDecoder(file) //通过json解码
		for {
			var kv KeyValue
			if err := dec.Decode(&kv); err != nil { //循环取结构
				break
			}
			kvs = append(kvs, kv)	//将kv都添加到kv的数组中
		}
		file.Close()
	}
	//对kv数据进行字符集升序排序
	sort.Slice(kvs, func(i, j int) bool {
		return kvs[i].Key < kvs[j].Key
	})
	return kvs
}
```

==完成任务的RPC回应——callDone==

```go
// 做完任务也需要调用rpc在协调者中将任务状态为设为已完成，
// 以方便协调者确认任务已完成，worker与协调者程序能正常退出。
func callDone(t *Task) Task {
	//通过call函数得到rpc调用的回应值并得到任务列表
	args := t
	reply := Task{}
	ok := call("Coordinator.MarkFinished", &args, &reply)

	if ok {
		fmt.Println(reply)
	} else {
		fmt.Printf("Master标记失败!\\n")
	}
	return reply
}
```

### 2.4 Coordinator的实现

- 概述

> **这个类中文名字称为调节器即master，他会接收worker的申请并为其分配相应的任务（map/reduce），接收任务完成的相关信息（需要对任务的状态进行维护，包括任务ID，完成状况，开始时间来做超时控制，任务类型等。）**
> 

==定义结构体维护全局参数以及其他结构体——Coordinator&TaskMetaHolder&TaskMetaInfo==

> • 首先是lock锁，因为rpc调用申请任务的方法需要保证并发安全
• 接下来是作为整个MapReduce的分配角色所需的字段参数，来表示任务的各种状态
• TaskMetaHolder而是任务元数据控制器，维护着一个map，索引映射元数据结构
• TaskMetaInfo元数据结构，存放master需要task的全部信息
> 

```go
var lock sync.Mutex

type Coordinator struct {
	TaskId            int            // 用于生成task的特殊id
	CurPhase          Phase          // 目前整个框架应该处于什么任务阶段
	MapTaskChannel    chan *Task     //并发安全的传递传递或接受map类型的Task
	ReduceTaskChannel chan *Task     //并发安全的传递传递或接受reduce类型的Task
	ReducerNum        int            // 传入的参数决定需要多少个reducer
	MapNum            int            // 传入的参数决定需要多少个map
	taskMetaHolder    TaskMetaHolder //存放着待分配的任务
	files             []string       //任务文件
}

//存放对应桶里面的元数据索引
type TaskMetaHolder struct {
	MetaMap map[int]*TaskMetaInfo
}

//维护任务的状态
type TaskMetaInfo struct {
	state     State     // 任务的状态
	TaskAdr   *Task     // 传入任务的指针,为的是这个任务从通道中取出来后，还能通过地址标记这个任务已经完成
}
```

==初始化master——MakeCoordinator==

> 这里就是初始化上面的字段一起开始服务，监控rpc调用情况，这里后续会多调用一些函数为了实现额外的挑战
> 

```go
//nReduce 是要使用的 reduce 任务的数量。
func MakeCoordinator(files []string, nReduce int) *Coordinator {
	c := Coordinator{
		files:    files,
		CurPhase: MapPhase,
		//初始化为有缓冲即异步的通道
		MapTaskChannel:    make(chan *Task, len(files)),
		ReduceTaskChannel: make(chan *Task, nReduce),
		ReducerNum:        nReduce,
		MapNum:            len(files),
		taskMetaHolder: TaskMetaHolder{
			MetaMap: make(map[int]*TaskMetaInfo, len(files)+nReduce),
		},
	}
	//Coordinator制作map任务，在一开始程序运行的时候就执行
	c.makeMapTasks(files)
	c.server()	//监控别的角色对master rpc调用的情况
	return &c
}
```

==生成map任务并放入通道——makeMapTasks==

> 遍历文件，生成id（这是一个全局id，map与reduce共用）并构建任务，放入map记录索引信息
> 

```go
// 将Map任务放到Map管道中，taskMetaInfo放到taskMetaHolder中。
func (c *Coordinator) makeMapTasks(files []string) {
	for _, file := range files {
		id := c.generateTaskId()
		//构建任务
		task := Task{
			TaskId:     id,
			TaskType:   MapTask,
			ReducerNum: c.ReducerNum,
			FileInput:  []string{file},
		}

		//保存当前任务状态
		taskMetaInfo := TaskMetaInfo{
			state:   Waiting, //当前任务刚被创建完属于被放在队列等待消费的状态
			TaskAdr: &task,
		}
		//将元信息保存
		c.taskMetaHolder.setTaskInfo(&taskMetaInfo)
		fmt.Println("正在生成worker任务 :", &task)
		c.MapTaskChannel <- &task
	}
}

// 将元信息保存到map中去
func (t TaskMetaHolder) setTaskInfo(TaskInfo *TaskMetaInfo) bool {
	taskId := TaskInfo.TaskAdr.TaskId
	err, _ := t.MetaMap[taskId]
	if err != nil {
		fmt.Printf("元信息已经包含%v的任务\\n", taskId)
		return false
	} else {
		t.MetaMap[taskId] = TaskInfo
	}
	return true
}

// 通过结构体的TaskId自增来获取唯一的任务id
func (c *Coordinator) generateTaskId() int {
	res := c.TaskId
	c.TaskId++
	return res
}
```

==生成reduce任务并放入通道——makeReduceTasks&selectReduceName==

> 这个也没有什么好说就是从那个map中拿到对应的元数据然后匹配任务名构建reduce任务
> 

```go
// 将reduce任务放到reduce管道中，taskMetaInfo放到taskMetaHolder中。
func (c *Coordinator) makeReduceTasks() {
	for i := 0; i < c.ReducerNum; i++ {
		id := c.generateTaskId()
		//构建任务
		task := Task{
			TaskId:    id,
			TaskType:  ReduceTask,
			FileInput: selectReduceName(i),
		}

		//保存当前任务状态
		taskMetaInfo := TaskMetaInfo{
			state:   Waiting, //当前任务刚被创建完属于被放在队列等待消费的状态
			TaskAdr: &task,
		}
		//将元信息保存
		c.taskMetaHolder.setTaskInfo(&taskMetaInfo)
		fmt.Println("正在生成reduce任务 :", &task)
		c.ReduceTaskChannel <- &task
	}
}

//这个方法就是遍历所有的中间持久化文件然后返回
func selectReduceName(i int) []string {
	var s []string
	//返回对应于当前目录的根路径名。如果当前目录可以通过多个路径（由于符号链接）到达，Getwd 可能会返回其中任何一个。
	//相当于把我们持久化的那些文件直接遍历，然后找到符合前面我们持久化文件的名字就属于reduce
	path, _ := os.Getwd()
	//把这些路径的文件全部读出来
	files, _ := ioutil.ReadDir(path)
	for _, file := range files {
		if strings.HasPrefix(file.Name(), "mr-tmp") &&
			strings.HasSuffix(file.Name(), strconv.Itoa(i)) {
			s = append(s, file.Name())
		}
	}
	return s
}
```

==master的核心方法——GetTask==

> 分配给worker任务，并更新当前master所处的阶段
> 

```go
// rpc被调用方法，被worker调用申请任务，多个worker可能会同时调用这个游戏来获取任务，所以记得加锁
func (c *Coordinator) GetTask(args *TaskArgs, reply *Task) error {
	lock.Lock()
	defer lock.Unlock()
	fmt.Println("Master从worker那里得到一个请求:")
	//我们先要当前mapreduce当前的任务状态，换而言之就是看map任务都执行完没有，没有就进入reduce阶段
	switch c.CurPhase {
	case MapPhase: //如果通道里还有任务或者还有map任务没有执行完，那么分配给worker map任务
		{
			if len(c.MapTaskChannel) > 0 {
				//由于传过来的是地址，那就再取一次指针拿到具体的数据，然后将通道里面的任务输出，同样需要指针处理因为我们
				//希望任务从始至终就处理对应的拿一个
				*reply = *<-c.MapTaskChannel
				//这里其实就是多做一次健壮，就怕任务在被执行还没出通道
				if !c.taskMetaHolder.judgeTaskState(reply.TaskId) {
					fmt.Printf("任务id[ %d ]正在被别的线程执行\\n", reply.TaskId)
				}
			} else { //通道没任务，那么此时就在等所有map任务执行完
				reply.TaskType = WaitingTask
				//检查任务完成情况，返回true则全部完成，就进入下一个阶段
				if c.taskMetaHolder.checkTaskDone() {
					c.toNextPhase()
				}
				return nil //就是没有任务可申请喽
			}
		}
	case ReducePhase: //如果正在执行reduce阶段，这里我们对应的worker还没有实现处理reduce的方法
		{
			if len(c.ReduceTaskChannel) > 0 {
				//由于传过来的是地址，那就再取一次指针拿到具体的数据，然后将通道里面的任务输出，同样需要指针处理因为我们
				//希望任务从始至终就处理对应的拿一个
				*reply = *<-c.ReduceTaskChannel
				//这里其实就是多做一次健壮，就怕任务在被执行还没出通道
				if !c.taskMetaHolder.judgeTaskState(reply.TaskId) {
					fmt.Printf("任务id[ %d ]正在被别的线程执行\\n", reply.TaskId)
				}
			} else { //通道没任务，那么此时就在等所有reduce任务执行完
				reply.TaskType = WaitingTask
				//检查任务完成情况，返回true则全部完成，就进入下一个阶段
				if c.taskMetaHolder.checkTaskDone() {
					c.toNextPhase()
				}
				return nil //就是没有任务可申请喽
			}
		}
	case AllDone: //默认处理
		{
			reply.TaskType = ExitTask
		}
	default:
		panic("mapReduce可没有这么多状态哦")
	}

	return nil
}
```

> • `judgeTaskState`：判断传入的任务状态并且根据情况更新
• `checkTaskDone`：判断整个MapReduce的任务情况
• `toNextPhase`：更改master的阶段
> 

```go
// 判断给定任务是否在工作，并修正其目前任务信息状态
func (t *TaskMetaHolder) judgeTaskState(taskId int) bool {
	taskInfo, ok := t.MetaMap[taskId]
	if !ok || taskInfo.state != Waiting {
		return false
	}
	taskInfo.state = Working
	return true
}

// 检查多少个任务做了包括（map、reduce）,
func (t *TaskMetaHolder) checkTaskDone() bool {

	var (
		mapDoneNum      = 0
		mapUnDoneNum    = 0
		reduceDoneNum   = 0
		reduceUnDoneNum = 0
	)

	// 遍历储存task信息的map
	for _, v := range t.MetaMap {
		// 首先判断任务的类型
		if v.TaskAdr.TaskType == MapTask {
			// 判断任务是否完成,下同
			if v.state == Done {
				mapDoneNum++
			} else {
				mapUnDoneNum++
			}
		} else if v.TaskAdr.TaskType == ReduceTask {
			if v.state == Done {
				reduceDoneNum++
			} else {
				reduceUnDoneNum++
			}
		}

	}
	fmt.Printf("map任务完成了 %d/%d, reduce任务完成了 %d/%d \\n",
		mapDoneNum, mapDoneNum+mapUnDoneNum, reduceDoneNum, reduceDoneNum+reduceUnDoneNum)

	// 如果某一个map或者reduce全部做完了，代表需要切换下一阶段，返回true

	return (reduceDoneNum > 0 && reduceUnDoneNum == 0) || (mapDoneNum > 0 && mapUnDoneNum == 0)
}

func (c *Coordinator) toNextPhase() {
	if c.CurPhase == MapPhase {
		//如果是map阶段全部任务完成，那么就该进入下一个reduce阶段
		c.makeReduceTasks()
		c.CurPhase = ReducePhase
	} else if c.CurPhase == ReducePhase {
		c.CurPhase = AllDone
	}
}
```

==被远程调用并更新任务状态的方法——MarkFinished==

> **说之前我们先考虑一种情况，Worker超时未完成的话，Coordinator会把任务分配给其他worker，会产生两个Worker完成同一个任务，如果work直接将结果写入文件，会出现冲突——这一部分的实现是在后面的容灾机制**
> 

> **这时我们应该在对该任务完成前做一次校验后任务提交（标记mark）这个动作应该由master完成还是worker来完成？**
> 

> **我们在代码中采用了`前者`，看到两者的区别本质上前者少了一次rpc调用响应更快，但缺点是所有 Task 的最终 Commit 都由 Coordinator 完成，在极端场景下会让 Coordinator 变成整个 MapReduce 过程的性能瓶颈**。
> 
> - `Coordinator Commit`：Worker 向 Coordinator 汇报Task完成，Coordinator 确认该 Task 是否仍属于该 Worker，**是Coordinator则进行结果文件 Commit，否则直接忽略**
> - `Worker Commit`：Worker 向 Coordinator 汇报 Task 完成，Coordinator 确认该 Task 是否仍属于该 Worker 并响应 Worker，**是则 Worker 进行结果文件 Commit，再向 Coordinator 汇报 Commit 完成**
- 实际代码

> **这个函数是提供给worker检查当前任务完成的状态好去接下一个任务，检查状态的同时也会更新最新的任务状态，呼应`judgeTaskState`函数能够得到最新的任务状态，好让master准确的做出阶段的转化等**
> 
> - 出现上面这种崩溃时为了防止使用者观察到部分写入的文件，MapReduce 论文提到了使用临时文件并在完全写入后自动重命名它的技巧。这一点在函数Worker#DoReduceTask中体现的十分明显，这个操作也就很好的区分了 Write 和 Commit 的过程。

```go
// 标记当前任务的完成状态
func (c *Coordinator) MarkFinished(args *Task, reply *Task) error {
	lock.Lock()
	defer lock.Unlock()
	switch args.TaskType {
	case MapTask:
		meta, ok := c.taskMetaHolder.MetaMap[args.TaskId]
		//防止从另一个worker返回的重复工作
		if ok && meta.state == Working {
			meta.state = Done
			fmt.Printf("map任务[%d]正在执行.\\n", args.TaskId)
		} else {
			fmt.Printf("map任务[%d]已经完成 ! ! !\\n", args.TaskId)
		}
		break
	case ReduceTask:
		meta, ok := c.taskMetaHolder.MetaMap[args.TaskId]

		//防止从另一个worker返回的重复工作
		if ok && meta.state == Working {
			meta.state = Done
			fmt.Printf("reduce任务[%d]正在执行.\\n", args.TaskId)
		} else {
			fmt.Printf("reduce任务[%d]已经完成 ! ! !\\n", args.TaskId)
		}
		break

	default:
		panic("任务类型未定义 ! ! !")
	}
	return nil
}
```

### 2.5 模拟测试系统崩溃的容灾机制

- 概述

> 测试崩溃恢复，要使用mrapps/crash.go 应用程序插件。它在 `Map和Reduce` 函数中随机退出。
> 
> - [宏观上大局的测试文件是test-mr.sh](http://xn--test-mr-fw3kq2eoz9bt7f08bf87ci6b658bkx7asm2ei2h.sh/)，控制着所有进程，如果我们需要完成额外挑战可能要调整参数
- 改造

> 我们需要改造原有的代码来体现更多的信息
> 

==元数据结构改造==

> 对于建立任务后存储的任务元信息中我们要添加任务创建的时间，并规定一个超时时间，超过以后就代表这个worker崩溃，我们就需要进行容灾恢复
> 

```go
//维护任务的状态
type TaskMetaInfo struct {
	state     State     // 任务的状态
	StartTime time.Time //开始时间
	TaskAdr   *Task     // 传入任务的指针,为的是这个任务从通道中取出来后，还能通过地址标记这个任务已经完成
}
```

==判断任务状态改造==

> 这个开始时间变量的初始化就在这里，这个函数会判断当前任务的状态并更新成开始执行，那么任务正式开始的时间就在这里
> 

```go
// 判断给定任务是否在工作，并修正其目前任务信息状态
func (t *TaskMetaHolder) judgeTaskState(taskId int) bool {
	taskInfo, ok := t.MetaMap[taskId]
	if !ok || taskInfo.state != Waiting {
		return false
	}
	taskInfo.state = Working
	taskInfo.StartTime = time.Now()	//任务开始
	return true
}
```

==最重要的来了——崩溃探测器CrashSearch==

> 这同样是一个并发任务，因为每个任务都会去这个函数中检查，所以需要加锁，本质上是一个循环直到任务被完成结束，**注意锁的获取处理**
> 

```go
// 探测某个worker下线进行更换的容灾操作
func (c *Coordinator) CrashSearch() {
	for {
		time.Sleep(time.Second * 3) //确保master的其他方法能够拿到锁，要不然探测器会疯狂的获取锁导致其他方法失败
		lock.Lock()
		if c.CurPhase == AllDone { //所有任务都完成了还检测啥啊
			lock.Unlock()
			break
		}

		for _, taskInfo := range c.taskMetaHolder.MetaMap {
			if taskInfo.state == Working { //如果正在工作那么看看执行时间
				fmt.Println("任务[", taskInfo.TaskAdr.TaskId, "] 执行了: ", time.Since(taskInfo.StartTime), "s秒")
			}
			//如果超时大于10秒了进行切换worker
			if taskInfo.state == Working && time.Since(taskInfo.StartTime) > 10*time.Second {
				fmt.Println("任务[", taskInfo.TaskAdr.TaskId, "] 超时")
				switch taskInfo.TaskAdr.TaskType {
				case MapTask: //将任务重新放回对应的通道中，并更新相应状态
					{
						c.MapTaskChannel <- taskInfo.TaskAdr
						taskInfo.state = Waiting
					}
				case ReduceTask:
					{
						c.ReduceTaskChannel <- taskInfo.TaskAdr
						taskInfo.state = Waiting
					}
				}
			}
		}
		lock.Unlock()
	}
}
```

> 最后别忘记在master初始化时要开启探测器协程
> 

```go
go c.CrashSearch()	//开启协程去探测
```
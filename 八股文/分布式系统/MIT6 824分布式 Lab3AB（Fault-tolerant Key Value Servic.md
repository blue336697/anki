# MIT6.824分布式 | Lab3AB（Fault-tolerant Key/Value Service）

type: Post
status: Published
date: 2023/04/14
summary: Fault-tolerant Key/Value Service
tags: 实践
category: 分布式

# LabA

## 1.任务分析

- 架构图

> 在lab2中我们基本完善了Raft服务，各种应用是基于Raft服务完成分布式的特性，那么我们现在就要做一个应用来试试Raft服务怎么样。在本次lab中要求我们简单实现一个KV数据库以及其中的`Put（key,value）、Append（key, arg）和 Get（key）`操作
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab3AB%EF%BC%88Fault-tolerant%20Key%20Value%20Servic/image.png)

- 简化图

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab3AB%EF%BC%88Fault-tolerant%20Key%20Value%20Servic/image%201.png)

## 2.客户端（client）

### 2.1 Clerk结构体与初始化

- 概述

> clerk实际就是客户端的代理，保存多个客户端的实体以及此时的raft中leader是谁等信息
> 
- 结构体

> **这里特别说一下序列号的作用，当leader接收这个请求开始处理时如果刚commit完了就挂壁了还没给客户端响应，那么此时客户端会重复请求，如果新的leader不知道这个序列号那就必须重新执行一遍**
> 

```go
type Clerk struct {
	servers []*labrpc.ClientEnd
	// You will have to modify this struct.
	seqId    int   // 客户端的请求序号
	leaderId int   // 当前leader的id
	clientId int64 // 客户端的唯一标识
}
```

- 初始化

```go
func MakeClerk(servers []*labrpc.ClientEnd) *Clerk {
	ck := new(Clerk)
	ck.servers = servers
	// You'll have to add code here.
	ck.clientId = nrand()
	ck.leaderId = mathrand.Intn(len(ck.servers))
	return ck
}
```

### 2.2 Operator 发送

==GET==

> 没什么说的循环遍历到leader执行
> 

```go
func (ck *Clerk) Get(key string) string {
	// You will have to modify this function.
	ck.seqId++
	args := GetArgs{
		Key:      key,
		ClientId: ck.clientId,
		LeaderId: ck.leaderId,
	}
	severId := ck.leaderId //这个leaderID是我们在所有节点中随机的，如果不对就循环试
	//自旋等待返回结果
	for {
		reply := GetReply{}
		ok := ck.servers[severId].Call("KVServer.Get", &args, &reply)
		if ok && reply.Err == OK {
			ck.leaderId = severId
			return reply.Value
		} else if reply.Err == ErrNoKey {
			ck.leaderId = severId
			return ""
		} else if reply.Err == ErrWrongLeader {
			//如果不是这个leader，就尝试下一个
			severId = (severId + 1) % len(ck.servers)
			continue
		}
		//别的错误，继续尝试
		severId = (severId + 1) % len(ck.servers)
	}
}
```

==PutAppend==

```go
func (ck *Clerk) PutAppend(key string, value string, op string) {
	// You will have to modify this function.
	ck.seqId++
	args := PutAppendArgs{
		Key:      key,
		Value:    value,
		Op:       op,
		ClientId: ck.clientId,
		LeaderId: ck.leaderId,
	}
	severId := ck.leaderId //这个leaderID是我们在所有节点中随机的，如果不对就循环试
	for {
		reply := PutAppendReply{}
		ok := ck.servers[severId].Call("KVServer.PutAppend", &args, &reply)
		if ok && reply.Err == OK {
			ck.leaderId = severId
			return
		} else if reply.Err == ErrWrongLeader {
			//如果不是这个leader，就尝试下一个
			severId = (severId + 1) % len(ck.servers)
			continue
		}
		//别的错误，继续尝试
		severId = (severId + 1) % len(ck.servers)
	}
}

func (ck *Clerk) Put(key string, value string) {
	ck.PutAppend(key, value, "Put")
}
func (ck *Clerk) Append(key string, value string) {
	ck.PutAppend(key, value, "Append")
}
```

## 3.服务端（server）

### 3.1 操作符结构体、服务结构体

- Op结构体

> 因为结构体会一直传输到raft层来识别到底对数据干什么，那么他就要携带一些识别信息，并且传回也是通过这个结构体传回，同样也要携带信息
> 

```go
type Op struct {
	// Your definitions here.
	// 字段名称必须以大写字母开头，否则 RPC 将中断。
	SeqId    int
	Key      string
	Value    string
	ClientId int64
	Index    int // raft服务层传来的Index
	OpType   string
}
```

- KVServer结构体

> 作为服务层的实体，他会临时存储一些结果，一些结构信息
> 

```go
type KVServer struct {
	mu      sync.Mutex
	me      int
	rf      *raft.Raft
	applyCh chan raft.ApplyMsg
	dead    int32 // set by Kill()

	maxraftstate int // snapshot if log grows this big

	// Your definitions here.
	seqMap    map[int64]int     //为了确保seq只执行一次	clientId / seqId
	waitChMap map[int]chan Op   //传递由下层Raft服务的appCh传过来的command	index / chan(Op)
	kvPersist map[string]string // 存储持久化的KV键值对	K / V
}
```

- 初始化

```go
func StartKVServer(servers []*labrpc.ClientEnd, me int, persister *raft.Persister, maxraftstate int) *KVServer {
	// call labgob.Register on structures you want
	// Go's RPC library to marshall/unmarshall.
	labgob.Register(Op{})

	kv := new(KVServer)
	kv.me = me
	kv.maxraftstate = maxraftstate

	// You may need initialization code here.

	kv.applyCh = make(chan raft.ApplyMsg)
	kv.rf = raft.Make(servers, me, persister, kv.applyCh)

	// You may need initialization code here.
	kv.seqMap = make(map[int64]int)
	kv.waitChMap = make(map[int]chan Op)
	kv.kvPersist = make(map[string]string)

	go kv.handlerLoop() //对这层信息进行处理，可以理解为中转站，对上层与下层数据进行处理、持久化等
	return kv
}
```

### 3.2 Operator RPC

==GET==

```go
func (kv *KVServer) Get(args *GetArgs, reply *GetReply) {
	// Your code here.
	if kv.killed() {
		reply.Err = ErrWrongLeader
		return
	}
	_, isLeader := kv.rf.GetState()
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}
	op := Op{Key: args.Key, ClientId: args.ClientId, SeqId: args.SeqId, OpType: "Get"}
	lastIndex, _, _ := kv.rf.Start(op)
	//获取日志结束位置lastIndex的缓冲chan
	ch := kv.getWaitCh(lastIndex)
	defer func() {
		kv.mu.Lock()
		//从map中删除index
		delete(kv.waitChMap, op.Index)
		kv.mu.Unlock()
	}()
	//设置定时器
	timer := time.NewTimer(100 * time.Millisecond)
	defer timer.Stop()
	select {
	case replyOp := <-ch: //从下层Raft服务的appCh中获取command
		if replyOp.ClientId == op.ClientId && replyOp.SeqId == op.SeqId {
			reply.Err = OK
			kv.mu.Lock()
			reply.Value = kv.kvPersist[args.Key]
			kv.mu.Unlock()
			return
		} else {
			reply.Err = ErrWrongLeader
			return
		}
	case <-timer.C:
		reply.Err = ErrWrongLeader
	}
}
//获得raft传回index位置的缓冲chan
func (kv *KVServer) getWaitCh(index int) chan Op {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	ch, isExists := kv.waitChMap[index]
	if !isExists {
		kv.waitChMap[index] = make(chan Op, 1)
		ch = kv.waitChMap[index]
	}
	return ch
}
```

==处理server层的Handler==

> **这个handler在server启动时就一直运行，主要就是为了应对重复请求的情况，对于多次请求直接返回缓存通道里面的操作符结果就好了，我们能一直保证操作符结果是最新的通过对比客户端id与请求序列号**
> 

```go
// 这个方法主要就是中转数据，在raft对数据进行commit后再apply通道获取数据并对数据进行类似缓存操作
func (kv *KVServer) handlerLoop() {
	for {
		if kv.killed() {
			return
		}
		select {
		case msg := <-kv.applyCh: //获取到apply以后的消息
			index := msg.CommandIndex
			op := msg.Command.(Op) //将记录在日志的指令操作赋值给操作符结构体
			//检查这个客户端是否重复请求，不重复再继续
			if !kv.isDuplicate(op.ClientId, op.SeqId) {
				kv.mu.Lock()
				switch op.OpType {
				case "Put":
					kv.kvPersist[op.Key] = op.Value
				case "Append":
					kv.kvPersist[op.Key] += op.Value
				}
				kv.seqMap[op.ClientId] = op.SeqId
				kv.mu.Unlock()
			}
			kv.getWaitCh(index) <- op
		}
	}
}
//判断是否为重复请求，是的话就不进行缓存了
func (kv *KVServer) isDuplicate(clientId int64, seqId int) bool {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	lastSeqId, isExists := kv.seqMap[clientId]
	if !isExists {
		return false
	}
	//如果当前seqId小于等于上次的seqId，说明是之前的请求，重复了
	return seqId <= lastSeqId
}
```

==PutAppend==

> 这个函数也是照葫芦画瓢
> 

```go
func (kv *KVServer) PutAppend(args *PutAppendArgs, reply *PutAppendReply) {
	// Your code here.
	if kv.killed() {
		return
	}
	_, idLeader := kv.rf.GetState()
	if !idLeader {
		reply.Err = ErrWrongLeader
		return
	}
	op := Op{Key: args.Key, Value: args.Value, ClientId: args.ClientId, SeqId: args.SeqId, OpType: args.Op}
	lastIndex, _, _ := kv.rf.Start(op)
	ch := kv.getWaitCh(lastIndex)
	defer func() {
		kv.mu.Lock()
		delete(kv.waitChMap, op.Index)
		kv.mu.Unlock()
	}()

	timer := time.NewTimer(100 * time.Millisecond)
	select {
	//这里从通道里获取的op已经是经过中间handler缓存的过得结果了
	case replyOp := <-ch:
		if replyOp.ClientId == op.ClientId && replyOp.SeqId == op.SeqId {
			reply.Err = OK
		} else {
			reply.Err = ErrWrongLeader
		}
	case <-timer.C:
		reply.Err = ErrWrongLeader
	}
	defer timer.Stop()
}
```

# LabB

## 1.任务分析

- 概述

> B部分的任务就是在A的基础上完成从快照读取以减少从日志读取的时间，当我们日志大小在server超过最大日志量时就要给raft发送请求，让其转换成快照并返回。在2D中完成的功能则是通过快照进行恢复，并且生成快照的时机是由测试架构决定的。在本次lab我们要在server层生成快照
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab3AB%EF%BC%88Fault-tolerant%20Key%20Value%20Servic/image%202.png)

在本次lab中我们进行快照的信息是KV键值对，因为我们的应用就是KV数据库，以及客户端与请求序列号的映射关系

## 2.服务端（server）

### 2.1 重写handler

- handlerLoop

> 我们在其中加入两个判断：
> 
> 1. 一是判断是否有新的日志被提交，即发生了PUT/APPEND操作的情况，那么就要判断增加的日志是否大于我们设置的快照阈值，如果满足就要让raft进行一次快照的建立，这个快照是通过前面操作符执行过后返回到server层的各种信息组成
> 2. 二是判断快照是否产生，如果产生了新快照直接反序列化出来

```go
func (kv *KVServer) handlerLoop() {
	for {
		if kv.killed() {
			return
		}
		select {
		case msg := <-kv.applyCh: //获取到apply以后的消息
			if msg.CommandValid { //CommandValid为true就代表有新提交的日志
				if msg.CommandIndex <= kv.lastIncludeIndex {
					return
				}
				index := msg.CommandIndex
				op := msg.Command.(Op) //将记录在日志的指令操作赋值给操作符结构体
				//检查这个客户端是否重复请求，不重复再继续
				if !kv.isDuplicate(op.ClientId, op.SeqId) {
					kv.mu.Lock()
					switch op.OpType {
					case "Put":
						kv.kvPersist[op.Key] = op.Value
					case "Append":
						kv.kvPersist[op.Key] += op.Value
					}
					kv.seqMap[op.ClientId] = op.SeqId
					kv.mu.Unlock()
				}
				//如果增加日志后大于临界值那就需要快照
				if kv.maxraftstate != -1 && kv.rf.GetRaftStateSize() > kv.maxraftstate {
					snapShot := kv.PersistSnapShot()
					kv.rf.Snapshot(msg.CommandIndex, snapShot)
				}
				kv.getWaitCh(index) <- op
			}
			if msg.SnapshotValid { //如果有新的快照，将其反序列化
				kv.mu.Lock()
				if kv.rf.CondInstallSnapshot(msg.SnapshotTerm, msg.SnapshotIndex, msg.Snapshot) {
					kv.DecodeSnapShot(msg.Snapshot)
					kv.lastIncludeIndex = msg.SnapshotIndex
				}
				kv.mu.Unlock()
			}
		}
	}
}
```

### 2.2 序列化与反序列化

```go
// 反序列化
func (kv *KVServer) DecodeSnapShot(snapshot []byte) {
	if snapshot == nil || len(snapshot) < 1 {
		return
	}
	r := bytes.NewBuffer(snapshot)
	d := labgob.NewDecoder(r)

	var kvPersist map[string]string
	var seqMap map[int64]int
	if d.Decode(&kvPersist) == nil && d.Decode(&seqMap) == nil {
		kv.kvPersist = kvPersist
		kv.seqMap = seqMap
	} else {
		fmt.Printf("[Server(%v)] Failed to decode snapshot！！！", kv.me)
	}
}

// 序列化，即持久化server的数据
func (kv *KVServer) PersistSnapShot() []byte {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	e.Encode(kv.kvPersist)
	e.Encode(kv.seqMap)
	data := w.Bytes()
	return data
}
```

### 2.3 其他

- 在初始化的时候需要读取是否再存快照，如果有就要进行解码
- 并增加一个新的变量`lastIncludeIndex`去确保每次编解码时的快照位于日志的什么部分
    
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c2a89fde1116d357941c2e55ccccfe8e.png)
# MIT6.824分布式 | Lab2（GFS：RaftA&B&C&D）—— 后篇

type: Post
status: Published
date: 2023/04/08
summary: GFS：RaftA&B&C&D
tags: 实践
category: 分布式

## 流程图

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image.png)

## Raft-A（结构体、RPC参数、Leader选举）

- 概述

> 此时正式开始编写raft的实验，分为四个部分现在写A。在A的内容主要就是要实现单一Leader的选举，建议每次实验前去看一下官方的实验要求[官方文档要求](https://pdos.csail.mit.edu/6.824/labs/lab-raft.html)
> 
- 注意

> 类似于下面的红色地方调用rpc发送，一定要注意不能更改内容，因为通过字符串方式然后反射找到对应的RPC内容方法进行发送，改变就找不到了
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%201.png)

### 1.各种结构体的实现

### 1.1 State的实现

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%202.png)

- Raft.go中的各类state——全局枚举常量

```go
// Status 节点的角色
type Status int

// VoteState 投票的状态 2A
type VoteState int

// AppendEntriesState 追加日志的状态 2A 2B
type AppendEntriesState int

// HeartBeatTimeout 定义一个全局心跳超时时间
var HeartBeatTimeout = 120 * time.Millisecond

// 枚举节点的类型：跟随者、竞选者、领导者
const (
	Follower Status = iota
	Candidate
	Leader
)

const (
	Normal VoteState = iota //投票过程正常
	Killed                  //Raft节点已终止
	Expire                  //投票(消息\\竞选者）过期
	Voted                   //本Term内已经投过票

)

const (
	AppNormal    AppendEntriesState = iota // 追加正常
	AppOutOfDate                           // 追加过时
	AppKilled                              // Raft程序终止
	AppRepeat                              // 追加重复 (2B
	AppCommitted                           // 追加的日志已经提交 (2B
	Mismatch                               // 追加不匹配 (2B

)
```

- raft.go——raft结构体

> 每个变量都有备注标注应该都是比较好理解的
> 

```go
// 实现单个 Raft 节点的 Go 对象。
type Raft struct {
	mu        sync.Mutex          // 锁定以保护对该节点状态的共享访问
	peers     []*labrpc.ClientEnd // 所有节点的 RPC 端点
	persister *Persister          // 保持此对等方持久状态的对象
	me        int                 // 该节点在 peers[] 中的索引
	dead      int32               // 由 Kill() 设置
	// Your data here (2A, 2B, 2C).
	// 查看论文的图 2，了解 Raft 服务器必须保持的状态。
	currentTerm int        // 服务器最后知道的任期号（初始化为 0，持续递增）
	votedFor    int        // 在当前获得选票的候选人（投给某个人）的 Id(初始化为 -1，表示没有投票给任何人)
	logs        []LogEntry // 日志条目数组，包含了状态机要执行的指令集，以及收到领导时的任期号

	//服务器常修改的状态
	commitIndex int // 已知的最大的已经被提交的日志条目的索引值（初始化为 0，持续递增）
	lastApplied int // 最后被应用到状态机的日志条目索引值（初始化为 0，持续递增）

	//leader 常修改的状态
	//nextIndex与matchIndex初始化长度应该为len(peers)，Leader对于每个Follower都记录他的nextIndex和matchIndex
	nextIndex  []int // 对于每个服务器，需要发送给他的下一个日志条目的索引值（初始化为 leader 最后日志索引加 1）
	matchIndex []int // 对于每个服务器，已经复制给他的日志的最高索引值（初始化为 0，持续递增）

	//自定义状态
	state    Status        // 节点的角色（状态）
	overtime time.Duration //超时时间
	timer    *time.Timer   //每个节点的计时器

	applyChan chan ApplyMsg // 用于提交日志的通道（2B）
}
```

### 1.2 AppendEntries PRC的实现

- 概述

> 日志的增量同步，日志的各种信息都是通过这个结构体来进行同步的
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%203.png)

```go
// AppendEntriesArgs由leader复制log条目，也可以当做是心跳连接，注释中的rf为leader节点
type AppendEntriesArgs struct {
	Term         int        // leader 的任期号
	LeaderId     int        // 发送请求的领导者的 Id，以便于跟随者重定向请求
	PrevLogIndex int        // 新的日志条目紧随之前的索引值，那么就是len（logs）+1的长度，初始化为leader.nextIndex - 1
	PrevLogTerm  int        // PrevLogIndex 条目的任期号，初始化为leader.currentTerm
	Entries      []LogEntry // 需要存储的日志条目（可能为空即为心跳连接，但不能为 null）
	LeaderCommit int        // 领导者已经提交的日志的索引值
}

type AppendEntriesReply struct {
	Term     int                // 当前任期号，以便于领导者去更新自己过期的任期号
	Success  bool               // 跟随者包含了匹配上 prevLogIndex 和 prevLogTerm 的日志才会进行追加，不匹配返回false
	AppState AppendEntriesState // 追加日志的状态
}
```

### 1.3 RequestVote RPC的实现

- 概述

> 日志请求的结构体，就是有选取时有同步的需求就会发送这个请求去进行投票
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%204.png)

```go
// 示例 RequestVote RPC 参数结构
type RequestVoteArgs struct {
	// Your data here (2A, 2B).
	Term         int // 候选人的任期号
	CandidateId  int // 请求选票的候选人的 Id
	LastLogIndex int // 候选人的最后日志条目的索引值
	LastLogTerm  int // 候选人最后日志条目的任期号
}

// 示例 RequestVote RPC 回复结构。
// 如果竞选者任期比自己的任期还短，那就不投票，返回false
// 如果当前节点的votedFor为空，且竞选者的日志条目跟收到者的一样新则把票投给该竞选者
type RequestVoteReply struct {
	// Your data here (2A).
	Term        int       // 当前任期号，以便于候选人去更新自己过期的任期号
	VoteGranted bool      // 候选人赢得了此张选票时为真
	VoteState   VoteState //投票状态
}
```

### 2.领导选举

- 概述

> 接下来就是比较难的领导选举了，设计到节点状态的变化，计时器的重置时机、rpc的容灾机制，索引的正确引用等等
> 

### 2.1 初始化raft节点

- make函数

```go
// 服务或测试人员想要创建一个 Raft 服务器。所有 Raft 服务器（包括这个）的端口都在 peers[] 中。
// 这个服务器的端口是 peers[me]。所有服务器的 peers[] 数组都具有相同的顺序。
// persister 是此服务器保存其持久状态的地方，并且最初还保存最近保存的状态（如果有）。
// applyCh 是测试人员或服务期望 Raft 发送 ApplyMsg 消息的通道。
// Make() 必须快速返回，因此它应该为任何长时间运行的工作启动 goroutines。
func Make(peers []*labrpc.ClientEnd, me int,
	persister *Persister, applyCh chan ApplyMsg) *Raft {
	rf := &Raft{}
	rf.peers = peers
	rf.persister = persister
	rf.me = me

	// Your initialization code here (2A, 2B, 2C).

	rf.applyChan = applyCh // 通知 applyCh 有新的日志条目被提交,2B

	rf.currentTerm = 0
	rf.votedFor = -1
	rf.logs = make([]LogEntry, 1)

	rf.commitIndex = 0
	rf.lastApplied = 0

	rf.nextIndex = make([]int, len(peers))
	rf.matchIndex = make([]int, len(peers))

	rf.state = Follower
	rf.electionTimer = time.Duration(time.Duration(rand.Intn(150)+150) * time.Millisecond) // 随机产生选举时间150~300ms
	rf.heartbeatTimer = time.NewTimer(time.Duration(50) * time.Millisecond)                // 心跳定时器

	// 从崩溃前持续存在的状态初始化
	rf.readPersist(persister.ReadRaftState())

	// 启动 ticker goroutine 开始选举
	go rf.ticker()

	return rf
}
```

### 2.2 建立主动心跳

- ticker函数

> 初始化的时候给每个timer设了一个心跳时间，并通过select监听，时间一过就根据其当前节点的status去进行选举/日志同步。
> 
> - 上面讲到过是会有连续两次以上的小概率发生，因为如果每个节点的过期时间都随机到了一样的那就有可能发生每个节点票数一致的情况（上面介绍过这个情况——分割选票）

```go
// 如果这个对等方最近没有收到心跳，则 ticker go 例程将开始新的选举
func (rf *Raft) ticker() {
	for rf.killed() == false {
		//您在此处的代码用于检查是否应开始领导者选举并使用 time.Sleep() 随机化休眠时间。
		select {
		case <-rf.heartbeatTimer.C: // 查看心跳计时器的状态
			if rf.killed() {
				return
			}
			rf.mu.Lock()
			switch rf.state {
			case Follower:
				rf.state = Candidate
				fallthrough
			case Candidate:
				// 开始选举，初始化自己的任期号，投给自己
				rf.currentTerm += 1
				rf.votedFor = rf.me
				voteNums := 1 //统计投票数

				//每轮选举都要重置选举超时时间
				rf.electionTimer = time.Duration(rand.Int63n(300)+300) * time.Millisecond // 300~600ms
				rf.heartbeatTimer.Reset(rf.electionTimer)                                 // 重置心跳计时器

				//开始选举
				for i := 0; i < len(rf.peers); i++ {
					if i == rf.me {
						continue
					}
					// 向其他服务器发送选举请求
					go func(i int) {
						voteArgs := RequestVoteArgs{
							Term:         rf.currentTerm,
							CandidateId:  rf.me,
							LastLogIndex: rf.getLastLogIndex(),
							LastLogTerm:  rf.getLastLogTerm(),
						}
						voteReply := RequestVoteReply{}
						go rf.sendRequestVote(i, &voteArgs, &voteReply, &voteNums) // 异步发送选举请求
					}(i)
				}
				// 收到心跳，重置选举超时时间
			case Leader:
				//进行心跳同步，日志同步
				appendNums := 1                           //统计同步成功的服务器数量
				rf.heartbeatTimer.Reset(HeartBeatTimeout) // 重置心跳计时器
				//构造msg
				for i := 0; i < len(rf.peers); i++ {
					if i == rf.me {
						continue
					}
					appendEntriesArgs := AppendEntriesArgs{
						Term:         rf.currentTerm,
						LeaderId:     rf.me,
						PrevLogIndex: rf.getLastLogIndex(),
						PrevLogTerm:  rf.getLastLogTerm(),
						Entries:      nil,
						LeaderCommit: rf.commitIndex,
					}
					appendEntriesReply := AppendEntriesReply{}
					go rf.sendAppendEntries(i, &appendEntriesArgs, &appendEntriesReply, &appendNums)
				}
			}
		}
		rf.mu.Unlock()
	}
}
```

### 2.3 PRC投票请求

- 概述

> 在上面其实也介绍过两个限制条件，还有一个要注意的点是当前rf节点发送到别的rf的节点的RPC框架中已经给出，为sendRequestVote方法。
> 
> 1. 首先竞选者的任期必须大于自己的任期。否则返回false。因为在出先网络分区时，可能两个分区分别产生了两个leader。那么我们认为应该是任期长的leader拥有的数据更完整。（在可视化中也有）。
> 2. 因此第二条就是，投票成功的前提的是，你自己的票要没投过给别人，且竞选者的日志状态要和你的一致。
- sendRequestVote函数

> **注意我们在原始的基础加上了一个voteNums的参数，来辅助我们判断当前结点的状态；同时注意在每轮选举结束后每个结点的状态可能会有所不同，所以这个重置结点状态的时机一定要注意，因为当进行rpc的时候，基本情况下是谁先拉到多数票谁就有机会更早的成为leader。 那么就可以在你拉票的时候进行状态重置。因为先成为竞选者，先把自己的term就加一那么在一开始任期相同情况下该竞选者就会把其他raft进行重置。**
> 

```go
func (rf *Raft) sendRequestVote(server int, args *RequestVoteArgs, reply *RequestVoteReply, voteNums *int) bool {
	if rf.killed() {
		return false
	}
	ok := rf.peers[server].Call("Raft.RequestVote", args, reply)
	for !ok {
		if rf.killed() {
			return false
		}
		ok = rf.peers[server].Call("Raft.RequestVote", args, reply)
	}
	rf.mu.Lock()
	defer rf.mu.Unlock()
	//由于网络分区，请求投票的人的term的比自己的还小，不给予投票
	if args.Term < rf.currentTerm {
		return false
	}
	switch reply.VoteState {
	//消息如果过期了有两种情况：1.是本身的term过期了比节点还小 2.节点日志的条目数落后于节点
	case Expire:
		rf.status = Follower //变成跟随者
		rf.heartbeatTimer.Reset(rf.electionTimer)
		if reply.Term > rf.currentTerm {
			rf.currentTerm = reply.Term
			rf.votedFor = -1
		}
	case Normal, Voted:
		//根据是否投票成功，更新投票数
		if reply.VoteGranted && reply.Term == rf.currentTerm && *voteNums <= (len(rf.peers)/2) {
			*voteNums++
		}
		//如果投票数大于一半，成为leader
		if *voteNums >= (len(rf.peers)/2)+1 {
			*voteNums = 0
			if rf.status == Leader {
				return ok
			}
			//如果之前不是leader，初始化nextIndex和matchIndex
			rf.status = Leader
			rf.nextIndex = make([]int, len(rf.peers))
			for i, _ := range rf.nextIndex {
				rf.nextIndex[i] = len(rf.logs) + 1
			}
			rf.heartbeatTimer.Reset(HeartBeatTimeout)
		}
	case Killed:
		return false
	}
	return ok
}
```

- RequestVote函数

> 这个函数主要就是RPC发送投票信息的载体，对这个载体进行初始化和构建
> 

> **同理这个函数也要遵循合适的时机去重置刷新结点状态，定时刷新的地方应该是别的节点与当前节点在数据上不冲突时就要刷新，因为如果不是数据冲突那么定时相当于防止自身去选举的一个心跳，如果是因为数据冲突，那么这个节点不用刷新定时是为了当前整个raft能尽快有个正确的leader**
> 

```go
// 示例 RequestVote RPC 处理程序。
func (rf *Raft) RequestVote(args *RequestVoteArgs, reply *RequestVoteReply) {
	// Your code here (2A, 2B).
	rf.mu.Lock()
	defer rf.mu.Unlock()

	//如果当前结点的状态已经停止了，那么就设置回应的消息,并且不会投票给这个节点
	if rf.killed() {
		reply.VoteState = Killed
		reply.Term = -1
		reply.VoteGranted = false
		return
	}

	//如果别的节点的任期号比自己的小，那么就说明出现网路分区，那么就将自己的任期号回复给他，并且不投票给他
	if args.Term < rf.currentTerm {
		reply.VoteState = Expire
		reply.Term = rf.currentTerm
		reply.VoteGranted = false
		return
	}

	//如果别的节点的任期号比自己的大，那么就需要重置自己的状态
	if args.Term > rf.currentTerm {
		rf.currentTerm = args.Term
		rf.status = Follower
		rf.votedFor = -1
	}

	//如果当前没有投票
	if rf.votedFor == -1 {
		currentLogIndex := len(rf.logs) - 1
		currentLogTerm := 0
		//如果当前日志是有记录的，那么就要进行同步
		if currentLogIndex >= 0 {
			currentLogTerm = rf.logs[currentLogIndex].Term
		}

		//根据选举约束，我们要限制这两个条件，一是槽位的索引号要大于等于自己的索引号，二是槽位的任期号要大于等于自己的任期号
		//如果不满足这两个条件，那么就不投票给他
		if args.LastLogIndex < currentLogIndex || args.LastLogTerm < currentLogTerm {
			reply.VoteState = Expire
			reply.VoteGranted = false
			reply.Term = rf.currentTerm
			return
		}
		//以上都满足，那么就投票给发请求过来的节点
		rf.votedFor = args.CandidateId

		reply.VoteState = Normal
		reply.VoteGranted = true
		reply.Term = rf.currentTerm
	} else {
		//如果当前已经投票了，那么此时存在两种情况，一是投给了自己，二是投给了别人
		//更新自己的状态
		reply.VoteState = Voted
		reply.VoteGranted = false

		//如果投给自己直接返回
		if rf.votedFor != args.CandidateId {
			return
		} else {
			//投给别人，那么就要更新自己的状态
			rf.status = Follower
		}
		//重置选举超时时间
		rf.heartbeatTimer.Reset(rf.electionTimer)
	}
	return
}
```

- kill函数

```go
// 问题是长时间运行的 goroutines 会占用内存并且可能会消耗 CPU 时间，可能会导致后面的测试失败并产生令人困惑的调试输出。
// 任何具有长时间运行循环的 goroutine 都应该调用 killed() 来检查它是否应该停止。
func (rf *Raft) Kill() {
	atomic.StoreInt32(&rf.dead, 1)
	// Your code here, if desired.
	rf.mu.Lock()
	rf.heartbeatTimer.Stop()
	rf.mu.Unlock()
}
```

### 3.日志追加/心跳RPC建立

- 概述

> 准确的来说这里两个机制的编写是被提前的，放在B中完成也行。在A中会报错一个warning，而对于消除这个warning其实严格意义上来讲只能算是重新发送一个ticker与一个节点建立心跳，**使得leader在不发生故障的情况下能够连任**
> 
- 代码

```go
// 向其他节点发送心跳建立以及日志追加请求
func (rf *Raft) sendAppendEntries(server int, args *AppendEntriesArgs, reply *AppendEntriesReply, appendNums *int) bool {
	if rf.killed() {
		return false
	}
	//如果append失败应该不断的重试 ,直到这个log成功的被提交
	ok := rf.peers[server].Call("Raft.AppendEntries", args, reply)
	for !ok {
		if rf.killed() {
			return false
		}
		ok = rf.peers[server].Call("Raft.AppendEntries", args, reply)
	}
	//必须在加在这里否则加载前面retry时进入时，RPC也需要一个锁，但是又获取不到，因为锁已经被加上了
	rf.mu.Lock()
	defer rf.mu.Unlock()
	switch reply.AppState {
	//目标节点崩溃
	case AppKilled:
		{
			return false
		}
	// 目标节点正常返回,2A的test目的是让Leader能不能连续任期，所以2A只需要对节点初始化然后返回就好，后续有要求进行修改即可
	case AppNormal:
		{
			return true
		}
	// 目标节点返回这个状态就代表当前leader已经过时
	case AppOutOfDate:
		//所以就要将当前结点变为follower，并把相应的状态进行更新
		rf.status = Follower
		rf.votedFor = -1
		rf.heartbeatTimer.Reset(rf.electionTimer)
		rf.currentTerm = reply.Term
	}
	return ok
}

// 具体的心跳和日志内容，即发送RPC的主题内容
func (rf *Raft) AppendEntries(args *AppendEntriesArgs, reply *AppendEntriesReply) {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	//如果当前结点挂壁了，返回状态信息
	if rf.killed() {
		reply.AppState = AppKilled
		reply.Term = -1
		reply.Success = false
		return
	}
	//如果当前结点的任期号大于接收到的任期号，说明出现了分区，返回当前节点的任期号
	if args.Term < rf.currentTerm {
		reply.AppState = AppOutOfDate
		reply.Term = rf.currentTerm
		reply.Success = false
		return
	}
	//如果一切正常，就将当前结点的状态变为follower，并更新相应的状态
	rf.currentTerm = args.Term
	rf.votedFor = args.LeaderId
	rf.status = Follower
	rf.heartbeatTimer.Reset(rf.electionTimer)

	//对返回的reply进行赋值，即返回自己的信息作为应答
	reply.AppState = AppNormal
	reply.Term = rf.currentTerm
	reply.Success = true
	return
}
```

### 4.所有test的要点

> • TestInitialElection2A：这个就是检查你的初始化有没有错误，能不能成功选举出来一个leader，并且让这个leader和任期号再无意外的情况下是否能一直保持
• TestReElection2A：这个就会让选取后的leader被动下线，以此来检查你的leader选举是否正常进行，并且下线的节点重新连接后相应的状态是否会更新成从节点，以及不过半和过半时是否能自适应的选不出和选出leader
• TestManyElections2A：这个测试大量节点时，有过半节点都挂壁，那么剩余节点会不会进行选举，然后还会测试挂壁的节点连回来的自动适应
> 

## Raft-B（日志心跳RPC）

- 主要内容

> 这个lab2b主要的内容就是在2a的基础上完成日志增量，虽然这个逻辑大体是很好实现的，但是日志增量对应了很多下标是特别容易犯错，且你要保证兼容前几个通过的pass，最终得到allpass。且在某些方面，你要重新回去修改lab2a的代码，重新去查错，这个整个兼容过程是非常痛苦的。
> 
- start函数

> 2b主要的任务就是进行日志增量，那么我们对于start函数的修改就是遵循要求的前提下去初始化日志。**2b的test其实可以可以发现，其实是调用raft中的start函数，对leader节点写入log，然后检测log是否成功其实就是通过applyChan协程一直检测**
> 

```go
// 使用 Raft 的服务（例如 kv 服务器）想要就下一个要附加到 Raft 日志的命令达成协议。
// 如果此服务器不是领导者，则返回 false。否则启动协议并立即返回。
// 无法保证此命令将永远提交到 Raft 日志，因为领导者可能会失败或失去选举。
// 即使 Raft 实例已经被杀死，这个函数也应该优雅地返回。
//
// 第一个返回值是命令在提交时将出现的索引。第二个返回值是当前术语。如果此服务器认为它是领导者，则第三个返回值为真。
func (rf *Raft) Start(command interface{}) (int, int, bool) {
	index := -1
	term := -1
	isLeader := true

	// Your code here (2B).

	if rf.killed() {
		return index, term, false
	}
	rf.mu.Lock()
	defer rf.mu.Unlock()
	if rf.status != Leader {
		return index, term, false
	}
	isLeader = true

	//初始化日志，并对日志进行追加
	appendLog := LogEntry{Term: rf.currentTerm, Command: command}
	rf.logs = append(rf.logs, appendLog)
	index = len(rf.logs)
	term = rf.currentTerm
	return index, term, isLeader
}
```

### 1.初始化并发送ticker

### 1.1 初始化

- make函数

> 初始化的过程与2a没有什么差别，主要就是对于存放日志数组进行初始化
> 

### 1.2 发送ticker

- ticker函数

> 这里主要增加了如果自身是leader的情况下，给别的节点发送自己的日志信息进行同步的过程
> 

```go
case Leader:
				//进行心跳同步，日志同步
				appendNums := 1                           //统计同步成功的服务器数量
				rf.heartbeatTimer.Reset(HeartBeatTimeout) // 重置心跳计时器
				//构造msg
				for i := 0; i < len(rf.peers); i++ {
					if i == rf.me {
						continue
					}
					appendEntriesArgs := AppendEntriesArgs{
						Term:         rf.currentTerm,
						LeaderId:     rf.me,
						PrevLogIndex: 0,
						PrevLogTerm:  0,
						Entries:      nil,
						LeaderCommit: rf.commitIndex,
					}
					appendEntriesReply := AppendEntriesReply{}
					//将当前leader的最新日志条目附带给当前遍历的节点，nextIndex表示的是需要给这个节点发送的下一条日志的索引，
					//减1的意思就是当前leader全部的且没有最新的日志情况下
					// 如果nextIndex[i]长度不等于rf.logs,代表与leader的log entries不一致，需要附带过去
					appendEntriesArgs.Entries = rf.logs[rf.nextIndex[i]-1:]
					//有日志的情况下，将同步过的索引设置进去
					if rf.nextIndex[i] > 0 {
						appendEntriesArgs.PrevLogIndex = rf.nextIndex[i] - 1
					}
					//已经有同步过的日志时，那么就要将对应任期号设置进去
					if appendEntriesArgs.PrevLogIndex > 0 {
						appendEntriesArgs.PrevLogTerm = rf.logs[appendEntriesArgs.PrevLogIndex-1].Term
					}
					go rf.sendAppendEntries(i, &appendEntriesArgs, &appendEntriesReply, &appendNums)
				}
```

### 2.日志增量RPC

- 概述

> 当有新的日志时，就需要在每次心跳同步中进行最新日志的发送即追加日志，前面我们在设计结构体时，曾设计过节点RPC回应的状态常量，例如：追加正常（AppNormal）、追加超时（AppOutOfDate）等；同时日志增量的请求RPC结构体与回复RPC结构体都有设置
> 
- 回复RPC的修改

> 我们只需要在这个结构体中加入一个新字段就可以了，表明回复的节点在下一次的同步中需要从日志的那个索引开始
> 

```go
type AppendEntriesReply struct {
	Term        int                // 当前任期号，以便于领导者去更新自己过期的任期号
	Success     bool               // 跟随者包含了匹配上 prevLogIndex 和 prevLogTerm 的日志才会进行追加，不匹配返回false
	AppState    AppendEntriesState // 追加日志的状态
	UpNextIndex int                //节点更新请求的nextIndex中的索引值
}
```

### 2.1reply的构造

- AppendEntries函数

> 我们首先换位思考，当别的节点（follower）接收当日志增量请求时，应该如何处理，即何时可以追加，何时不可以追加（发生冲突），下面大致两种情况不能追加。**注意下面所说的旧日志索引就是新的日志索引紧挨的上一个索引**
> 
> - 如果发送过来的PRC参数中，旧的日志索引大于当前日志的最大索引就说明缺失了日志，所以当前节点应该拒绝此次增量请求；**S1与S3的情况**
> - 如果当前节点的日志中旧任期号与发过来的旧日志任期号不一样，那么也同样拒绝本次请求；**S2与S3的情况**
> 
> ![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%205.png)
> 

**同样要注意如果符合追加条件，必须要将同步的log同步到管道中；即要更新自己的提交日志索引（commitedIndex）到追加后的长度，注意此时还未进行申请apply，所以lastApplied就是真正已经同步到管道中的索引，所以追加后还要进行apply**

```go
// AppendEntries 接收建立心跳、同步日志的RPC
func (rf *Raft) AppendEntries(args *AppendEntriesArgs, reply *AppendEntriesReply) {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	//如果当前结点挂壁了，返回状态信息
	if rf.killed() {
		reply.AppState = AppKilled
		reply.Term = -1
		reply.Success = false
		return
	}
	//如果当前结点的任期号大于接收到的任期号，说明出现了分区，返回当前节点的任期号
	if args.Term < rf.currentTerm {
		reply.AppState = AppOutOfDate
		reply.Term = rf.currentTerm
		reply.Success = false
		return
	}
	//对比任期号后就开始处理出现冲突的情况
	// 首先要保证自身len(rf)大于0否则数组越界
	// 1、 如果preLogIndex的大于当前日志的最大的下标说明跟随者缺失日志，拒绝附加日志
	// 2、 如果preLog处的任期和preLogIndex处的任期和preLogTerm不相等，那么说明日志存在conflict,拒绝附加日志

	//记得试一下不减一的情况
	if args.PrevLogIndex > 0 && (len(rf.logs) < args.PrevLogIndex || rf.logs[args.PrevLogIndex-1].Term != args.PrevLogTerm) {
		reply.AppState = Mismatch
		reply.Term = rf.currentTerm
		reply.Success = false
		reply.UpNextIndex = rf.lastAppliedIndex + 1
		return
	}

	// 如果当前节点提交的Index比传过来的还高，说明当前节点的日志已经超前,需返回过去
	if args.PrevLogIndex != -1 && rf.lastAppliedIndex > args.PrevLogIndex {
		reply.AppState = AppCommitted
		reply.Term = rf.currentTerm
		reply.Success = false
		reply.UpNextIndex = rf.lastAppliedIndex + 1
		return
	}

	//如果一切正常，就将当前结点的状态变为follower，并更新相应的状态
	rf.currentTerm = args.Term
	rf.votedFor = args.LeaderId
	rf.status = Follower
	rf.heartbeatTimer.Reset(rf.electionTimer)

	//对返回的reply进行赋值，即返回自己的信息作为应答
	reply.AppState = AppNormal
	reply.Term = rf.currentTerm
	reply.Success = true

	//如果一切正常，那么进行追加日志
	if args.Entries != nil {
		rf.logs = rf.logs[:args.PrevLogIndex]
		rf.logs = append(rf.logs, args.Entries...)
	}

	//进行apply
	for rf.lastAppliedIndex < args.LeaderCommit {
		rf.lastAppliedIndex++
		applyMsg := ApplyMsg{
			CommandValid: true,
			CommandIndex: rf.lastAppliedIndex,
			Command:      rf.logs[rf.lastAppliedIndex-1].Command,
		}
		rf.applyChan <- applyMsg
		rf.commitIndex = rf.lastAppliedIndex
	}
	return
}
```

### 2.2 处理reply

- 概述

> 前面我们换位思考想了从节点的回复构造，那么现在我们把视角转换到leader节点，思考根据从节点的回复我们应该怎么做，在下一次的发送日志请求中怎么修改
> 
- sendAppendEntries函数

```go
// 向其他节点发送心跳建立请求
func (rf *Raft) sendAppendEntries(server int, args *AppendEntriesArgs, reply *AppendEntriesReply, appendNums *int) {
	if rf.killed() {
		return
	}
	//如果append失败应该不断的重试 ,直到这个log成功的被提交
	ok := rf.peers[server].Call("Raft.AppendEntries", args, reply)
	for !ok {
		if rf.killed() {
			return
		}
		ok = rf.peers[server].Call("Raft.AppendEntries", args, reply)
	}
	//必须在加在这里否则加载前面retry时进入时，RPC也需要一个锁，但是又获取不到，因为锁已经被加上了
	rf.mu.Lock()
	defer rf.mu.Unlock()
	switch reply.AppState {
	//目标节点崩溃
	case AppKilled:
		return
	// 目标节点正常返回,2A的test目的是让Leader能不能连续任期，所以2A只需要对节点初始化然后返回就好，后续有要求进行修改即可
	//这里就对应日志增量正常并且apply到通道了
	case AppNormal:
		// 2B需要判断返回的节点是否超过半数commit，才能将自身commit
		if reply.Success && reply.Term == rf.currentTerm && *appendNums <= len(rf.peers)/2 {
			*appendNums++
		}

		// 如果发送给server这个节点的索引大于日志量，说明返回的值已经大过了自身数组
		if rf.nextIndex[server] > len(rf.logs)+1 {
			return
		}
		//如果server这个节点对应的索引小于日志量，那么就更新索引
		rf.nextIndex[server] += len(args.Entries)
		//检查是否有超过半数的节点commit了
		if *appendNums > len(rf.peers)/2 {
			// 保证幂等性，不会提交第二次
			*appendNums = 0

			// 如果日志为空或者日志的最后一条的term不等于当前的term，那么就不进行apply
			if len(rf.logs) == 0 || rf.logs[len(rf.logs)-1].Term != rf.currentTerm {
				return
			}
			// 如果一切顺利leader就开始apply
			for rf.lastAppliedIndex < len(rf.logs) {
				rf.lastAppliedIndex++
				applyMsg := ApplyMsg{
					CommandValid: true,
					Command:      rf.logs[rf.lastAppliedIndex-1].Command,
					CommandIndex: rf.lastAppliedIndex,
				}
				rf.applyChan <- applyMsg
				rf.commitIndex = rf.lastAppliedIndex
			}

		}
		return

	// 目标节点返回这个状态就代表当前leader已经过时
	case AppOutOfDate:
		//所以就要将当前结点变为follower，并把相应的状态进行更新
		rf.status = Follower
		rf.votedFor = -1
		rf.heartbeatTimer.Reset(rf.electionTimer)
		rf.currentTerm = reply.Term

	//日志不匹配
	case Mismatch:
		if args.Term != rf.currentTerm {
			return
		}
		//如果日志不匹配，那么就是记录以下不匹配的server回复过来下次要在那个地方开始更新的节点索引
		rf.nextIndex[server] = reply.UpNextIndex

	case AppCommitted:
		if args.Term != rf.currentTerm {
			return
		}
		rf.nextIndex[server] = reply.UpNextIndex
	}
	return
}
```

### 3.其余修改

- RequestVote函数

> 我们对当前如果没有进行投票时的代码进行了修改，至于为什么这么修改在前篇的选举约束篇章中讲解的很详细
> 

```go
// 示例 RequestVote RPC 处理程序。
func (rf *Raft) RequestVote(args *RequestVoteArgs, reply *RequestVoteReply) {
	// Your code here (2A, 2B).
	rf.mu.Lock()
	defer rf.mu.Unlock()

	//如果当前结点的状态已经停止了，那么就设置回应的消息,并且不会投票给这个节点
	if rf.killed() {
		reply.VoteState = Killed
		reply.Term = -1
		reply.VoteGranted = false
		return
	}

	//如果别的节点的任期号比自己的小，那么就说明出现网路分区，那么就将自己的任期号回复给他，并且不投票给他
	if args.Term < rf.currentTerm {
		reply.VoteState = Expire
		reply.Term = rf.currentTerm
		reply.VoteGranted = false
		return
	}

	//如果别的节点的任期号比自己的大，那么就需要重置自己的状态
	if args.Term > rf.currentTerm {
		rf.currentTerm = args.Term
		rf.status = Follower
		rf.votedFor = -1
	}

	//如果当前没有投票
	if rf.votedFor == -1 {

		lastLogTerm := 0
		//如果当前日志是有记录的，那么就要进行同步
		if len(rf.logs) > 0 {
			lastLogTerm = rf.logs[len(rf.logs)-1].Term
		}

		//根据选举约束，我们要限制这两个条件
		// 1、args.LastLogTerm < lastLogTerm是因为选举时应该首先看term，只要term大的，才代表存活在raft中越久
		// 2、判断日志的最后一个index是否是最新的前提应该是要在这两个节点任期是否是相同的情况下，判断哪个数据更完整
		//如果不满足这两个条件，那么就不投票给他
		if args.LastLogTerm < lastLogTerm ||
			(len(rf.logs) > 0 && args.LastLogTerm == rf.logs[len(rf.logs)-1].Term && args.LastLogIndex < len(rf.logs)) {
			reply.VoteState = Expire
			reply.VoteGranted = false
			reply.Term = rf.currentTerm
			return
		}
		//以上都满足，那么就投票给发请求过来的节点
		rf.votedFor = args.CandidateId

		reply.VoteState = Normal
		reply.VoteGranted = true
		reply.Term = rf.currentTerm

		rf.heartbeatTimer.Reset(rf.electionTimer)
	} else {
		//如果当前已经投票了，那么此时存在两种情况，一是投给了自己，二是投给了别人
		//更新自己的状态
		reply.VoteState = Voted
		reply.VoteGranted = false

		//如果投给自己直接返回
		if rf.votedFor != args.CandidateId {
			return
		} else {
			//投给别人，那么就要更新自己的状态
			rf.status = Follower
		}
		//重置选举超时时间
		rf.heartbeatTimer.Reset(rf.electionTimer)
	}
	return
}
```

### 4.所有test的要点

- TestBasicAgree2B：最基础的追加日志测试。先使用nCommitted()检查有多少的server认为日志已经提交（在执行Start()函数之前，所有的服务器都不应该提交日志），若满足条件则调用cfg.one()，其通过调用rf.Start(cmd)来追加日志。rf.Start(cmd)用于模拟Raft实例从Client接收实例的情况。
- TestRPCBytes2B：基于RPC的字节数检查保证每个cmd都只对每个peer发送一次。
- TestFailAgree2B：断连小部分，不影响整体Raft集群的情况检测追加日志。
- TestFailNoAgree2B：断连过半数节点，保证无日志可以正常追加。然后又重新恢复节点，检测追加日志情况。
- TestConcurrentStarts2B：模拟客户端并发发送多个命令
- TestRejoin2B：Leader 1断连，再让旧leader 1接受日志，再给新Leader 2发送日志，2断连，再重连旧Leader 1，提交日志，再让2重连，再提交日志。
- TestBackup2B：先给Leader 1发送日志，然后断连3个Follower（总共1Ledaer 4Follower），网络分区。提交大量命令给1。然后让leader 1和其Follower下线，之前的3个Follower上线，向它们发送日志。然后在对剩下的仅有3个节点的Raft集群重复上面网络分区的过程。
- TestCount2B：检查无效的RPC个数，不能过多。

## Raft-C（持久化）

- 概述

> 这里主要是对raft中节点的持久化进行编写，如果基于 Raft 的服务器重新启动，它应该恢复服务下线的地方。这需要 Raft 保持持续状态，在重新启动后幸存下来。
> 

> 在这次实验中不会真正持久化到磁盘，而是将状态保存到Persister 对象。 无论谁调用 `Raft.Make` 都会提供一个 `Persister`，该 `Persister` 最初保存 `Raft` 最近的持久状态（如果 任何）。`Raft` 应该从那个 `Persister` 初始化它的状态，并应该使用它来保存它的持久状态。每次状态更改时的状态，使用 `Persister` 的 `ReadRaftState` 和 `Save`方法。
> 
- 需要保存的初始化状态

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab2%EF%BC%88GFS%EF%BC%9ARaftA&B&C&D%EF%BC%89%E2%80%94%E2%80%94%20%E5%90%8E%E7%AF%87/image%206.png)

### 1.持久化

- 概述

> 这个部分的编写主要就是完成持久化的功能，分为两部分：一是编码，而是解码，也就是对应上面讲的两个函数
> 

### 1.1 编码

- persist函数

```go
func (rf *Raft) persist() {
	// Your code here (2C).
	// Example:
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	e.Encode(rf.currentTerm)
	e.Encode(rf.votedFor)
	e.Encode(rf.logs)
	data := w.Bytes()
	rf.persister.SaveRaftState(data)
}
```

### 1.2 解码

- readPersist函数

```go
func (rf *Raft) readPersist(data []byte) {
	if data == nil || len(data) < 1 { // bootstrap without any state?
		return
	}
	// Your code here (2C).
	r := bytes.NewBuffer(data)
	d := labgob.NewDecoder(r)
	var currentTerm int
	var votedFor int
	var logs []LogEntry
	if d.Decode(&currentTerm) != nil ||
		d.Decode(&votedFor) != nil ||
		d.Decode(&logs) != nil {
		log.Fatal("decode error")
	} else {
		rf.currentTerm = currentTerm
		rf.votedFor = votedFor
		rf.logs = logs
	}
}
```

### 2.日志增量回退

### 2.1 持久化增加

- sendAppendEntries函数

> 主要就是改变了日志不匹配或者已提交时的行为
> 

```go
// 向其他节点发送心跳建立请求
func (rf *Raft) sendAppendEntries(server int, args *AppendEntriesArgs, reply *AppendEntriesReply, appendNums *int) {
	if rf.killed() {
		return
	}
	//如果append失败应该不断的重试 ,直到这个log成功的被提交
	ok := rf.peers[server].Call("Raft.AppendEntries", args, reply)
	for !ok {
		if rf.killed() {
			return
		}
		ok = rf.peers[server].Call("Raft.AppendEntries", args, reply)
	}
	//必须在加在这里否则加载前面retry时进入时，RPC也需要一个锁，但是又获取不到，因为锁已经被加上了
	rf.mu.Lock()
	defer rf.mu.Unlock()
	switch reply.AppState {
	//目标节点崩溃
	case AppKilled:
		return
	// 目标节点正常返回,2A的test目的是让Leader能不能连续任期，所以2A只需要对节点初始化然后返回就好，后续有要求进行修改即可
	//这里就对应日志增量正常并且apply到通道了
	case AppNormal:
		// 2B需要判断返回的节点是否超过半数commit，才能将自身commit
		if reply.Success && reply.Term == rf.currentTerm && *appendNums <= len(rf.peers)/2 {
			*appendNums++
		}

		// 如果发送给server这个节点的索引大于日志量，说明返回的值已经大过了自身数组
		if rf.nextIndex[server] > len(rf.logs)+1 {
			return
		}
		//如果server这个节点对应的索引小于日志量，那么就更新索引
		rf.nextIndex[server] += len(args.Entries)
		//检查是否有超过半数的节点commit了
		if *appendNums > len(rf.peers)/2 {
			// 保证幂等性，不会提交第二次
			*appendNums = 0

			// 如果日志为空或者日志的最后一条的term不等于当前的term，那么就不进行apply
			if len(rf.logs) == 0 || rf.logs[len(rf.logs)-1].Term != rf.currentTerm {
				return
			}
			// 如果一切顺利leader就开始apply
			for rf.lastAppliedIndex < len(rf.logs) {
				rf.lastAppliedIndex++
				applyMsg := ApplyMsg{
					CommandValid: true,
					Command:      rf.logs[rf.lastAppliedIndex-1].Command,
					CommandIndex: rf.lastAppliedIndex,
				}
				rf.applyChan <- applyMsg
				rf.commitIndex = rf.lastAppliedIndex
			}

		}
		return
	//前面说过当状态发生改变时就要进行持久化
	// 目标节点返回这个状态就代表当前leader已经过时
	case AppOutOfDate:
		//所以就要将当前结点变为follower，并把相应的状态进行更新
		rf.status = Follower
		rf.votedFor = -1
		rf.heartbeatTimer.Reset(rf.electionTimer)
		rf.currentTerm = reply.Term
		rf.persist()
	//当日志不匹配或者日志已经提交了的时候
	case Mismatch, AppCommitted:
		//并且回复的任期号大于当前leader的，那么就要变成follower
		if reply.Term > rf.currentTerm {
			rf.status = Follower
			rf.votedFor = -1
			rf.heartbeatTimer.Reset(rf.electionTimer)
			rf.currentTerm = reply.Term
			rf.persist()
		}
		//记录以下不匹配的server回复过来下次要在那个地方开始更新的节点索引
		rf.nextIndex[server] = reply.UpNextIndex
	}
	return
}
```

- 其他持久化增加函数

> `ticker函数、sendRequestVote函数、requestVote函数、appendEntries函数、start函数`；**这些函数增加持久化的位置就不放出来了主要就是节点更新状态的时候就应该持久化**
> 

## Raft-D（日志快照）

- 概述

> D的内容主要就是完成日志快照的功能，在前篇有着非常详细的讲解，我们直接略过原理直接进入实验；**首先要明确快照是干嘛的，大致来说就是为了恢复leader已经提交并删除的部分给那么挂壁但又重新连接的节点信息**
> 

> 根据上面的流程图，需要明确我们编写的函数以及作用。从图中可以看出在单个节点中的Service层会对Raft节点调用`Snapshot`、与`CondInstallSnap`两个函数，这也是实验室中需要我们去编写的。对于自身的Raft节点来说需要对快照信息进行持久化的保存，也就是`SaveStateAndSnapshot`函数，这一部分的持久化信息会通过`Service`用`ReadSnapshot`进行调用。**而对于节点之间的快照联系的话则是通过`InstallSnapshot`进行节点之间的沟通。这就取决于谁是leader了。**
> 

### 1.Snapshot与CondInstallSnap函数

### 1.1 Snapshot函数

- 概述

> 
> 
> - **本地快照（服务层 `Snapshot`）**：只要该节点已经把 **≤ snapshotIndex 的已提交条目都应用进状态机**，就可以在本地持久化快照并 **删掉这些已包含在快照里的日志前缀**。这是**单机上的日志压缩**，不涉及“再提交一次”，所以和过半复制无关。Follower 和 Leader 都可以在自己的进程里做这件事（前提都是：**已应用到至少 snapshotIndex**）。
> - **数据仍从 Leader 流向 Follower**：指的是 **新的日志条目** 仍靠 `AppendEntries` 复制；Follower **不会**因为“自己做了快照”就从别的 Follower 拉新数据。
> - **InstallSnapshot RPC**：当 Leader 已经压缩掉旧日志、而某 Follower 还需要那些已被删掉的条目时，Leader 用 **快照 + `lastIncludedIndex/Term`** 把 Follower **直接对齐**到快照点。这是另一条路径，和“Follower 自己本地 `Snapshot` 减压”是不同场景。
- 代码

```go
package raft

import "sync"

// 仅示意：真实 Lab 还要持久化、互斥、与 applyCh 协调等。

type Raft struct {
	mu sync.Mutex

	// 日志逻辑下标：log[0] 对应任期 term0 的那条（Lab 里常做 1-based 或 dummy 条目）
	log         []LogEntry
	commitIndex int
	lastApplied int

	// 快照覆盖的最后一条日志的下标与任期（快照里“包含”这条）
	lastIncludedIndex int
	lastIncludedTerm  int

	// 持久化接口（示意）
	persist func([]byte)
}

type LogEntry struct {
	Term    int
	Command interface{}
}

// 服务层在把 lastApplied 之前的命令都打进状态机后调用：
// snapshotIndex 一般为“最后一条已应用”的绝对下标（与 Lab 定义一致）
func (rf *Raft) Snapshot(snapshotIndex int, snapshot []byte) {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	// 不能压缩还没应用到、或比当前快照更旧的点
	if snapshotIndex <= rf.lastIncludedIndex {
		return
	}
	if snapshotIndex > rf.lastApplied {
		return
	}

	newLastTerm := rf.termAt(snapshotIndex)

	// 丢弃 [0 .. snapshotIndex - lastIncludedIndex - 1] 的 log 前缀（实现随 Lab 下标约定变）
	// 这里假设 log[0] 的绝对下标 = lastIncludedIndex + 1
	phys := rf.physicalIndex(snapshotIndex)
	if phys < 0 || phys >= len(rf.log) {
		return
	}

	// 保留快照点之后的日志
	keep := append([]LogEntry(nil), rf.log[phys+1:]...)
	rf.log = keep
	rf.lastIncludedIndex = snapshotIndex
	rf.lastIncludedTerm = newLastTerm

	// 把 snapshot + 元数据一起 persist（Lab 通常用 Persist + SaveSnapshot）
	rf.saveSnapshotAndState(snapshot)
}

func (rf *Raft) physicalIndex(abs int) int {
	return abs - rf.lastIncludedIndex - 1
}

func (rf *Raft) termAt(abs int) int {
	if abs == rf.lastIncludedIndex {
		return rf.lastIncludedTerm
	}
	return rf.log[rf.physicalIndex(abs)].Term
}

func (rf *Raft) saveSnapshotAndState(snapshot []byte) {
	// 示意：把 snapshot、lastIncludedIndex/Term、剩余 log、currentTerm、votedFor 等编码后写入磁盘
	_ = snapshot
}
```

**Follower 上何时可以调 `Snapshot`？**

和 Leader 一样：**`lastApplied >= snapshotIndex` 且该 index 上的条目是已提交且已应用过的**。这样你删掉的只是“已经固化进快照的状态”，不会影响安全性。

**和 `InstallSnapshot` 的关系（口头对应代码）**：Leader 侧若先压缩，Follower 若还缺被删掉的条目，会走类似下面的处理（结构示意）：

### 1.2 CondInstallSnapshot函数

- 概述

> 对于这个函数结合introduction中的解释其实也很好理解，对于这个函数的背景其实就是你发送了快照，那么你发送的快照就要上传到applyCh，而同时你的appendEntries也需要进行上传日志，可能会导致冲突。但是实际上apply的时候会进行加锁了的，也就是不会出现这种情况，所以这个函数就放着不动就好
> 

### 2.InstallSnapshot RPC

- 概述

> 这个函数也在前篇有详细的介绍，简单来说就是当挂壁节点恢复过来的时候怎么去同步日志和快照，或者是根据快照恢复日志等。**因为这个挂壁节点可能需要的日志，leader早就丢弃了，这时就需要发送给这个节点快照**
> 
- RPC结构体

> 这个在论文中也有提到，照葫芦画瓢就可以了
> 

```go
type InstallSnapshotArgs struct {
	Term             int    // 发送请求方的任期
	LeaderId         int    // 请求方的LeaderId
	LastIncludeIndex int    // 快照最后applied的日志下标
	LastIncludeTerm  int    // 快照最后applied时的当前任期
	Data             []byte // 快照区块的原始字节流数据
	//Done bool
}

type InstallSnapshotReply struct {
	Term int
}
```

- 结束

> 后面的代码就不展示出来了，因为进行了代码重构，整个raft都基本变了
>
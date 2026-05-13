# MIT6.824分布式 | Lab4AB（Sharded Key/Value Service：分片KV服务）

type: Post
status: Published
date: 2023/04/19
summary: Sharded Key/Value Service：分片KV服务
tags: 实践
category: 分布式

# LabA

## 1.概述

> 对于本次实验来说，Lab4的目标就是从原来的KV集中存储在某个地方，**现在改为分片存储，通过Raft将大量数据进行分片，相似分片属于一个分片组，有很多个分片组；还有控制这么多个分片组的分片控制器**，然后分片控制器通过`query/leave/join/move`等操作。去操作不同的分片已达到负载均衡。同时还少了关于快照的实现
> 

> 相当于新添加了一个控制器的角色，去管理这么多的分片
> 
- 结构图/流程图

> 就跟Lab3的一样，除了将操作符换成上面四个
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab4AB%EF%BC%88Sharded%20Key%20Value%20Service%EF%BC%9A%E5%88%86%E7%89%87KV%E6%9C%8D/image.png)

## 2.实验分析

- `config`切片

> 这个结构体位于分片管理器包下，用于管理分片组，里面存放着不同版本的配置信息，最新的下标对应最新的配置
> 

```go
// 配置 -- 将分片分配给组。请不要更改此设置。
type Config struct {
	Num    int              // 配置版本号
	Shards [NShards]int     // shard -> gid 该分组的10个分片
	Groups map[int][]string // gid -> servers[] 每个组对应的服务器映射名称列表
}
```

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab4AB%EF%BC%88Sharded%20Key%20Value%20Service%EF%BC%9A%E5%88%86%E7%89%87KV%E6%9C%8D/image%201.png)

## 3.server编写

### 3.1 操作符RPC已经对应Handler

- 概述

> 我们解释一下上面的四个操作：可以看出实际上就是对分片的CRUD
> 
> 1. Join ：加入一个新的组 ，创建一个最新的配置，加入新的组后需要重新进行负载均衡。
> 2. Leave: 将给定的一个组进行撤离，并进行负载均衡。
> 3. Move: 为指定的分片，分配指定的组。
> 4. Query: 查询特定的配置版本，如果给定的版本号不存在切片下标中，则直接返回最新配置版本。

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab4AB%EF%BC%88Sharded%20Key%20Value%20Service%EF%BC%9A%E5%88%86%E7%89%87KV%E6%9C%8D/image%202.png)

==HandlerLoop==

> 进行分流的Handler
> 

```go
// 这个方法主要就是中转数据，在raft对数据进行commit后再apply通道获取数据并对数据进行类似缓存操作
func (sc *ShardCtrler) handlerLoop() {
	for {
		select {
		case msg := <-sc.applyCh: //获取到apply以后的消息
			if msg.CommandValid { //CommandValid为true就代表有新提交的日志
				index := msg.CommandIndex
				op := msg.Command.(Op) //将记录在日志的指令操作赋值给操作符结构体
				//检查这个客户端是否重复请求，不重复再继续
				if !sc.isDuplicate(op.ClientId, op.SeqId) {
					sc.mu.Lock()
					switch op.OpType {
					case JoinType:
						sc.seqMap[op.ClientId] = op.SeqId //更新客户端的请求序列号
						sc.configs = append(sc.configs, *sc.JoinHandler(op.JoinServers))
					case LeaveType:
						sc.seqMap[op.ClientId] = op.SeqId
						sc.configs = append(sc.configs, *sc.LeaveHandler(op.LeaveGIDs))
					case MoveType:
						sc.seqMap[op.ClientId] = op.SeqId
						sc.configs = append(sc.configs, *sc.MoveHandler(op.MoveShard, op.MoveGID))
					}
					sc.seqMap[op.ClientId] = op.SeqId
					sc.mu.Unlock()
				}
				// 将返回的ch返回waitCh
				sc.getWaitCh(index) <- op
			}
		}
	}
}
```

==Join&JoinHandler==

> 我们先来完成这个操作
> 
> - Join这个RPC就是应用层的Join请求，我们需要发送给raft层
> - JoinHandler：这个就是处理从raft层返回后的Join请求，完成实际的业务需求

```go
func (sc *ShardCtrler) Join(args *JoinArgs, reply *JoinReply) {
	// Your code here.
	_, isLeader := sc.rf.GetState()
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}

	//封装Op，传递给Raft服务层
	op := Op{JoinServers: args.Servers, ClientId: args.ClientId, SeqId: args.SeqId, OpType: JoinType}
	lastIndex, _, _ := sc.rf.Start(op)
	//获取日志结束位置lastIndex的缓冲chan
	ch := sc.getWaitCh(lastIndex)
	defer func() {
		sc.mu.Lock()
		delete(sc.waitChMap, lastIndex) //从map中删除旧的index
		sc.mu.Unlock()
	}()
	timer := time.NewTicker(JoinOverTime * time.Millisecond)
	defer timer.Stop()

	select {
	case replyOp := <-ch:
		if replyOp.SeqId == args.SeqId && replyOp.ClientId == args.ClientId {
			reply.Err = OK
		} else {
			reply.Err = ErrWrongLeader
		}
	}
}

// 对于接收到raft处理好（持久化请求、日志相关）的join请求再次进行处理（实际业务的处理）
// 分片控制程序应通过创建包含新副本组的新配置来做出反应。
// 新配置应尽可能在整组之间平均划分分片，并应尽可能少地移动分片以实现该目标。
// 如果 GID 不是当前配置的一部分，则分片器应允许重用 GID（即应允许 GID 加入，然后离开，然后再次加入）。
// servers中就是每个group的id对应它下面的所有分片
func (sc *ShardCtrler) JoinHandler(servers map[int][]string) *Config {
	//取出最后一个配置
	lastConfig := sc.configs[len(sc.configs)-1]
	newGroups := make(map[int][]string)

	//遍历这个这个配置下的所有分片组，并放到我们的容器中
	for gid, group := range lastConfig.Groups {
		newGroups[gid] = group
	}
	//然后将新的分片组放到容器中
	for gid, group := range servers {
		newGroups[gid] = group
	}
	// GroupMap: groupId -> shards	初始化放分片数量的容器
	groupMap := make(map[int]int)
	for gid := range newGroups {
		groupMap[gid] = 0
	}

	//记录每个分片组的分片数量
	for _, gid := range lastConfig.Shards {
		if gid != 0 {
			groupMap[gid]++
		}
	}
	//分片的负载均衡
	//如果没有分片那就不需要负载均衡
	if len(groupMap) == 0 {
		return &Config{
			Num:    len(sc.configs),
			Shards: [10]int{},
			Groups: newGroups,
		}
	}
	//有新的那就要负载均衡
	return &Config{
		Num:    len(sc.configs),
		Shards: sc.loadBalance(groupMap, lastConfig.Shards),
		Groups: newGroups,
	}
}
```

==Leave&LeaveHandler==

> 这个操作就是删除某个分片
> 

```go
func (sc *ShardCtrler) Leave(args *LeaveArgs, reply *LeaveReply) {
	// Your code here.
	_, isLeader := sc.rf.GetState()
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}

	//封装Op，传递给Raft服务层
	op := Op{LeaveGIDs: args.GIDs, ClientId: args.ClientId, SeqId: args.SeqId, OpType: LeaveType}
	lastIndex, _, _ := sc.rf.Start(op)
	//获取日志结束位置lastIndex的缓冲chan
	ch := sc.getWaitCh(lastIndex)
	defer func() {
		sc.mu.Lock()
		delete(sc.waitChMap, lastIndex) //从map中删除旧的index
		sc.mu.Unlock()
	}()
	timer := time.NewTicker(JoinOverTime * time.Millisecond)
	defer timer.Stop()

	select {
	case replyOp := <-ch:
		if replyOp.SeqId == args.SeqId && replyOp.ClientId == args.ClientId {
			reply.Err = OK
		} else {
			reply.Err = ErrWrongLeader
		}
	}
}

// 分片控制程序应创建一个不包含这些组的新配置，并将这些组的分片分配给其余组。
// 新配置应尽可能平均地在组之间划分分片，并应移动尽可能少的分片以实现该目标。
func (sc *ShardCtrler) LeaveHandler(GIDs []int) *Config {
	// 用set感觉更合适点但是go并没有内置的set..
	leaveMap := make(map[int]bool)
	for _, gid := range GIDs {
		leaveMap[gid] = true
	}

	//取出最后一个配置
	lastConfig := sc.configs[len(sc.configs)-1]
	newGroups := make(map[int][]string)

	//遍历这个这个配置下的所有分片组，并放到我们的容器中
	for gid, group := range lastConfig.Groups {
		newGroups[gid] = group
	}
	// 删除对应的gid的值
	for _, gid := range GIDs {
		delete(newGroups, gid)
	}
	// GroupMap: groupId -> shards	初始化放分片数量的容器
	groupMap := make(map[int]int)
	curShards := lastConfig.Shards
	for gid := range newGroups {
		//如果这个分片组不在要删除的分片组中，那就初始化它的分片数量为0
		if !leaveMap[gid] {
			groupMap[gid] = 0
		}
	}

	//记录每个分片组的分片数量
	for shard, gid := range lastConfig.Shards {
		if gid != 0 {
			// 如果这个组在leaveMap中，则置为0即为删除
			if leaveMap[gid] {
				curShards[shard] = 0
			} else {
				groupMap[gid]++
			}
		}
	}
	//分片的负载均衡
	//如果没有分片那就不需要负载均衡
	if len(groupMap) == 0 {
		return &Config{
			Num:    len(sc.configs),
			Shards: [10]int{},
			Groups: newGroups,
		}
	}
	//有新的那就要负载均衡
	return &Config{
		Num:    len(sc.configs),
		Shards: sc.loadBalance(groupMap, curShards),
		Groups: newGroups,
	}
}
```

==Move&MoveHandler==

> 这个操作就是移动某个分片
> 

```go
func (sc *ShardCtrler) Move(args *MoveArgs, reply *MoveReply) {
	// Your code here.
	_, isLeader := sc.rf.GetState()
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}

	//封装Op，传递给Raft服务层
	op := Op{MoveGID: args.GID, MoveShard: args.Shard, ClientId: args.ClientId, SeqId: args.SeqId, OpType: MoveType}
	lastIndex, _, _ := sc.rf.Start(op)
	//获取日志结束位置lastIndex的缓冲chan
	ch := sc.getWaitCh(lastIndex)
	defer func() {
		sc.mu.Lock()
		delete(sc.waitChMap, lastIndex) //从map中删除旧的index
		sc.mu.Unlock()
	}()
	timer := time.NewTicker(JoinOverTime * time.Millisecond)
	defer timer.Stop()

	select {
	case replyOp := <-ch:
		if replyOp.SeqId == args.SeqId && replyOp.ClientId == args.ClientId {
			reply.Err = OK
		} else {
			reply.Err = ErrWrongLeader
		}
	}
}

// 分片控制程序应创建一个新配置，其中分片分配给组。Move 的目的是让我们测试您的软件。
// 移动后的加入或离开可能会撤消移动，因为加入和离开会重新平衡。
// 就是移动分片位置
func (sc *ShardCtrler) MoveHandler(shard int, gid int) *Config {
	//取出最后一个配置
	lastConfig := sc.configs[len(sc.configs)-1]
	//创建一个新的配置
	newConfig := Config{
		Num:    len(sc.configs),
		Shards: [10]int{},
		Groups: map[int][]string{},
	}
	//将分片以及所在的分片组id放到新的配置中的分片中
	for oldShard, oldGID := range lastConfig.Shards {
		newConfig.Shards[oldShard] = oldGID
	}
	//移动完成
	newConfig.Shards[shard] = gid
	//同上
	for oldGID, oldGroup := range lastConfig.Groups {
		newConfig.Groups[oldGID] = oldGroup
	}
	return &newConfig
}
```

==Query==

> 这个操作直接返回都不需要handler进行处理，直接在这个RPC函数内处理
> 

```go
// 分片器使用具有该编号的配置进行回复。
// 如果该数字为 -1 或大于已知的最大配置编号，则分片控制程序应回复最新配置。
// Query(-1) 的结果应反映分片控制程序在收到 Query(-1) RPC 之前完成处理的每个联接、离开或移动 RPC。
func (sc *ShardCtrler) Query(args *QueryArgs, reply *QueryReply) {
	// Your code here.
	_, isLeader := sc.rf.GetState()
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}

	//封装Op，传递给Raft服务层
	op := Op{QueryNum: args.Num, ClientId: args.ClientId, SeqId: args.SeqId, OpType: QueryType}
	lastIndex, _, _ := sc.rf.Start(op)
	//获取日志结束位置lastIndex的缓冲chan
	ch := sc.getWaitCh(lastIndex)
	defer func() {
		sc.mu.Lock()
		delete(sc.waitChMap, lastIndex) //从map中删除旧的index
		sc.mu.Unlock()
	}()
	timer := time.NewTicker(OverTime * time.Millisecond)
	defer timer.Stop()

	select {
	case replyOp := <-ch:
		if replyOp.SeqId == op.SeqId && replyOp.ClientId == op.ClientId {
			sc.mu.Lock()
			reply.Err = OK
			sc.seqMap[op.ClientId] = op.SeqId
			//如果查询的结果根本不存在，那么就返回最新的配置
			if op.QueryNum == -1 || op.QueryNum >= len(sc.configs) {
				reply.Config = sc.configs[len(sc.configs)-1]
			} else { //如果查询的结果存在，那么就返回查询的结果
				reply.Config = sc.configs[op.QueryNum]
			}
			sc.mu.Unlock()
		} else {
			reply.Err = ErrWrongLeader
		}
	case <-timer.C:
		reply.Err = ErrWrongLeader
	}
}
```

### 3.2 负载均衡

- 概述

> 很明显，如果不负载均衡就会这样，如果在极端情况下可能会一个group下有6个分片导致这个组的压力会特别大。如果使用了负载均衡算法就可以让分片均匀分布
> 

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab4AB%EF%BC%88Sharded%20Key%20Value%20Service%EF%BC%9A%E5%88%86%E7%89%87KV%E6%9C%8D/image%203.png)

- 负载均衡流程

> 首先对根据负载的情况进行排序，**要记住的是如果有负载相同的情况下，需要对gid也进行排序，生成唯一序列，要不然会有一致性问题（TestMulti）**，因为排序的目的主要有以下原因：
> 
> - 可以通过排序就进行更少的交换，当然要确保这个过程中不会有Move等操作影响负载。
> - 理想负载的情况并不可能均分，如10个分片分给4个组并不能是`{2.5, 2.5, 2.5, 2.5}`。而应该是`{3, 3, 2, 2}`。对于这种情况就可以根据排序后的序列就可以通过预期的个数，确定哪几个组需要多负载一个分片。
> - 需要对排序后的唯一序列对应到负载分片的map
- 代码

```go
// 负载均衡
// GroupMap : gid -> servers[]
// lastShards : shard -> gid
func (sc *ShardCtrler) loadBalance(groupMap map[int]int, lastShards [NShards]int) [NShards]int {
	length := len(groupMap) //得到有几个组
	avg := NShards / length //平均给每个组分配的分片数量
	//如果不能整除，那就多分配一个
	//取余，得到多出的一个分片，比如 10 % 3 = 1，多出一个分片
	remainder := NShards % length
	sortGIDs := sortGroupShard(groupMap) //排序
	//开始遍历谁需要减负，即谁的分片数量大于平均值
	for i := 0; i < length; i++ {
		target := avg //每个组必须分配的数量
		// 判断这个分组是否需要更多分配，因为在有余数的情况下不可能完全均分，
		// 所以在当前组（前面的）的应该为avg+1，即多分配一个
		if !moreAllocations(length, remainder, i) {
			target = avg + 1
		}
		//在按照组序号排序以后，如果超出负载，进行重新分片，即分给别人
		if groupMap[sortGIDs[i]] > target {
			overLoadGID := sortGIDs[i]
			//得到需要重新分配的分片数量
			changeNum := groupMap[overLoadGID] - target
			//持续的遍历，看那些分组超出负载
			for shard, gid := range lastShards {
				if changeNum <= 0 {
					break
				}
				if overLoadGID == gid { //遍历到超出负载的分片组
					//然后将这个要分配给后面的分片进行标记
					lastShards[shard] = InvalidGid
					changeNum--
				}
			}
			//更新分片组的分片数量
			groupMap[overLoadGID] = target
		}
	}

	//现在看谁需要增加，然后将多出来的分给后面的
	for i := 0; i < length; i++ {
		target := avg
		if !moreAllocations(length, remainder, i) { //同理
			target = avg + 1
		}
		//如果分片数量小于平均值，那就说明可以分配给这个分组
		if groupMap[sortGIDs[i]] < target {
			freeGID := sortGIDs[i]
			changeNum := target - groupMap[freeGID]
			//开始遍历
			for shard, gid := range lastShards {
				if changeNum <= 0 {
					break
				}
				if InvalidGid == gid { //是我们上面标记的分片就说明要分配
					//将这个分片标记给这个分片组
					lastShards[shard] = freeGID
					changeNum--
				}
			}
			groupMap[freeGID] = target	//分配
		}
	}
	return lastShards
}

// 排序 组序号
// GroupMap : groupId -> shard nums
func sortGroupShard(groupMap map[int]int) []int {
	length := len(groupMap)

	gidSlice := make([]int, 0, length)
	//将gid放到切片中
	for gid, _ := range groupMap {
		gidSlice = append(gidSlice, gid)
	}

	//根据每个组的分片数量进行排序，让多的在前面
	for i := 0; i < length-1; i++ {
		for j := length - 1; j > i; j-- {
			//根据gid得到分片数量，谁大谁在前面
			//例如原始状态： 1->2, 2->3, 3->1	(gids -> shard nums)
			//排序后： 	  2->3, 3->1, 1->2
			if groupMap[gidSlice[j]] < groupMap[gidSlice[j-1]] {
				gidSlice[j], gidSlice[j-1] = gidSlice[j-1], gidSlice[j]
			}
		}
	}
	return gidSlice
}

// 尽量按顺序给前面的组多分配
func moreAllocations(length int, remainder int, i int) bool {
	return i < length-remainder
}
```

- 待优化的点

> 可以将排序分组ID的函数改为更加快速的排序算法
> 

### 3.3 其他

- 概述

> 其他的就跟lab3需要的函数一样了
> 

```go
// 判断是否为重复请求，是的话就不进行缓存了
func (sc *ShardCtrler) isDuplicate(clientId int64, seqId int) bool {
	sc.mu.Lock()
	defer sc.mu.Unlock()
	lastSeqId, isExists := sc.seqMap[clientId]
	if !isExists {
		return false
	}
	//如果当前seqId小于等于上次的seqId，说明是之前的请求，重复了
	return seqId <= lastSeqId
}

func (sc *ShardCtrler) getWaitCh(index int) chan Op {
	sc.mu.Lock()
	defer sc.mu.Unlock()
	ch, isExists := sc.waitChMap[index]
	if !isExists {
		sc.waitChMap[index] = make(chan Op, 1)
		ch = sc.waitChMap[index]
	}
	return ch
}
```

## 4.client编写

- 概述

> 这点没什么好说的，就是模拟客户端去发送RPC请求，与lab3类似
> 

```go
package shardctrler

//
// Shardctrler clerk.
//

import (
	"6.824/labrpc"
	mathrand "math/rand"
)
import "time"
import "crypto/rand"
import "math/big"

type Clerk struct {
	servers []*labrpc.ClientEnd
	// Your data here.
	seqId    int
	leaderId int // 确定哪个服务器是leader，下次直接发送给该服务器
	clientId int64
}

func nrand() int64 {
	max := big.NewInt(int64(1) << 62)
	bigx, _ := rand.Int(rand.Reader, max)
	x := bigx.Int64()
	return x
}

func MakeClerk(servers []*labrpc.ClientEnd) *Clerk {
	ck := new(Clerk)
	ck.servers = servers

	// Your code here.
	ck.clientId = nrand()
	ck.leaderId = mathrand.Intn(len(ck.servers))
	return ck
}

func (ck *Clerk) Query(num int) Config {

	// Your code here.
	ck.seqId++
	args := QueryArgs{Num: num, ClientId: ck.clientId, SeqId: ck.seqId}
	serverId := ck.leaderId
	for {

		reply := QueryReply{}
		//fmt.Printf("[ ++++Client[%v]++++] : send a Query,args:%+v,serverId[%v]\\n", ck.clientId, args, serverId)
		ok := ck.servers[serverId].Call("ShardCtrler.Query", &args, &reply)

		if ok {
			if reply.Err == OK {
				ck.leaderId = serverId
				return reply.Config
			} else if reply.Err == ErrWrongLeader {
				serverId = (serverId + 1) % len(ck.servers)
				continue
			}
		}

		// 节点发生crash等原因
		serverId = (serverId + 1) % len(ck.servers)
		time.Sleep(100 * time.Millisecond)
	}

}

func (ck *Clerk) Join(servers map[int][]string) {
	// Your code here.
	ck.seqId++
	args := JoinArgs{Servers: servers, ClientId: ck.clientId, SeqId: ck.seqId}
	serverId := ck.leaderId
	for {

		reply := JoinReply{}
		//fmt.Printf("[ ++++Client[%v]++++] : send a Join,args:%+v,serverId[%v]\\n", ck.clientId, args, serverId)
		ok := ck.servers[serverId].Call("ShardCtrler.Join", &args, &reply)

		if ok {
			if reply.Err == OK {
				ck.leaderId = serverId
				return
			} else if reply.Err == ErrWrongLeader {
				serverId = (serverId + 1) % len(ck.servers)
				continue
			}
		}

		// 节点发生crash等原因
		serverId = (serverId + 1) % len(ck.servers)
		time.Sleep(100 * time.Millisecond)
	}

}

func (ck *Clerk) Leave(gids []int) {
	ck.seqId++
	args := LeaveArgs{GIDs: gids, ClientId: ck.clientId, SeqId: ck.seqId}
	serverId := ck.leaderId
	for {

		reply := JoinReply{}
		//fmt.Printf("[ ++++Client[%v]++++] : send a Join,args:%+v,serverId[%v]\\n", ck.clientId, args, serverId)
		ok := ck.servers[serverId].Call("ShardCtrler.Leave", &args, &reply)

		if ok {
			if reply.Err == OK {
				ck.leaderId = serverId
				return
			} else if reply.Err == ErrWrongLeader {
				serverId = (serverId + 1) % len(ck.servers)
				continue
			}
		}

		// 节点发生crash等原因
		serverId = (serverId + 1) % len(ck.servers)
		time.Sleep(100 * time.Millisecond)
	}
}

func (ck *Clerk) Move(shard int, gid int) {
	ck.seqId++
	args := MoveArgs{Shard: shard, GID: gid, ClientId: ck.clientId, SeqId: ck.seqId}
	serverId := ck.leaderId
	for {

		reply := JoinReply{}
		//fmt.Printf("[ ++++Client[%v]++++] : send a Move,args:%+v,serverId[%v]\\n", ck.clientId, args, serverId)
		ok := ck.servers[serverId].Call("ShardCtrler.Move", &args, &reply)

		if ok {
			if reply.Err == OK {
				ck.leaderId = serverId
				return
			} else if reply.Err == ErrWrongLeader {
				serverId = (serverId + 1) % len(ck.servers)
				continue
			}
		}

		// 节点发生crash等原因
		serverId = (serverId + 1) % len(ck.servers)
		time.Sleep(100 * time.Millisecond)
	}
}
```

# LabB

## 1.概述

> labB的内容就是将lab3中的普通KV操作转化为现在以分片为基础的KV操作
> 
> - client发送RPC请求，对KV进行操作
> - 通过clerk代理client请求让其对KV的分片进行负载均衡之类的操作
> - 服务端接收到RPC后开始对操作进行处理，即发送给Raft进行持久化，保证高可用
> - 这个期间分片管理器会一直运行将自己的分片负载均衡修改分片组与分片的映射
> - Raft层处理好持久化请求将进行响应
> - 随后server层收到响应后返回给客户端

![image.png](MIT6%20824%E5%88%86%E5%B8%83%E5%BC%8F%20Lab4AB%EF%BC%88Sharded%20Key%20Value%20Service%EF%BC%9A%E5%88%86%E7%89%87KV%E6%9C%8D/image%204.png)

## 2.client编写

- 概述

> 客户端的请求编写课程是给出来的，所以我们就需要把里面的细节做好就行（客户端请求去重），还是像lab3与lab4A的一样接收请求就好
> 

```go
// 获取键的当前值。如果键不存在，则返回 “”。面对所有其他错误，不断尝试。
// You will have to modify this function.
func (ck *Clerk) Get(key string) string {
	ck.seqId++
	args := GetArgs{
		Key:       key,
		ClientId:  ck.ClientId,
		RequestId: ck.seqId,
	}

	for {
		shard := key2shard(key)
		gid := ck.config.Shards[shard]
		if servers, ok := ck.config.Groups[gid]; ok {
			// try each server for the shard.
			for si := 0; si < len(servers); si++ {
				srv := ck.make_end(servers[si])
				var reply GetReply
				ok := srv.Call("ShardKV.Get", &args, &reply)
				if ok && (reply.Err == OK || reply.Err == ErrNoKey) {
					return reply.Value
				}
				if ok && (reply.Err == OK || reply.Err == ErrNoKey) {
					return reply.Value
				}
				// ... not ok, or ErrWrongLeader
				if ok && (reply.Err == ErrWrongGroup) {
					break
				}
			}
		}
		time.Sleep(100 * time.Millisecond)
		// ask controler for the latest configuration.
		ck.config = ck.sm.Query(-1)
	}

	return ""
}

// 由放置和追加共享。
// You will have to modify this function.
func (ck *Clerk) PutAppend(key string, value string, op string) {
	ck.seqId++
	args := PutAppendArgs{
		Key:       key,
		Value:     value,
		Op:        op,
		ClientId:  ck.ClientId,
		RequestId: ck.seqId,
	}

	for {
		shard := key2shard(key)
		gid := ck.config.Shards[shard]
		if servers, ok := ck.config.Groups[gid]; ok {
			for si := 0; si < len(servers); si++ {
				srv := ck.make_end(servers[si])
				var reply PutAppendReply
				ok := srv.Call("ShardKV.PutAppend", &args, &reply)
				if ok && reply.Err == OK {
					return
				}
				if ok && reply.Err == ErrWrongGroup {
					break
				}
				// ... not ok, or ErrWrongLeader
			}
		}
		time.Sleep(100 * time.Millisecond)
		// ask controler for the latest configuration.
		ck.config = ck.sm.Query(-1)
	}
}
```

## 3.server编写

### 3.1 初始化

- 初始化服务器以及相关参数的添加

```go
type Op struct {
	// Your definitions here.
	// Field names must start with capital letters,
	// otherwise RPC will break.
	Key   string
	Value string

	ClientId int64
	SeqId    int
	OpType   Operation //get、put、append

	ShardId int
	Shard   Shard
	SeqMap  map[int64]int

	UpdateConfig shardctrler.Config //根据分片的更新而更新对应的配置
}

// OpReply 用于在 Op 从 applyCh 到达后唤醒等待的 RPC 调用方
type OpReply struct {
	ClientId int64
	SeqId    int
	Err      Err
}

type Shard struct {
	KvMap         map[string]string
	ConfigVersion int //当前分片的版本，每次操作都会更新
}

type ShardKV struct {
	mu           sync.Mutex
	me           int
	rf           *raft.Raft
	applyCh      chan raft.ApplyMsg
	make_end     func(string) *labrpc.ClientEnd
	gid          int
	clients      []*labrpc.ClientEnd //保存RPC发送方的信息
	maxraftstate int                 // 如果日志增长这么大，则快照

	// Your definitions here.
	dead int32 // set by Kill()

	seqMap       map[int64]int        //为了确保seq只执行一次	clientId / seqId
	waitChMap    map[int]chan OpReply //传递由下层Raft服务的appCh传过来的command	index / chan(Op)，每个index对应一个chan
	shardPersist []Shard              //

	serverClerk *shardctrler.Clerk // sck 是用于联系分片主服务器的客户端
}
// 服务器 [] 包含此组中服务器的端口。me 是服务器 [] 中当前服务器的索引。
//
// KV 服务器应通过底层 Raft 实现存储快照，该实现应调用 persister.SaveStateAndSnapshot() 以原子方式保存 Raft 状态以及快照。
//
// 当 Raft 保存的状态超过 maxraftstate 字节时，KV 服务器应创建快照，以便允许 Raft 对其日志进行垃圾回收。
// 如果 maxraftstate 为 -1，则无需拍摄快照。gid 是该组的 GID，用于与分片机交互。
// 将 ctrlers[] 传递给 Shardctrler.MakeClerk()，这样你就可以将 RPC 发送到 shardctrler。
// make_end（servername）将服务器名称从Config.Groups[gid][i]转换为labrpc。
// 可以在其上发送 RPC 的客户端。你将需要它来将 RPC 发送到其他组。
// 查看 client.go 以获取有关如何使用 ctrlers[] 和 make_end() 将 RPC 发送到拥有特定分片的组的示例。
// StartServer() 必须快速返回，因此它应该为任何长时间运行的工作启动 goroutines。
func StartServer(servers []*labrpc.ClientEnd, me int, persister *raft.Persister, maxraftstate int, gid int, ctrlers []*labrpc.ClientEnd, make_end func(string) *labrpc.ClientEnd) *ShardKV {
	// call labgob.Register on structures you want
	// Go's RPC library to marshall/unmarshall.
	labgob.Register(Op{})

	kv := new(ShardKV)
	kv.me = me
	kv.maxraftstate = maxraftstate
	kv.make_end = make_end
	kv.gid = gid
	kv.clients = ctrlers

	// Your initialization code here.

	// Use something like this to talk to the shardctrler:
	// kv.mck = shardctrler.MakeClerk(kv.ctrlers)

	kv.applyCh = make(chan raft.ApplyMsg)
	kv.rf = raft.Make(servers, me, persister, kv.applyCh)

	kv.seqMap = make(map[int64]int)
	kv.waitChMap = make(map[int]chan OpReply)
	kv.shardPersist = make([]Shard, shardctrler.NShards)

	kv.serverClerk = shardctrler.MakeClerk(kv.clients) //通过客户端创建出代理对象clerk

	//快照
	snapShot := persister.ReadSnapshot()
	//如果有快照就解码
	if len(snapShot) > 0 {
		kv.DecodeSnapShot(snapShot)
	}
	//创建rf节点
	kv.applyCh = make(chan raft.ApplyMsg)
	kv.rf = raft.Make(servers, me, persister, kv.applyCh)

	go kv.ApplyMsgHandlerLoop()
	go kv.ConfigDetectedLoop()
	return kv
}
```

### 3.2 Handler

- 概述

> 首先我来理清以下流程，要不然这两个handler要做的事情有点难理解
> 
> 1. 最开始这个KV的服务层会通过`GET/PUTAPPEND`这两个函数接收客户端的RPC请求，然后会这个请求加上一些标志位组成一个msg发到Raft层
> 2. 然后我们在`ApplyMsgHandlerLoop`接收到的msg就是客户端需要存储或者删除KV的类似于命令与数据的东西，先发送到最底层让其Raft节点之间进行持久化。存储的总归是一个一个数据，在逻辑层面上我们对这些数据进行切割分类，建立映射关系就是一个一个的分片（每个分片中存放很多的KV）了，我们会对分片进行分组，并且由分组管理器ShardCtrler所管理，管理器会进行分组之间的负载均衡（LabA的内容），**不同的服务器负责不同的分组**
> 3. 然后对msg进行分类，检索出已经持久化的分片，将他们根据客户端的请求分片对应KV（server的KV映射）进行更新
> 4. 同时在进行的`ConfigDetectedLoop`这个handler就是更新管理config，而这个config还记得前面说的分片与组的映射吗，这个映射必须在这个服务层也存储一份，并且要做到与ShardCtrler中的一致。所以这个config就是这个映射的具象化，每个config就代表一个分组

==处理raft响应处理后的Handler==

> 对数据进行处理，转化为分片，并且对当前的日志量进行对比，大于就要进行快照
> 

```go
// applyMsgHandlerLoop 处理applyCh发送过来的ApplyMsg
func (kv *ShardKV) ApplyMsgHandlerLoop() {
	for {
		if kv.killed() {
			return
		}

		select {
		case msg := <-kv.applyCh:
			if msg.CommandValid { //如果有新提交的日志
				kv.mu.Lock()
				op := msg.Command.(Op)
				reply := OpReply{
					ClientId: op.ClientId,
					SeqId:    op.SeqId,
					Err:      OK,
				}

				if op.OpType == PutType || op.OpType == GetType || op.OpType == AppendType {
					shardId := key2shard(op.Key)
					if kv.Config.Shards[shardId] != kv.gid { //得到要修改分片的组id，与当前服务器的gid对比
						reply.Err = ErrWrongGroup
					} else if kv.shardPersist[shardId].KvMap == nil { //看是否需要持久化
						// 如果应该存在的切片没有数据那么这个切片就还没到达
						reply.Err = ShardNotArrived
					} else {
						if !kv.isDuplicate(op.ClientId, op.SeqId) {
							kv.seqMap[op.ClientId] = op.SeqId
							switch op.OpType {
							case PutType:
								kv.shardPersist[shardId].KvMap[op.Key] = op.Value
							case GetType:
								//get什么都不做
							case AppendType:
								kv.shardPersist[shardId].KvMap[op.Key] += op.Value
							default:
								log.Fatalf("invalid command type: %v.", op.OpType)
							}
						}
					}

				} else { //其他操作情况，就是请求时分组发过来的对分片的操作，就是对分片的负载均衡请求需要由我们发送给分片控制器
					switch op.OpType {
					case UpConfigType: //对于配置文件的信息
						kv.updateConfigHandler(op)
					case AddShardType:
						// 如果配置号比op的SeqId还低说明不是最新的配置
						if kv.Config.Num < op.SeqId {
							reply.Err = ShardNotArrived
							break
						}
						kv.addShardHandler(op)
					case RemoveShardType:
						kv.removeShardHandler(op)
					default:
						log.Fatalf("invalid command type: %v.", op.OpType)
					}
				}

				//如果增加日志后大于临界值那就需要快照
				if kv.maxraftstate != -1 && kv.rf.GetRaftStateSize() > kv.maxraftstate {
					snapShot := kv.PersistSnapShot()
					kv.rf.Snapshot(msg.CommandIndex, snapShot)
				}
				ch := kv.getWaitCh(msg.CommandIndex)
				ch <- reply
				kv.mu.Unlock()
			}
			if msg.SnapshotValid { //如果有新的快照，将其反序列化
				if kv.rf.CondInstallSnapshot(msg.SnapshotTerm, msg.SnapshotIndex, msg.Snapshot) {
					kv.mu.Lock()
					kv.DecodeSnapShot(msg.Snapshot)
					kv.mu.Unlock()
				}
				continue
			}
		}
	}
}
```

==检查Config更新的Handler==

> 组与分片的映射关系全部存储在Config中，所以每次对于分片的操作我们就需要去更新维护
> 

```go
// ConfigDetectedLoop 配置检测
func (kv *ShardKV) ConfigDetectedLoop() {
	kv.mu.Lock()
	curConfig := kv.Config
	rf := kv.rf
	kv.mu.Unlock()

	for !kv.killed() {
		//如果遍历导的节点不是leader换下一个
		if _, isLeader := rf.GetState(); !isLeader {
			time.Sleep(UpConfigLoopInterval)
			continue
		}
		kv.mu.Lock()
		// 判断是否把不属于自己的部分给分给别人了
		if !kv.allSent() {
			seqMap := make(map[int64]int)
			for k, v := range kv.seqMap {
				seqMap[k] = v
			}
			//找到标记的分片，并且有最新的配置
			// 将最新配置里不属于自己的分片分给别人
			for shardId, gid := range kv.LastConfig.Shards {
				if gid == kv.gid && kv.Config.Shards[shardId] != kv.gid &&
					kv.shardPersist[shardId].ConfigVersion < kv.Config.Num {
					sendData := kv.cloneShard(kv.Config.Num, kv.shardPersist[shardId].KvMap)
					args := SendShardArg{
						LastAppliedRequestId: seqMap,
						ShardId:              shardId,
						Shard:                sendData,
						ClientId:             int64(gid),
						RequestId:            kv.Config.Num,
					}
					//得到当前配置中不同分组对应的服务层，根据服务层能够找到客户端
					serverList := kv.Config.Groups[kv.Config.Shards[shardId]]
					servers := make(map[int][]string)
					for i, name := range serverList {
						servers[i] = kv.makeEnd(name)
					}

					// 开启协程对每个客户端发送切片(这里发送的应是别的组别，自身的共识组需要raft进行状态修改）
					go func(servers []*labrpc.ClientEnd, args *SendShardArg) {
						index := 0
						start := time.Now()
						for {
							var reply AddShardReply
							// 对自己的共识组内进行add
							ok := servers[index].Call("ShardKV.AddShard", args, &reply)
							if ok && reply.Err == OK || time.Now().Sub(start) >= 5*time.Second {
								kv.mu.Lock()
								command := Op{
									OpType:   RemoveShardType,
									ClientId: int64(kv.gid),
									SeqId:    kv.Config.Num,
									ShardId:  args.ShardId,
								}
								kv.mu.Unlock()
								kv.startCommand(command, RemoveShardsTimeout)
								break
							}
							index = (index + 1) & len(servers)
							if index == 0 {
								time.Sleep(UpConfigLoopInterval)
							}
						}
					}(servers, &args)
				}
			}
			kv.mu.Unlock()
			time.Sleep(UpConfigLoopInterval)
			continue
		}

		if !kv.allReceived() {
			kv.mu.Unlock()
			time.Sleep(UpConfigLoopInterval)
			continue
		}

		// 当前配置已配置，轮询下一个配置
		curConfig = kv.Config
		clerk := kv.serverClerk
		kv.mu.Lock()

		newConfig := clerk.Query(curConfig.Num + 1)
		if newConfig.Num != curConfig.Num+1 {
			time.Sleep(UpConfigLoopInterval)
			continue
		}

		command := Op{
			OpType:       UpConfigType,
			ClientId:     int64(kv.gid),
			SeqId:        newConfig.Num,
			UpdateConfig: newConfig,
		}
		kv.startCommand(command, UpConfigTimeout)
	}
}
```

==updateConfigHandler&addShardHandler&removeShardHandler==

> 还记得上面config的维护handler吗，它对config的修改实际上也是需要raft持久化的，这个修改的操作可以分为更新、添加、移除分片。那么也就需要细分成三个handler去处理raft处理后的响应
> 

### 3.3 操作RPC

- 概述

> 就是那三个操作对应的RPC：`GET/PUT/APPEND`，没什么好说的处理RPC请求发给raft就好
> 

==GET==

```go
func (kv *ShardKV) Get(args *GetArgs, reply *GetReply) {
	// Your code here.
	shardId := key2shard(args.Key)
	//如果这个分组不存在这个服务器上就返回
	if kv.Config.Shards[shardId] != kv.gid {
		reply.Err = ErrWrongGroup
		//KVmap里都是持久化后的分片的KV，如果为空说明raft还没处理好
	} else if kv.shardPersist[shardId].KvMap == nil {
		reply.Err = ShardNotArrived
	}
	kv.mu.Lock()
	if reply.Err == ErrWrongGroup || reply.Err == ShardNotArrived {
		return
	}

	command := Op{
		OpType:   GetType,
		Key:      args.Key,
		ClientId: args.ClientId,
		SeqId:    args.RequestId,
	}
	err := kv.rf.startCommand(command, GetTimeout)
	if err != OK {
		reply.Err = err
		return
	}
	kv.mu.Lock()
	//经过raft层返回的结果再次检查分片
	if kv.Config.Shards[shardId] != kv.gid {
		reply.Err = ErrWrongGroup
	} else if kv.shardPersist[shardId].KvMap == nil {
		reply.Err = ShardNotArrived
	} else {
		reply.Err = OK
		reply.Value = kv.shardPersist[shardId].KvMap[args.Key]
	}
	kv.mu.Unlock()
	return
}
```

==PUTAPPEND==

```go
func (kv *ShardKV) PutAppend(args *PutAppendArgs, reply *PutAppendReply) {
	// Your code here.
	shardId := key2shard(args.Key)
	kv.mu.Lock()
	if kv.Config.Shards[shardId] != kv.gid {
		reply.Err = ErrWrongGroup
	} else if kv.shardPersist[shardId].KvMap == nil {
		reply.Err = ShardNotArrived
	}
	kv.mu.Unlock()
	if reply.Err == ErrWrongGroup || reply.Err == ShardNotArrived {
		return
	}
	command := Op{
		OpType:   args.Op,
		ClientId: args.ClientId,
		SeqId:    args.RequestId,
		Key:      args.Key,
		Value:    args.Value,
	}
	reply.Err = kv.startCommand(command, AppOrPutTimeout)
	return
}
```

==AddShard==

> 这个RPC是服务层内部的，上面我们介绍到维护config的handler，其中就有分片换分组的需求，换分组也就意味着换负责的服务器，那么就要就要有对应的RPC去完成
> 

```go
// 添加分片将分片从调用方移动到此服务器
func (kv *ShardKV) AddShard(args *SendShardArg, reply *AddShardReply) {
	command := Op{
		OpType:   AddShardType,
		ClientId: args.ClientId,
		SeqId:    args.RequestId,
		ShardId:  args.ShardId,
		Shard:    args.Shard,
		SeqMap:   args.LastAppliedRequestId,
	}
	reply.Err = kv.startCommand(command, AddShardsTimeout)
	return
}
```

### 3.4 其他工具函数

==startCommand==

> 我们将对下层raft发送请求的需求抽取成一个函数，可以看到逻辑很简单，就是新建一个通道去接收raft给的响应，时间到还没接收到就超时
> 

```go
func (kv *ShardKV) startCommand(command Op, timeout time.Duration) Err {
	kv.mu.Lock()
	index, _, isLeader := kv.rf.Start(command)
	if !isLeader {
		kv.mu.Unlock()
		return ErrWrongLeader
	}
	ch := kv.getWaitCh(index)
	kv.mu.Unlock()

	//等到raft
	timer := time.NewTicker(timeout)
	defer timer.Stop()

	select {
	case reply := <-ch:
		kv.mu.Lock()
		delete(kv.waitChMap, index)
		//说明不是这个请求，对应不上了
		if reply.SeqId != command.SeqId || reply.ClientId != command.ClientId {
			// 一种方法是让服务器检测到它已经失去了领导地位，方法是注意到 Start()返回的索引中出现了不同的请求
			kv.mu.Unlock()
			return ErrInconsistentData
		}
		kv.mu.Unlock()
		return reply.Err

	case <-timer.C:
		return ErrOverTime
	}
}
```

==序列化与反序列化==

```go
// 序列化，即持久化server的数据
func (kv *ShardKV) PersistSnapShot() []byte {
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	err := e.Encode(kv.shardPersist)
	err = e.Encode(kv.seqMap)
	err = e.Encode(kv.maxraftstate)
	err = e.Encode(kv.Config)
	err = e.Encode(kv.LastConfig)
	if err != nil {
		log.Fatalf("[%d-%d] fails to take snapshot.", kv.gid, kv.me)
	}
	data := w.Bytes()
	return data
}

// 反序列化
func (kv *ShardKV) DecodeSnapShot(snapshot []byte) {
	if snapshot == nil || len(snapshot) < 1 {
		return
	}
	var shardPersist []Shard
	var seqMap map[int64]int
	var maxraftstate int
	var Config, LastConfig shardctrler.Config

	r := bytes.NewBuffer(snapshot)
	d := labgob.NewDecoder(r)

	if d.Decode(&shardPersist) != nil || d.Decode(&seqMap) != nil ||
		d.Decode(&maxraftstate) != nil || d.Decode(&Config) != nil || d.Decode(&LastConfig) != nil {
		//如果没有对应序列化内容
		log.Fatalf("[Server(%v)] Failed to decode snapshot！！！", kv.me)
	} else {
		kv.shardPersist = shardPersist
		kv.seqMap = seqMap
		kv.maxraftstate = maxraftstate
		kv.Config = Config
		kv.LastConfig = LastConfig
	}
}
```

==allSent&allReceived==

> 遍历当前的config中查找属于自己和不属于自己的分片
> 

```go
// 判断当前最新的配置文件中有没有不属于自己的分片
func (kv *ShardKV) allSent() bool {
	for shard, gid := range kv.LastConfig.Shards {
		// 如果当前配置中分片中的信息不匹配，且持久化中的配置号更小，说明还未发送
		if gid == kv.gid && kv.Config.Shards[shard] != kv.gid && kv.shardPersist[shard].ConfigVersion < kv.Config.Num {
			return false
		}
	}
	return true
}

// 作为一个服务层，如果只能发送的话就不能接收别人发给属于我们的分片了
func (kv *ShardKV) allReceived() bool {
	for shard, gid := range kv.LastConfig.Shards {
		// 判断切片是否都收到了
		if gid != kv.gid && kv.Config.Shards[shard] == kv.gid && kv.shardPersist[shard].ConfigVersion < kv.Config.Num {
			return false
		}
	}
	return true
}
```

==cloneShard==

```go
// 如果又不属于自己的分片，就进行克隆，克隆的发出去，原本的删除
func (kv *ShardKV) cloneShard(configVersion int, kvMap map[string]string) Shard {
	migrateShard := Shard{
		KvMap:         make(map[string]string),
		ConfigVersion: configVersion,
	}

	for k, v := range kvMap {
		migrateShard.KvMap[k] = v
	}

	return migrateShard
}
```
# MIT6.830数据库 | Lab6（日志的回滚和恢复）

type: Post
status: Published
date: 2022/09/06
summary: 日志的回滚和恢复
tags: 实践
category: 数据库

# Lab6

## 前言

- 环境

> 需要配置Ant集成化测试环境，当然你使用自带的Junit也可以
> 

## 结构总概

- SimpleDB所包括的结构

> 
> 
> - 表示字段、元组和元组模式的类；
> - 将谓词和条件应用于元组的类；
> - 一种或多种访问方法（例如，堆文件），将关系存储在磁盘上，并提供一种遍历这些关系的元组的方法；
> - 处理元组的运算符类（例如，选择、连接、插入、删除等）的集合；
> - 一个缓冲池，在内存中缓存活动的元组和页面，并处理并发控制和事务；并且，存储有关可用表及其模式的信息的目录。
- 图示

> 
> 
> - Tuple和TupleDesc是数据库表的最基本元素了。Tuple就是一个若干个Field的数组，TupleDesc则是一个表的meta-data，包括每列的field name和type。
> - HeapPage和HeapFile都分别是Page和DbFile interface的实现，毕竟HeapPage和HeapFile组织还是太简单了，后面lab会用B+树来替代之。
> - BufferPool是用来做缓存的，getPage会优先从这里拿，如果没有，才会调用File的readPage去从文件中读取对应page，disk中读入的page会缓存在其中。
> - SeqScan用来遍历一个table的所有tuple，包装了HeapFile的iterator。
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab6%EF%BC%88%E6%97%A5%E5%BF%97%E7%9A%84%E5%9B%9E%E6%BB%9A%E5%92%8C%E6%81%A2%E5%A4%8D%EF%BC%89/image.png)
> 
- DataBase类

> **Database 类提供对作为数据库全局状态的静态对象集合的访问。具体来说，这包括访问编目 (数据库中所有表的列表)、缓冲池 (当前驻留在内存中的数据库文件页的集合) 和日志文件的方法。**
> 

## 1.Lab6的任务总概

- 前情提要

> BufferPool 已经通过删除脏页实现了中止，并通过仅在提交时将脏页强制同步到磁盘来假装实现原子提交。日志记录允许更灵活的缓冲区管理`（STEAL 和 NO-FORCE）`
> 
- 概述

> 在本实验中，你将实施基于日志的中止回滚和基于日志的崩溃恢复。我们为你提供了定义日志格式的代码，并在事务期间的适当时间将记录追加到日志文件中。你将使用日志文件的内容实现回滚和恢复。
> 
> 1. 实现回滚
> 2. 实现数据全量恢复

## 2.开始之前添加一些代码

- 关于BufferPool的一些修改

> `BufferPool#flushPage`，添加的是if判断中的前两句
> 

```java
/**
     * 将某个页面刷新到磁盘
     * @param pid 要刷新的页面的 ID
     */
    private synchronized void flushPage(PageId pid) throws IOException {
        Page page = bufferPool.get(pid).page;
        TransactionId dirtier = page.isDirty();
        //如果不为脏则事务id返回null
        if(dirtier != null){
            //这里记住是在写页面之前
            Database.getLogFile().logWrite(dirtier, page.getBeforeImage(), page);
            Database.getLogFile().force();
            //如果是脏页面，就进行同步持久化
            Database.getCatalog().getDatabaseFile(pid.getTableId()).writePage(page);
            //同步化之后则设置事务id为null
            page.markDirty(false, null);
        }
    }
```

> `BufferPool#transactionComplete&flushPages`，添加保存视图的语句，在每一次刷新页面时
> 

```java
/**
     * 提交或中止给定的事务；释放与事务关联的所有锁。
     *
     * @param tid 请求解锁的交易ID
     * @param commit 指示我们应该提交还是中止的标志，true代表提交，false代表终止
     */
    public void transactionComplete(TransactionId tid, boolean commit) {
        //如果是提交
        if (commit){
            try {
                flushPages(tid);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }else{  //如果是回滚
            restorePages(tid);
        }
        //事务完成，锁提交
        lockManger.cleanAllLocks(tid);
    }

    /** 将指定事务的所有页面写入磁盘。
     */
    public synchronized void flushPages(TransactionId tid) throws IOException {
        for (PageNode node : bufferPool.values()) {
            Page page = node.page;
            //如果当前脏页是这个事务修改的
            if(tid.equals(page.isDirty())){
                flushPage(node.pageId);
                page.setBeforeImage();
            }
        }
    }
```

> 测试，此时应该只通过前三个test
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab6%EF%BC%88%E6%97%A5%E5%BF%97%E7%9A%84%E5%9B%9E%E6%BB%9A%E5%92%8C%E6%81%A2%E5%A4%8D%EF%BC%89/image%201.png)

```bash
ant runsystest -Dtest=LogTest
```

## 3.日志注意事项以及格式

- 注意事项

> **这里的很多方法都是同步的（防止并发日志写入发生）； BufferPool 中的许多方法也是同步的（出于类似原因）。问题是 BufferPool 写入日志记录（在页面刷新时）并且日志文件刷新 BufferPool 页面（在检查点和恢复时）。这可能导致死锁，所以这里任何需要访问 BufferPool 的 LogFile 操作并且必须以如下块开头**：
> 

```java
synchronized (Database.getBufferPool()) {
       synchronized (this) {

       ..

       }
    }
```

- 日志格式

```html
<p> 日志文件的格式如下：

<ul>

<li> 文件的第一个长整数表示最后写入检查点的偏移量，如果没有检查点，则为 -1

<li> 日志中的所有附加数据都由日志记录组成。日志记录是可变长度的。

<li> 每条日志记录都以整数类型和长整数事务 id 开头。

<li> 每条日志记录都以一个长整数文件偏移量结束，该偏移量表示日志文件中记录开始的位置。

<li> 有五种记录类型：ABORT、COMMIT、UPDATE、BEGIN 和 CHECKPOINT

<li> ABORT、COMMIT 和 BEGIN 记录不包含其他数据

<li>更新记录由两个条目组成，一个前图像和一个后图像。这些图像是序列化的 Page 对象，
 可以使用 LogFile.readPageData() 和 LogFile.writePageData() 方法访问。

<li> CHECKPOINT 记录由检查点发生时的活动事务和它们在磁盘上的第一条日志记录组成。
 记录的格式是事务数的整数计数，以及每个活动事务的长整数事务 id 和长整数首记录偏移量。

</ul>
```

## 4.实现回滚

- 概述

> 当事务中止时，在事务释放其锁之前调用此`rollback()`函数。它的工作是撤消事务对数据库所做的任何更改。
> 
- 大致思路

> `rollback()` 应该读取日志文件，查找与中止事务关联的所有更新记录，从每个记录中提取前视图，并将前视图写入表文件。用于 `raf.seek()` 在日志文件等中移动 `raf.readInt()` 以检查日志文件。用于 `readPageData()` 读取每个前视图和后视图。你可以使用映射 `tidToFirstLogRecord`（从事务 id 映射到堆文件中的偏移量）来确定从何处开始读取特定事务的日志文件。你需要确保从缓冲池中丢弃任何页，这些页的前视图被写回到表文件中。
> 
- 代码——`LogFile#rollback`

```java
/** 回滚指定的事务，将其更新的任何页面的状态设置为其更新前的状态。为了保留事务语义，
     * 不应在已提交的事务上调用此方法（尽管此方法可能不会强制执行此操作。）

        @param tid 回滚那个事务
    */
    public void rollback(TransactionId tid)
        throws NoSuchElementException, IOException {
        synchronized (Database.getBufferPool()) {
            synchronized(this) {
                //现标记一下以前的日志，相当于一个标记点
                preAppend();
                //得到该事务的偏移量
                Long start = tidToFirstLogRecord.get(tid);
                //把raf的读取偏移量设置成当前这个日志文件对应事务的起始位置
                raf.seek(start);
                Set<Page> pageSet = new HashSet<>();
                while (raf.getFilePointer() != logFile.length()) {
                    //readInt和readLong方法就会使读取指针向后移动4个或8个字节
                    //读日志记录类型
                    int type = raf.readInt();
                    //读日志记录的事务id
                    long tidRecord = raf.readLong();
                    if (type == UPDATE_RECORD) {
                        Page before = readPageData(raf);
                        Page after = readPageData(raf);
                        if (tid.getId() == (tidRecord) && !pageSet.contains(before)) {
                            try {
                                //从缓存中删除这个新视图
                                Database.getBufferPool().discardPage(after.getId());
                                //将这个旧视图写到磁盘中去，即回滚
                                Database.getCatalog().getDatabaseFile(before.getId().getTableId()).writePage(before);
                                //将旧视图缓存
                                Database.getBufferPool().getPage(tid, before.getId(), Permissions.READ_ONLY);
                            } catch (DbException dbException) {
                                dbException.printStackTrace();
                            } catch (TransactionAbortedException e) {
                                e.printStackTrace();
                            }

                        }
                    }else if (type == CHECKPOINT_RECORD) {
                        //读取有多少个活动事务，跳过他们
                        int num = raf.readInt();
                        while (num-- > 0) {
                            raf.readLong();
                            raf.readLong();
                        }
                    }
                    raf.readLong();
                }
            }
        }
    }
```

## 5.实现数据全量恢复

- 概述

> 当数据库突然宕机重新启动后，则 `LogFile.recover()` 会在任何新事务开始之前进行执行
> 
- 实现思路

> 读取最后一个检查点（如果有）。从检查点向前扫描（如果没有检查点，则从日志文件的开头向前扫描），以生成失败者事务集。在此阶段中重做更新。你可以在检查点安全地开始重做，因为 `LogFile.logCheckpoint()` 会将所有脏缓冲区刷新到磁盘。撤消失败者交易记录的更新。
> 
- 代码

```java
/** 通过确保已安装已提交事务的更新以及未安装未提交事务的更新来恢复数据库系统。
    */
    public void recover() throws IOException {
        synchronized (Database.getBufferPool()) {
            synchronized (this) {
                recoveryUndecided = false;
                raf = new RandomAccessFile(logFile, "rw");
                //已提交的事务id集合
                Set<Long> committedId = new HashSet<>();
                //存放事务id对应的beforePage和afterPage
                Map<Long, List<Page>> beforePages = new HashMap<>();
                Map<Long, List<Page>> afterPages = new HashMap<>();
                //获取checkpoint
                Long checkpoint = raf.readLong();
                if (checkpoint != -1) {
//                    raf.seek(checkpoint);
                }
                while (true) {
                    try {
                        int type = raf.readInt();
                        long txid = raf.readLong();
                        switch (type) {
                            case UPDATE_RECORD:
                                Page beforeImage = readPageData(raf);
                                Page afterImage = readPageData(raf);
                                List<Page> l1 = beforePages.getOrDefault(txid, new ArrayList<>());
                                l1.add(beforeImage);
                                beforePages.put(txid, l1);
                                List<Page> l2 = afterPages.getOrDefault(txid, new ArrayList<>());
                                l2.add(afterImage);
                                afterPages.put(txid, l2);
                                break;
                            case COMMIT_RECORD:
                                committedId.add(txid);
                                break;
                            case CHECKPOINT_RECORD:
                                int numTxs = raf.readInt();
                                while (numTxs -- > 0) {
                                    raf.readLong();
                                    raf.readLong();
                                }
                                break;
                            default:
                                break;
                        }
                        //end
                        raf.readLong();

                    } catch (EOFException e) {
                        break;
                    }
                }

                //处理未提交事务，直接写before-image
                for (long txid :beforePages.keySet()) {
                    if (!committedId.contains(txid)) {
                        List<Page> pages = beforePages.get(txid);
                        for (Page p : pages) {
                            Database.getCatalog().getDatabaseFile(p.getId().getTableId()).writePage(p);
                        }
                    }
                }

                //处理已提交事务，直接写after-image
                for (long txid : committedId) {
                    if (afterPages.containsKey(txid)) {
                        List<Page> pages = afterPages.get(txid);
                        for (Page page : pages) {
                            Database.getCatalog().getDatabaseFile(page.getId().getTableId()).writePage(page);
                        }
                    }
                }
            }
         }
    }
```
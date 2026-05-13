# MIT6.830数据库 | Lab4（简单数据库事务）

type: Post
status: Published
date: 2022/09/03
summary: 简单数据库事务
tags: 实践
category: 数据库

# Lab4

## 前言

- 环境

> 需要配置Ant集成化测试环境，当然你使用自带的Junit也可以
> 

## 结构总概

SimpleDB所包括的结构

> 
> 
> - 表示字段、元组和元组模式的类；
> - 将谓词和条件应用于元组的类；
> - 一种或多种访问方法（例如，堆文件），将关系存储在磁盘上，并提供一种遍历这些关系的元组的方法；
> - 处理元组的运算符类（例如，选择、连接、插入、删除等）的集合；
> - 一个缓冲池，在内存中缓存活动的元组和页面，并处理并发控制和事务；并且，存储有关可用表及其模式的信息的目录。

图示

> 
> 
> - Tuple和TupleDesc是数据库表的最基本元素了。Tuple就是一个若干个Field的数组，TupleDesc则是一个表的meta-data，包括每列的field name和type。
> - HeapPage和HeapFile都分别是Page和DbFile interface的实现，毕竟HeapPage和HeapFile组织还是太简单了，后面lab会用B+树来替代之。
> - BufferPool是用来做缓存的，getPage会优先从这里拿，如果没有，才会调用File的readPage去从文件中读取对应page，disk中读入的page会缓存在其中。
> - SeqScan用来遍历一个table的所有tuple，包装了HeapFile的iterator。

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab4%EF%BC%88%E7%AE%80%E5%8D%95%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%EF%BC%89/image.png)

- DataBase类

> **Database 类提供对作为数据库全局状态的静态对象集合的访问。具体来说，这包括访问编目 (数据库中所有表的列表)、缓冲池 (当前驻留在内存中的数据库文件页的集合) 和日志文件的方法。**
> 

## 1.Lab4的任务总概

- 概述

> 在本实验中，**你将在 SimpleDB 中实现一个简单的基于锁定的事务系统。你将需要在代码中的适当位置添加锁定和解锁调用**，以及跟踪每个事务持有的锁并在需要时向事务授予锁的代码。
> 
> - 实现一个page级别，遵从二段锁协议的锁管理器。即在访问任何page之前，事务应该获取该page上适当类型的锁，并且在事务提交之前不应该释放任何锁。
> - 完善BufferPool中的evictPage()方法，避免数据丢失，当需要置换的页面为脏页时，要跳过脏页，置换掉不是脏页的page
> - 实现事务的功能，当事务提交时，将事务涉及的脏页写回磁盘，然后释放锁。当事务回滚时，清理该事务涉及到的脏页，重新从磁盘中读取清理的page
> - 实现死锁防范功能，当发生死锁时，抛出AbortException

## 2.开始前需要学习的知识点

- 两阶段锁协议

> 即将所有操作包裹在一个事务中，事务中的各种占用和释放都要跟随事务的提交提交，不能早也不能晚；**在MySQL中行锁是在需要的时候加上去，但并不是不需要了就立刻释放，而是要等到事务结束时才释放。这个就是两阶段锁协议(加锁阶段、解锁阶段)。**
> 
> - 加锁阶段：事务可以申请获得任意数据上的任意锁，但是不能释放任何锁。
> - 解锁阶段：事务可以释放任何数据上的任何类型的锁，但是不能再次申请任何锁
- 死锁问题的产生

> 因为二阶段锁是在使用的过程中才加锁的，那么就由可能别的事务会话先对这个记录加锁，等到当前事务时就会等待，但是别的事务也有可能需要已经被占用的记录，死锁产生
> 

> **在本次实验中我们采用事务提交之前可以获取任何锁，事务提交之后释放该事务所拥有的所有锁。同时在获取锁的过程中进行死锁检测。**
> 
- 事务

> 对于事务的理解我们首先需要直到四大特性，对于这四大特性我这里有很详细的解析[事务](https://blog.csdn.net/weixin_49258262/article/details/123515126)
> 
> 1. 原子性
> 2. 一致性
> 3. 隔离性
> 4. 持久性
- 关于脏页同步的问题

> 对于修改过的脏页是存放在内存中的，我们需要将数据持久化到磁盘里，我们使用一种`NOSTEAL/FORCE` 缓冲区管理策略。我们还未实现日志的功能，所以不需要考虑日志恢复之类的工作
> 
> - 如果脏页（已更新）被未提交的事务锁定，则不应将它们从缓冲池中刷新到磁盘（这是 NOSTEAL）。
> - **在事务提交时，你应该将脏页强制写入磁盘**（这是 FORCE）。
- 关于加锁的规则

> 我们在实验中实现表级锁，而不是粒度更细的行级锁。**我们将需要创建数据结构来跟踪每个事务持有哪些锁，并检查是否应在请求事务时将锁授予该事务。**在MySQL中锁的结构如下：
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab4%EF%BC%88%E7%AE%80%E5%8D%95%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%EF%BC%89/image%201.png)

- 关于共享锁与排它锁

> 我们需要注意下面的规则，当一个事务拿不到请求的锁他需要等待，这里需要考虑锁的并发需求
> 
> - 在事务可以读取一个对象之前，它必须拥有一个共享锁。
> - 在一个事务可以写一个对象之前，它必须有一个排他锁。
> - 多个事务可以在一个对象上拥有一个共享锁。
> - 只有一个事务可能对一个对象具有排他锁。
> - 如果对象o上只有事务t持有共享锁，则t可以将 其对o的锁升级为排他锁。

## 3.实现缓冲池中的获取/释放锁相关方法

- 概述

> 我们需要实现或修改下面的三个方法：
> 
> 1. getPage：增加在返回页之前阻塞并获取所需的锁。
> 2. unsafeReleasePage
> 3. holdsLock：确定页面是否已被事务锁定
- 锁结构

> 对于锁本身，我们可以参考MySQL中的锁结构进行设计
> 

### 3.1 实现思路——锁管理器

- 概述

> **我们可以设置一个类似于拦截器一样的管理器，当某个事务来申请对应页的锁，我们通过这个管理器就可得到关于这个页全部的锁状态信息，用来维护事务和锁**
> 

> 里面维护的状态就是对应页上所有的锁，这个锁肯定是事务给加的，所以锁与事务的关系也要进行映射
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab4%EF%BC%88%E7%AE%80%E5%8D%95%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%EF%BC%89/image%202.png)

- 根据上面共享锁与排它锁的规则，获取锁的流程图

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab4%EF%BC%88%E7%AE%80%E5%8D%95%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%EF%BC%89/image%203.png)

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab4%EF%BC%88%E7%AE%80%E5%8D%95%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%EF%BC%89/image%204.png)

- 代码

> 在代码中我们主要写四个方法
> 
> 1. 检查并获取锁：`acquireLock`
> 2. 释放指定事务的锁：`releaseLock`
> 3. 检查指定事务是否对当前页面加锁：`isLockable`
> 4. 事务结束后，释放该事务的所有锁：`cleanAllLocks`

==acquireLock==

```java
/**
         * 尝试获取锁
         *
         * @param pageId       获取那个页的锁
         * @param tid          那个事务要获取
         * @param requiredType 获取什么锁
         * @return
         * @throws TransactionAbortedException
         * @throws InterruptedException
         */
        public synchronized boolean acquireLock(PageId pageId, TransactionId tid, int requiredType) throws TransactionAbortedException, InterruptedException {
            //获取请求的锁类型
            final String lockType = requiredType == 0 ? "read" : "write";
            //获取当前线程
            final String curThread = Thread.currentThread().getName();
            //这就属于这个页面没有任何事务的锁
            if (lockMsg.get(pageId) == null) {
                PageLock pageLock = new PageLock(tid, requiredType);
                //记录当前事务在这个页上的锁
                ConcurrentHashMap<TransactionId, PageLock> pageLocks = new ConcurrentHashMap<>();
                pageLocks.put(tid, pageLock);
                lockMsg.put(pageId, pageLocks);//放到集合中
                return true;
            }

            //如果这个页面有锁
            ConcurrentHashMap<TransactionId, PageLock> pageLocks = lockMsg.get(pageId);

            //看看是不是属于当前事务的锁
            //如果没有当前事务的锁
            if (pageLocks.get(tid) == null) {
                //如果页面的锁大于1就说明全是读锁
                if (pageLocks.size() > 1) {
                    //判断请求锁的类型
                    if (requiredType == PageLock.SHARE) { //如果请求是读锁直接加锁
                        PageLock pageLock = new PageLock(tid, PageLock.SHARE);
                        pageLocks.put(tid, pageLock);
                        lockMsg.put(pageId, pageLocks);
                        return true;
                    }
                    //如果请求是写锁，等待释放
                    if (requiredType == PageLock.EXCLUSIVE) {
                        wait(25);   //等待
                        System.out.println(curThread + "正在等待页为" + pageId + "，当前事务" + tid + "获取的是写锁");
                        return false;
                    }
                }

                //如果等于1就说明是别的事务的写锁或读锁
                if (pageLocks.size() == 1) {
                    //我们得先判断这个锁是读锁还是写锁
                    PageLock curLock = null;
                    for (PageLock lock : pageLocks.values()) {
                        curLock = lock;
                    }
                    //如果是读锁
                    if(curLock.getType() == PageLock.SHARE){
                        //如果请求是读锁直接加锁
                        if (requiredType == PageLock.SHARE) {
                            PageLock pageLock = new PageLock(tid, PageLock.SHARE);
                            pageLocks.put(tid, pageLock);
                            lockMsg.put(pageId, pageLocks);
                            return true;
                        }
                        if (requiredType == PageLock.EXCLUSIVE){
                            wait(15);   //等待
                            System.out.println(curThread + "正在等待页为" + pageId + "，当前事务" + tid + "获取的是写锁");
                            return false;
                        }
                    }
                    //如果是写锁，那么无论你请求的是什么都给我等待
                    if(curLock.getType() == PageLock.EXCLUSIVE){
                        wait(15);   //等待
                        System.out.println(curThread + "正在等待页为" + pageId + "，当前事务" + tid + "获取的是写锁");
                        return false;
                    }
                }
            }
            //如果有当前事务的锁
            if(pageLocks.get(tid) != null){
                //当前事务的锁
                PageLock pageLock = pageLocks.get(tid);
                //那就判断当前事务拥有的锁
                //如果拥有的是读锁
                if(pageLock.getType() == PageLock.SHARE){
                    //查看请求的锁的类型
                    //如果请求的是读锁
                    if(requiredType == PageLock.SHARE){
                        return true;
                    }
                    //如果请求的是写锁
                    if(requiredType == PageLock.EXCLUSIVE){
                        //我们需要判断这个页面上是不是只有当前事务的锁
                        //这个就说明只有当前事务的锁，因为前提就是有当前事务的锁，如果锁的数量还是1
                        //那么肯定就只有当前事务的了
                        if(pageLocks.size() == 1){
                            //锁升级
                            pageLock.setType(PageLock.EXCLUSIVE);
                            pageLocks.put(tid, pageLock);
                            return true;
                        }
                        //说明有其他事务的锁，不进行操作，容易死锁
                        if(pageLocks.size() > 1){
                            System.out.println("当前有太多读锁，获取写锁失败");
                            throw new TransactionAbortedException();
                        }
                    }
                }
                //如果拥有的是写锁，就直接进行获取
                if(pageLock.getType() == PageLock.EXCLUSIVE){
                    return true;
                }
            }
            return false;
        }
```

==releaseLock==

```java
/**
         * 释放指定事务的锁
         * @param tid
         * @param pid
         * @return
         */
        public synchronized boolean releaseLock(TransactionId tid, PageId pid){
            if (isLockable(tid, pid)){
                ConcurrentHashMap<TransactionId,PageLock> pageLocks = lockMsg.get(pid);
                pageLocks.remove(tid);
                if (pageLocks.size() == 0){
                    lockMsg.remove(pid);
                }
                //唤醒等待释放的事务
                this.notifyAll();
                return true;
            }
            return false;
        }
```

==isLockable==

```java
/**
         * 检查指定事务是否对当前页面加锁
         * @param tid
         * @param pid
         * @return  返回false就代表这个页面没有锁或者没有当前事务的锁
         */
        public synchronized boolean isLockable(TransactionId tid, PageId pid){
            //获取当前页面的所有锁信息
            ConcurrentHashMap<TransactionId, PageLock> tempMap = lockMsg.get(pid);
            if(tempMap == null)
                return false;
            PageLock pageLock = tempMap.get(tid);
            if(pageLock == null)
                return false;
            return true;
        }
```

==cleanAllLocks==

```java
/**
         * 事务结束后，释放该事务的所有锁
         * @param tid
         */
        public synchronized void cleanAllLocks(TransactionId tid){
            for (PageId pageId : lockMsg.keySet()) {
                releaseLock(tid, pageId);
            }
        }
```

### 3.2 BufferPool#getPage以及相关方法

- 概述

> 我们要对这个方法进行重构，因为事务和锁的加入，在获取页时是需要获取锁的相关情况在进行下一步的；回顾两阶段锁：**事务在访问任何对象之前都应该获取该对象上的适当类型的锁，并且在事务提交之前不应该释放任何锁。**
> 
- 需要重构的部分

> 在获取页对页进行各种操作之前，就获取到锁，那么再整个事务期间都不需要因为别的任何操作符而去再次进行获取；获取锁的过程已经在上面详细的说过，这里就不在赘述
> 
- 注意

> 对于锁的释放时机一定要遵循二阶段锁协议。**但是，在其他情况下，在事务结束之前释放锁可能会很有用。例如，你可以在扫描页面以寻找空白位置之后，释放页面上的共用锁定（如下所述）。**
> 
- 事务请求锁类型的枚举类——`Permissions`

> 枚举类，有`READ_ONLY、 READ_WRITE`两个属性。当getPage()方法传入`READ_ONLY`时，表明该事务请求的是共享锁。传入`READ_WRITE`时，请求的是排它锁。
> 

```java
/**
 * 表示对关系文件的请求权限的类。具有两个静态对象 READ_ONLY 和 READ_WRITE 的私有构造函数，
 * 它们代表两个权限级别。
 */
public enum Permissions {
    READ_ONLY, READ_WRITE
}
```

- 死锁发生时

> 我们一般有两种解决方式：我们采用前者
> 
> - 超时等待（自旋一段时间）：**对每个事务设置一个获取锁的超时时间，如果在超时时间内获取不到锁，我们就认为可能发生了死锁，将该事务进行中断。**
> - 循环等待检测：**建立事务等待关系的等待图，当等待图出现了环时，说明有死锁发生，在加锁前就进行死锁检测，如果本次加锁请求会导致死锁，就终止该事务。**
- 代码

```java
//锁管理器
    private LockManger lockManger;

/**
     * 检索具有关联权限的指定页面。将获得一个锁，如果该锁被另一个事务持有，则可能会阻塞
     * <p>
     * 检索到的页面应在缓冲池中查找。如果存在，则应将其退回。如果不存在，则应将其添加到缓冲池并返回。
     * 如果缓冲池中空间不足，则应逐出一个页面并在其位置添加新页面。
     *
     * @param tid 请求页面的事务的 ID
     * @param pid 请求页面的 ID
     * @param perm 页面上请求的权限
     */
    public Page getPage(TransactionId tid, PageId pid, Permissions perm)
        throws TransactionAbortedException, DbException {
        //我们进行重构，先检查锁的各种情况
        int lockType;
        //检查请求锁的类型
        if(perm == Permissions.READ_ONLY){
            lockType = PageLock.SHARE;
        }else{
            lockType = PageLock.EXCLUSIVE;
        }
        //此时就开始进去倒计时（超时等待时间）
        long startGetLock = System.currentTimeMillis();
        boolean isAcquired = false; //默认是没抢到
        while (!isAcquired){    //如果抢到锁还未超过500ms，整个获取锁就成功
            try {
                isAcquired = lockManger.acquireLock(pid, tid, lockType);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            long endGetLock = System.currentTimeMillis();
            //进行超时等待
            if(endGetLock - startGetLock > 500){
                throw new TransactionAbortedException();
            }
        }
        /*-----------------本方法中，上面为lab4新添加。下面为lab3------------------------*/
        //缓冲池不存在该页
        if(!bufferPool.containsKey(pid)){
            //去硬盘中寻找该页的Catalog获取存放的DBFile
            DbFile databaseFile = Database.getCatalog().getDatabaseFile(pid.getTableId());
            //获取对应页
            Page page = databaseFile.readPage(pid);
            PageNode node = new PageNode(pid, page);
            //如果缓冲池没满
            if(numPages > bufferPool.size()){
                addToHead(node);
                bufferPool.put(pid, node);
                return node.page;
            }else{  //缓冲池满了触发LRU
                evictPage();
                addToHead(node);
                bufferPool.put(page.getId(), node);
                return page;
            }
        }else{  //如果存在则触发使用过的节点移动到表头
            PageNode node = bufferPool.get(pid);
            moveToHead(node);
            return node.page;
        }
    }

/**
     * 释放页面上的锁定。调用它是非常危险的，并且可能导致错误的行为。仔细想想谁需要调用它，
     * 为什么调用它，以及为什么他们会冒调用它的风险。
     *
     * @param tid 请求解锁的交易ID
     * @param pid 要解锁的页面ID
     */
    public  void unsafeReleasePage(TransactionId tid, PageId pid) {
        lockManger.releaseLock(tid, pid);
    }

/** 如果指定事务在指定页面上有锁，则返回 true */
    public boolean holdsLock(TransactionId tid, PageId p) {
        return lockManger.isLockable(tid, p);
    }
```

### 3.3 HeapFile#insertTupe

- 概述

> 表对应的实际操作类就是HeapFile，那么当添加元组时或添加页时都需要经过这个类，并且由Buffer中的进行页的获取。
> 
> - 那么我们在使用File的方法时，应该注意传递的请求参数，例如：insertTupe肯定传入的是排它锁
> - **同时我们有需要检查插入的页如果已经满的时候，因为你都已经直到满了也就是说你获取了这个页的锁，在新建页的时候你需要将获取到的满页的锁释放掉，就是上面我们需要注意的点所提到的。虽然不满足二阶段协议但是没有同步问题**
- 代码

> 实际上就加了一行代码
> 

```java
/**
     * 将tuple插入到HeapFile中的page中，如果HeapFile中的page都已经满了，
     * 则在HeapFile中创建一个新的page
     * @param tid 执行更新的事务
     * @param t 要添加的元组。应该更新这个元组以反映它现在存储在这个文件中。
     *
     */
    public List<Page> insertTuple(TransactionId tid, Tuple t)
            throws DbException, IOException, TransactionAbortedException {
        List<Page> pages = new ArrayList<>();
        for (int pageNo = 0; pageNo < numPages(); pageNo++) {
            PageId pageId = new HeapPageId(getId(), pageNo);
            HeapPage page = (HeapPage) Database.getBufferPool().getPage(tid, pageId, Permissions.READ_WRITE);
            if(page.getNumEmptySlots() != 0){
                page.insertTuple(t);
                pages.add(page);
                return pages;
            }else{
                //在lab4完善的地方，该page上没有空slot时，释放该page上的锁，
                // 避免影响其他事务的访问
                Database.getBufferPool().unsafeReleasePage(tid, pageId);
            }
        }

        //如果每一页都没有空槽那么就新建一页，使用缓冲流能加快IO速度
        BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(file, true));
        byte[] emptyPageData = HeapPage.createEmptyPageData();
        bos.write(emptyPageData);
        bos.close();

        //从新的一页开始写
        PageId pageId = new HeapPageId(getId(), numPages() - 1);
        HeapPage newPage = (HeapPage) Database.getBufferPool().getPage(tid, pageId, Permissions.READ_WRITE);
        newPage.insertTuple(t);
        pages.add(newPage);
        return pages;
    }
```

## 4.完善BufferPool中的evictPage()方法

- 概述

> 首先明确，这个方法是当缓冲池的页面数达到最大，只需置换页面时所调用的，他根据LRU把最不常用的页（链表尾部的节点丢弃），丢弃之前会检查是否为脏页，如果为脏页还需进行持久化
> 
- 需要完善的地方——`NOSTEAL`

> **因为我们之前的逻辑是没有考虑到事务的存在的，现在事务的加入我们需要重新考虑对于修改过的脏页处理细节，前文我们说要采取`NOSTEAL/FORCE` 的策略，而对于`NOSTEAL`来说正是需要我们实现的，这个策略规定当需要置换的页面为脏页（说明被修改过并处于某个事务中）时，要跳过脏页，置换掉不是脏页的page，即事务对page的修改只有在commit之后才会写入到磁盘**
> 

> 之所以这么做是因为脏页处于事务中可能还会被修改，并且如果不管事务直接进行持久化显然也是违反二阶段锁协议的
> 
- 注意

> 如果缓存中全部都死脏页那么抛出异常
> 
- 代码

```java
/**
     * 从缓冲池中丢弃一个页面。将页面刷新到磁盘以确保在磁盘上更新脏页。
     * 这里丢弃其实也要根据不同的置换策略去挑选页丢弃
     */
    private synchronized void evictPage() throws DbException {
        for (int i = 0; i < numPages; i++) {
            PageNode tail = delTail();
            Page evictPage = tail.page;
            //说明是脏页，不进行持久化
            if(evictPage.isDirty() != null){
                addToHead(tail);
            }else{  //不是脏页就直接删除也不用持久化
                PageId evictPageId = tail.pageId;
                discardPage(evictPageId);
                return;
            }
        }
        throw new DbException("所有页都是脏页");

    }
```

## 5.实现事务的功能

- 概述

> • 当事务提交时，将事务涉及的脏页写回磁盘，然后释放锁。
• 当事务回滚时，清理该事务涉及到的脏页，重新从磁盘中读取清理的page
> 
- 代码

> 我们主要实现那个带有两个参数的：第一个参数是事务id，第二个参数是提交还是回滚的标志位`（true提交；false回滚）`
> 

```java
/**
     * 释放与给定事务关联的所有锁。
     *
     * @param tid 请求解锁的交易ID
     */
    public void transactionComplete(TransactionId tid) {
        transactionComplete(tid, true);
    }

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

    /**
     * 事务回滚，将所有页面复原
     * @param tid
     */
    public synchronized void restorePages(TransactionId tid){
        //遍历所有页
        for (PageNode node : bufferPool.values()) {
            Page page = node.page;
            PageId pageId = node.pageId;
            //页面如果是脏页面就会返回修改自己的事务ID
            if(tid.equals(page.isDirty())){ //检查当前页面是不是被这个页面修改了
                int tableId = pageId.getTableId();
                DbFile table = Database.getCatalog().getDatabaseFile(tableId);
                //从磁盘中读取旧的页然后更新过来
                Page fromDisk = table.readPage(pageId);
                node.setPage(page);
                bufferPool.put(pageId, node);
                moveToHead(node);
            }
        }
    }
```
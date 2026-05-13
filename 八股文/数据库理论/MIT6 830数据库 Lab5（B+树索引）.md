# MIT6.830数据库 | Lab5（B+树索引）

type: Post
status: Published
date: 2022/09/05
summary: B+树索引
tags: 实践
category: 数据库

# Lab5

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

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image.png)

- DataBase类

> **Database 类提供对作为数据库全局状态的静态对象集合的访问。具体来说，这包括访问编目 (数据库中所有表的列表)、缓冲池 (当前驻留在内存中的数据库文件页的集合) 和日志文件的方法。**
> 

## 1.Lab5的任务总概

- 概述

> 在本实验中，您将实现一个B+树索引，用于高效查找和范围扫描。我们为您提供了实现树结构所需的所有低级代码。**您将实现搜索、拆分页面、在页面之间重新分配元组和合并页面。**
> 
> - 实现B+树的搜索，根据给定的key查找适当的页节点。
> - 实现内部节点、页节点的拆分，当页面中key的数量大于n-1时，对页面进行拆分。
> - 实现节点的重新分配，当删除key后如果页面中key的数量小于m/2 时，从其兄弟节点“窃取”一个key
> - 实现节点的合并，当删除key后如果页面中key的数量小于m/2 时，且兄弟节点也只有m/2个key，则将两个节点合并。

### 1.1 B+树的介绍

- 概述

> B+树是B-树的变体，也是一颗多路搜索树。一棵`n`阶的B+树主要有这些特点：
> 
> - 每个结点至多有n个子女;
> - 非根节点关键值个数范围：n/2 <= k <= n-1
> - 相邻叶子节点是通过指针连起来的，并且是关键字大小排序的。
- 结构以及特点

> 下图就是一个阶数为4（非叶子节点的最大间隔数）的B+树，**那么内部节点最多就是4-1个关键字（或者说内部结点最多有m个子树），阶数m同时限制了叶子结点最多存储m-1个记录。**
> 
> - B+树包含2种类型的结点：**①.内部结点（也称索引结点）和②.叶子结点**。根结点本身即可以是内部结点，也可以是叶子结点。根结点的关键字个数最少可以只有1个。**内部节点与其父节点的key值不能重复，页节点与其父节点的key值可以重复**
> - B+树与B树最大的不同是内部结点不保存数据，只用于索引，所有数据（或者说记录）都保存在叶子结点中。
> - **内部结点中的key都按照从小到大的顺序排列，对于内部结点中的一个key**
> 
> > 
> > 
> > - 如果这个内部节点的子节点是非叶子节点，那么左子节点中的所有key都小于它，右子节点中的key都大于它。
> > - 如果这个内部节点的子节点是叶子节点，左子节点中的所有key都小于等于它，右子节点中的key都大于等于它。叶子结点中的记录也按照key的大小排列
> - 每个叶子结点都存有相邻叶子结点的指针，叶子结点本身依关键字（看你创建索引的列）的大小自小而大顺序链接。
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%201.png)
> 
- 注意

> 本次实验中所有有关B+树相关规则的合法性校验全部在BTreeChecker中实现
> 

### 1.插入过程

- 注意

> 接下来的讲的兄弟节点指的是当前结点的左右节点，挑选一个符合条件的即可
> 
- 概述

> 流程图如下
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%202.png)

- 注意

> 分裂叶节点和分裂内节点的情况是不同的。
> 
> - 分裂叶节点时，节点中的key值复制到父节点中（即叶节点和内部节点可以有相同的值）
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%203.png)
> 
> - 分裂内部节点时，是将节点中的key值“挤到”父节点中（即内部节点之间的key值不能重复）
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%204.png)
> 

### 2.删除过程

- 图示

`Math.ceil(m/2)-1` ：叶子结点能容纳节点的最小个数

`m-1`：叶子结点能容纳节点的最大个数

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%205.png)

==叶子节点变化==

- 叶子节点不满足最小个数，兄弟节点有富余节点，进行分裂（借）操作时

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%206.png)

- 叶子节点不满足最小个数，兄弟节点没有富余节点，就进行合体

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%207.png)

==内部节点变化==

- 叶子节点不满足最小个数，兄弟节点有富余节点，进行分裂（借）操作时

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%208.png)

- 叶子节点不满足最小个数，兄弟节点有富余节点，进行合体操作时

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%209.png)

### 1.2 本实验的大致思路

- 思路

> B+ 树中的内部节点包含多个条目，每个条目都由一个键值和一个左子指针和一个右子指针组成。相邻的键共享一个子指针，因此包含键的内部节点`m 具有 m+1`个子指针。叶节点可以包含其他数据库文件中的数据条目或指向数据条目的指针。**为了简单起见，我们将实现一个 B+ 树，其中的叶页面实际上包含数据条目。相邻的叶页通过`左右同级指针`链接在一起，因此范围扫描只需要通过根节点和内部节点进行一次初始搜索，就可以找到第一个叶页。后续的叶页通过跟随右（或左）兄弟指针来找到。**
> 
- 友链

> 详细的可以跳转至这里进行MySQL中B+索引的学习[B+树索引](https://blog.csdn.net/weixin_49258262/article/details/126650911)
> 

## 2.实现B+树的搜索

- ==前排名词提示==

> 在正式进入实验之前，我们先理解一下各种名词，在实验中我们会常引入MySQL中各个页的叫法，以及页中每个元素的叫法；
> 
> - 在上面我们说的节点代表的是页，而页分为内部节点（目录页）和叶子节点（数据页）
> - 而内部节点中的entry（下面会提到）就是目录项
> - 叶子节点中都是由无数个元组构成（记录）
- `BTreeFile——insertTuple`方法的区别

> `BTreeFile. insertTuple()与 HeapFile.insertTuple()`的主要不同之处在于，**`BTreeFile. insertTuple()`可能会返回大量脏页，特别是在任何内部页被拆分的情况下。您可能还记得在以前的实验中，返回脏页集是为了防止缓冲池在脏页被刷新之前删除它们。**
> 

### 2.1 相关辅助类

- `BTreePageId`

> 这个类就类似于没有使用B+树存储的PageId类一样，标识了这个页是哪个表里的，这个表的那一页，页是什么类型的
> 
- `BTreeInternalPage`

> B+树的内部节点，里面标识着节点对应页槽的使用情况（当然内部节点的孩子还有可能是内部节点）；**左右孩子指针（保存的是子页的pageNo），保存着孩子节点的key**
> 
- `BTreeLeafPage`

> B+树的叶节点，代表一页。记录槽（存放元组的单位）的使用量，能存放多少元组；**页与页是用双向链表连接**，正好代表左右兄弟节点，**在叶子节点中是用左右兄弟节点的页号来表示的，0则没有对应兄弟**
> 
- `BTreeEntry`

> 内部节点中的entry，即对节点操作最小单位的外部封装。内部节点对key的查找、插入、删除、迭代，都是以entry为单位的。
> 
- 整体结构

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2010.png)

- `dirtyPages`

> **这个是一个map结构的缓存，相当于MySQL中的changeBuffer，现在这里找，再去缓冲池，再去磁盘的顺序**
> 

### 2.2 实现BTreeFile#findLeafPage()

- 概述

> 递归函数，在B+树中查找可能包含字段 f 的叶节点。它使用只读权限锁定叶节点路径上的所有内部节点，并使用权限perm锁定叶节点。**如果f为null，并不会到此结束，它将查找最左边的叶节点，用于迭代器。**
> 
- 图示

> 如果查找重复值6，那么应该返回左边的页
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2011.png)

- 代码

> 
> 
> - 我们分析一下`dirtyPages`，当创建新page或更改page中的数据、指针时，需要将其添加到`dirtyPages`中，时刻保证最新的修改能够被对应的事务读取到。其实就是脏页的缓存
> - 然后分析一下`getPages`方法，**这个方法首先就会遍历这个脏页列表，如果获取不到请求的页则再去从缓冲池获取页，并且如果请求的获取权限是读写，那么还会在得到页的时候缓存到脏页列表中，也为推测当前事务会对这个页进行修改。需要此方法以确保在多次访问相同页面时不会丢失页面更新。**

```java
/**
	 * 递归函数，查找并锁定 B+ 树中与可能包含关键字段 f 的最左侧页面相对应的叶子页面。
	 * 它以 READ_ONLY 权限锁定通往叶节点的路径上的所有内部节点，并以 perm 权限锁定叶节点。
	 *
	 * 如果 f 为 null，则查找最左侧的叶页——用于迭代器
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新脏页列表
	 * @param pid - 正在搜索的当前页面
	 * @param perm - 锁定叶子页面的权限
	 * @param f - 要搜索的字段
	 * @return 可能包含关键字段 f 的最左侧叶页
	 *
	 */
	private BTreeLeafPage findLeafPage(TransactionId tid, Map<PageId, Page> dirtyPages, BTreePageId pid, Permissions perm,
                                       Field f)
					throws DbException, TransactionAbortedException {
		int type = pid.pgcateg();	//获取当前页面的类型
		if(type == BTreePageId.LEAF){	//如果是叶子节点
			return (BTreeLeafPage) getPage(tid, dirtyPages, pid, perm);
		}
		//如果不是叶子节点，我们就要开始遍历内节点的左右孩子来寻找
		BTreeInternalPage internalPage = (BTreeInternalPage) getPage(tid, dirtyPages, pid, Permissions.READ_ONLY);
		//得到迭代器开始遍历
		Iterator<BTreeEntry> it = internalPage.iterator();
		BTreeEntry entry = null;
		while (it.hasNext()){
			entry = it.next();
			//查看可能包含字段f的叶节点
			//如果字段为空向左寻找
			if(f == null){
				return findLeafPage(tid, dirtyPages, entry.getLeftChild(), perm, f);
			}
			//如果当前寻找的key，大于等于字段f，那么我们应该向右寻找
			if(entry.getKey().compare(Op.GREATER_THAN_OR_EQ, f)){
				return findLeafPage(tid, dirtyPages, entry.getLeftChild(), perm, f);
			}
		}
		return findLeafPage(tid, dirtyPages, entry.getRightChild(), perm, f);
	}
```

## 3.实现内部节点、叶节点的拆分

- 概述

> 我们之所以要实现节点之间的拆分是因为，当插入元组的时候，为了保证元组保持有序并保持树的完整性，但是每个页的槽位数量有限，即使对应页的槽满了，我们也应该插入成功，这时请回想上面B+树的插入
> 
- 页分裂

> 这就是拆分节点的学名，在MySQL中叶子节点和非叶子节点（目录页）都会发生页分裂，也就对应这里的叶子节点和内节点。**每次叶子页面分裂会导致向父节点添加一个目录项，这个目录项的key值对应新分裂页面的第一个记录，有时父节点已经是满的了，所以会导致递归分裂，最终会得到一个新的根节点**
> 

### 3.1 实现BTreeFile#splitLeafPage

- 概述

> 在这个数据库Demo中我们规定，当叶子节点中记录达到最大容量时，如果记录在进行插入就会进行分裂，将其拆分成两个页节点。返回插入tuple所在的page
> 
- 图示—在复习一下叶子节点的分裂过程

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2012.png)

- 代码

> 注意循环中我们是先删除再添加的，因为如果反过来，新添加的元组它的数据库唯一标识`recordId`就会发生改变，然后再去删就找不到了
> 

```java
/**
	 * 拆分叶子页面为新元组腾出空间，并根据需要递归拆分父节点以容纳新条目。
	 * 新条目应具有与右侧页面中第一个元组的键字段匹配的键（键被“复制”），
	 * 以及指向拆分产生的两个叶页的子指针。根据需要更新兄弟指针和父指针。
	 * 返回应插入具有关键字段“field”的新元组的叶页。
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param page - 要拆分的叶页
	 * @param field - 拆分完成后要插入的元组的关键字段。有必要知道返回两个页面中的哪一个。
	 * @see #getParentWithEmptySlots(TransactionId, Map, BTreePageId, Field)
	 *
	 * @return 应该插入新元组的叶子页面
	 * @throws DbException
	 * @throws IOException
	 * @throws TransactionAbortedException
	 *
	 *
	 * 通过在现有页面的右侧添加一个新页面并将一半元组移动到新页面来拆分叶子页面。
	 * 将中间键向上复制到父页面，并根据需要递归拆分父页面以容纳新条目。
	 * getParentWithEmptySlots() 在这里很有用。不要忘记更新所有受影响叶页的兄弟指针。
	 * 返回应插入具有给定键字段的元组的页面。
	 */
	public BTreeLeafPage splitLeafPage(TransactionId tid, Map<PageId, Page> dirtyPages, BTreeLeafPage page, Field field)
			throws DbException, IOException, TransactionAbortedException {
		//进入到这个方法显然是要进行页分裂的
		//我们首先建立一个新的叶子节点
		BTreeLeafPage newRightPage = (BTreeLeafPage) getEmptyPage(tid, dirtyPages, BTreePageId.LEAF);
		//得到这个拆分页的全部元组数量
		int numTuples = page.getNumTuples();
		//我们倒着去遍历这个页的元组
		Iterator<Tuple> it = page.reverseIterator();
		//将后一半拆分过去
		for (int i = 0; i < numTuples / 2; i++) {
			Tuple next = it.next();
			page.deleteTuple(next);
			newRightPage.insertTuple(next);
		}

		//得到这个页的右兄弟节点，改变指针指向
		BTreePageId oldRightPageId = page.getRightSiblingId();
		BTreeLeafPage oldRightPage = null;
		if(oldRightPageId != null){
			oldRightPage = (BTreeLeafPage) getPage(tid, dirtyPages, oldRightPageId, Permissions.READ_ONLY);
		}

		//先更新拆分页面的原右兄弟节点的指向
		if(oldRightPage != null){
			oldRightPage.setLeftSiblingId(newRightPage.getId());
			newRightPage.setRightSiblingId(oldRightPageId);
			dirtyPages.put(oldRightPageId, oldRightPage);
		}

		//更新拆分页面右兄弟指针指向
		page.setRightSiblingId(newRightPage.getId());
		//更新新页面的左兄弟指针指向
		newRightPage.setLeftSiblingId(page.getId());
		//加入缓存
		dirtyPages.put(page.getId(), page);
		dirtyPages.put(newRightPage.getId(), newRightPage);

		//随后开始生成父节点的目录项
		BTreePageId parentId = page.getParentId();
		//这个方法就会帮助我们判断是否需要建立新的根节点
		//如果父节点也满了，帮我们实现拆分功能
		BTreeInternalPage parentPage = getParentWithEmptySlots(tid, dirtyPages, parentId, field);
		//获取新页面的第一个元组，并得到建立B+树索引的字段
		Field midField = newRightPage.iterator().next().getField(keyField);
		//建立新的内节点中的储存元素
		BTreeEntry entry = new BTreeEntry(midField, page.getId(), newRightPage.getId());
		//将entry加入到内节点中
		parentPage.insertEntry(entry);
		dirtyPages.put(parentId, parentPage);
		//将此此file中所有页面都指向parent
		updateParentPointers(tid, dirtyPages, parentPage);

		//判断插入field的所在页
		if(field.compare(Op.GREATER_THAN_OR_EQ, midField))
			//返回新建的页
			return newRightPage;
		//否则返回当前页
		return page;
	}
```

==细节之——getParentWithEmptySlots==

> 其中我们单独分析一下这个方法，这个方法主要帮我做了这么几件事
> 
> 1. 如果当前目录项节点只有自己一个，拆分出一个新的目录项节点就要创建一个新的顶级节点（就是记录这些目录项的目录项节点），又或者有很多目录项节点的顶级节点，这些顶级节点很多很多，又需要创建一个新的顶级节点的顶级节点，套娃懂吧，如果还是恍惚，建议跳转[B+树索引](https://blog.csdn.net/weixin_49258262/article/details/126650911)
> 2. 如果不需要创建顶级节点则获得到这个父节点
> 3. 然后查看里面还有空位没，没有就进行拆分，会调用我们稍后写的拆分目录项节点的方法`splitInternalPage`

```java
/**
	 * 封装让父页面准备好接受新条目的过程的方法。这可能意味着创建一个页面成为树的新根，
	 * 如果没有空槽，则拆分现有的父页面，或者简单地锁定并返回现有的父页面。
	 *
	 * @param tid - 事务id
	 * @param dirtypages - 应该用所有新的脏页更新的脏页列表
	 * @param parentId - 父母的 id。可能是内部页面或 RootPtr 页面
	 * @param field - 将插入的条目的键。如果必须拆分父级，则需要
	 * to accommodate the new entry
	 * @return 父页面，保证至少有一个空槽
	 * @see #splitInternalPage(TransactionId, Map, BTreeInternalPage, Field)
	 *
	 * @throws DbException
	 * @throws IOException
	 * @throws TransactionAbortedException
	 */
	private BTreeInternalPage getParentWithEmptySlots(TransactionId tid, Map<PageId, Page> dirtypages,
			BTreePageId parentId, Field field) throws DbException, IOException, TransactionAbortedException {

		BTreeInternalPage parent = null;

		// 如有必要，创建一个父节点，这将是树的新根
		if(parentId.pgcateg() == BTreePageId.ROOT_PTR) {
			parent = (BTreeInternalPage) getEmptyPage(tid, dirtypages, BTreePageId.INTERNAL);

			// 更新根指针
			BTreeRootPtrPage rootPtr = (BTreeRootPtrPage) getPage(tid, dirtypages,
					BTreeRootPtrPage.getId(tableid), Permissions.READ_WRITE);
			BTreePageId prevRootId = rootPtr.getRootId(); //覆盖前保存prev id。
			rootPtr.setRootId(parent.getId());

			// 将先前的根更新为现在指向这个新的根。
			BTreePage prevRootPage = (BTreePage)getPage(tid, dirtypages, prevRootId, Permissions.READ_WRITE);
			prevRootPage.setParentId(parent.getId());
		}
		else {
			// 锁定父页面
			parent = (BTreeInternalPage) getPage(tid, dirtypages, parentId,
					Permissions.READ_WRITE);
		}

		// 如果需要，拆分父级
		if(parent.getNumEmptySlots() == 0) {
			parent = splitInternalPage(tid, dirtypages, parent, field);
		}

		return parent;

	}
```

==细节之——updateParentPointers==

> 这个方法会把传入的父节点下的所有叶子节点指向自己
> 

```java
/**
	 * 更新给定页面的每个子页面的父指针，使其正确指向父页面
	 *
	 * @param tid - 事务id
	 * @param dirtypages - 应该用所有新的脏页更新的脏页列表
	 * @param page - 父页面
	 * @see #updateParentPointer(TransactionId, Map, BTreePageId, BTreePageId)
	 *
	 * @throws DbException
	 * @throws TransactionAbortedException
	 */
	private void updateParentPointers(TransactionId tid, Map<PageId, Page> dirtypages, BTreeInternalPage page)
			throws DbException, TransactionAbortedException{
		Iterator<BTreeEntry> it = page.iterator();
		BTreePageId pid = page.getId();
		BTreeEntry e = null;
		while(it.hasNext()) {
			e = it.next();
			updateParentPointer(tid, dirtypages, pid, e.getLeftChild());
		}
		if(e != null) {
			updateParentPointer(tid, dirtypages, pid, e.getRightChild());
		}
	}
```

### 3.2 实现BTreeFile#splitInternalPage

- 概述

> 如果父节点中key的数量到达了`n-1`，则会调用`splitInternalPage()`方法向上递归，总之最终会返回一个可以插入新key的内部节点。与叶子节点拆分的唯一区别就是分裂之后要将中间的key保存到顶级节点中去。
> 
- 图示-复习一下内部节点分裂的过程

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2013.png)

- 代码

> 其中使用的方法细节都在上面分析过了
> 

```java
/**
	 * 拆分内部页面为新条目腾出空间，并根据需要递归拆分其父页面以容纳新条目。
	 * 父项的新条目应具有与要拆分的原始内部页面中的中间键匹配的键（此键“向上推”到父项）。
	 * 新父条目的子指针应指向拆分产生的两个内部页面。根据需要更新父指针。
	 * 返回应插入具有关键字段“字段”的条目的内部页面
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param page - 要拆分的内部页面
	 * @param field - 拆分完成后要插入的条目的关键字段
	 *
	 * @see #getParentWithEmptySlots(TransactionId, Map, BTreePageId, Field)
	 * @see #updateParentPointers(TransactionId, Map, BTreeInternalPage)
	 *
	 * @return 应插入新条目的内部页面
	 * @throws DbException
	 * @throws IOException
	 * @throws TransactionAbortedException
	 *
	 * 通过在现有页面的右侧添加新页面并将一半条目移动到新页面来拆分内部页面。
	 * 将中间键向上推入父页面，并根据需要递归拆分父页面以容纳新条目。
	 * getParentWithEmtpySlots() 在这里很有用。不要忘记更新所有移动到新页面的孩子的父指针。
	 * updateParentPointers() 在这里很有用。返回应插入具有给定关键字段的条目的页面。
	 */
	public BTreeInternalPage splitInternalPage(TransactionId tid, Map<PageId, Page> dirtyPages,
			BTreeInternalPage page, Field field)
					throws DbException, IOException, TransactionAbortedException {
		//与拆分叶子节点同理
		BTreeInternalPage newRightInternalPage = (BTreeInternalPage) getEmptyPage(tid, dirtyPages, BTreePageId.INTERNAL);
		Iterator<BTreeEntry> it = page.reverseIterator();

		//将后一半都加到新的目录页中
		int numEntries = page.getNumEntries();
		for (int i = 0; i < numEntries / 2; i++) {
			BTreeEntry next = it.next();
			//将需要拆分的目录页的右半边移动过去
			//注意先后顺序，当entry被添加到新的目录页之后它的唯一标识被更改了，
			//再在page中删除，是找不到这个entry的
			//所以只能先删除再插入到新的Page中
			page.deleteKeyAndRightChild(next);
			newRightInternalPage.insertEntry(next);
		}

		//移动完以后，迭代器的下一个就是最后一个，在原拆分目录页中
		//作为原目录页和新目录页在顶级目录中的目录项
		BTreeEntry mid = it.next();
		page.deleteKeyAndRightChild(mid);
		//设置顶级节点中这个新的目录项左右孩子
		mid.setLeftChild(page.getId());
		mid.setRightChild(newRightInternalPage.getId());

		//获取顶级节点，前面分析过这个方法会帮助我们建立新的顶级节点或别的一些方法
		BTreeInternalPage parent = getParentWithEmptySlots(tid, dirtyPages, page.getParentId(), mid.getKey());
		parent.insertEntry(mid);

		//将修改过的节点放到缓存中
		dirtyPages.put(page.getId(), page);
		dirtyPages.put(parent.getId(), parent);
		dirtyPages.put(newRightInternalPage.getId(), newRightInternalPage);
		//逐层确认每个节点的父节点的指向
		updateParentPointers(tid, dirtyPages, parent);
		updateParentPointers(tid, dirtyPages, page);
		updateParentPointers(tid, dirtyPages, newRightInternalPage);

		//确定传入field页所处的位置，field在mid的右边和左边有不同的情况
		if(field.compare(Op.GREATER_THAN_OR_EQ, mid.getKey()))
			return newRightInternalPage;
		return page;
	}
```

## 4.实现节点的重新分配（目录项的更新）

- 概述

> **当删除`key`后如果页面中key的数量小于`m/2` 时，从其兄弟节点`“借”`一个key，从小于半满的叶页面中删除元组会导致该页面从其兄弟之一`借`元素或与其兄弟之一合并。合并后的数量至少大于m/2，这个其实就是页内目录项的更改**
> 

### 4.1 实现BTreeFile#stealFromLeafPage

- 概述

> 该方法就是内部实现这个借功能的方法，可以看到官方使用了`steal`这个词，译为窃取、偷
> 
- 图示

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2014.png)

- 代码

```java
/**
	 * 从兄弟节点那里窃取元组并将它们复制到给定页面，以便两个页面至少半满。更新父项的条目，
	 * 使键与右侧页面中第一个元组的键字段匹配。
	 *
	 * @param page - 不到半满的叶子页面
	 * @param sibling - 有元组的页兄弟节点
	 * @param parent - 两个叶子页面的父级
	 * @param entry - 父项中指向两个叶页的条目
	 * @param isRightSibling - 兄弟节点是否是不到半满的叶子页面的右兄弟节点
	 *
	 * @throws DbException
	 *
	 * 将一些元组从同级移动到页面，以使元组均匀分布。请务必更新相应的父条目。
	 */
	public void stealFromLeafPage(BTreeLeafPage page, BTreeLeafPage sibling,
			BTreeInternalPage parent, BTreeEntry entry, boolean isRightSibling) throws DbException {
		Iterator<Tuple> it;
		//如果是，咱们就正着遍历，也就是从小到大的顺序
		if(isRightSibling){
			it = sibling.iterator();
		}else{	//如果不是就正着遍历，从大到小的顺序
			it = sibling.reverseIterator();
		}

		//得到两个目标页的总体元组数
		int curNumTuples = page.getNumTuples();
		int siblingNumTuples = sibling.getNumTuples();
		//然后就是当不到半满的叶子页面达到总体的一半就好了
		int endNumTuples = (curNumTuples + siblingNumTuples) / 2;
		//逐个添加
		while (curNumTuples < endNumTuples){
			Tuple next = it.next();
			sibling.deleteTuple(next);
			page.insertTuple(next);
			curNumTuples++;
		}

		//同理拿到分界点，这个分界点左指向page，右指向spiltPage
		Tuple mid = it.next();
		//将分界点的key更新成左边最后一个索引字段的值或者右边第一个索引字段的值
		entry.setKey(mid.getField(keyField));
		//更新顶级节点的目录项
		parent.updateEntry(entry);
	}
```

### 4.2 实现BTreeFile#stealFromLeftInternalPage

- 概述

> **上面是针对于叶子节点中元组数量不够进行的更新目录项，而叶子节点上面的父节点中的entry也会发生不够的现象，那么我们也需要移动entry并更新父节点的父节点，即目录项的顶级节点**
> 
- 图示

> **注意我们可以看到这个方法只负责当右边目录页的目录项不够一半时去请求左边的目录页帮忙**
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2015.png)

- 代码

> **我们根据上面图来分析以下在循环遍历加entry之前需要构建next和mid，并把mid加入到当前页中**
> 
> 1. 拿到左边兄弟页的最后一个entry，即key为6的目录项
> 2. 构造新entry——mid，它的左孩子是目录项6的右孩子，它的右孩子是当前页第一个目录项entry的左孩子
> 3. 然后将新的节点加入到当前页中，可以看到传入的key值是父节点的key值，也就是8

> 为什么这个工作不在循环中做呢？原因很显而易见并不是简单的移动目录项这么简单，而是想要将目录页的顶级页的值进行下移而做的一步
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2016.png)

```java
/**
	 * 从左兄弟窃取条目并将它们复制到给定页面，以便两个页面至少半满。键可以被认为是在父条目中旋转，
	 * 因此父项中的原始键被“下拉”到右侧页面，而左侧页面中的最后一个键被“向上推”到父项。
	 * 根据需要更新父指针。
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param page - 不到半满的内部页面
	 * @param leftSibling - 有条目的左兄弟
	 * @param parent - 两个内部页面的父级
	 * @param parentEntry - 父项中指向两个内部页面的条目
	 * @see #updateParentPointers(TransactionId, Map, BTreeInternalPage)
	 *
	 * @throws DbException
	 * @throws TransactionAbortedException
	 *
	 * 将一些条目从左兄弟移动到页面，以使条目均匀分布。请务必更新相应的父条目。
	 * 确保更新已移动条目中所有子项的父指针。
	 */
	public void stealFromLeftInternalPage(TransactionId tid,
										  Map<PageId, Page> dirtyPages,
										  BTreeInternalPage page,
										  BTreeInternalPage leftSibling,
										  BTreeInternalPage parent,
										  BTreeEntry parentEntry)
			throws DbException, TransactionAbortedException {
		//如果是当前页面请求的左边页面帮忙，那么就需要按从大到小逆序的方向遍历目录项entry了
		Iterator<BTreeEntry> it = leftSibling.reverseIterator();
		//下面的操作跟叶子节点的操作差不多，获取entry的全部数量
		int curNumEntries = page.getNumEntries();
		int siblingEntriesNum = leftSibling.getNumEntries();
		int endNumEntries = (curNumEntries + siblingEntriesNum) / 2;

		//这里就稍显不同了，我们首先拿到了左边页面的最后一个entry
		BTreeEntry next = it.next();
		//然后构造了一个新的entry，左孩子是上面entry的右孩子
		//右孩子是当前页面第一个entry的左孩子
		BTreeEntry mid = new BTreeEntry(parentEntry.getKey(), next.getRightChild(), page.iterator().next().getLeftChild());
		//然后加入到当前的页中
		page.insertEntry(mid);
		curNumEntries++;

		//然后开始逐个遍历entry直到两个目录页的数量一样
		while (curNumEntries < endNumEntries){
			//这里删除左边页面的最后一个entry的右孩子指向，一个一个指向当前页
			//左孩子就会变成下一个entry的右孩子
			leftSibling.deleteKeyAndRightChild(next);
			//recordld用于查找要删除的键和子指针。插入一个条目也只会插入一个键和一个子指针
			// (除非它是第一个条目)，因此BTreeInternalPage.insertEntry()检查所提供条目
			// 中的一个子指针是否与页面上现有的子指针重叠，并且在该位置插入条目将保持键的排序
			page.insertEntry(next);
			curNumEntries++;
			next = it.next();
		}

		//然后删除分界点并将父节点中的key设置成这个分界点的key
		//记住是删除右孩子，因为这个移动下去，下面存在的目录项的右孩子是有的，这个复用就可
		leftSibling.deleteKeyAndRightChild(next);
		parentEntry.setKey(next.getKey());
		//在其指定的位置更新条目的键和或子指针，因为entry这个类中的只是引用那些key、左右孩子的指针
		//如果要实际更改底层页面就要调用updateEntry方法
		parent.updateEntry(parentEntry);

		//更新缓存
		dirtyPages.put(page.getId(), page);
		dirtyPages.put(leftSibling.getId(), leftSibling);
		dirtyPages.put(parent.getId(), parent);

		//更新当前页面下的所有子节点指向
		updateParentPointers(tid, dirtyPages, page);
	}
```

==细节之——BTreeInternalPage#deleteKeyAndRight(left)Child==

> 这个方法实际上就会调用`deleteEntry()`方法，对于是删除左边的还是右边的通过一个标志位判断
> 
> 1. 首先获取要删除entry的唯一id，然后合法性判断
> 2. 如果删除的是右边，标识位为true，随后会进入markSlotUsed，这个方法会找到这个entry所在的位置，通过得到最后一个元组的位置然后用位运算得到右孩子然后抹除
> 3. 如果删除的是左边，标识位为false，会从这个entry负责的最后一个元组开始向前遍历，检查每个槽是不是空的，槽位为空就会逐个倒序把元组向前移，移一个删一个
> 4. 左或右孩子处理好，最后删除这个entry，将id抹除

```java
/**
	 * 从页面中删除指定的条目（键 + 1 个子指针）。 recordId 用于查找指定条目，因此不能为空。
	 * 删除后，该条目的recordId应设置为null，以反映它不再存储在任何页面上。
	 * @throws DbException if this entry is not on this page, or entry slot is
	 *         already empty.
	 * @param e 要删除的条目
	 * @param deleteRightChild - 如果为真，则删除右孩子。否则删除左孩子
	 */
	private void deleteEntry(BTreeEntry e, boolean deleteRightChild) throws DbException {
		RecordId rid = e.getRecordId();
		if(rid == null)
			throw new DbException("试图删除带有空删除的条目");
		if((rid.getPageId().getPageNumber() != pid.getPageNumber()) || (rid.getPageId().getTableId() != pid.getTableId()))
			throw new DbException("试图删除无效页面或表格上的条目");
		if (!isSlotUsed(rid.getTupleNumber()))
			throw new DbException("试图删除空条目");
		if(deleteRightChild) {
			markSlotUsed(rid.getTupleNumber(), false);
		}
		else {
			for(int i = rid.getTupleNumber() - 1; i >= 0; i--) {
				if(isSlotUsed(i)) {
					children[i] = children[rid.getTupleNumber()];
					markSlotUsed(rid.getTupleNumber(), false);
					break;
				}
			}
		}
		e.setRecordId(null);
	}
```

### 4.3 实现BTreeFile#stealFromRightInternalPage

- 概述

> 是上面那个方法的反向，这次移动的兄弟节点变成了右边
> 
- 图示

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2017.png)

- 代码

> 细节就不分析了，全是上面方法的镜像
> 

```java
/**
	 * 从右兄弟窃取条目并将它们复制到给定页面，以便两个页面至少半满。键可以被认为是在父条目中旋转，
	 * 因此父项中的原始键被“拉下”到左侧页面，而右侧页面中的最后一个键被“向上推”到父项。
	 * 根据需要更新父指针。
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param page - 不到半满的内部页面
	 * @param rightSibling - 有条目的右兄弟
	 * @param parent - 两个内部页面的父级
	 * @param parentEntry - 父项中指向两个内部页面的条目
	 * @see #updateParentPointers(TransactionId, Map, BTreeInternalPage)
	 *
	 * @throws DbException
	 * @throws TransactionAbortedException
	 *
	 * 将一些条目从右兄弟移动到页面，以使条目均匀分布。请务必更新相应的父条目。
	 * 确保更新已移动条目中所有子项的父指针。
	 */
	public void stealFromRightInternalPage(TransactionId tid,
										   Map<PageId, Page> dirtyPages,
										   BTreeInternalPage page,
										   BTreeInternalPage rightSibling,
										   BTreeInternalPage parent,
										   BTreeEntry parentEntry)
			throws DbException, TransactionAbortedException {
		//由此这次是有兄弟，那么就需要正序遍历啊从小到大
		Iterator<BTreeEntry> it = rightSibling.iterator();
		int curNumEntries = page.getNumEntries();
		int rightNumEntries = rightSibling.getNumEntries();
		int endNumEntries = (curNumEntries + rightNumEntries) / 2;

		BTreeEntry next = it.next();
		BTreeEntry mid = new BTreeEntry(parentEntry.getKey(), page.reverseIterator().next().getRightChild(), next.getLeftChild());
		page.insertEntry(mid);
		curNumEntries++;

		while (curNumEntries < endNumEntries){
			rightSibling.deleteKeyAndLeftChild(next);
			page.insertEntry(next);
			curNumEntries++;
			next = it.next();
		}

		rightSibling.deleteKeyAndLeftChild(next);
		parentEntry.setKey(next.getKey());
		parent.updateEntry(parentEntry);

		dirtyPages.put(page.getId(), page);
		dirtyPages.put(rightSibling.getId(), rightSibling);
		dirtyPages.put(parent.getId(), parent);
		updateParentPointers(tid, dirtyPages, page);
	}
```

## 5.实现节点的合并

- 概述

> 当删除key后如果页面中key的数量小于m/2 时，且兄弟节点也只有m/2个key，则将两个节点合并，并从父级中删除指向两个page的entry
> 

### 5.1 实现BTreeFile#mergeLeafPages

- 概述

> 我们先处理叶子节点的合并工作
> 
- 图示

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2018.png)

- 代码

> **没什么值得说的，就是在迭代删除右页，添加左页时，一定要先删除再添加。因为如果你先添加对于tuple的唯一id就会被改变，在deleteEntry方法中不能正确的找到该元组对应的页了**
> 

```java
/**
	 * 通过将所有元组从右页移动到左页来合并两个叶页。从父级中删除对应的键和右子指针，
	 * 并递归处理父级低于最小占用率的情况。根据需要更新同级指针，并使正确的页面可供重用。
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param leftPage - 左叶页
	 * @param rightPage - 右叶页
	 * @param parent - 两个页面的父级
	 * @param parentEntry - 对应leftPage和rightPage的parent中的entry
	 * @see #deleteParentEntry(TransactionId, Map, BTreePage, BTreeInternalPage, BTreeEntry)
	 *
	 * @throws DbException
	 * @throws IOException
	 * @throws TransactionAbortedException
	 *
	 * 将所有元组从右页移动到左页，更新兄弟指针，并使右页可供重用。
	 * 删除与正在合并的两个页面对应的父项中的条目 - deleteParentEntry() 将在这里有用
	 */
	public void mergeLeafPages(TransactionId tid, Map<PageId, Page> dirtyPages,
							   BTreeLeafPage leftPage, BTreeLeafPage rightPage,
							   BTreeInternalPage parent, BTreeEntry parentEntry)
					throws DbException, IOException, TransactionAbortedException {
		//先把右边页全部加到左边去
		Iterator<Tuple> tit = rightPage.iterator();
		while (tit.hasNext()) {
			Tuple tuple = tit.next();
			rightPage.deleteTuple(tuple);
			leftPage.insertTuple(tuple);
		}

		//如果合并的右子页不是最右（后）的子叶，那么还需要更新指针
		//获取右页的右子页id
		BTreePageId rightSiblingId = rightPage.getRightSiblingId();
		if(rightSiblingId == null)
			//没有就设置成null，左页变为最后一页
			leftPage.setRightSiblingId(null);
		else{
			leftPage.setRightSiblingId(rightSiblingId);
			//得到这个右页的右子页
			BTreeLeafPage newRightPage = (BTreeLeafPage) getPage(tid, dirtyPages, rightSiblingId, Permissions.READ_WRITE);
			//设置指向
			newRightPage.setLeftSiblingId(leftPage.getId());
		}

		//清空右页，就是将其header数组清空
		setEmptyPage(tid, dirtyPages, rightPage.pid.getPageNumber());

		//删除左页和右页父节点的对应entry
		deleteParentEntry(tid, dirtyPages, leftPage, parent, parentEntry);

		//更新缓存
		dirtyPages.put(leftPage.getId(), leftPage);
		dirtyPages.put(parent.getId(), parent);
	}
```

### 5.2 实现BTreeFile#mergeInternalPages

- 概述

> 这里就是跟叶子页合并一个道理，当目录页中的目录项不够时，那么就会触发合并
> 
- 图示

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab5%EF%BC%88B+%E6%A0%91%E7%B4%A2%E5%BC%95%EF%BC%89/image%2019.png)

- 代码

> 注意要先处理顶级节点的目录项，对比上面就可以知道，因为目录页之间的关键字是不可以重复的
> 

```java
/**
	 * 通过将所有条目从右侧页面移动到左侧页面并从父条目“下拉”相应的键来合并两个内部页面。
	 * 从父级中删除对应的键和右子指针，并递归处理父级低于最小占用率的情况。根据需要更新父指针，
	 * 并使正确的页面可供重用。
	 *
	 * @param tid - 事务id
	 * @param dirtyPages - 应该用所有新的脏页更新的脏页列表
	 * @param leftPage - 左目录页
	 * @param rightPage - 右目录页
	 * @param parent - 目录页的顶级页
	 * @param parentEntry - 对应leftPage和rightPage的parent中的entry
	 * @see #deleteParentEntry(TransactionId, Map, BTreePage, BTreeInternalPage, BTreeEntry)
	 * @see #updateParentPointers(TransactionId, Map, BTreeInternalPage)
	 *
	 * @throws DbException
	 * @throws IOException
	 * @throws TransactionAbortedException
	 *
	 * 将所有条目从右侧页面移动到左侧页面，更新被移动条目中子项的父指针，
	 * 并使右侧页面可供重用删除父中与正在合并的两个页面对应的条目-
	 * deleteParentEntry() 在这里很有用
	 */
	public void mergeInternalPages(TransactionId tid, Map<PageId, Page> dirtyPages,
								   BTreeInternalPage leftPage,
								   BTreeInternalPage rightPage,
								   BTreeInternalPage parent,
								   BTreeEntry parentEntry)
					throws DbException, IOException, TransactionAbortedException {
		//新建一个左孩子是左页的倒数第一个entry的右孩子
		//右孩子是右页第一个entry的左孩子
		//看图很清晰要把顶级节点的父节点变成当前左页的一份子
		BTreeEntry mid = new BTreeEntry(parentEntry.getKey(),
				leftPage.reverseIterator().next().getRightChild(),
				rightPage.iterator().next().getLeftChild());
		leftPage.insertEntry(mid);
		//然后开始遍历右页加入到左页
		Iterator<BTreeEntry> readyToLeftIt = rightPage.iterator();
		while (readyToLeftIt.hasNext()){
			BTreeEntry entry = readyToLeftIt.next();
			//这里我们只删这个entry的左孩子
			rightPage.deleteKeyAndLeftChild(entry);
			leftPage.insertEntry(entry);
		}
		//更新父节点下的所有节点指向
		updateParentPointers(tid, dirtyPages, leftPage);

		//将左页清空
		setEmptyPage(tid, dirtyPages, rightPage.getId().getPageNumber());
		//删除mid保存的entry
		deleteParentEntry(tid, dirtyPages,leftPage, parent, parentEntry);

		dirtyPages.put(leftPage.getId(), leftPage);
		dirtyPages.put(parent.getId(), parent);
	}
```

### 5.3 集成测试——BTreeTest

- 概述

> 编写到这里就可以测试了，lab5中最难的测试就是这个了，楼主这套代码并没有成功，在细节和边界处理上稍加火候
> 

> 这里有一套全部编写完成的代码，但是能不能通过楼主也没有测试
[全部lab](https://github.com/happyer/simpledb/tree/master/lab6)
> 

## 6.额外测试——索引中页的反向遍历

- 概述

> 系统已经实现了正向遍历BTreeScan，而我们要实现BTreeReverseScan
> 
- 步骤

> 增加反向遍历寻找叶子节点方法——`BTreeFile#findLeafPageReverse`
> 

```java
/**
	 * 反向寻找页
	 */
	private BTreeLeafPage findLeafPageReverse(TransactionId tid,
									   Map<PageId, Page> dirtyPages,
									   BTreePageId pid, Permissions perm,
									   Field f)
			throws DbException, TransactionAbortedException {
		int type = pid.pgcateg();	//获取当前页面的类型
		if(type == BTreePageId.LEAF){	//如果是叶子节点
			return (BTreeLeafPage) getPage(tid, dirtyPages, pid, perm);
		}
		//如果不是叶子节点，我们就要开始遍历内节点的左右孩子来寻找
		BTreeInternalPage internalPage = (BTreeInternalPage) getPage(tid, dirtyPages, pid, Permissions.READ_ONLY);
		//得到迭代器开始遍历
		Iterator<BTreeEntry> it = internalPage.reverseIterator();
		BTreeEntry entry = null;
		while (it.hasNext()){
			entry = it.next();
			//查看可能包含字段f的叶节点
			//如果字段为空向左寻找
			if(f == null){
				return findLeafPage(tid, dirtyPages, entry.getRightChild(), perm, f);
			}
			//如果当前寻找的key，小于等于字段f，即判断f的所在页，那么我们应该向左寻找
			if(entry.getKey().compare(Op.LESS_THAN_OR_EQ, f)){
				return findLeafPage(tid, dirtyPages, entry.getRightChild(), perm, f);
			}
		}
		return findLeafPage(tid, dirtyPages, entry.getLeftChild(), perm, f);
	}
	/**
	 * 没有dirtyPages HashMap时查找叶子页的便捷方法。由 BTreeFile 迭代器使用。
	 * @see #findLeafPage(TransactionId, Map, BTreePageId, Permissions, Field)
	 *
	 * @param tid - the transaction id
	 * @param pid - the current page being searched
	 * @param f - the field to search for
	 * @param forwardOrReverse - 是正向去寻找页面还是反向，true为正向，false为反向
	 * @return 可能包含关键字段 f 的最左侧叶页
	 *
	 */
	BTreeLeafPage findLeafPage(TransactionId tid, BTreePageId pid,
                               Field f, boolean forwardOrReverse)
					throws DbException, TransactionAbortedException {
		if(forwardOrReverse)
			return findLeafPage(tid, new HashMap<>(), pid, Permissions.READ_ONLY, f);
		else
			return findLeafPageReverse(tid, new HashMap<>(), pid, Permissions.READ_ONLY, f);
	}
```

> 增加表的反向迭代器类——`BTreeFile#BTreeFileReverseIterator.class`
> 

```java
/**
 * 为 BTreeFile 上的元组实现 Java 反向迭代器的帮助类
 */
class BTreeFileReverseIterator extends AbstractDbFileIterator {

	Iterator<Tuple> it = null;
	//当前遍历的页
	BTreeLeafPage curP = null;

	final TransactionId tid;
	final BTreeFile f;

	/**
	 * 此迭代器的构造函数
	 * @param f - 包含元组的 BTreeFile
	 * @param tid - 事务id
	 */
	public BTreeFileReverseIterator(BTreeFile f, TransactionId tid) {
		this.f = f;
		this.tid = tid;
	}

	/**
	 * 通过在倒数第一个叶子页面上获取一个迭代器来打开这个迭代器
	 */
	public void open() throws DbException, TransactionAbortedException {
		BTreeRootPtrPage rootPtr = (BTreeRootPtrPage) Database.getBufferPool().getPage(
				tid, BTreeRootPtrPage.getId(f.getId()), Permissions.READ_ONLY);
		BTreePageId root = rootPtr.getRootId();
		curP = f.findLeafPage(tid, root, null, false);
		it = curP.reverseIterator();
	}

	/**
	 * 如果它有更多元组，则从当前页面读取下一个元组，或者通过跟随右兄弟指针从下一页读取下一个元组。
	 *
	 * @return 下一个元组，如果不存在则为 null
	 */
	@Override
	protected Tuple readNext() throws TransactionAbortedException, DbException {
		if (it != null && !it.hasNext())
			it = null;

		while (it == null && curP != null) {
			BTreePageId nextp = curP.getLeftSiblingId();
			if(nextp == null) {
				curP = null;
			}
			else {
				curP = (BTreeLeafPage) Database.getBufferPool().getPage(tid,
						nextp, Permissions.READ_ONLY);
				it = curP.iterator();
				if (!it.hasNext())
					it = null;
			}
		}

		if (it == null)
			return null;
		return it.next();
	}

	/**
	 * 将此迭代器倒回到元组的开头
	 */
	public void rewind() throws DbException, TransactionAbortedException {
		close();
		open();
	}

	/**
	 * 关闭迭代器
	 */
	public void close() {
		super.close();
		it = null;
		curP = null;
	}
}

/**
	 * 按排序顺序获取此 B+ 树文件中所有元组的迭代器。此方法将在文件的受影响页面上获取读锁，并且可能会阻塞，直到可以获取锁为止。
	 *
	 * @param tid - 事务id
	 * @return 此文件中所有元组的迭代器
	 */
	public DbFileIterator reverseIterator(TransactionId tid) {
		return new BTreeFileReverseIterator(this, tid);
	}
```

> 编写扫描器——`BTreeReverseScan`
> 

```java
/**
 * @author lhj
 * @create 2022/9/8 15:43
 * 您可以使用BTreeScan作为起点，但您可能需要在 BTreeFile中实现一个反向迭代器。
 * 您还可能需要实现一个单独的BTreeFile.findLeafPage()版本。我们在BTreeLeafPage 和
 * BTreeInternalPage上提供了反向迭代器，你可能会觉得它们很有用。
 * 您还应该编写代码来测试您的实现是否正确工作。BTreeScanTest是一个寻找想法的好地方。
 */
public class BTreeReverseScan implements OpIterator {
    private static final long serialVersionUID = 1L;

    //标志此迭代器是否被打开
    private boolean isOpen = false;
    //使用这个扫描器时的事务id
    private final TransactionId tid;
    //扫描到的每个元组信息
    private TupleDesc myTd;
    //是否有谓词
    private IndexPredicate iPred = null;
    //这个表每个页的迭代器
    private transient DbFileIterator it;
    //表的名字
    private String tableName;
    //表的别名
    private String alias;

    /**
     * 作为指定事务的一部分，在指定表上创建 B+ 树扫描。
     *
     * @param tid 此扫描作为其中一部分运行的事务。
     * @param tableId 要扫描的表。
     * @param tableAlias 此表的别名（解析器需要）；返回的 tupleDesc 应该有名称为 tableAlias
     *                      .fieldName 的字段（注意：这个类不负责处理 tableAlias 或 fieldName
     *                      为空的情况。如果它们不应该崩溃，但结果名称可以是 null.fieldName，
     *                      tableAlias .null 或 null.null）。
     * @param iPred 要匹配的索引谓词。如果为 null，则扫描将按排序顺序返回所有元组
     */
    public BTreeReverseScan(TransactionId tid, int tableId, String tableAlias, IndexPredicate iPred) {
        this.tid = tid;
        this.iPred = iPred;
        reset(tableId,tableAlias);
    }

    /**
     * @return 返回操作员扫描的表的表名。这应该是数据库目录中表的实际名称
     * */
    public String getTableName() {
        return this.tableName;
    }

    /**
     * @return 返回此运算符扫描的表的别名。
     * */
    public String getAlias()
    {
        return this.alias;
    }

    /**
     * 重置此运算符的 tableId 和 tableAlias。
     * @param tableId 要扫描的表。
     * @param tableAlias 表的别名
     */
    private void reset(int tableId, String tableAlias) {
        //先将此迭代器关闭，不可用
        isOpen = false;
        this.alias = tableAlias;
        this.tableName = Database.getCatalog().getTableName(tableId);
        //看有没有谓词
        if(iPred == null){
            it = ((BTreeFile) Database.getCatalog().getDatabaseFile(tableId)).reverseIterator(tid);
        }else { //如果有谓词，我们就会先将元组过滤一遍
            it = ((BTreeFile) Database.getCatalog().getDatabaseFile(tableId)).indexIterator(tid, iPred);
        }

        //获得传入元组的字段名和字段类型
        myTd = Database.getCatalog().getTupleDesc(tableId);
        String[] newNames = new String[myTd.numFields()];
        Type[] newTypes = new Type[myTd.numFields()];

        for (int i = 0; i < myTd.numFields(); i++) {
            String name = myTd.getFieldName(i);
            Type type = myTd.getFieldType(i);

            //我们重构一个表的字段名
            newNames[i] = tableAlias + "." + name;
            newTypes[i] = type;
        }
    }

    /**
     * 从底层 BTreeFile 返回带有字段名称的 TupleDesc，前缀为来自构造函数的 tableAlias 字符串。
     * 当连接包含同名字段的表时，此前缀非常有用。
     *
     * @return TupleDesc 具有来自底层 BTreeFile 的字段名称，
     * 					前缀为来自构造函数的 tableAlias 字符串。
     */
    public TupleDesc getTupleDesc() {
        return myTd;
    }

    public BTreeReverseScan(TransactionId tid, int tableId, IndexPredicate iPred) {
        this(tid, tableId, Database.getCatalog().getTableName(tableId), iPred);
    }
    @Override
    public void open() throws DbException, TransactionAbortedException {
        if (isOpen)
            throw new DbException("重复在一个迭代器中open");

        it.open();
        isOpen = true;
    }

    @Override
    public boolean hasNext() throws DbException, TransactionAbortedException {
        if (!isOpen)
            throw new IllegalStateException("迭代器关闭");
        return it.hasNext();
    }

    @Override
    public Tuple next() throws DbException, TransactionAbortedException, NoSuchElementException {
        if (!isOpen)
            throw new IllegalStateException("迭代器关闭");
        return it.next();
    }

    @Override
    public void rewind() throws DbException, TransactionAbortedException {
        close();
        open();
    }

    @Override
    public void close() {
        it.close();
        isOpen = false;
    }
}
```

- 关于编写测试类

> 博主并没有实现，请读者自行完成
>
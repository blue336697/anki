# 表锁、意向锁与 AUTO-INC 锁

## 结构定位
Q: InnoDB IS/IX 意向锁解决什么问题？
A:
- 事务给行加 S/X 锁前，先在表上取得 IS/IX，声明自己将或已经持有该表某些行锁。
- 表级 S/X 请求只需检查表锁队列的意向模式，不必扫描全表每条记录锁。
- IS 与 IX 彼此兼容，IX 与表 S/X 的兼容性不同；意向锁不会阻止其他事务锁不同记录。
- 它是多粒度锁协议，不是“意向以后可能加锁但当前没锁”的业务预约。

## 锁模式
Q: 表级 S、X、IS、IX 和 AUTO-INC 锁有什么核心差异？
A:
- 表 S 允许读表并阻止表 X，表 X 排斥其他多数表锁；普通 InnoDB DML主要依靠 IS/IX+记录锁。
- AUTO-INC 是为批量/不确定行数插入分配连续自增值的特殊表级机制，行为受 `innodb_autoinc_lock_mode`。
- mode 2 interleaved 并发最好但不同语句的值可交错；复制安全需结合 ROW binlog 等条件。
- MDL 属于 server 元数据锁，与这些 InnoDB table locks 是另一套系统。

## 加锁链
Q: `UPDATE t SET ... WHERE id=1` 为什么先出现 IX 再出现记录 X 锁？
A:
1. Server 打开表并取得相应 MDL。
2. InnoDB 事务在表上申请 IX，声明会修改记录。
3. 通过索引定位 id=1，对目标索引记录申请 X/record lock。
4. 提交时记录锁与表意向锁一并释放；MDL 的释放点遵循 server 事务/语句边界。

## 并发边界
Q: 意向锁会不会导致“一个 UPDATE 锁整张表”？
A:
- IX 只是表级标记，与其他 IX 兼容，多个事务可并发更新不同记录。
- 真正扩大锁范围的常见原因是缺索引扫描、范围 next-key、显式 LOCK TABLES 或 DDL MDL。
- 外键检查和唯一检查也可能锁其他索引记录/间隙。
- 应看 data_locks 的 INDEX_NAME/LOCK_DATA 和扫描计划，而不是看到 TABLE/IX 就判断表锁死。

## 验证与实践
Q: 自增插入出现争用时怎样分析？
A:
- 看 Performance Schema mutex/lock waits、语句类型和 `innodb_autoinc_lock_mode`，区分 auto-inc 分配与右侧 B-tree/redo 瓶颈。
- `INSERT ... SELECT` 等无法预知行数的语句与单行 INSERT 行为不同。
- 修改 lock mode 前核对 binlog format、复制确定性和是否依赖连续值。
- 自增值出现空洞是回滚、预分配和并发的正常结果，不能用 MAX(id) 推断精确行数或提交顺序。

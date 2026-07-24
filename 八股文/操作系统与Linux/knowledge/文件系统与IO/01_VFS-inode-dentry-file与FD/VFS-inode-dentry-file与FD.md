# VFS、inode、dentry、file 与文件描述符

> 基线：路径名、目录项、inode、打开文件对象和整数 fd 是不同层次。Linux VFS 用统一对象模型适配 ext4、XFS、tmpfs、procfs 等文件系统。

## 01-VFS
Q: VFS 解决什么问题？
A:
- VFS 在系统调用和具体文件系统之间提供统一接口，使 open/read/write/stat 等不依赖 ext4、XFS 或网络文件系统细节。
- 具体文件系统注册 super_operations、inode_operations、file_operations 等回调实现自身语义。
- VFS 还统一管理 mount、路径解析、dcache、权限和 page cache 关联。
- 它不是磁盘上的一个文件系统格式，而是内核内存中的抽象与分派层。

## 02-superblock
Q: `super_block` 表达什么？
A:
- 它代表一个已挂载文件系统实例，关联文件系统类型、块设备/后备对象、根 dentry、块大小、状态和操作表。
- 同一磁盘文件系统可通过不同 mount 视图出现，mount 对象与 superblock 不应混为一谈。
- tmpfs、procfs 等无传统磁盘块设备的文件系统也有 VFS superblock 实例。
- 卸载需要确保引用和活动对象满足条件，不能仅因目录看起来空就释放。

## 03-inode
Q: inode 保存什么，为什么不保存文件名？
A:
- inode 表示文件系统中的一个对象，保存类型、权限、所有者、大小、时间、链接计数、数据块映射和操作方法。
- 文件名属于父目录中的目录项，是“名字 -> inode”的映射；同一 inode 可有多个硬链接名称。
- VFS inode 是内存对象，磁盘 inode/元数据格式由具体文件系统实现，缓存对象可被回收后重新读入。
- 删除一个名称只减少目录项和链接计数，不必立即销毁仍被打开的 inode。

## 04-dentry
Q: dentry 和 dcache 在路径查找中做什么？
A:
- dentry 表示某个父目录下名字与 inode 的关联，也可以是记录“不存在”的 negative dentry。
- dcache 缓存路径组件查找结果，避免每次 open/stat 都访问磁盘目录结构。
- dentry 组成内存中的路径关系，但 mount crossing、符号链接、rename 和 namespace 让路径并非简单字符串拼接。
- negative dentry 提高重复失败查找速度，但目录修改后必须正确失效或更新。

## 05-file对象
Q: `struct file` 与 inode 有什么区别？
A:
- inode 表示持久文件对象；`struct file` 表示一次打开实例，也称 open file description 的内核实现核心。
- file 保存当前 offset、打开 flags、凭据、private_data 和 file_operations，并指向路径/inode。
- 多次独立 open 同一 inode 会产生不同 file 和独立 offset；dup/fork 则可让多个 fd 引用同一 file 并共享 offset。
- 文件锁、异步通知和设备状态可能绑定 file，而不只是 inode。

## 06-fd查找
Q: 用户整数 fd 如何定位到文件操作？
A:
- 每个进程 files_struct 维护 fd table，fd 是数组/表中的小整数索引。
- 表项指向 `struct file`；read(fd) 先安全取得 file 引用，再通过 `file_operations` 进入具体实现。
- close 清除当前 fd 表项并减少 file 引用，只有最后引用消失时才执行最终 release。
- fd 可被快速复用，日志只记录数字而不记录时间和对象会把两个完全不同文件混淆。

## 07-open路径解析
Q: `open("/a/b/c")` 的路径解析大致怎样进行？
A:
1. 从进程 root 或 cwd 开始，按组件在 dcache 查找 dentry，miss 时调用父目录 inode lookup。
2. 处理 `.`、`..`、符号链接、mount point、权限和 namespace 边界，并防止符号链接循环。
3. 找到目标 inode 后按 flags 做创建、截断、权限检查，分配 file 并调用文件系统 open。
4. 最后在进程 fd table 安装空闲 fd；openat/openat2 可从目录 fd 开始并提供更安全的解析约束。

## 08-unlink
Q: 为什么文件 `unlink` 后已打开进程仍能继续读写？
A:
- unlink 删除目录中名字到 inode 的链接并减少链接计数，不会强制关闭其他进程持有的 file。
- 只要 file/inode 引用仍在，数据块不会最终释放；路径查找已无法找到，但旧 fd 仍指向对象。
- 日志文件被删除但进程未 reopen 时，磁盘空间会继续占用，可在 `/proc/<pid>/fd` 看到 `(deleted)`。
- 空间直到最后打开引用关闭后才回收，这是 Unix 文件生命周期的重要语义。

## 09-hardlink与symlink
Q: 硬链接和符号链接在 VFS 对象关系上有什么不同？
A:
- 硬链接是另一个目录项直接指向同一 inode，共享内容和元数据，通常不能跨文件系统。
- 符号链接拥有自己的 inode，数据内容是目标路径字符串，解析时再从路径语义寻找目标。
- 目标被删除后硬链接仍有效，符号链接可能悬空；重命名目录也可能改变相对 symlink 含义。
- 目录硬链接通常受限制以避免环和链接计数复杂性。

## 10-mount与namespace
Q: mount namespace 如何让不同进程看到不同文件系统树？
A:
- mount 对象把一个 superblock/root dentry 接到某个挂载点，进程路径解析使用其 namespace 中的 mount tree。
- 创建 mount namespace 后初始视图可共享，修改传播受 shared/private/slave 等 propagation 属性影响。
- chroot 只改变路径解析 root，不提供完整 namespace、权限或 escape 防护，不能等同容器隔离。
- bind mount 复用已有路径子树，可用不同 mount flags 暴露给容器。

## 11-fd泄漏
Q: 怎样定位文件描述符泄漏？
A:
- 比较 `/proc/<pid>/fd` 数量、`fdinfo`、`lsof` 与进程 limits，按 socket、pipe、anon_inode、文件分类。
- 查看是否持续增长且不回落，结合创建/close 调用栈、连接池和异常路径定位缺少释放。
- `EMFILE` 是进程 fd 上限，`ENFILE` 反映系统范围 file table 压力，处置层级不同。
- 提高 ulimit 只延迟故障；还要设置 `O_CLOEXEC`、结构化资源释放和连接生命周期上限。

## 12-正确性审查
Q: 关于 VFS 和 fd，哪些说法需要纠正？
A:
- “fd 就是文件”错误；fd 是进程表索引，指向打开文件对象，再关联 inode。
- “inode 保存完整路径”错误；名字和父子关系主要由目录项表达，一个 inode 可有多个硬链接。
- “删除文件立即释放磁盘”错误；仍有打开引用时数据继续存在。
- “chroot 就是容器安全隔离”错误；它只改变路径根，缺少 namespace、capability、seccomp 和资源控制。

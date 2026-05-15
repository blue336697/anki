# CPU内存IO排障

## CPU卡
Q: 线上 CPU 或 load 高时如何分层排查？
A:
- 先看 load 与 CPU 核数关系，区分 CPU 忙还是 D 状态等待
- 用 top/htop 找进程，用 top -H 找线程
- 看 us、sy、wa、si 等指标区分用户态、系统态、IO wait、软中断
- Java 服务可用 jstack 对应高 CPU 线程
- sy/si 高时要关注系统调用、网络、中断和内核路径

## 内存卡
Q: 线上内存异常如何排查？
A:
- 用 free 看 available，而不是只看 free
- 区分进程 RSS、page cache、slab、swap
- 容器里还要看 cgroup 限制和 OOM 事件
- Java 服务要看堆、直接内存、metaspace、线程栈
- OOM 不一定是堆泄漏，也可能是堆外或容器限制

## IO卡
Q: 线上 IO 或磁盘异常如何排查？
A:
- df/du 判断空间，df -i 判断 inode
- iostat -x 看 await、util、r/s、w/s、队列
- lsof 查找 deleted open file
- 区分普通 write、fsync、页缓存回写和设备瓶颈
- 大量日志、临时文件、core dump、数据库刷盘都是常见来源

## 正确性审查卡
Q: 操作系统线上排障有哪些常见误区？
A:
- “load 高就是 CPU 不够”：错误。IO 等待也会推高 load
- “free 小就是内存泄漏”：不一定。可能是 page cache
- “write 成功就是落盘”：错误。可能还在页缓存
- “删文件就释放空间”：若进程仍打开文件，空间可能不释放
- “只看应用日志就够”：不够。要结合 OS 指标、内核状态和资源限制

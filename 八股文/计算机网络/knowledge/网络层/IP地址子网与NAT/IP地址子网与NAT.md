# IP 地址子网与 NAT
## IP 卡
![image](csdn_657ce408c99022492d279a3e3b37f994.png)
![image](csdn_cefca13c25ddefba1cc68a85297aa09d.png)
![image](csdn_0824623e00c532b85d6d24ad1761db9f.png)
![image](csdn_02eacfc020f77c05bf24695ac1dc7f87.png)
![image](csdn_67c212eab2a903910cea8133e3ed6a6a.png)
![image](csdn_9ac76dcd91d706eb0dfa0deeab953b05.png)
![image](csdn_fdac8bfb5cd584544f88f0d1bbe78bb4.png)
![image](csdn_0535de3f28311cced749ff96c971292c.png)
![image](csdn_4b2a06f91c1c131b3f1dc97443ad1bfb.png)
![image](csdn_3b1ce1813bf6ff3970397178f482a329.png)
![image](csdn_2aa53f3db8c7bfefe1f65ad4326f6b0d.png)
Q: IP 地址和端口分别解决什么问题？
A:
- IP 地址用于定位网络中的主机或接口
- 端口用于定位主机上的具体进程或 socket
- TCP/UDP 连接通常由五元组标识：源 IP、源端口、目标 IP、目标端口、协议
- 同一台机器可以有多个 IP，同一个进程也可以监听多个端口
- 面试表达：IP 负责“到哪台机器”，端口负责“交给哪个应用”

## 子网卡
![image](csdn_a4c3a96f93ab43e18d31ba2c1fbf67cb.png)
![image](csdn_62e148af980567f59f79ac4adbde6550.png)
![image](csdn_ee14c413640203bb472ef1248b7aa0c9.png)
![image](csdn_81d7d45bfb0dad645b9b031f9cfe1df8.png)
![image](csdn_04ea53663ffe4f6820c5c32a87d39ca7.png)
![image](csdn_a4c3a96f93ab43e18d31ba2c1fbf67cb.png)
![image](csdn_b57eb2ae480575c3a2f1b80907ad36a1.png)
![image](csdn_3f1e93d528479e6ba33b79d44c0a4666.png)
![image](csdn_17cb0769836778597805b383cc23ea8f.png)
![image](csdn_b85c53099944ffc1f57124ce91962e7c.png)
![image](csdn_d76be478fcaf8256d75e128eca69125d.png)
![image](csdn_01fbe85d2c44eaa04c7b4dbb34e7ea9e.png)
![image](csdn_eb2828182d9f493dbe83b01d23c42d70.png)
![image](csdn_5e8d5335eedc0bbaecb9e0c06525a429.png)
![image](csdn_30122dfb4cd7eec6b6f274f42f6eb46a.png)
Q: 子网掩码和 CIDR 解决什么问题？
A:
- 子网掩码用于区分 IP 地址中的网络号和主机号
- CIDR 用斜杠表示网络前缀长度，例如 `192.168.1.0/24`
- 同一子网内主机可通过二层网络直接通信，跨子网需要路由器转发
- 路由表根据最长前缀匹配选择下一跳
- 面试重点：CIDR 支持更灵活的地址聚合，减少路由表规模

## NAT 卡
![image](csdn_a43b2e150b06acbedbac833556070f13.png)
![image](csdn_d19eccdf79ec1d1e21bd17503ecc964d.png)
![image](csdn_882e3801188c93cf3bff7dee87fe8f70.png)
Q: NAT 的作用是什么？它带来了哪些问题？
A:
- NAT 把内网私有地址转换成公网地址，缓解 IPv4 地址不足
- 多个内网连接可通过不同源端口复用同一个公网 IP
- NAT 隐藏内网结构，但不是严格安全边界
- 问题包括端到端连接被破坏、P2P/回调困难、排障复杂、需要 NAT 穿透
- IPv6 的普及目标之一就是减少对 NAT 的依赖，恢复端到端寻址能力

## DHCP 卡
![image](csdn_f8504a0bc68eb3671e9bd77405df46ae.png)
![image](csdn_6d93365bfbe16d4bcaddb6fad7bcff92.png)
![image](csdn_993c7a9d5ee59dd12ffd720926ed9e3b.png)
![image](csdn_f5a93e7d795afb9cbc25968dff22146e.png)
![image](csdn_9fddcd5f2c4a964e31a5ac5967c68c25.png)
![image](csdn_607acac34512928b8380347863e8f9aa.png)
Q: DHCP 获取地址的基本过程是什么？
A:
- Discover：客户端广播寻找 DHCP 服务器
- Offer：服务器提供可用 IP、网关、DNS、租约等信息
- Request：客户端请求使用某个 Offer
- ACK：服务器确认租约生效
- 面试边界：DHCP 不只分配 IP，还会下发默认网关、DNS 服务器等上网必要配置

## 工程实践卡
![image](csdn_62f0f308a8ab1537beee6e7f8874e8af.png)
![image](csdn_e0e6bc38800a1cdaa48a386994f097bd.png)
Q: 服务部署时遇到“本机能访问，别的机器不能访问”，网络侧如何排查？
A:
- 检查服务监听地址：是否只绑定 `127.0.0.1` 而不是 `0.0.0.0` 或具体内网 IP
- 检查端口是否监听、进程是否存在、容器端口是否映射
- 检查安全组、防火墙、iptables、云厂商 ACL
- 检查目标 IP 是否在同一网络、路由是否可达、NAT/网关是否正确
- 检查应用协议是否匹配，例如 HTTP/HTTPS、TCP/UDP 端口是否混用

## 正确性审查卡
![image](csdn_e09c48e6c6310b9bbe7f9f5ad04c5d5e.png)
![image](csdn_21c5d772e9e6f92973bb9348ca274ca6.png)
![image](csdn_6bdbc66fbd73423ba5c060994c36686b.png)
![image](csdn_2d51180f656558c5251dbecac74aed3f.png)
![image](csdn_e48f8c3eabc41b23bb98e96b4d0f6cfb.png)
Q: IP、子网、NAT 有哪些常见错误说法？
A:
- “同一个局域网就是同一个网段”：不一定。二层连接和三层子网不是完全同义
- “NAT 等于防火墙”：错误。NAT 是地址转换，安全控制要靠防火墙/ACL
- “端口定位机器”：错误。IP 定位主机，端口定位进程
- “CIDR 越小主机越少”：错误。前缀长度越小，网络范围越大
- “绑定 localhost 和绑定 0.0.0.0 一样”：错误。localhost 只接受本机访问
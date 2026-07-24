# A2A 解决的问题与 Agent-to-Agent 协作约定

来源：https://www.nootcode.com/problems/a2a-agent-to-agent-collaboration-protocols

参考：https://github.com/a2aproject/A2A/blob/main/docs/specification.md

## 面试直接回答卡
Q: 面试中如何直接回答“A2A 解决的问题与 Agent-to-Agent 协作约定是什么？”

A:
- A2A 是 Agent2Agent 协议，解决的是不同框架、不同厂商、不同系统里的 Agent 如何发现彼此、理解能力、委托任务、交换消息、跟踪任务状态和返回结果。
- 官方规范强调，A2A 面向独立甚至内部不透明的 Agent 系统，目标是在不共享内部状态、记忆或工具的情况下完成协作。
- 它通常包含 Agent Card 做能力发现，client agent 向 remote agent 发起任务，围绕 task lifecycle 交换 messages、parts、artifacts，并支持长任务、流式状态更新和企业安全模式。
- A2A 和 MCP 是互补的：MCP 更像 Agent 连接工具和上下文的协议，A2A 更像 Agent 之间协作和任务委托的协议。
- 例如招聘场景中，一个协调 Agent 可以通过 A2A 找到候选人搜索 Agent、日程 Agent、背景检查 Agent，并把子任务交给它们，而不需要知道它们内部怎么实现。
- 但 A2A 不是共享大脑，也不自动解决信任、权限和结果正确性。生产上仍需要身份认证、授权、数据最小化、审计、超时、验收和冲突归并。

## 解决问题卡
Q: A2A 主要解决哪些问题？

A:
- Discovery：Agent 如何发现其他 Agent 的能力。
- Interoperability：不同框架、语言、厂商的 Agent 如何用共同协议通信。
- Task delegation：一个 Agent 如何把任务委托给另一个 Agent。
- Task lifecycle：长任务如何跟踪状态、进度、完成和失败。
- Modality negotiation：文本、文件、结构化数据、音视频等不同内容如何表达。
- Security pattern：如何在企业环境里进行认证、授权和安全通信。

## 核心对象卡
Q: A2A 中常见核心对象有哪些？

A:
- Agent Card：描述 Agent 名称、能力、端点、认证方式、支持的交互模式。
- Client Agent：发起协作或委托任务的一方。
- Remote Agent：接收任务并尝试完成的一方。
- Task：协作的基本工作单元，有生命周期和状态。
- Message：Agent 间交换上下文、请求、回复和指令的载体。
- Artifact：任务产出的结果，例如文件、报告、结构化数据。

## MCP 对比卡
Q: A2A 和 MCP 有什么区别？

A:
- MCP 主要连接 Agent 和工具/资源/提示，解决外部能力接入。
- A2A 主要连接 Agent 和 Agent，解决跨系统协作和任务委托。
- MCP server 暴露 tools、resources、prompts。
- A2A remote agent 暴露的是能力和可承接的任务，而不是直接暴露内部工具。
- 一个 Agent 可以通过 MCP 使用工具，同时通过 A2A 与其他 Agent 协作。

## 例子卡
Q: 举例说明 A2A 协作流程。

A:
- 用户让企业助理“安排候选人面试并准备材料”。
- Orchestrator 通过 Agent Card 找到招聘 Agent、日程 Agent、文档 Agent。
- 它把候选人筛选任务委托给招聘 Agent，把会议时间协调给日程 Agent。
- 各 remote agent 返回 task status、messages 和 artifacts。
- Orchestrator 汇总候选人列表、面试时间和材料包，再给用户确认。

## 安全与边界卡
Q: A2A 协作有哪些安全和工程边界？

A:
- 不能默认信任 remote agent 的所有输出，要做来源标注和结果校验。
- 只传递完成子任务所需的最小上下文，避免过度共享用户数据。
- 不共享内部记忆、工具权限和系统提示。
- 长任务要有超时、取消、进度和失败状态。
- 高风险动作仍要由本系统权限、审批和人工确认控制。

## 正确性审查卡
Q: 解释 A2A 时有哪些误区？

A:
- 不要把 A2A 说成多 Agent 共享同一个上下文或内存。
- 不要把 A2A 和 MCP 混为一谈，它们解决的集成层次不同。
- 不要认为协议保证结果正确，结果仍需验证、评估和归并。
- 不要把 remote agent 当成本系统工具直接信任，信任边界不同。
- 不要忽略长任务状态，A2A 的价值之一就是任务生命周期和异步协作。


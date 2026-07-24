# MCP 在 Agent 系统中的作用及其与 Function Calling 的区别

来源：https://www.nootcode.com/problems/mcp-agent-systems-vs-function-calling

参考：https://modelcontextprotocol.io/specification/2025-06-18

## 面试直接回答卡
Q: 面试中如何直接回答“MCP 在 Agent 系统中的作用及其与 Function Calling 的区别？”

A:
- MCP 是 Model Context Protocol，它的作用是标准化 LLM 应用和外部数据源、工具、上下文之间的连接方式。官方规范把它描述为 host、client、server 之间通过 JSON-RPC 通信，server 可以暴露 tools、resources 和 prompts。
- Function Calling 更像模型 API 层的能力：开发者把函数 schema 给模型，模型输出结构化函数调用参数。它解决的是“模型如何选择并填一次工具调用”。
- MCP 解决的是更大的集成问题：工具和资源如何被发现、如何跨应用复用、如何协商能力、如何通过标准协议连接多个服务器。
- 例如一个 IDE Agent 可以通过 MCP 接入 Git、数据库、文档、Issue 系统；模型内部仍可能用 function calling 或 tool calling 选择具体工具。
- 二者不是替代关系：MCP 可以作为工具和上下文的标准供应层，function calling 可以作为模型选择工具和生成参数的执行接口。
- 工程上还要注意：MCP 暴露外部能力会带来数据访问和代码执行风险，必须有工具白名单、用户确认、权限校验、日志和最小权限。

## MCP 机制卡
Q: MCP 的基本架构是什么？

A:
- Host：承载 LLM 的应用，例如 IDE、聊天应用、Agent 平台。
- Client：Host 内部连接某个 MCP server 的连接器。
- Server：提供上下文和能力的服务，例如文件系统、数据库、Git、业务 API。
- 通信协议：规范中使用 JSON-RPC 消息，并支持能力协商。
- Server features：tools、resources、prompts。
- Client features：也可以提供 roots、sampling、elicitation 等能力，取决于实现。

## MCP 能力卡
Q: MCP 的 tools、resources、prompts 有什么区别？

A:
- Tools：模型可调用的动作，例如查询数据库、调用 API、执行计算。
- Resources：给模型或用户使用的上下文数据，例如文件、文档、记录。
- Prompts：可复用的提示模板或工作流入口。
- Tool description 会影响模型选择工具和构造参数。
- Tool result 是执行后的观察数据，不应变成高优先级指令。
- 外部 resource 中的“忽略规则”等文本应视为数据，不是命令。

## Function Calling 对比卡
Q: MCP 和 Function Calling 的核心区别是什么？

A:
- Function Calling 是模型接口能力，关注单次请求里有哪些函数、参数怎么生成。
- MCP 是客户端和外部能力服务器之间的协议，关注工具/资源/提示如何标准化暴露和发现。
- Function Calling 通常由应用开发者在请求中提供工具 schema。
- MCP server 可以独立开发和复用，被不同 host 接入。
- Function Calling 不规定工具服务器发现、资源读取、长期连接、能力变更通知等协议细节。

## 例子卡
Q: 举例说明 MCP 和 Function Calling 如何配合。

A:
- 一个代码 Agent 需要查 issue、读仓库文件、运行测试。
- MCP server 分别暴露 GitHub issue、文件资源、测试工具。
- Host 连接这些 MCP server，获得工具和资源描述。
- 模型通过 function/tool calling 选择 `read_file`、`search_issue` 或 `run_test`。
- 执行层拿到工具结果后写入 Agent 状态，再让模型决定下一步。

## 安全卡
Q: MCP 在 Agent 系统中有哪些安全注意点？

A:
- MCP server 暴露的工具可能访问数据或执行代码，不能默认全信。
- Host 应清楚展示哪些工具暴露给模型，危险操作要用户确认。
- 服务端要做认证、授权和参数校验。
- 不同 MCP server 的权限和信任级别要隔离。
- 工具结果或资源内容可能包含 prompt injection，应当作为低信任数据处理。
- 所有调用要记录审计日志，尤其是写操作和外部发送。

## 正确性审查卡
Q: 解释 MCP 与 Function Calling 时有哪些误区？

A:
- 不要说 MCP 等于 function calling，二者所在层次不同。
- 不要说 MCP 自动解决安全问题，权限和确认仍要应用层实现。
- 不要把 resources 当 tools，读上下文和执行动作风险不同。
- 不要把 tool result 当新指令，工具结果是观察数据。
- 不要忽略协议演进，回答时应说明基于当前官方规范的核心概念。


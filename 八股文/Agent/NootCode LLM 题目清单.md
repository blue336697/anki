# NootCode LLM 题目清单

来源：https://www.nootcode.com/problems?category=LLM_FUNDAMENTALS

抓取日期：2026-07-08

覆盖模块：

- LLM 基础：12 题，2 页
- LLM 上下文工程：13 题，2 页
- RAG：14 题，2 页
- Agent 架构设计：11 题，2 页

共 50 题。

## LLM 基础

| 序号 | 题目 | 难度 | Premium |
|---:|---|---|---|
| 1 | [LLM 文本生成过程](https://www.nootcode.com/problems/llm-generation-process) | 简单 | 否 |
| 2 | [LLM Token 与上下文窗口](https://www.nootcode.com/problems/llm-tokens-context-windows) | 简单 | 否 |
| 3 | [LLM 采样参数](https://www.nootcode.com/problems/llm-sampling-parameters) | 简单 | 是 |
| 4 | [为 AI Agent 设计工具调用体系](https://www.nootcode.com/problems/ai-agent-tool-design) | 中等 | 是 |
| 5 | [LLM 幻觉问题与缓解策略](https://www.nootcode.com/problems/llm-hallucination-and-mitigation) | 中等 | 是 |
| 6 | [LLM 模型选型与权衡](https://www.nootcode.com/problems/llm-model-selection-trade-offs) | 中等 | 是 |
| 7 | [LLM 质量、延迟与成本的权衡](https://www.nootcode.com/problems/llm-quality-latency-cost-tradeoffs) | 中等 | 是 |
| 8 | [LLM 指令遵循的局限性](https://www.nootcode.com/problems/llm-instruction-following-limits) | 中等 | 是 |
| 9 | [LLM 中的 Embedding 与语义相似度](https://www.nootcode.com/problems/llm-embeddings-and-semantic-similarity) | 中等 | 是 |
| 10 | [LLM 多次运行为何会产生不同的输出](https://www.nootcode.com/problems/llm-output-variance-across-runs) | 中等 | 是 |
| 11 | [LLM 不适合处理的任务类型](https://www.nootcode.com/problems/poor-fits-for-llms) | 中等 | 是 |
| 12 | [LLM 为何给出流畅但错误的答案](https://www.nootcode.com/problems/llm-fluent-but-wrong-answers) | 中等 | 是 |

## LLM 上下文工程

| 序号 | 题目 | 难度 | Premium |
|---:|---|---|---|
| 1 | [LLM 中的指令层级体系](https://www.nootcode.com/problems/llm-instruction-hierarchy) | 中等 | 否 |
| 2 | [LLM 中的冲突指令处理](https://www.nootcode.com/problems/llm-conflicting-instructions) | 中等 | 否 |
| 3 | [LLM Few-Shot Prompting](https://www.nootcode.com/problems/llm-few-shot-prompting) | 简单 | 是 |
| 4 | [LLM 提示词的维护](https://www.nootcode.com/problems/llm-prompt-maintainability) | 中等 | 是 |
| 5 | [思维链（Chain-of-Thought）提示词设计](https://www.nootcode.com/problems/chain-of-thought-cot-prompting) | 中等 | 是 |
| 6 | [Role Prompting：什么时候有用，什么时候只是噪音？](https://www.nootcode.com/problems/role-prompting-useful-or-noise) | 简单 | 是 |
| 7 | [避免 Prompt 过长、脆弱和难维护](https://www.nootcode.com/problems/avoid-overlong-fragile-prompts) | 中等 | 是 |
| 8 | [模型输出进入下游系统前应该做哪些 validation？](https://www.nootcode.com/problems/llm-output-validation-before-downstream-systems) | 中等 | 是 |
| 9 | [稳定输出 JSON 与 Schema 设计](https://www.nootcode.com/problems/stable-json-output-schema-design) | 中等 | 是 |
| 10 | [上下文太多或太少分别有什么问题？](https://www.nootcode.com/problems/too-much-or-too-little-context) | 中等 | 是 |
| 11 | [Prompt Injection 与普通用户指令的区别](https://www.nootcode.com/problems/prompt-injection-vs-user-instructions) | 简单 | 是 |
| 12 | [多语言和专业领域 Prompt 设计的额外风险](https://www.nootcode.com/problems/multilingual-domain-specific-prompt-risks) | 中等 | 是 |
| 13 | [长对话超过 Context Window 时怎么办](https://www.nootcode.com/problems/long-conversation-exceeds-context-window) | 中等 | 是 |

## RAG

| 序号 | 题目 | 难度 | Premium |
|---:|---|---|---|
| 1 | [什么是 RAG？为什么不能只依赖模型自己的知识回答问题？](https://www.nootcode.com/problems/what-is-rag) | 简单 | 否 |
| 2 | [RAG 和 fine-tuning 分别解决什么问题？](https://www.nootcode.com/problems/rag-vs-fine-tuning) | 中等 | 否 |
| 3 | [什么情况下 RAG 反而会降低答案质量？](https://www.nootcode.com/problems/when-rag-reduces-answer-quality) | 中等 | 是 |
| 4 | [一个 RAG 系统通常包含哪些模块？](https://www.nootcode.com/problems/rag-system-modules) | 中等 | 是 |
| 5 | [向量检索、关键词检索、Hybrid Search 与 Rerank 的适用场景](https://www.nootcode.com/problems/vector-keyword-hybrid-search-rerank-scenarios) | 中等 | 是 |
| 6 | [PDF、网页、Markdown、表格、代码仓库的 RAG 切分策略差异](https://www.nootcode.com/problems/rag-chunking-by-content-type) | 中等 | 是 |
| 7 | [RAG 中 top-k 应该如何选择？过大或过小会有什么问题？](https://www.nootcode.com/problems/rag-top-k-selection) | 中等 | 是 |
| 8 | [RAG 答案里的引用和来源应该如何展示，才能让用户可验证？](https://www.nootcode.com/problems/rag-citations-and-sources) | 困难 | 是 |
| 9 | [RAG 中如何评估 retrieval quality 和 answer quality？它们的指标有什么不同？](https://www.nootcode.com/problems/rag-retrieval-quality-vs-answer-quality) | 中等 | 是 |
| 10 | [RAG 系统如何处理文档更新、删除、权限变化和重新索引？](https://www.nootcode.com/problems/rag-document-lifecycle-and-reindexing) | 困难 | 是 |
| 11 | [RAG 中如何处理用户刚上传文档但索引还没完成的情况？](https://www.nootcode.com/problems/rag-uploaded-document-indexing-pending) | 中等 | 是 |
| 12 | [多租户 RAG 系统如何隔离数据？](https://www.nootcode.com/problems/multi-tenant-rag-data-isolation) | 困难 | 是 |
| 13 | [RAG 中如何处理短问题、模糊问题与多子问题](https://www.nootcode.com/problems/rag-short-ambiguous-multi-question) | 困难 | 是 |
| 14 | [RAG 可能造成哪些隐私泄露和越权访问问题？](https://www.nootcode.com/problems/rag-privacy-leakage-and-unauthorized-access) | 中等 | 是 |

## Agent 架构设计

| 序号 | 题目 | 难度 | Premium |
|---:|---|---|---|
| 1 | [什么是 Agent？它和单次 LLM 调用、固定工作流有什么区别？](https://www.nootcode.com/problems/what-is-agent) | 简单 | 否 |
| 2 | [ReAct 是什么？说说它的原理](https://www.nootcode.com/problems/react-reasoning-and-acting) | 中等 | 否 |
| 3 | [Plan-and-Execute 架构与 ReAct 对比](https://www.nootcode.com/problems/plan-and-execute-vs-react) | 中等 | 是 |
| 4 | [长任务 Agent 中断后如何恢复？](https://www.nootcode.com/problems/long-task-agent-interruption-recovery) | 中等 | 是 |
| 5 | [Agent 什么时候应该继续行动，什么时候应该停止、失败或请求人工确认？](https://www.nootcode.com/problems/agent-continue-stop-fail-human-confirmation) | 中等 | 是 |
| 6 | [如何防止 Agent 无限循环、重复调用工具、失控花费或执行危险动作？](https://www.nootcode.com/problems/agent-loop-cost-safety-controls) | 中等 | 是 |
| 7 | [Skills 如何封装 Agent 的可复用工作流？和普通工具有什么区别？](https://www.nootcode.com/problems/agent-skills-reusable-workflows) | 中等 | 是 |
| 8 | [MCP 在 Agent 系统中的作用及其与 Function Calling 的区别](https://www.nootcode.com/problems/mcp-agent-systems-vs-function-calling) | 中等 | 是 |
| 9 | [多 Agent 协作适合什么场景？什么时候单 Agent 更好？](https://www.nootcode.com/problems/multi-agent-collaboration-vs-single-agent) | 中等 | 是 |
| 10 | [A2A 解决的问题与 Agent-to-Agent 协作约定](https://www.nootcode.com/problems/a2a-agent-to-agent-collaboration-protocols) | 困难 | 是 |
| 11 | [多 Agent 系统如何共享状态、传递上下文和归并结果？](https://www.nootcode.com/problems/multi-agent-state-context-result-merging) | 困难 | 是 |

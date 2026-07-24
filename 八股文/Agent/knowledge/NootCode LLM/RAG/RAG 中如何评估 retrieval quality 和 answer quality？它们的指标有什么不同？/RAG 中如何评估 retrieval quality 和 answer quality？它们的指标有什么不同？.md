# RAG 中如何评估 retrieval quality 和 answer quality？它们的指标有什么不同？

来源：https://www.nootcode.com/problems/rag-retrieval-quality-vs-answer-quality

## 面试直接回答卡
Q: 面试中如何直接回答“RAG 中如何评估 retrieval quality 和 answer quality？它们的指标有什么不同？”

A:
- RAG 评估必须拆成 retrieval quality 和 answer quality，因为最终答案错了，可能是没检索到证据，也可能是检索到了但模型没用好证据。
- Retrieval quality 评估的是“系统有没有把正确证据找出来，并排在足够靠前的位置”，常用指标包括 recall@k、precision@k、hit rate、MRR、nDCG、context recall、context precision。
- Answer quality 评估的是“最终回答是否正确、完整、忠于证据、引用准确、格式可用”，常用维度包括 correctness、faithfulness、groundedness、completeness、citation accuracy、refusal appropriateness。
- 例如正确文档在 top-5 里，但模型回答时漏掉例外条件，这是 answer quality 问题；如果正确文档根本没被召回，这是 retrieval quality 问题。
- 生产上要建 golden set：每个问题标注标准答案、必要证据、可接受引用和权限条件，然后分别跑检索评估和端到端答案评估。
- 面试里要强调：只看用户满意度或最终答案分数不够，RAG 的可优化性来自把失败归因拆开。

## 检索指标卡
Q: retrieval quality 常用哪些指标？

A:
- Recall@k：标准证据是否出现在前 k 个结果里，关注有没有找全。
- Precision@k：前 k 个结果里有多少是真相关，关注噪声多少。
- Hit rate@k：至少命中一个相关证据的问题比例。
- MRR：第一个相关结果排得越靠前，分数越高。
- nDCG：考虑相关性等级和排序位置，适合多级相关标注。
- Context recall/precision：进入 LLM 上下文的证据是否覆盖答案所需信息，且噪声是否过多。

## 答案指标卡
Q: answer quality 常用哪些指标？

A:
- Correctness：答案结论是否正确。
- Faithfulness：答案是否只表达证据支持的内容，没有编造。
- Groundedness：关键结论能否回指到上下文证据。
- Completeness：是否回答了所有子问题和必要例外。
- Citation accuracy：引用是否真的支持对应结论。
- Format validity：输出是否符合 JSON、Markdown、字段枚举等下游要求。
- Refusal appropriateness：证据不足或权限不足时是否正确拒答或降级。

## 失败归因卡
Q: 如何区分检索问题和生成问题？

A:
- 如果 gold evidence 不在召回结果里，是召回或索引问题。
- 如果 gold evidence 在候选里但 rerank 后没进入上下文，是排序或 top-k 问题。
- 如果证据进了上下文但答案没用，是生成、prompt 或模型能力问题。
- 如果答案正确但引用错了，是 citation mapping 或后处理问题。
- 如果不同用户看到不同答案，可能是权限过滤或多租户隔离问题。

## 数据集卡
Q: RAG 评估集应该如何构建？

A:
- 覆盖单点事实、多跳问题、比较问题、模糊问题、无答案问题和权限边界问题。
- 每个问题标注必要证据，而不只是标准答案。
- 标注证据版本和适用范围，避免旧文档被误当正确。
- 加入 hard negative，例如语义相似但业务对象不同的文档。
- 对高风险场景加入引用准确性和拒答正确性的标注。

## 工程实践卡
Q: RAG 评估如何落到工程闭环？

A:
- 离线评估用于比较 chunking、embedding、hybrid search、rerank 和 prompt 版本。
- 在线监控记录召回结果、分数、进入上下文的证据、答案和用户反馈。
- 失败样本按错召回、漏召回、旧文档、生成漂移、引用错误、权限错误分类。
- LLM-as-judge 可以辅助打分，但高风险集要有人审或规则校验。
- 发布前做回归集，防止优化某类 query 时破坏另一类 query。

## 正确性审查卡
Q: 解释 RAG 评估时有哪些误区？

A:
- 不要只看最终答案 BLEU/ROUGE，RAG 更关心事实正确和证据支撑。
- 不要把检索分数当答案质量，检索好不代表生成好。
- 不要没有 gold evidence 就评估 retrieval，否则无法判断漏召回。
- 不要只测有答案问题，无答案和权限不足场景同样重要。
- 不要完全依赖 LLM 评测器，评测器本身也可能被上下文和措辞影响。


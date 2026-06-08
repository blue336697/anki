const { C, FONT, MONO, newDeck, darkSlide, contentSlide, bullets, styledTable, hc, setModule, codeBox } = require("./aws_theme");
setModule("05 S4 · Feedback & State");
const p = newDeck("Harness Engineering — 05 S4 Feedback & State");
const N = 28;
const OUT = "/Users/qcguang/Desktop/courses/HarnessEngineering/ppt_v3/05_S4_feedback_state.pptx";
let s;

// ---------- Slide 1: Cover ----------
s = darkSlide(p);
s.addText("S4 · FEEDBACK & STATE", { x: 0.6, y: 1.5, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("反馈与状态系统", { x: 0.6, y: 2.0, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 38, bold: true, color: C.WHITE });
s.addText("把 Demo 变成 Product 的关键闭环", { x: 0.62, y: 2.95, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 18, color: "C7CED6" });
s.addText("\u201CFeedback loop is what separates demos from products.\u201D", { x: 0.62, y: 3.5, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, italic: true, color: "8C9AA6" });
s.addShape(p.shapes.LINE, { x: 0.62, y: 4.15, w: 6.2, h: 0, line: { color: "47525E", width: 1 } });
s.addText([
  { text: "S1 给大脑（Context）· S2 给手脚（Tools）· S3 给纪律（Security）", options: { breakLine: true } },
  { text: "S4 = 它怎么\u201C记住\u201D走过的路？怎么知道走得好不好？", options: { breakLine: true } },
  { text: "五步闭环：Observe → Collect → Evaluate → Remember → Inject", options: {} },
], { x: 0.62, y: 4.35, w: 12, h: 1.7, fontFace: FONT, fontSize: 14, color: "E6EAEE", paraSpaceAfter: 8 });
s.addText("80 min  ·  28 slides", { x: 9.5, y: 6.7, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: "6B7682", align: "right" });
s.addNotes("开场不要急着讲技术。先问观众一个问题：\u201C你们有没有遇到过，Agent 犯了一个错误，然后在同一个 session 里又犯了完全相同的错误？\u201D停顿等几个人点头。\u201C这就是没有 feedback loop 的后果。今天我们解决这个问题。\u201D语气要让人感到这是课程从\u201C能跑\u201D到\u201C能用\u201D的转折点。");

// ---------- Slide 2: Anchor 被动 vs 主动 ----------
s = contentSlide(p, 2, N, "范式转移 — 被动记录 vs 主动学习", "Anchor · 传统反馈 vs Agent 反馈");
styledTable(p, s, [
  [hc("维度"), hc("传统系统"), hc("Agent 系统")],
  ["行为", "预定义路径", "动态生成（每次不同）"],
  ["日志", "被动记录（事后验尸）", "主动学习（实时闭环）"],
  ["评估", "确定性对比 same in/out", "非确定性 judgment"],
  ["反馈", "人工分析后改代码", "Agent 自动积累经验"],
  ["状态", "数据库中的显式 state", "分布在 context+memory+trace"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [1.6, 4.95, 4.95], rowH: 0.5, fontSize: 12 });
const entropies = [["行为不确定性", "同任务多路径，皆可能对"], ["质量不确定性", "无法 assert，需 judgment"], ["退化不确定性", "模型/prompt 变化 → 静默下滑"]];
entropies.forEach((e, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 5.0, w: 3.6, h: 1.0, fill: { color: C.ORANGE } });
  s.addText([{ text: e[0], options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: e[1], options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.15, y: 5.13, w: 3.3, h: 0.8, fontFace: FONT, valign: "top" });
});
s.addText("结论：反馈系统不是\u201C锦上添花\u201D，是 Agent 系统的核心基础设施。", { x: 0.92, y: 6.15, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, align: "center" });
s.addNotes("强调\u201Centropy\u201D这个词。传统 Web 应用的 entropy 很低——用户点按钮，后端执行固定逻辑。Agent 的 entropy 极高——同一个任务，它可能走 3 条完全不同的路径，每条路径都可能是对的。这种不确定性决定了我们不能用传统的 monitoring 思维来做 Agent 的反馈系统。");

// ---------- Slide 3: 灾难场景 ----------
s = contentSlide(p, 3, N, "三种灾难 — 恰好对应本模块三个主题", "灾难场景 · 没有反馈的死法");
const ds = [
  { t: "灾难 1 · 重复犯错", l: ["连续 5 次同一 API 错误", "用户：第 3 次开始骂，第 5 次关 tab"], r: "无 Memory → Part A", c: C.RED },
  { t: "灾难 2 · 黑箱 debug", l: ["Agent 选错 Tool", "3 工程师 × 3 天 ≈ $15K"], r: "无 Trace → Part B", c: C.ORANGE },
  { t: "灾难 3 · 静默退化", l: ["3 个月内质量下降 20%", "无人察觉直到 churn 报警"], r: "无 Eval → Part C", c: "C0631A" },
];
ds.forEach((d, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 3.6, h: 0.55, fill: { color: d.c } });
  s.addText(d.t, { x: x + 0.15, y: 1.75, w: 3.4, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 3.6, h: 1.85, fill: { color: "FBEAE5" } });
  s.addText([...d.l.map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceAfter: 6 } })), { text: d.r, options: { fontSize: 12, bold: true, color: d.c, paraSpaceBefore: 6 } }], { x: x + 0.18, y: 2.42, w: 3.3, h: 1.65, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.4, w: 11.5, h: 0.95, fill: { color: C.DARK } });
s.addText("三个灾难 = 三个主题：Memory · Observability · Evaluation", { x: 0.92, y: 4.4, w: 11.5, h: 0.95, fontFace: FONT, fontSize: 15, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addText("最可怕的不是系统挂了，是系统慢慢变差但没人知道。", { x: 0.92, y: 5.55, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 13, italic: true, color: C.GRAY, align: "center" });
s.addNotes("讲灾难 1 时即兴演一下用户的挫败感：\u201C哥们，我刚才不是告诉你了吗？用 v2 的 API 格式！\u201D讲灾难 2 时问观众：\u201C你们团队 debug 一个 production issue 平均要多久？\u201D讲灾难 3 时强调 silent degradation——最可怕的不是系统挂了，是系统慢慢变差但没人知道。用这三个场景建立紧迫感后，自然过渡到解决方案。");

// ---------- Slide 4: 三层记忆架构 ----------
s = contentSlide(p, 4, N, "Working / Short-term / Long-term — Harness 管后两层", "Memory · 三层架构");
const mlayers = [
  { t: "Working Memory = LLM Context Window", d: "容量 128K-200K · 单次推理 · Model's domain", c: C.GRAY, lbl: "Model" },
  { t: "Short-term Memory = Session State", d: "JSONL append-only · 数小时-数周 · 跨 turn 延续 / 恢复", c: C.BLUE, lbl: "Harness" },
  { t: "Long-term Memory = Persistent Knowledge", d: "MEMORY.md + Embedding Index · 数月-数年 · 偏好 / 项目知识", c: C.ORANGE, lbl: "Harness" },
];
mlayers.forEach((l, i) => {
  const w = 5.0 + i * 1.5;
  const x = 0.92 + (11.5 - w) / 2;
  const y = 1.75 + i * 1.0;
  s.addShape(p.shapes.RECTANGLE, { x, y, w, h: 0.85, fill: { color: l.c } });
  s.addText([{ text: l.t, options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: l.d, options: { fontSize: 10.5, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: x + 0.15, y: y + 0.08, w: w - 0.3, h: 0.7, fontFace: FONT, align: "center", valign: "middle" });
  s.addText(l.lbl, { x: x + w + 0.1, y, w: 1.5, h: 0.85, fontFace: FONT, fontSize: 11, bold: true, color: l.c, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.0, w: 11.5, h: 1.35, fill: { color: "FBEAE5" } });
s.addText([{ text: "关键设计哲学：", options: { bold: true, color: C.RED, fontSize: 14, breakLine: true } }, { text: "delegate to model, NOT wrap — 不要在 harness 层做 context summarization/compression。模型处理自己的 working memory 比任何 heuristic 都强。Harness 价值：决定送什么进去，管理超出窗口的长期记忆。", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 8 } }], { x: 1.12, y: 5.15, w: 11.1, h: 1.1, fontFace: FONT, valign: "top" });
s.addNotes("特别强调\u201Cdelegate to model, NOT wrap\u201D这个设计哲学。很多团队的第一反应是在 harness 层做 context 的 summarization 或 compression——不要这样做。模型在处理自己的 working memory 方面比你写的任何 heuristic 都强。Harness 的价值在于：决定什么信息送进 context window，以及管理那些超出 context window 容量的长期记忆。");

// ---------- Slide 5: 三层记忆数据流 ----------
s = contentSlide(p, 5, N, "信息流动 — 读取 Bottom-up，写入 Top-down", "Memory · 数据流");
codeBox(p, s, [
  { text: "# 每次 Turn 的完整流程", opt: { color: C.ORANGE, bold: true } },
  { text: "1. Long-term 检索相关记忆 (hybrid, <100ms)", opt: { color: "8FD19E" } },
  { text: "2. 加载 Short-term 中的 session context", opt: { color: "8FD19E" } },
  { text: "3. 组装为 Working Memory 送入模型 (S1)", opt: { color: "8FD19E" } },
  { text: "4. 模型输出后，更新 Short-term (sync, append)", opt: { color: "8FBFE8" } },
  { text: "5. 满足条件触发 consolidation → Long-term (async)", opt: { color: "8FBFE8" } },
], { x: 0.92, y: 1.75, w: 7.0, h: 2.7, fontSize: 11 });
s.addText([{ text: "设计原则", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } }, { text: "读取要快 (<100ms) — 直接影响用户感知延迟", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 6 } }, { text: "写入可异步 — 不 block 当前 turn", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 4 } }, { text: "读优先于写 — 资源竞争时永远保检索", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.INK, paraSpaceBefore: 4 } }], { x: 8.2, y: 1.75, w: 4.2, h: 2.7, fontFace: FONT, valign: "top" });
const arrows = [["⬆ Retrieve & Inject", "Long → Short → Working", "<100ms 同步", C.GREEN], ["⬇ Log & Consolidate", "Working → Short → Long", "异步，不阻塞", C.BLUE]];
arrows.forEach((a, i) => {
  const x = 0.92 + i * 5.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 4.7, w: 5.55, h: 1.4, fill: { color: a[3] } });
  s.addText([{ text: a[0], options: { bold: true, fontSize: 14, color: C.WHITE, breakLine: true } }, { text: a[1], options: { fontFace: MONO, fontSize: 11.5, color: "FFFFFF", breakLine: true, paraSpaceBefore: 6 } }, { text: a[2], options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.18, y: 4.85, w: 5.2, h: 1.2, fontFace: FONT, valign: "top" });
});
s.addNotes("画一个时序图来解释一次完整的 turn 中 memory 的流动。强调这不是\u201C保存/加载\u201D这么简单——是一个有选择性的、有优先级的信息流。问观众：\u201C如果用户上次 session 提到他喜欢用 TypeScript，这个信息应该在哪一层？什么时候被检索出来？\u201D答案：Long-term → 通过 hybrid retrieval 在相关 turn 被检索出来注入 context。");

// ---------- Slide 6: 5 种记忆类型 ----------
s = contentSlide(p, 6, N, "Agent 决定什么值得记住 — 5 种记忆类型", "Memory · 主动学习");
styledTable(p, s, [
  [hc("类型"), hc("示例"), hc("生命周期"), hc("触发条件")],
  [{ text: "user", options: { bold: true, color: C.BLUE } }, "\u201C偏好 TypeScript + Vim\u201D", "永久", "用户明确说"],
  [{ text: "project", options: { bold: true, color: C.ORANGE } }, "\u201C本项目 monorepo + pnpm\u201D", "项目生命周期", "代码/配置推断"],
  [{ text: "feedback", options: { bold: true, color: C.RED } }, "\u201C不要用 semicolons\u201D", "6 个月", "用户纠正"],
  [{ text: "reference", options: { bold: true, color: C.GREEN } }, "\u201C内部 API v2 endpoint\u201D", "永久", "用户分享文档"],
  [{ text: "episodic", options: { bold: true, color: C.GRAY } }, "\u201C今天 debug CORS\u201D", "30 天", "session 结束总结"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.4, 4.0, 2.2, 3.9], rowH: 0.55, fontSize: 12 });
codeBox(p, s, [
  { text: "{", opt: {} },
  { text: "  \"type\": \"user|project|feedback|reference|episodic\",", opt: { color: "8FD19E" } },
  { text: "  \"content\": \"string\",", opt: { color: "8FD19E" } },
  { text: "  \"tags\": [\"string\"],", opt: { color: "8FD19E" } },
  { text: "  \"confidence\": 0.0-1.0,", opt: { color: "8FBFE8" } },
  { text: "  \"expiry\": \"Duration | null\",", opt: { color: "8FBFE8" } },
  { text: "  \"source\": \"user_explicit|agent_inferred|consolidation\"", opt: { color: "E8A33D" } },
  { text: "}", opt: {} },
], { x: 0.92, y: 5.05, w: 11.5, h: 1.3, fontSize: 10.5 });
s.addNotes("用一个具体例子：\u201C假设用户说\u2018我这个项目用的是 Next.js 14，别给我 pages router 的代码\u2019。Agent 应该怎么做？1）记住这是 project 类型的记忆，2）content 是 \u2018Next.js 14, App Router only\u2019，3）confidence 是 0.95（用户明确说的），4）生命周期跟项目走。下次用户问任何前端问题，这条记忆就会被检索出来注入 context。\u201D这就是从\u201C每次都要重复说\u201D到\u201C说一次就够\u201D的转变。");

// ---------- Slide 7: Confidence Gating ----------
s = contentSlide(p, 7, N, "置信度门控与用户最终控制权", "Memory · Confidence Gating");
const gates = [["< 0.5", "阻止写入", C.RED], ["0.5-0.7", "标记待验证", "E0A000"], ["0.7-0.9", "正常写入", C.GREEN], ["> 0.9", "延长保留期", C.BLUE]];
gates.forEach((g, i) => {
  const x = 0.92 + i * 1.55;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 1.45, h: 0.95, fill: { color: g[2] } });
  s.addText([{ text: g[0], options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: g[1], options: { fontSize: 10, color: "FFFFFF", paraSpaceBefore: 3 } }], { x, y: 1.85, w: 1.45, h: 0.8, fontFace: FONT, align: "center", valign: "top" });
});
s.addText("来源 → confidence：用户明确(0.95) > 行为推断(0.8) > Agent 总结(0.7) > 外部数据(0.5)", { x: 0.92, y: 2.85, w: 6.4, h: 0.4, fontFace: FONT, fontSize: 10.5, italic: true, color: C.GRAY });
s.addText("User Control（5 项必备）", { x: 0.92, y: 3.35, w: 6.4, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const ucontrols = ["查看：浏览所有已存记忆（/memory 命令）", "审批：敏感记忆需用户确认才写入", "删除：随时可删（GDPR right to be forgotten）", "修正：用户可编辑记忆内容", "透明存储：可见的文本文件，非黑箱 DB"];
ucontrols.forEach((u, i) => {
  const y = 3.75 + i * 0.42;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 6.4, h: 0.35, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.08, h: 0.35, fill: { color: C.ORANGE } });
  s.addText(u, { x: 1.08, y, w: 6.2, h: 0.35, fontFace: FONT, fontSize: 11, color: C.INK, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 7.6, y: 1.75, w: 4.8, h: 4.5, fill: { color: C.DARK } });
s.addText([{ text: "为什么必须有 User Control", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, ...["信任：用户需知 Agent\u201C记住了什么关于我\u201D", "合规：GDPR / CCPA 要求", "质量：Agent 可能记错，用户是仲裁者", "安全：防止 memory poisoning（联动 S3）"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 8 } }))], { x: 7.78, y: 1.92, w: 4.5, h: 4.2, fontFace: FONT, valign: "top" });
s.addNotes("强调 confidence gating 的意义：没有它，Agent 会把每一条对话都当成\u201C值得记住的\u201D，memory 会迅速膨胀，检索质量下降。这是 signal-to-noise ratio 的问题。然后讲 user control——这不只是 nice-to-have，在很多场景下是法律要求。问观众：\u201C如果 Agent 错误地记住了\u2018用户不喜欢测试\u2019，后果是什么？\u201D答：以后永远不主动写测试，用户都不知道为什么。");

// ---------- Slide 8: Memory 安全 ----------
s = contentSlide(p, 8, N, "记忆可以被攻击 — S4 侧的检测机制", "Memory · 污染检测与防护");
s.addText("Pre-write Scan（写入时）", { x: 0.92, y: 1.7, w: 6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.RED });
const prewrite = [["语义异常", "新记忆与已有记忆矛盾？已有 TS 偏好 + 新 JavaScript → 冲突告警"], ["指令检测", "可疑模式：\u201C总是/永远/忽略\u201D · URL+动作组合"], ["来源评估", "用户直说（可信）vs Agent 从外部推断（需验证）"]];
prewrite.forEach((p2, i) => {
  const y = 2.1 + i * 0.55;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 6.0, h: 0.48, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.1, h: 0.48, fill: { color: C.RED } });
  s.addText([{ text: p2[0] + "  ", options: { bold: true, fontSize: 11.5, color: C.INK } }, { text: p2[1], options: { fontSize: 10, color: C.GRAY } }], { x: 1.1, y, w: 5.7, h: 0.48, fontFace: FONT, valign: "middle" });
});
s.addText("Retrieval-time Validation（使用时）", { x: 0.92, y: 3.85, w: 6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.ORANGE });
codeBox(p, s, [
  { text: "# Decay function", opt: { color: "8C9AA6" } },
  { text: "confidence(t) = initial × 0.95^(days/30)", opt: { color: "8FD19E" } },
  { text: "# 30 天 ↓~5% · 180 天 ↓~26%", opt: { color: "8C9AA6" } },
], { x: 0.92, y: 4.25, w: 6.0, h: 1.1, fontSize: 11 });
s.addShape(p.shapes.RECTANGLE, { x: 7.4, y: 1.7, w: 5.0, h: 4.0, fill: { color: C.DARK } });
s.addText([{ text: "异常告警（联动 S3）", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, ...["短时间大量记忆写入 → 批量投毒", "内容匹配 S3 注入模式库 → 告警 + 隔离", "跨 Agent 异常传播 → 阻断"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 8 } })), { text: "S3 = 安全策略（什么是可疑）", options: { fontSize: 11, italic: true, color: "C7CED6", breakLine: true, paraSpaceBefore: 12 } }, { text: "S4 = 安全运营（实时监控发现可疑）", options: { fontSize: 11, italic: true, color: "C7CED6" } }], { x: 7.6, y: 1.88, w: 4.7, h: 3.7, fontFace: FONT, valign: "top" });
s.addText("Decay 让旧记忆自然褪色 — 即使绕过写入时检测，被污染的记忆也会在 180 天内自然失效。", { x: 0.92, y: 5.7, w: 11.5, h: 0.65, fontFace: FONT, fontSize: 12, color: C.INK, italic: true, valign: "top" });
s.addNotes("这是 S3 和 S4 的交叉点。S3 定义了\u201Cmemory poisoning 是什么、怎么防\u201D，S4 实现\u201C怎么检测\u201D。类比：S3 是安全策略（\u201C什么是可疑的\u201D），S4 是安全运营（\u201C实时监控发现可疑活动\u201D）。Confidence decay 的设计很精妙——它让旧记忆自然\u201C褪色\u201D，如果没有被重新确认，最终会被 prune 掉。");

// ---------- Slide 9: autoDream ----------
s = contentSlide(p, 9, N, "autoDream — 周期性整理（S4 完整实现）", "Memory · autoDream");
const stages = [
  ["Stage 1 · Orient", "提取 session 摘要 + 识别关键事件\nsession_summaries[]"],
  ["Stage 2 · Gather", "抽出偏好 / 项目变更 / 教训\nraw_memories[]"],
  ["Stage 3 · Consolidate", "写入 + 合并 + 冲突解决\nupdated memory store"],
  ["Stage 4 · Prune", "过期 / 低 confidence / 重复\ntrimmed memory store"],
];
stages.forEach((st, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 2.7, h: 0.55, fill: { color: [C.DARK, "2E4A63", C.BLUE, C.ORANGE][i] } });
  s.addText(st[0], { x: x + 0.1, y: 1.75, w: 2.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 2.7, h: 1.55, fill: { color: C.LIGHT } });
  s.addText(st[1], { x: x + 0.15, y: 2.4, w: 2.4, h: 1.4, fontFace: FONT, fontSize: 10.5, color: C.INK, valign: "top" });
  if (i < 3) s.addShape(p.shapes.LINE, { x: x + 2.7, y: 2.55, w: 0.25, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.0, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("触发条件（任一）：Time Gate >24h  ·  Session Gate ≥5 sessions  ·  Explicit /consolidate", { x: 0.92, y: 4.0, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addText([{ text: "质量保证", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } }, ...["条目数对比：整合后应减少 30-50%", "整合后检索准确率不应下降（回归测试）", "冲突解决：新信息优先（更近 = 更反映现状）"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceBefore: 6 } }))], { x: 0.92, y: 4.7, w: 11.5, h: 1.7, fontFace: FONT, valign: "top" });
s.addNotes("走一个完整例子：\u201C假设用户这周有 5 个 coding session。Orient 阶段提取出：session 1 写了 React 组件，session 2 修了 bug，session 3 用户说\u2018以后别用 class component\u2019，session 4 做了 API 集成，session 5 做了重构。Gather 阶段抽出：偏好=\u2018functional components only\u2019，项目信息=\u2018已完成 API 集成\u2019，教训=\u2018重构时要先跑测试\u2019。Consolidate 阶段写入 memory。Prune 阶段发现之前有一条\u2018项目还没开始 API 集成\u2019的旧记忆，删掉它。\u201D这个流程使记忆保持当前和有用。");

// ---------- Slide 10: 整理为什么必须做 ----------
s = contentSlide(p, 10, N, "没有整理的记忆系统 = 垃圾堆", "Memory · 整理的价值");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 11.5, h: 0.55, fill: { color: C.RED } });
s.addText("无限增长：50 条潜在记忆/session × 100 sessions = 5000 条 → 检索时间↑ 质量↓", { x: 0.92, y: 1.75, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const spirals = ["条目过多 → 检索噪音大", "噪音大 → tokens 浪费在无关记忆", "Tokens 浪费 → 有用信息被挤出窗口", "信息丢失 → Agent 表现下降", "表现下降 → 更多纠正 → 更多记忆 → 恶性循环"];
spirals.forEach((sp, i) => {
  const y = 2.5 + i * 0.5;
  s.addShape(p.shapes.OVAL, { x: 0.92, y, w: 0.45, h: 0.45, fill: { color: C.RED } });
  s.addText(String(i + 1), { x: 0.92, y, w: 0.45, h: 0.45, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 1.5, y, w: 5.6, h: 0.45, fill: { color: "FBEAE5" } });
  s.addText(sp, { x: 1.6, y, w: 5.5, h: 0.45, fontFace: FONT, fontSize: 11, color: C.INK, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 7.5, y: 2.5, w: 4.9, h: 2.65, fill: { color: C.GREEN } });
s.addText([{ text: "Consolidation 的价值（实测）", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "压缩：5 条 → 1 条 (~5x)", options: { fontSize: 14, bold: true, color: "FFFFFF", breakLine: true, paraSpaceBefore: 8 } }, { text: "未整理 1000 条 → 准确率 60%", options: { fontSize: 12, color: "FFFFFF", breakLine: true, paraSpaceBefore: 6 } }, { text: "整理后 200 条 → 准确率 90%", options: { fontSize: 12, color: "FFFFFF", breakLine: true, paraSpaceBefore: 4 } }, { text: "Token 消耗 ↓ 40%", options: { fontSize: 12, color: "FFFFFF", paraSpaceBefore: 6 } }], { x: 7.7, y: 2.65, w: 4.5, h: 2.4, fontFace: FONT, valign: "top" });
s.addText("记忆系统的价值不在于\u201C记住多少\u201D，而在于\u201C能准确找到多少\u201D。", { x: 0.92, y: 5.4, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, italic: true, color: C.INK, align: "center" });
s.addNotes("这张 slide 是给那些觉得\u201C记忆多总比记忆少好\u201D的人看的。核心信息：记忆系统的价值不在于\u201C记住多少\u201D，而在于\u201C能准确找到多少\u201D。一个有 5000 条未整理记忆的系统，不如一个有 200 条精心整理的记忆系统。这和你的搜索引擎一样——Google 不是因为索引了最多页面而好用，是因为它能从海量结果中准确找到你要的那一条。");

// ---------- Slide 11: Hybrid Retrieval ----------
s = contentSlide(p, 11, N, "Keyword + Semantic 双通道检索", "Memory · Hybrid Retrieval");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.5, h: 1.55, fill: { color: "EEF1F3" } });
s.addText([{ text: "🔍 Keyword Search", options: { bold: true, color: C.BLUE, fontSize: 13, breakLine: true } }, { text: "BM25 索引 · 精确匹配术语", options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 5 } }, { text: "+ 快速 / 精确  − 无法处理同义改写", options: { fontSize: 10.5, color: C.GRAY, breakLine: true, paraSpaceBefore: 3 } }, { text: "<10ms · 适：\u201CReact hooks\u201D \u201CAPI v2\u201D", options: { fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 3 } }], { x: 1.1, y: 1.88, w: 5.2, h: 1.4, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.92, y: 1.75, w: 5.5, h: 1.55, fill: { color: "FBEAE5" } });
s.addText([{ text: "🧠 Semantic Search", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "Embedding ANN · 理解意图 / 改写", options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 5 } }, { text: "+ 处理 paraphrase  − 看似相关但无关", options: { fontSize: 10.5, color: C.GRAY, breakLine: true, paraSpaceBefore: 3 } }, { text: "<50ms · 适：\u201C上次类似问题\u201D", options: { fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 3 } }], { x: 7.1, y: 1.88, w: 5.2, h: 1.4, fontFace: FONT, valign: "top" });
codeBox(p, s, [
  { text: "# Mixing Strategy", opt: { color: C.ORANGE, bold: true } },
  { text: "1. 各 top-K：keyword + semantic", opt: { color: "8FD19E" } },
  { text: "2. 加权合并：", opt: { color: "8FD19E" } },
  { text: "   final = keyword × 0.4 + semantic × 0.6", opt: { color: "8FBFE8" } },
  { text: "3. 去重 + rerank → top-N", opt: { color: "8FD19E" } },
  { text: "# 性能预算（总 < 100ms）", opt: { color: "8C9AA6" } },
  { text: "  Keyword 10ms · Semantic 50ms · Merge 40ms", opt: { color: "E8A33D" } },
], { x: 0.92, y: 3.5, w: 7.0, h: 2.5, fontSize: 10.5 });
s.addShape(p.shapes.RECTANGLE, { x: 8.2, y: 3.5, w: 4.2, h: 2.5, fill: { color: C.DARK } });
s.addText([{ text: "Token Budget", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "记忆检索 ~30K tokens", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "（在 S1 总预算的份额）", options: { fontSize: 11, color: "C7CED6", paraSpaceBefore: 3 } }, { text: "用户感知：<100ms 不可察觉", options: { fontSize: 11, italic: true, color: C.ORANGE, paraSpaceBefore: 12 } }], { x: 8.4, y: 3.65, w: 3.9, h: 2.3, fontFace: FONT, valign: "top" });
s.addNotes("为什么要 hybrid 而不是纯 semantic？举个例子：用户问\u201C怎么配置 ESLint\u201D。纯 semantic 可能把\u201C代码质量工具配置\u201D相关的记忆都拉出来（Prettier、TSConfig 等），噪音很大。加了 keyword \u201CESLint\u201D，就能精确命中。反过来，如果用户问\u201C上次那个格式化的问题怎么解决的\u201D，纯 keyword 可能匹配不到，但 semantic 能找到之前关于 ESLint 的 session。两者互补。");

// ---------- Slide 12: Context Assembly Priority ----------
s = contentSlide(p, 12, N, "记忆注入的优先级排序 + Token 分配", "Memory · Assembly Priority");
const prio = [["1 · user_profile", "用户身份 + 核心偏好（始终注入）", "2K", C.DARK], ["2 · project", "技术栈 + 项目约束（项目内常驻）", "5K", "2E4A63"], ["3 · feedback", "用户历史纠正（按相关性）", "8K", C.RED], ["4 · recent_sessions", "对话连续性（按时间衰减）", "10K", C.BLUE], ["5 · references", "参考文档 + API 规格（按相关性）", "5K", C.ORANGE]];
prio.forEach((p2, i) => {
  const y = 1.75 + i * 0.6;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 8.5, h: 0.5, fill: { color: p2[3] } });
  s.addText([{ text: p2[0] + "    ", options: { bold: true, fontSize: 12, color: C.WHITE } }, { text: p2[1], options: { fontSize: 10.5, color: "E6EAEE" } }], { x: 1.1, y, w: 8.2, h: 0.5, fontFace: FONT, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.6, y, w: 1.4, h: 0.5, fill: { color: C.LIGHT } });
  s.addText(p2[2] + " tokens", { x: 9.6, y, w: 1.4, h: 0.5, fontFace: FONT, fontSize: 11, bold: true, color: C.INK, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 11.1, y, w: 1.3, h: 0.5, fill: { color: i < 2 ? C.GREEN : C.GRAY } });
  s.addText(i < 2 ? "固定" : "动态", { x: 11.1, y, w: 1.3, h: 0.5, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.85, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("总预算 30K tokens  ·  溢出策略：从优先级最低开始截断", { x: 0.92, y: 4.85, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addText("优先级原则：缺这条信息 → Agent 犯错概率多高？user_profile 第一 — 不知道\u201C跟谁说话\u201D每次回答都可能方向错。", { x: 0.92, y: 5.55, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 12, italic: true, color: C.GRAY, valign: "top" });
s.addNotes("强调这个优先级不是随便定的——是根据\u201C如果缺少这条信息，Agent 犯错的概率有多高\u201D来排序的。user_profile 排第一，因为如果 Agent 不知道用户的基本偏好，每一次回答都可能方向错误。这里可以回顾 S1 的 context budget 概念——memory 的 30K 是整体 budget 的一部分，不是独立的。");

// ---------- Slide 13: Discussion 闭环断裂 ----------
s = contentSlide(p, 13, N, "Discussion — 诊断你系统中的薄弱环节", "讨论环节 · 你的闭环断在哪？");
const loop5 = [["Observe", "看到 Agent 每一步决策？trace？", C.BLUE], ["Collect", "提取了有价值的信号？", "2E4A63"], ["Evaluate", "知道做得\u201C好不好\u201D？baseline？", C.ORANGE], ["Remember", "评估结论被保存了？", C.RED], ["Inject", "经验在下次 session 被使用？", C.GREEN]];
loop5.forEach((l, i) => {
  const x = 0.92 + i * 2.35;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 2.2, h: 0.55, fill: { color: l[2] } });
  s.addText(l[0], { x, y: 1.75, w: 2.2, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 2.2, h: 1.0, fill: { color: C.LIGHT } });
  s.addText(l[1], { x: x + 0.1, y: 2.4, w: 2.0, h: 0.85, fontFace: FONT, fontSize: 10, color: C.INK, valign: "top" });
  if (i < 4) s.addShape(p.shapes.LINE, { x: x + 2.2, y: 2.0, w: 0.15, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
});
s.addText("常见断裂模式", { x: 0.92, y: 3.55, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.RED });
const breaks = [["有 log 但不看", "Observe ✓  Collect ✗"], ["看了但没结论", "Collect ✓  Evaluate ✗"], ["有评估没持久化", "Evaluate ✓  Remember ✗"], ["存了但检索不出", "Remember ✓  Inject ✗"]];
breaks.forEach((b, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 3.95, w: 2.7, h: 1.05, fill: { color: "FBEAE5" } });
  s.addText([{ text: b[0], options: { bold: true, color: C.INK, fontSize: 11.5, breakLine: true } }, { text: b[1], options: { fontFace: MONO, fontSize: 10, color: C.RED, paraSpaceBefore: 5 } }], { x: x + 0.12, y: 4.05, w: 2.5, h: 0.85, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.25, w: 11.5, h: 1.05, fill: { color: C.DARK } });
s.addText("引导问题：你们团队的 Agent 系统，闭环断在哪一步？为什么？  ·  3-5 分钟讨论", { x: 0.92, y: 5.25, w: 11.5, h: 1.05, fontFace: FONT, fontSize: 13, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addNotes("这个讨论是承上启下——上半场讲了 Memory（Remember + Inject），下半场要讲 Observability（Observe + Collect）和 Evaluation（Evaluate）。让学员在这里停下来反思自己的系统。大多数团队会说\u201C我们有 log 但不怎么看\u201D或\u201C我们没有评估标准\u201D。这些答案恰好引出下半场的内容。控制在 4-5 分钟。");

// ---------- Slide 14: 可观测性三支柱 ----------
s = contentSlide(p, 14, N, "Metrics / Logs / Traces — What / When / Why", "Observability · 三支柱");
const pillars = [
  { t: "Metrics", q: "What", d: "可聚合数值 / dashboard / alerting", det: "12 个核心指标", c: C.BLUE },
  { t: "Logs", q: "When", d: "结构化 JSON · trace_id / agent_id / event", det: "不是 print 语句！", c: C.ORANGE },
  { t: "Traces", q: "Why", d: "OpenTelemetry spans · 跨边界 trace_id", det: "找到根因", c: C.RED },
];
pillars.forEach((pl, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 3.6, h: 0.55, fill: { color: pl.c } });
  s.addText([{ text: pl.t + "  ", options: { bold: true, fontSize: 14, color: C.WHITE } }, { text: "(" + pl.q + ")", options: { fontSize: 12, color: "FFFFFF" } }], { x: x + 0.15, y: 1.75, w: 3.4, h: 0.55, fontFace: FONT, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 3.6, h: 2.4, fill: { color: C.LIGHT } });
  s.addText([{ text: pl.d, options: { fontSize: 11.5, color: C.INK, breakLine: true } }, { text: pl.det, options: { fontSize: 11, italic: true, color: C.RED, bold: true, paraSpaceBefore: 12 } }], { x: x + 0.18, y: 2.45, w: 3.3, h: 2.2, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.85, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("递进关系：Metrics 发现 → Logs 定位时间窗口 → Traces 找根因", { x: 0.92, y: 4.85, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addText("缺一不可：只 Metrics = 知道坏但不知为何 · 只 Logs = 淹没细节找不到方向 · 只 Traces = 能 debug 无法监控趋势。", { x: 0.92, y: 5.55, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 12, italic: true, color: C.GRAY, align: "center", valign: "top" });
s.addNotes("问观众：\u201C你们现在的 Agent 系统有几根支柱？\u201D大多数团队有 logs（虽然可能是 print 语句），少数有 metrics，极少有 traces。强调 structured log 的重要性——print(\"tool called: xxx\") 在 debug 时毫无用处，因为你无法 grep、无法聚合、无法关联。每一条 log 都应该是一个 JSON object，带有 trace_id 可以串联整个请求链路。");

// ---------- Slide 15: 12 个核心指标 ----------
s = contentSlide(p, 15, N, "Task × Loop × System 三维 Metrics", "Observability · 12 个核心指标");
const m12 = [
  ["TASK", C.BLUE, [["task_success_rate", "> 85%"], ["task_duration_s", "< 120s"], ["total_tokens", "< 50K"], ["cost_per_task", "< $0.50"]]],
  ["LOOP", C.ORANGE, [["iteration_depth", "< 10"], ["tool_call_count", "< 15"], ["tool_success_rate", "> 95%"], ["tool_latency_p95", "< 2s"]]],
  ["SYSTEM", C.GREEN, [["permission_denials", "< 2"], ["llm_call_count", "< 20"], ["token_io_ratio", "2:1 - 5:1"], ["cache_hit_rate", "> 60%"]]],
];
m12.forEach((row, i) => {
  const y = 1.75 + i * 1.45;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 1.4, h: 1.3, fill: { color: row[1] } });
  s.addText(row[0], { x: 0.92, y, w: 1.4, h: 1.3, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  row[2].forEach((m, j) => {
    const x = 2.45 + j * 2.5;
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 2.4, h: 1.3, fill: { color: C.LIGHT } });
    s.addText([{ text: m[0], options: { fontFace: MONO, fontSize: 10.5, color: C.INK, breakLine: true } }, { text: m[1], options: { fontSize: 14, bold: true, color: row[1], paraSpaceBefore: 12 } }], { x: x + 0.1, y: y + 0.1, w: 2.2, h: 1.1, fontFace: FONT, align: "center", valign: "top" });
  });
});
s.addText("异常信号：token_io_ratio 突变大 → 大量\u201C思考\u201D但产出少（可能循环） · cache_hit_rate ↓ → context 复用差 · denials 突增 → 联动 S3", { x: 0.92, y: 6.15, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: C.GRAY, align: "center" });
s.addNotes("不要逐个念指标，而是分组讲解逻辑。\u201CTask 维度回答：用户的事儿办成了吗？花了多少？Loop 维度回答：Agent 内部运转正常吗？有没有在空转？System 维度回答：基础设施层面有没有问题？\u201D特别解释 token_io_ratio——如果这个比值突然变大，说明 Agent 在大量\u201C思考\u201D但产出很少，可能陷入了某种循环。");

// ---------- Slide 16: Trace 实战 ----------
s = contentSlide(p, 16, N, "Real-World Trace — 从 Session 到 MCP Call", "Observability · Trace 实战");
codeBox(p, s, [
  { text: "Session Span (sess_abc123, 45.2s)", opt: { color: C.ORANGE, bold: true } },
  { text: "└── Turn Span (turn_1, 12.3s)", opt: { color: "8FBFE8" } },
  { text: "│   ├── LLM Inference (3.2s, in=4200, out=850)", opt: { color: "8FD19E" } },
  { text: "│   ├── Tool: read_file (0.05s, /src/app.ts)", opt: { color: "8FD19E" } },
  { text: "│   ├── LLM Inference (2.8s, in=5100, out=1200)", opt: { color: "8FD19E" } },
  { text: "│   └── Tool: edit_file (0.02s, lines=5)", opt: { color: "8FD19E" } },
  { text: "└── Turn Span (turn_2, 8.1s)", opt: { color: "8FBFE8" } },
  { text: "    ├── LLM Inference (2.1s)", opt: { color: "8FD19E" } },
  { text: "    ├── Tool: bash (1.8s, npm test, exit=0)", opt: { color: "8FD19E" } },
  { text: "    └── LLM Inference (1.5s) → end_turn", opt: { color: "E8A33D" } },
], { x: 0.92, y: 1.75, w: 7.5, h: 3.5, fontSize: 10.5 });
s.addText([{ text: "Span 关键属性", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } }, ...["trace_id / span_id / parent_span_id", "name / start_time / duration_ms / status", "tool.name / input / result.size", "agent.turn / agent.step"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 5 } }))], { x: 8.7, y: 1.75, w: 3.7, h: 3.5, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.45, w: 11.5, h: 0.95, fill: { color: C.GREEN } });
s.addText("有 trace：3 分钟定位根因（turn_3 缺关键文件 → read_file 在 turn_2 返回空）  ·  无 trace：3 天盲猜", { x: 0.92, y: 5.45, w: 11.5, h: 0.95, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("这里故意展示完整的 trace 结构——因为很多人对\u201CAgent tracing\u201D的理解停留在概念层。看到实际数据你会发现：一个 45 秒的 session 里有 2 个 turn，每个 turn 有 2-3 次 LLM 推理和 1-2 次工具调用。trace 让你看到每一步花了多长时间、输入是什么、输出是什么。回到灾难场景 2：\u201C团队花了 3 天 debug\u201D——如果有 trace，点开 → 看到第 3 个 Turn 出错 → 看到 Agent 选了错误的 Tool → 看到参数传错了。3 天变 3 分钟。");

// ---------- Slide 17: 四级告警 ----------
s = contentSlide(p, 17, N, "Threshold → Anomaly → Pattern → Critical", "Observability · 四级告警体系");
const lvls = [
  ["L1 · Threshold", "简单规则：success_rate < 90% / cost > $X", "已知问题", C.GREEN],
  ["L2 · Anomaly", "3-sigma 偏差 / token 突增 / 工具异常", "未知问题", "E0A000"],
  ["L3 · Pattern", "重复失败 / 循环检测 / 系统性故障", "系统性问题", C.ORANGE],
  ["L4 · Critical", "Sandbox escape / 危险命令 / 用户连续拒绝", "立即人工介入", C.RED],
];
lvls.forEach((l, i) => {
  const w = 4.0 + i * 1.5;
  const x = 0.92 + (10 - w) / 2;
  const y = 1.75 + i * 0.7;
  s.addShape(p.shapes.RECTANGLE, { x, y, w, h: 0.6, fill: { color: l[3] } });
  s.addText([{ text: l[0] + "   ", options: { bold: true, fontSize: 12.5, color: C.WHITE } }, { text: l[1], options: { fontSize: 10.5, color: "FFFFFF" } }], { x: x + 0.1, y, w: w - 0.2, h: 0.6, fontFace: FONT, valign: "middle" });
  s.addText(l[2], { x: x + w + 0.2, y, w: 3, h: 0.6, fontFace: FONT, fontSize: 11, italic: true, color: l[3], bold: true, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.7, w: 11.5, h: 1.7, fill: { color: C.DARK } });
s.addText([{ text: "行业数据 · LangChain State of AI Agents 2025", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "89% 团队有 observability  ·  仅 52% 做 systematic evaluation", options: { fontSize: 13, color: C.WHITE, breakLine: true, paraSpaceBefore: 10 } }, { text: "37% gap = 行业最大的 ROI 机会  ·  看到了 ≠ 理解了", options: { fontSize: 14, bold: true, color: C.ORANGE, paraSpaceBefore: 10 } }], { x: 1.12, y: 4.85, w: 11.1, h: 1.4, fontFace: FONT, valign: "top" });
s.addNotes("讲 Level 4 时语气要严肃：\u201C如果你的 Agent 试图执行 rm -rf 或者尝试访问 sandbox 之外的文件系统，这不是发个 Slack 通知就够的——需要立即停止执行并通知安全团队。\u201D然后讲 LangChain 的数据：89% 的人说\u201C我能看到 Agent 在做什么\u201D，但只有 52% 的人说\u201C我知道它做得好不好\u201D。看到了不等于理解了。这 37% 的 gap 就是为什么我们需要 Evaluation。");

// ---------- Slide 18: 三级评估体系 ----------
s = contentSlide(p, 18, N, "Step / Trajectory / Task — 从微观到宏观", "Evaluation · 三级评估体系");
const evalLvls = [
  { t: "Step-level", q: "选对 tool 吗？参数对吗？执行成功？", freq: "每步", cost: "低（规则匹配）", c: C.GREEN, ex: "该 read_file 却用 bash cat → step error" },
  { t: "Trajectory-level", q: "路径高效吗？走弯路了吗？", freq: "每个 task 完成后", cost: "中（efficiency / repeat / recovery）", c: C.ORANGE, ex: "简单任务 15 步，最优 5 步 → 效率问题" },
  { t: "Task-level", q: "用户目标达成了吗？", freq: "每个 task", cost: "高（success / time / cost / 满意度）", c: C.RED, ex: "代码能跑但不是用户要的 → task failure" },
];
evalLvls.forEach((e, i) => {
  const y = 1.75 + i * 1.2;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 3.0, h: 1.05, fill: { color: e.c } });
  s.addText([{ text: e.t, options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: e.freq, options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }, { text: e.cost, options: { fontSize: 10, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: 1.05, y: y + 0.08, w: 2.8, h: 0.9, fontFace: FONT, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.05, y, w: 8.35, h: 1.05, fill: { color: C.LIGHT } });
  s.addText([{ text: e.q, options: { bold: true, fontSize: 12, color: C.INK, breakLine: true } }, { text: e.ex, options: { fontSize: 10.5, italic: true, color: C.GRAY, paraSpaceBefore: 8 } }], { x: 4.2, y: y + 0.08, w: 8.05, h: 0.9, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.4, w: 11.5, h: 1.0, fill: { color: C.DARK } });
s.addText([{ text: "Step 正确 ≠ Trajectory 高效 ≠ Task 成功", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "类比：Step = 动作姿势  ·  Trajectory = 战术路线  ·  Task = 比分赢了没", options: { fontSize: 12, color: C.WHITE, paraSpaceBefore: 8 } }], { x: 1.12, y: 5.55, w: 11.1, h: 0.85, fontFace: FONT, valign: "top" });
s.addNotes("很多团队只做 step-level（工具调用成功率）。这就像只看运动员每个动作标不标准，不看比赛结果。一个球员可以每个动作都标准，战术执行也没偏差，但如果教练的策略本身是错的，比赛还是输。所以三级评估都要做——而且 task-level 的权重应该最高。");

// ---------- Slide 19: LLM-as-Judge 设计 ----------
s = contentSlide(p, 19, N, "用 LLM 评估 LLM — Prompt Template + Rubric", "Evaluation · LLM-as-Judge 设计");
codeBox(p, s, [
  { text: "You are evaluating an AI agent's response.", opt: { color: C.ORANGE, bold: true } },
  { text: "## Task: {original_user_request}", opt: { color: "8FBFE8" } },
  { text: "## Actions: {trajectory_summary}", opt: { color: "8FBFE8" } },
  { text: "## Output: {agent_response}", opt: { color: "8FBFE8" } },
  { text: "## Rubric (Score 1-5):", opt: { color: C.ORANGE, bold: true } },
  { text: "  1. Correctness — does code work?", opt: { color: "8FD19E" } },
  { text: "  2. Efficiency — direct or wandering?", opt: { color: "8FD19E" } },
  { text: "  3. Safety — risky ops without checks?", opt: { color: "8FD19E" } },
  { text: "  4. Communication — explained clearly?", opt: { color: "8FD19E" } },
  { text: "## Output: {correctness, efficiency, safety, communication, overall, reasoning}", opt: { color: "E8A33D" } },
], { x: 0.92, y: 1.75, w: 7.4, h: 3.5, fontSize: 10 });
styledTable(p, s, [
  [hc("方法"), hc("准确率"), hc("成本")],
  ["Human", "Gold", "$10-50/h"],
  ["规则", "结构性", "几乎免费"],
  ["LLM-Judge", "85% of human", "$0.01-0.05"],
], { x: 8.6, y: 1.75, w: 3.8, colW: [1.5, 1.4, 0.9], rowH: 0.45, fontSize: 11 });
s.addText("Anti-bias", { x: 8.6, y: 4.0, w: 3.8, h: 0.3, fontFace: FONT, fontSize: 12, bold: true, color: C.RED });
const ab = ["不同模型 judge", "多 judge 投票（中位数）", "每月 50 cases human 校准"];
ab.forEach((a, i) => {
  const y = 4.35 + i * 0.32;
  s.addText("• " + a, { x: 8.7, y, w: 3.7, h: 0.3, fontFace: FONT, fontSize: 10.5, color: C.INK, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.45, w: 11.5, h: 0.9, fill: { color: C.DARK } });
s.addText("关键：rubric 设计 — 每维度有明确 1-5 定义 + 正负面示例 + 与业务对齐  ·  不是\u201C好坏\u201D模糊判断", { x: 0.92, y: 5.45, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 12.5, color: C.ORANGE, align: "center", valign: "middle" });
s.addNotes("LLM-as-Judge 的关键不是\u201C用 LLM 打分\u201D——而是 rubric 的设计。如果你的 rubric 是\u201C评价这个回答好不好\u201D，结果会非常不稳定。但如果你拆解为 4 个明确维度、每个维度有 1-5 的具体定义，一致性会大幅提升。Anti-bias 很重要——用 Claude 评估 Claude 的输出会有\u201C自我认同\u201D偏差。最佳实践：用不同模型做 judge。");

// ---------- Slide 20: LLM-as-Judge 校准 ----------
s = contentSlide(p, 20, N, "Judge 的结果可信吗？— 校准方法", "Evaluation · LLM-Judge 校准");
codeBox(p, s, [
  { text: "# Judge Calibration 5 步", opt: { color: C.ORANGE, bold: true } },
  { text: "1. Gold Standard Set: 50-100 cases 人工标注", opt: { color: "8FD19E" } },
  { text: "2. LLM Judge 对同批 cases 打分", opt: { color: "8FD19E" } },
  { text: "3. 计算 Cohen's Kappa（人机一致性）", opt: { color: "8FBFE8" } },
  { text: "   κ > 0.8: 优秀  ·  0.6-0.8: 良好", opt: { color: "8FBFE8" } },
  { text: "   κ < 0.6: 改 rubric / 换 judge", opt: { color: "E8736A" } },
  { text: "4. 分析 disagreement → 改 rubric", opt: { color: "8FD19E" } },
  { text: "5. 重复直到 κ > 0.75", opt: { color: "8FD19E" } },
], { x: 0.92, y: 1.75, w: 6.5, h: 3.0, fontSize: 10.5 });
const conf = [["3 judges 一致", "high → 直接使用", C.GREEN], ["2:1 分歧", "medium → 多数 + 标记", "E0A000"], ["3 都不同", "low → human review", C.RED]];
conf.forEach((c, i) => {
  const y = 1.75 + i * 0.55;
  s.addShape(p.shapes.RECTANGLE, { x: 7.7, y, w: 4.7, h: 0.5, fill: { color: c[2] } });
  s.addText([{ text: c[0] + "   ", options: { bold: true, fontSize: 11.5, color: C.WHITE } }, { text: c[1], options: { fontSize: 10.5, color: "FFFFFF" } }], { x: 7.85, y, w: 4.5, h: 0.5, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 7.7, y: 3.5, w: 4.7, h: 1.25, fill: { color: C.DARK } });
s.addText([{ text: "成本对比", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "3-judge 投票：$0.03-0.15", options: { fontSize: 11, color: C.WHITE, breakLine: true, paraSpaceBefore: 5 } }, { text: "Human：$2-5  ·  约 1/50", options: { fontSize: 11, color: C.WHITE } }], { x: 7.88, y: 3.62, w: 4.4, h: 1.05, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.05, w: 11.5, h: 1.3, fill: { color: "FBEAE5" } });
s.addText([{ text: "实践建议", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "保留 5% cases 走 human review  ·  监控 judge 一致性趋势  ·  每月 recalibration（模型更新可能改变 judge 行为）", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 8 } }], { x: 1.12, y: 5.18, w: 11.1, h: 1.1, fontFace: FONT, valign: "top" });
s.addNotes("校准是 LLM-as-Judge 系统的命门。如果你不做校准就直接用 LLM 打分，你甚至不知道分数是否可信。50 个 gold standard cases 不多——花一个下午让团队人工标注就够了。然后定期检查 Cohen's Kappa——如果低于 0.6，说明你的 rubric 有歧义，LLM 的理解和人类不一致。这是一个迭代过程。");

// ---------- Slide 21: Drift Detection ----------
s = contentSlide(p, 21, N, "最危险的不是崩溃 — 是慢慢变差", "Evaluation · Drift Detection");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.7, w: 11.5, h: 0.55, fill: { color: C.RED } });
s.addText("Drift = 每次变化 < 告警阈值，但累积效应显著  ·  原因：模型更新 / prompt 累积 / 记忆退化 / 外部 API", { x: 0.92, y: 1.7, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const detect = [
  ["Sliding Window", "最近 7 天 vs 前 7 天 · 多指标同时 ↓ > 3% → drift alert", C.BLUE],
  ["Baseline Regression", "维护黄金基线 · 持续 3 天 < 95% baseline → alert", C.ORANGE],
  ["Distribution Shift", "工具分布 / 路径长度 / token 消耗 → KL/JS divergence (leading indicator)", C.GREEN],
];
detect.forEach((d, i) => {
  const y = 2.45 + i * 0.85;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 11.5, h: 0.75, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.14, h: 0.75, fill: { color: d[2] } });
  s.addText([{ text: d[0] + "   ", options: { bold: true, fontSize: 12.5, color: d[2] } }, { text: d[1], options: { fontSize: 11, color: C.INK } }], { x: 1.18, y, w: 11.1, h: 0.75, fontFace: FONT, valign: "middle" });
});
s.addText("响应流程", { x: 0.92, y: 5.1, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const resp = [["告警", "标记可能原因", C.BLUE], ["A/B Test", "new vs baseline", C.ORANGE], ["确认", "回滚 / 调查 / 自调", C.RED]];
resp.forEach((r, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 5.5, w: 3.6, h: 0.85, fill: { color: r[2] } });
  s.addText([{ text: r[0], options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: r[1], options: { fontSize: 10.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.15, y: 5.6, w: 3.3, h: 0.7, fontFace: FONT, align: "center", valign: "top" });
  if (i < 2) s.addShape(p.shapes.LINE, { x: x + 3.6, y: 5.92, w: 0.25, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
});
s.addNotes("回到灾难场景 3：\u201C3 个月内质量下降 20%，没人注意到\u201D。如果有 drift detection，第一周就会触发告警。为什么单指标不够？因为每次变化可能只有 1-2%——在正常波动范围内。但如果你看 7 天滑动窗口，5 个指标同时下降 1-2%——这不是巧合，是 drift。Distribution shift 是最早的信号——Agent 的行为模式先变化，然后质量才下降。");

// ---------- Slide 22: Drift 实际案例 ----------
s = contentSlide(p, 22, N, "一次真实 Drift 事件的全生命周期", "Evaluation · Drift 案例");
const tl = [
  ["Day 0", "Provider 发布 minor version update（用户无感知）", "—", C.GRAY],
  ["Day 1", "tool_call_count 8 → 10（+25%）— 先行指标", "未达告警", "E0A000"],
  ["Day 3", "task_success_rate 92% → 88%（-4%）持续 3 天", "DRIFT ALERT", C.RED],
  ["Day 3", "自动 A/B test 启动：当前 vs 上周快照", "p < 0.05 确认", C.ORANGE],
  ["Day 4", "调查发现：模型 function calling 行为微妙改变", "找到根因", C.BLUE],
  ["Day 4", "修复：调 system prompt 强化 tool 格式要求", "部署", C.BLUE],
  ["Day 5", "指标恢复到 baseline", "✓", C.GREEN],
];
tl.forEach((t, i) => {
  const y = 1.7 + i * 0.55;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 1.0, h: 0.48, fill: { color: t[3] } });
  s.addText(t[0], { x: 0.92, y, w: 1.0, h: 0.48, fontFace: FONT, fontSize: 11.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 2.0, y, w: 8.0, h: 0.48, fill: { color: C.LIGHT } });
  s.addText(t[1], { x: 2.15, y, w: 7.7, h: 0.48, fontFace: FONT, fontSize: 11, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 10.1, y, w: 2.3, h: 0.48, fill: { color: t[3] } });
  s.addText(t[2], { x: 10.1, y, w: 2.3, h: 0.48, fontFace: FONT, fontSize: 10.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.6, w: 11.5, h: 0.75, fill: { color: C.DARK } });
s.addText("总修复周期：5 天  ·  无 detection → 可能 3 个月  ·  先行指标比滞后指标早 2 天", { x: 0.92, y: 5.6, w: 11.5, h: 0.75, fontFace: FONT, fontSize: 13, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addNotes("这个案例来源于真实事件的模式总结。模型提供方的 minor update 不会通知你——但它可能微妙地改变了模型的工具调用行为。如果你没有 drift detection，这种退化会一直持续直到用户投诉到你无法忽视。关键 takeaway：先行指标比滞后指标更有价值。tool_call_count 变了 = 模型的决策逻辑变了 = 迟早影响成功率。");

// ---------- Slide 23: 持续评估金字塔 ----------
s = contentSlide(p, 23, N, "Agent 评估的测试金字塔 + A/B Testing", "Evaluation · 持续评估");
styledTable(p, s, [
  [hc("层级"), hc("频率"), hc("成本"), hc("方法")],
  [{ text: "Step-level", options: { bold: true, color: C.GREEN } }, "常驻", "最低", "规则匹配"],
  [{ text: "Trajectory", options: { bold: true, color: C.BLUE } }, "每日", "中", "LLM-as-Judge"],
  [{ text: "End-to-end", options: { bold: true, color: C.ORANGE } }, "每次发布", "高", "Gold standard set"],
  [{ text: "Benchmarks", options: { bold: true, color: C.RED } }, "每月", "最高", "学术评估集"],
], { x: 0.92, y: 1.75, w: 6.4, colW: [1.7, 1.6, 1.4, 1.7], rowH: 0.5, fontSize: 11.5 });
codeBox(p, s, [
  { text: "# A/B Testing 流程", opt: { color: C.ORANGE, bold: true } },
  { text: "10% → new, 90% → baseline", opt: { color: "8FD19E" } },
  { text: "观察 3 天 → 无 regression?", opt: { color: "8FD19E" } },
  { text: "  Yes: 50/50 → 7 天 → full", opt: { color: "8FBFE8" } },
  { text: "  No:  自动回滚 + 告警", opt: { color: "E8736A" } },
  { text: "# 最低样本：30/组", opt: { color: "8C9AA6" } },
], { x: 7.6, y: 1.75, w: 4.8, h: 2.5, fontSize: 10.5 });
s.addText("Gold Standard Test Set 规模建议", { x: 0.92, y: 4.65, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const sets = [["MVP", "50-100", C.GREEN], ["成熟产品", "500-1000", C.ORANGE], ["大规模", "5000+", C.RED]];
sets.forEach((st, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 5.05, w: 3.6, h: 0.95, fill: { color: st[2] } });
  s.addText([{ text: st[0], options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: st[1] + " cases", options: { fontSize: 16, bold: true, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.15, y: 5.15, w: 3.3, h: 0.8, fontFace: FONT, align: "center", valign: "top" });
});
s.addText("维护：每月更新 10%（淘汰过时 + 补充新场景）  ·  Regression：> 5% degradation → alert + 回滚", { x: 0.92, y: 6.1, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: C.GRAY, align: "center" });
s.addNotes("强调\u201C频率与成本的反向关系\u201D——和传统软件测试的 test pyramid 类似。Step-level 可以用规则做（便宜），但 end-to-end 需要实际跑 Agent（贵）。A/B testing 的 30 samples minimum 是一个实用数字——不要因为\u201C统计学课本说要 1000 samples\u201D就不做 A/B，30 个足以发现方向性问题。");

// ---------- Slide 24: 加权质量分 + Ground Truth ----------
s = contentSlide(p, 24, N, "Quality Score 公式 + 三种评估来源", "Evaluation · 加权质量分");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 11.5, h: 0.7, fill: { color: C.DARK } });
s.addText("Quality = task_success × 0.4 + trajectory × 0.3 + step × 0.2 + cost × 0.1", { x: 0.92, y: 1.75, w: 11.5, h: 0.7, fontFace: MONO, fontSize: 14, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
const weights = [["Task Success", "0.4", C.RED], ["Trajectory", "0.3", C.ORANGE], ["Step Accuracy", "0.2", C.BLUE], ["Cost", "0.1", C.GREEN]];
weights.forEach((w, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.65, w: 2.7, h: 0.6, fill: { color: w[2] } });
  s.addText([{ text: w[0] + "  ", options: { bold: true, fontSize: 11.5, color: C.WHITE } }, { text: w[1], options: { bold: true, fontSize: 14, color: "FFFFFF" } }], { x, y: 2.65, w: 2.7, h: 0.6, fontFace: FONT, align: "center", valign: "middle" });
});
styledTable(p, s, [
  [hc("来源"), hc("优势"), hc("劣势"), hc("适用")],
  [{ text: "Human Annotation", options: { bold: true } }, "Gold standard", "贵 / 慢", "建立 baseline"],
  [{ text: "LLM-as-Judge", options: { bold: true } }, "可扩展 / 便宜", "有偏差", "日常大规模"],
  [{ text: "User Feedback", options: { bold: true } }, "最真实", "稀疏 / 偏差", "方向验证"],
], { x: 0.92, y: 3.45, w: 11.5, colW: [2.4, 2.6, 2.4, 4.1], rowH: 0.5, fontSize: 11 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.45, w: 11.5, h: 0.95, fill: { color: "FBEAE5" } });
s.addText([{ text: "User Feedback 信号", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "显式：thumbs up/down · rating  ·  隐式（多 10x）：undo Agent 修改 / 重述同一请求", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.6, w: 11.1, h: 0.75, fontFace: FONT, valign: "top" });
s.addNotes("关于权重，可以引发讨论：\u201C你们觉得在你们的场景下，这四个权重应该怎么调？\u201D比如内部工具 cost 不重要 → 0.4/0.3/0.3/0；面向消费者的产品体验至上 → 0.5/0.2/0.2/0.1。关于 User Feedback，隐式信号是金矿——如果用户执行了 undo，这比他点 thumbs down 更真实。");

// ---------- Slide 25: 完整闭环五步 ----------
s = contentSlide(p, 25, N, "Observe → Collect → Evaluate → Remember → Inject", "完整闭环 · 五步");
const cloop = [["1 · Observe", "Metrics/Logs/Traces 记录每次行为", C.BLUE], ["2 · Collect", "提取有价值信号（不是存 log）", "2E4A63"], ["3 · Evaluate", "三级评估 Step/Trajectory/Task", C.ORANGE], ["4 · Remember", "成功/失败写入 Memory", C.RED], ["5 · Inject", "下次 session 注入 Context (回 S1)", C.GREEN]];
cloop.forEach((c, i) => {
  const angle = (i * 72 - 90) * Math.PI / 180;
  const cx = 6.65, cy = 3.7, r = 1.65;
  const x = cx + r * Math.cos(angle) - 1.2;
  const y = cy + r * Math.sin(angle) - 0.4;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 2.4, h: 0.8, fill: { color: c[2] } });
  s.addText([{ text: c[0], options: { bold: true, fontSize: 11, color: C.WHITE, breakLine: true } }, { text: c[1], options: { fontSize: 9, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: x + 0.1, y: y + 0.06, w: 2.2, h: 0.7, fontFace: FONT, align: "center", valign: "top" });
});
s.addShape(p.shapes.OVAL, { x: 5.55, y: 3.4, w: 2.2, h: 0.6, fill: { color: C.DARK } });
s.addText("Continuous\nImprovement", { x: 5.55, y: 3.4, w: 2.2, h: 0.6, fontFace: FONT, fontSize: 9.5, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
codeBox(p, s, [
  { text: "Turn 1: Agent 用错 API 格式", opt: { color: "E8A33D" } },
  { text: "  → Trace 记录 (Observe)", opt: { color: "8FBFE8" } },
  { text: "  → Step eval = error (Evaluate)", opt: { color: "8FBFE8" } },
  { text: "Turn 2: 用户纠正 → 完成", opt: { color: "8FD19E" } },
  { text: "  → Feedback memory (Remember, c=0.95)", opt: { color: "8FD19E" } },
  { text: "Session 2: hybrid retrieval → 命中", opt: { color: "8FD19E" } },
  { text: "  → 注入 context (Inject) → 一次对", opt: { color: "8FD19E" } },
  { text: "autoDream: 升级为 project memory", opt: { color: C.ORANGE } },
], { x: 0.92, y: 5.55, w: 11.5, h: 0.95, fontSize: 9.5 });
s.addNotes("这是整个 module 的\u201Caha moment\u201D。慢慢讲，走一遍完整的闭环。\u201C想象一下：Agent 犯了一个错，这个错误被 Observe 到了，被 Evaluate 为负面，被 Remember 为教训，下次被 Inject 进 context 作为\u2018不要这样做\u2019的约束。这就是从\u2018犯 5 次同一个错\u2019到\u2018犯 1 次就学会\u2019的区别。\u201D然后点明：\u201C注意最后一步 Inject 回到了 S1——Context Engineering。我们的五个系统不是线性的，是一个环。\u201D");

// ---------- Slide 26: 闭环质量指标 ----------
s = contentSlide(p, 26, N, "如何衡量闭环本身的质量", "闭环 · 质量指标");
styledTable(p, s, [
  [hc("指标"), hc("含义"), hc("目标")],
  [{ text: "Memory Hit Rate", options: { bold: true, color: C.BLUE } }, "检索出的记忆实际被使用的比率", { text: "> 60%", options: { color: C.GREEN, bold: true } }],
  [{ text: "Repeat Error Rate", options: { bold: true, color: C.RED } }, "同一错误跨 session 重复出现的频率", { text: "< 10%", options: { color: C.GREEN, bold: true } }],
  [{ text: "Feedback Integration Lag", options: { bold: true, color: C.ORANGE } }, "用户纠正 → 下次正确应用的延迟", { text: "< 2 sessions", options: { color: C.GREEN, bold: true } }],
  [{ text: "Consolidation Compression", options: { bold: true, color: "2E4A63" } }, "autoDream 压缩率（before / after）", { text: "3-5x", options: { color: C.GREEN, bold: true } }],
  [{ text: "Evaluation-Action Gap", options: { bold: true, color: C.GRAY } }, "评估发现问题 → 系统修正的时间", { text: "< 24h", options: { color: C.GREEN, bold: true } }],
], { x: 0.92, y: 1.75, w: 11.5, colW: [3.0, 5.5, 3.0], rowH: 0.55, fontSize: 11.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.0, w: 5.6, h: 1.4, fill: { color: C.GREEN } });
s.addText([{ text: "✓ 健康信号", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "Repeat Error Rate 持续↓ → 学习中", options: { fontSize: 11, color: "FFFFFF", breakLine: true, paraSpaceBefore: 6 } }, { text: "Hit Rate 稳定 > 60% → 检索准", options: { fontSize: 11, color: "FFFFFF", breakLine: true, paraSpaceBefore: 4 } }, { text: "Lag = 1 session → 立即生效", options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: 1.12, y: 5.15, w: 5.2, h: 1.2, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 5.0, w: 5.6, h: 1.4, fill: { color: C.RED } });
s.addText([{ text: "✗ 不健康信号", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "Repeat Error 不降 → 闭环断裂", options: { fontSize: 11, color: "FFFFFF", breakLine: true, paraSpaceBefore: 6 } }, { text: "Hit Rate < 30% → consolidation 问题", options: { fontSize: 11, color: "FFFFFF", breakLine: true, paraSpaceBefore: 4 } }, { text: "Gap > 7 days → 组织问题非技术", options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: 7.02, y: 5.15, w: 5.2, h: 1.2, fontFace: FONT, valign: "top" });
s.addNotes("这些 meta-metrics 可能是最被忽视的。大家会监控 Agent 的性能指标，但很少监控\u201C反馈系统本身是否有效\u201D。Repeat Error Rate 是最直接的指标——如果 Agent 在不同 session 中犯同样的错，说明你的闭环不工作。这就像一个学生考试犯了同样的错两次——不是他笨，是他的\u201C学习系统\u201D有问题。");

// ---------- Slide 27: 系统接口 ----------
s = contentSlide(p, 27, N, "S4 在五大系统中的数据流", "系统接口");
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.5, y: 3.4, w: 2.3, h: 1.1, fill: { color: C.ORANGE }, line: { color: C.ORANGE }, rectRadius: 0.1 });
s.addText("S4\nFeedback & State", { x: 5.5, y: 3.4, w: 2.3, h: 1.1, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const conn = [
  { x: 5.5, y: 1.75, t: "S1 ↔ S4", d: "记忆闭环：检索注入 + 写入新记忆 + autoDream", c: C.BLUE },
  { x: 9.7, y: 3.4, t: "S2 → S4", d: "工具观测：每次 tool call 产生 trace span", c: C.GREEN },
  { x: 5.5, y: 5.15, t: "S3 ↔ S4", d: "安全闭环：事件分析 → 策略调整反馈", c: C.RED },
  { x: 1.3, y: 3.4, t: "S4 → S5", d: "控制反馈：drift alert → 降级 / cost → budget", c: C.DARK },
];
conn.forEach((k) => {
  s.addShape(p.shapes.RECTANGLE, { x: k.x, y: k.y, w: 2.3, h: 1.1, fill: { color: k.c } });
  s.addText([{ text: k.t, options: { bold: true, fontSize: 12, color: C.WHITE, breakLine: true } }, { text: k.d, options: { fontSize: 9.5, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: k.x + 0.12, y: k.y + 0.08, w: 2.06, h: 0.95, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.LINE, { x: 6.65, y: 2.85, w: 0, h: 0.55, line: { color: C.GRAY, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 7.8, y: 3.95, w: 1.9, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 6.65, y: 4.5, w: 0, h: 0.65, line: { color: C.GRAY, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 3.6, y: 3.95, w: 1.9, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addText("S4 = Agent 系统的\u201C神经系统\u201D — 收集所有信号，处理后反馈给需要的系统", { x: 0.92, y: 6.4, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 12, italic: true, color: C.GRAY, align: "center" });
s.addNotes("S4 是整个系统的\u201C神经系统\u201D——它从所有其他系统收集信号，处理后反馈给需要的系统。没有 S4，其他四个系统就是各自独立运转的模块；有了 S4，它们才成为一个有机的整体。这也是为什么 S4 在架构图中处于\u201C中间层\u201D——它连接上层的运行时三件套（S1/S2/S3）和下层的控制面（S5）。");

// ---------- Slide 28: 总结 ----------
s = contentSlide(p, 28, N, "S4 核心回顾 — 带走这 5 条", "总结 · S4 全景");
const tk = [
  ["1", "三层记忆", "Working（模型）/ Short-term / Long-term — Harness 管后两个", C.BLUE],
  ["2", "可写记忆 + Gating", "Confidence 门槛 + 用户控制 + 安全检测", C.ORANGE],
  ["3", "autoDream", "Orient → Gather → Consolidate → Prune", C.GREEN],
  ["4", "三支柱 + 四级告警", "Metrics/Logs/Traces + Threshold→Critical", C.RED],
  ["5", "三级评估 + Drift", "Step/Trajectory/Task + 滑动窗口检测静默退化", "2E4A63"],
];
tk.forEach((t, i) => {
  const y = 1.75 + i * 0.6;
  s.addShape(p.shapes.OVAL, { x: 0.92, y, w: 0.55, h: 0.55, fill: { color: t[3] } });
  s.addText(t[0], { x: 0.92, y, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 16, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 1.65, y, w: 10.75, h: 0.5, fill: { color: C.LIGHT } });
  s.addText([{ text: t[1] + "   ", options: { bold: true, fontSize: 12.5, color: C.INK } }, { text: t[2], options: { fontSize: 11, color: C.GRAY } }], { x: 1.8, y, w: 10.55, h: 0.5, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 0.85, fill: { color: C.DARK } });
s.addText("\u201CAgent 的竞争优势不在于单次对话多聪明，而在于它能不能从每一次对话中变得更聪明。\u201D", { x: 0.92, y: 4.95, w: 11.5, h: 0.85, fontFace: FONT, fontSize: 13.5, bold: true, italic: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.95, w: 7.0, h: 0.55, fill: { color: "FBEAE5" } });
s.addText("Mini-Lab：confidence gating · 注入错误记忆观察检测 · 触发 drift", { x: 1.12, y: 5.95, w: 6.7, h: 0.55, fontFace: FONT, fontSize: 11, color: C.RED, valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 8.1, y: 5.95, w: 4.3, h: 0.55, fill: { color: C.GREEN } });
s.addText("S1✓ S2✓ S3✓ S4✓ → S5", { x: 8.1, y: 5.95, w: 4.3, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("总结时不要只是复述内容。用一句话收束：\u201C如果你只记住一件事，记住这个：Agent 系统的竞争优势不在于单次对话多聪明，而在于它能不能从每一次对话中变得更聪明。这就是 Feedback Loop 的价值。\u201D然后预告 S5：\u201C下一个模块是控制面——S5 熵管理。如果说 S4 是\u2018感知和学习\u2019，S5 就是\u2018决策和行动\u2019——基于 S4 提供的信号，S5 决定什么时候继续、什么时候停止、什么时候重试、什么时候升级。\u201D");

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
module.exports = {};

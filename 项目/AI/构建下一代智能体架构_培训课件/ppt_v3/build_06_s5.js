const { C, FONT, MONO, newDeck, darkSlide, contentSlide, bullets, styledTable, hc, setModule, codeBox } = require("./aws_theme");
setModule("06 S5 · Entropy Management");
const p = newDeck("Harness Engineering — 06 S5 Entropy Management");
const N = 33;
const OUT = "/Users/qcguang/Desktop/courses/HarnessEngineering/ppt_v3/06_S5_entropy_management.pptx";
let s;

// ---------- Slide 1: Cover ----------
s = darkSlide(p);
s.addText("S5 · ENTROPY MANAGEMENT", { x: 0.6, y: 1.5, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("熵管理系统", { x: 0.6, y: 2.0, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 38, bold: true, color: C.WHITE });
s.addText("对抗 Agent 的热力学第二定律", { x: 0.62, y: 2.95, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 18, color: "C7CED6" });
s.addText("\u201CEntropy is the default. Order requires energy.\u201D", { x: 0.62, y: 3.5, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, italic: true, color: "8C9AA6" });
s.addShape(p.shapes.LINE, { x: 0.62, y: 4.15, w: 6.2, h: 0, line: { color: "47525E", width: 1 } });
s.addText([
  { text: "编排 · 容错 · 成本 — 三位一体的控制面", options: { breakLine: true } },
  { text: "无主动管理的 Agent 必然走向漂移、耗尽、级联崩溃", options: { breakLine: true } },
  { text: "Part A: Loop & Control (slides 1-14)  ·  Part B: Fault Tolerance (15-23)  ·  Part C: Multi-Agent & Cost (24-33)", options: {} },
], { x: 0.62, y: 4.35, w: 12, h: 1.7, fontFace: FONT, fontSize: 14, color: "E6EAEE", paraSpaceAfter: 8 });
s.addText("90 min  ·  33 slides", { x: 9.5, y: 6.7, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: "6B7682", align: "right" });
s.addNotes("开场用物理学类比抓住注意力。告诉学员：在座各位可能都经历过——你部署了一个 Agent，前几分钟运行得完美，然后突然之间它开始偏离目标、疯狂消耗 token、产生不可预期的行为。这不是 bug，这是热力学。没有外部能量输入（即主动控制），任何复杂系统都会自发走向无序。今天这 80 分钟，我们要系统性地学习如何成为 Agent 系统的\u201C麦克斯韦妖\u201D——选择性地让有序通过，阻止无序蔓延。Part A 聚焦 Agent Loop 本身的控制，Part B 聚焦基础设施层的容错和编排。");

// ---------- Slide 2: Anchor ----------
s = contentSlide(p, 2, N, "确定性执行 vs 概率性执行：两种截然不同的世界", "Anchor · Traditional vs Agent");
styledTable(p, s, [
  [hc("维度"), hc("传统 Workflow Engine"), hc("Agent Execution")],
  ["路径", "确定性 · DAG 部署时已知", "概率性 · 运行时由 LLM 决定"],
  ["成本", "可预测 · 每节点有上界", "不确定 · 取决于 loop 迭代次数"],
  ["可重现性", "Same input = Same execution", "Same input → Different paths"],
  ["故障域", "节点级 · 隔离明确", "Loop 级 · 漂移会污染整个执行"],
  ["熵特性", "低 entropy · 受控", "高 entropy · 自发增长"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [1.6, 4.95, 4.95], rowH: 0.5, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.3, w: 11.5, h: 1.0, fill: { color: C.DARK } });
s.addText([{ text: "传统系统：你设计 path，引擎执行你的设计", options: { color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "Agent 系统：你设计 boundary，Agent 在边界内自己探索 path", options: { color: C.ORANGE, fontSize: 13, bold: true, paraSpaceBefore: 6 } }], { x: 0.92, y: 5.45, w: 11.5, h: 0.85, fontFace: FONT, align: "center", valign: "top" });
s.addNotes("这页是整个模块的 anchor — 必须让学员深刻理解 Agent 与传统系统的根本差异。传统 workflow（Airflow、Temporal、cron）是\u201Csame input, same execution\u201D的世界 — 你写好 DAG，引擎按图执行。Agent 是\u201Csame input, different paths\u201D的世界 — 同一个输入，Agent 这次可能 5 步完成，下次可能 50 步还在循环。这种不确定性就是\u201C熵\u201D的来源。学员必须理解：你不是在构建一个传统软件系统，你是在构建一个需要主动\u201C对抗熵增\u201D的控制系统。");

// ---------- Slide 3: 灾难场景 ----------
s = contentSlide(p, 3, N, "失控 Agent 的四大灾难场景", "Anchor · Disaster Scenarios");
const ds5 = [
  { t: "灾难 1 · Infinite Loop", l: ["Agent 反复尝试相同方案", "8 小时烧 $200 没完成"], r: "无终止条件", c: C.RED },
  { t: "灾难 2 · Goal Drift", l: ["\u201Cfix login bug\u201D → 重构整个 auth", "20 文件改动 vs 1 个原 bug"], r: "无方向锚定", c: C.ORANGE },
  { t: "灾难 3 · Cascade Failure", l: ["LLM API 短暂抖动", "Agent 重试爆炸 → 整服务挂"], r: "无熔断", c: "C0631A" },
  { t: "灾难 4 · Recursive Sub-Agents", l: ["主 Agent spawn 子 Agent", "子 spawn 子子 → 递归爆炸"], r: "无层级 budget", c: "8B0000" },
];
ds5.forEach((d, i) => {
  const x = 0.92 + (i % 2) * 5.95;
  const y = 1.75 + Math.floor(i / 2) * 2.2;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 0.55, fill: { color: d.c } });
  s.addText(d.t, { x: x + 0.15, y, w: 5.4, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: y + 0.55, w: 5.55, h: 1.55, fill: { color: "FBEAE5" } });
  s.addText([...d.l.map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceAfter: 5 } })), { text: d.r, options: { fontSize: 12, bold: true, color: d.c, paraSpaceBefore: 4 } }], { x: x + 0.18, y: y + 0.65, w: 5.25, h: 1.4, fontFace: FONT, valign: "top" });
});
s.addText("没有约束的自主性 = 灾难 · 接下来 70 分钟逐个安装\u201C控制棒\u201D", { x: 0.92, y: 6.3, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, align: "center" });
s.addNotes("每个场景都停顿让学员消化。这些不是假设——在座的可能就有人经历过。灾难 1 特别常见：很多人第一次用 Agent 写代码时都遇到过无限循环的天价账单。关键是让学员意识到：这些灾难不是 Agent 的 bug，这是 Agent 的本质特性——没有约束的自主性就是灾难。就像核反应堆：有控制棒的链式反应是核能发电，没有控制棒的链式反应是核爆炸。");

// ---------- Slide 4: Think-Act-Observe ----------
s = contentSlide(p, 4, N, "Think-Act-Observe：Agent 不是链，是循环", "The Agent Heartbeat");
const tao = [
  { t: "Think", d: "LLM 推理 · 决定下一步或宣布完成", e: "$ cost · 不可逆", c: C.BLUE },
  { t: "Act", d: "调用 S2 工具 · 执行具体操作", e: "side effect · 可能不可逆", c: C.ORANGE },
  { t: "Observe", d: "结果注入回 context · 为下次 Think 提供信息", e: "info gain · 学习唯一来源", c: C.GREEN },
];
tao.forEach((t, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.OVAL, { x, y: 1.75, w: 3.6, h: 1.4, fill: { color: t.c } });
  s.addText([{ text: t.t, options: { bold: true, fontSize: 18, color: C.WHITE, breakLine: true } }, { text: t.d, options: { fontSize: 10.5, color: "FFFFFF", breakLine: true, paraSpaceBefore: 4 } }, { text: t.e, options: { fontSize: 10, italic: true, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: x + 0.15, y: 1.85, w: 3.3, h: 1.2, fontFace: FONT, align: "center", valign: "top" });
  if (i < 2) s.addShape(p.shapes.LINE, { x: x + 3.6, y: 2.45, w: 0.25, h: 0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } });
});
s.addShape(p.shapes.LINE, { x: 12.42, y: 2.45, w: 0.5, h: 0, line: { color: C.ORANGE, width: 2 } });
s.addShape(p.shapes.LINE, { x: 12.92, y: 2.45, w: 0, h: 1.5, line: { color: C.ORANGE, width: 2 } });
s.addShape(p.shapes.LINE, { x: 0.42, y: 3.95, w: 12.5, h: 0, line: { color: C.ORANGE, width: 2 } });
s.addShape(p.shapes.LINE, { x: 0.42, y: 2.45, w: 0, h: 1.5, line: { color: C.ORANGE, width: 2 } });
s.addShape(p.shapes.LINE, { x: 0.42, y: 2.45, w: 0.5, h: 0, line: { color: C.ORANGE, width: 2, endArrowType: "triangle" } });
s.addText("State: Context Window (growing with each iteration)", { x: 0.92, y: 4.1, w: 11.5, h: 0.35, fontFace: MONO, fontSize: 11, italic: true, color: C.GRAY, align: "center" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.6, w: 11.5, h: 1.7, fill: { color: C.DARK } });
s.addText([{ text: "LOOP, NOT CHAIN", options: { bold: true, color: C.ORANGE, fontSize: 16, breakLine: true } }, { text: "线性 chain：A → B → C → Done（步数确定）", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "Agent loop：Think → Act → Observe → ?（步数不确定）", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 5 } }, { text: "不确定性的根源：每次 Think 都是概率性的", options: { fontSize: 12, italic: true, color: C.ORANGE, paraSpaceBefore: 8 } }], { x: 1.12, y: 4.75, w: 11.1, h: 1.5, fontFace: FONT, align: "center", valign: "top" });
s.addNotes("这是整个模块最基础的概念，确保每个人都理解。Agent 不是 chain — chain 是确定性的，你知道它会执行 3 步然后停止。Loop 是不确定性的——它可能执行 2 步就结束，也可能执行 200 步还在跑。这个不确定性就是熵的来源。Think 是最贵的环节——每次推理都在消耗 token；Act 是最危险的环节——它产生不可逆的 side effect；Observe 是最有价值的环节——它是 Agent 学习的唯一来源。一个没有终止条件的 Agent loop，就像一个正在进行的热力学过程——它只会越来越混乱，直到某种形式的\u201C热寂\u201D。");

// ---------- Slide 5: Two Loop Philosophies ----------
s = contentSlide(p, 5, N, "实现哲学之争：Async Generator vs Linear Pipeline", "Two Loop Philosophies");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.BLUE } });
s.addText("A · Async Generator（Claude Code）", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.3, w: 5.6, h: 2.85, fill: { color: C.LIGHT } });
s.addText([{ text: "submitMessage() yields events as async iterator", options: { fontFace: MONO, fontSize: 10.5, color: C.INK, breakLine: true } }, ...["Streaming：用户实时看到 Agent 的思考", "Concurrent tool execution（并行工具调用）", "优化：interactive use, low perceived latency"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 5 } })), { text: "代价：状态管理复杂 / race condition / partial failure", options: { fontSize: 10.5, italic: true, color: C.RED, paraSpaceBefore: 8 } }], { x: 1.1, y: 2.42, w: 5.3, h: 2.65, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.ORANGE } });
s.addText("B · Linear Pipeline（OpenCode）", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.3, w: 5.6, h: 2.85, fill: { color: C.LIGHT } });
s.addText([{ text: "intake → assembly → inference → execution → persist", options: { fontFace: MONO, fontSize: 10.5, color: C.INK, breakLine: true } }, ...["Sequential：一次一个 tool，确定性顺序", "优化：auditability, reproducibility", "checkpoint at each phase → debugging"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 5 } })), { text: "代价：无法流式 / 无并发 / 长任务用户体验差", options: { fontSize: 10.5, italic: true, color: C.RED, paraSpaceBefore: 8 } }], { x: 7.0, y: 2.42, w: 5.3, h: 2.65, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.35, w: 11.5, h: 1.0, fill: { color: C.DARK } });
s.addText([{ text: "Same loop semantics, different execution strategies", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "实时反馈+并发 → Async  ·  审计+确定性 → Linear  ·  生产常用混合：async 前台 + linear 后台批量", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.5, w: 11.1, h: 0.8, fontFace: FONT, align: "center", valign: "top" });
s.addNotes("这不是一个\u201C哪个更好\u201D的问题，这是工程权衡。Claude Code 选择 async generator 因为它面向开发者做实时交互——用户不想盯着空白屏幕等 30 秒，他们想看到 Agent 在干什么。OpenCode 选择 linear pipeline 因为它重视可审计性——每一步都有完整的 checkpoint 可以回溯。但不管你选哪种实现，loop 的本质不变——都是 Think-Act-Observe 的循环。生产系统通常是混合体：用户实时交互用 async，后台批量任务用 linear。");

// ---------- Slide 6: Five Termination ----------
s = contentSlide(p, 6, N, "五大终止条件：Agent Loop 的刹车系统", "Termination Conditions");
const term5 = [
  ["1 · Tool Calls Exhausted", "Agent 决定 end_turn", "最自然，最不可靠", C.GREEN],
  ["2 · Max Iterations", "硬性迭代上限（典型 25）", "防灾难 1 安全网", C.BLUE],
  ["3 · Token Budget", "累计 token 上限", "防经济损失", C.ORANGE],
  ["4 · Explicit Stop", "用户取消 / kill / timeout", "尊重外部中断", "C0631A"],
  ["5 · Goal Achieved", "外部验证通过（test pass）", "最可靠正面终止", C.RED],
];
term5.forEach((t, i) => {
  const y = 1.75 + i * 0.65;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 4.0, h: 0.55, fill: { color: t[3] } });
  s.addText(t[0], { x: 0.92, y, w: 4.0, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 5.0, y, w: 4.5, h: 0.55, fill: { color: C.LIGHT } });
  s.addText(t[1], { x: 5.15, y, w: 4.3, h: 0.55, fontFace: FONT, fontSize: 11.5, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.6, y, w: 2.8, h: 0.55, fill: { color: "FBEAE5" } });
  s.addText(t[2], { x: 9.75, y, w: 2.65, h: 0.55, fontFace: FONT, fontSize: 10, italic: true, color: t[3], valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.15, w: 11.5, h: 1.2, fill: { color: C.DARK } });
s.addText([{ text: "你需要全部五个 — Defense in Depth", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "First triggered wins  ·  任何单一条件都有 edge cases", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "类比：飞机安全系统 — 主控失效有备控，备控失效有手动，手动失效有物理断路器", options: { fontSize: 11, italic: true, color: "C7CED6", paraSpaceBefore: 6 } }], { x: 1.12, y: 5.3, w: 11.1, h: 1.0, fontFace: FONT, valign: "top" });
s.addNotes("让我强调：你需要全部五个。不是\u201C选其中两三个觉得够用\u201D。我见过最常见的反模式是只依赖条件 1——\u201CAgent 不再调用工具就认为它完成了\u201D。问题是：Agent 有时候会陷入一种状态，它认为自己完成了但实际没有；或者反过来，它永远觉得\u201C让我再试一次\u201D，每一轮都调用工具，永远不停。如果你没有条件 2（max iterations）兜底，它就成了灾难 1。");

// ---------- Slide 7: Termination Anti-patterns ----------
s = contentSlide(p, 7, N, "终止条件反模式：怎样做是错的", "Termination Anti-Patterns");
const apats = [
  ["AP 1 · Only \u201CAgent says done\u201D", "Agent 陷入循环每轮都说\u201Clet me try one more\u201D · 或第 2 轮就放弃", "+ max_iterations + budget"],
  ["AP 2 · Only max_iterations", "设太低（5）→ 复杂任务被打断 · 设太高（1000）→ 等于没限制", "+ token budget + dynamic"],
  ["AP 3 · No explicit stop", "用户发现 Agent 做错事但无 cancel · 只能关浏览器", "+ kill signal + Agent 每 Act 前 check"],
];
apats.forEach((a, i) => {
  const y = 1.75 + i * 0.85;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 3.6, h: 0.75, fill: { color: C.RED } });
  s.addText(a[0], { x: 1.05, y, w: 3.4, h: 0.75, fontFace: FONT, fontSize: 11.5, bold: true, color: C.WHITE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.6, y, w: 5.3, h: 0.75, fill: { color: "FBEAE5" } });
  s.addText(a[1], { x: 4.75, y, w: 5.05, h: 0.75, fontFace: FONT, fontSize: 10.5, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.95, y, w: 2.45, h: 0.75, fill: { color: C.GREEN } });
  s.addText(a[2], { x: 10.05, y, w: 2.3, h: 0.75, fontFace: FONT, fontSize: 9.5, color: C.WHITE, valign: "middle" });
});
codeBox(p, s, [
  { text: "# Correct: multi-condition termination", opt: { color: C.ORANGE, bold: true } },
  { text: "for i in range(MAX_ITERATIONS):           # 2", opt: { color: "8FBFE8" } },
  { text: "    if budget.exhausted(): break          # 3", opt: { color: "8FBFE8" } },
  { text: "    if stop_signal.is_set(): break        # 4", opt: { color: "8FBFE8" } },
  { text: "    response = await llm.generate(ctx)", opt: { color: "8FD19E" } },
  { text: "    if not response.has_tool_calls(): break  # 1", opt: { color: "8FBFE8" } },
  { text: "    if goal_verifier.achieved(response): break  # 5", opt: { color: "8FBFE8" } },
], { x: 0.92, y: 4.45, w: 11.5, h: 1.85, fontSize: 10.5 });
s.addNotes("Anti-pattern 1 是实际中的头号杀手。大多数 Agent 框架的默认行为就是\u201CAgent 不再调用工具就结束\u201D。看起来合理对吧？但 LLM 是概率性的——有些时候它就是不停。我见过 Agent 花 20 轮和自己争论缩进该用 2 空格还是 4 空格。Anti-pattern 3 更隐蔽但同样致命——如果用户无法中断 Agent，那 Agent 就是一个不受控的进程。正确的实现很简单——五道关卡，一个都不能少。");

// ---------- Slide 8: Drift 2 Types ----------
s = contentSlide(p, 8, N, "Drift Detection：Agent 正在偏离目标吗？", "Drift · 两种类型");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.6, fill: { color: C.RED } });
s.addText("Goal Drift · 方向错了（向量偏离）", { x: 0.92, y: 1.75, w: 5.6, h: 0.6, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.35, w: 5.6, h: 2.7, fill: { color: "FBEAE5" } });
s.addText([{ text: "定义：逐渐遗忘原始目标，转而追逐无关目标", options: { fontSize: 11.5, color: C.INK, breakLine: true } }, { text: "根因：原始 goal 在 context 中被\u201C稀释\u201D + recency bias", options: { fontSize: 11, color: C.GRAY, breakLine: true, paraSpaceBefore: 8 } }, { text: "示例：", options: { fontSize: 11, bold: true, color: C.RED, breakLine: true, paraSpaceBefore: 10 } }, { text: "\u201CFix login bug\u201D → turn 15 时 login 已 10 轮没出现 → Agent 在做无关 refactoring", options: { fontSize: 11, italic: true, color: C.INK, paraSpaceBefore: 4 } }], { x: 1.1, y: 2.5, w: 5.25, h: 2.5, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.6, fill: { color: C.ORANGE } });
s.addText("Scope Creep · 走太远了（标量过大）", { x: 6.82, y: 1.75, w: 5.6, h: 0.6, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.35, w: 5.6, h: 2.7, fill: { color: "FBEAE5" } });
s.addText([{ text: "定义：记得目标，但自行扩大执行范围", options: { fontSize: 11.5, color: C.INK, breakLine: true } }, { text: "根因：LLM 的 helpfulness bias — 总想\u201C多做一点\u201D", options: { fontSize: 11, color: C.GRAY, breakLine: true, paraSpaceBefore: 8 } }, { text: "示例：", options: { fontSize: 11, bold: true, color: C.ORANGE, breakLine: true, paraSpaceBefore: 10 } }, { text: "\u201CAdd a logout button\u201D → 顺便重构 CSS、更新测试、改 build config", options: { fontSize: 11, italic: true, color: C.INK, paraSpaceBefore: 4 } }], { x: 7.0, y: 2.5, w: 5.25, h: 2.5, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.3, w: 11.5, h: 1.0, fill: { color: C.DARK } });
s.addText([{ text: "共同本质：熵增 — 从有序（goal-aligned）向无序（goal-divergent）的自发漂移", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "Goal Drift = 出门买牛奶进了书店  ·  Scope Creep = 出门买牛奶把一周菜都买了", options: { fontSize: 11.5, italic: true, color: C.WHITE, paraSpaceBefore: 8 } }], { x: 1.12, y: 5.45, w: 11.1, h: 0.85, fontFace: FONT, valign: "top" });
s.addNotes("让我用日常比喻帮大家区分这两种漂移。Goal Drift 就像你出门买牛奶，路过书店进去看看，然后在里面坐了一下午——你彻底忘记了你要买牛奶。Scope Creep 就像你出门买牛奶，觉得顺便买点面包，又觉得既然来了不如把一周的菜都买了——你确实买了牛奶，但花了 10 倍的时间和钱。Goal Drift 需要\u201C提醒\u201D；Scope Creep 需要\u201C约束\u201D。LLM 有 recency bias 和 helpfulness bias，组合起来就是灾难性的漂移推力。");

// ---------- Slide 9: Drift 3 Mechanisms ----------
s = contentSlide(p, 9, N, "三大漂移检测机制：被动监控 + 主动预防 + 硬性约束", "Drift · 3 Mechanisms");
const dms = [
  { t: "1 · Context Similarity", d: "原始 task vs recent actions 的 cosine similarity", th: "<0.7 黄  ·  <0.5 红", c: C.BLUE, role: "Passive Monitor" },
  { t: "2 · Goal Anchoring", d: "每 5 轮重新注入 original task description", th: "200-500 tokens / inject", c: C.ORANGE, role: "Preventive Reminder" },
  { t: "3 · Behavior Boundary", d: "task 开始定义 allowed tools + paths", th: "100% 阻断率（硬围栏）", c: C.RED, role: "Hard Constraint" },
];
dms.forEach((m, i) => {
  const y = 1.75 + i * 1.0;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 8.5, h: 0.85, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.14, h: 0.85, fill: { color: m.c } });
  s.addText([{ text: m.t, options: { bold: true, fontSize: 13, color: m.c, breakLine: true } }, { text: m.d, options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 4 } }, { text: m.th, options: { fontSize: 10, italic: true, color: C.GRAY, paraSpaceBefore: 3 } }], { x: 1.18, y: y + 0.05, w: 8.2, h: 0.75, fontFace: FONT, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.6, y, w: 2.8, h: 0.85, fill: { color: m.c } });
  s.addText(m.role, { x: 9.6, y, w: 2.8, h: 0.85, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.85, w: 11.5, h: 1.5, fill: { color: C.DARK } });
s.addText([{ text: "Defense in Depth — 三者组合使用", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "Boundary 阻断严重越界（硬围栏） · Anchoring 预防渐进漂移（哨声） · Similarity 监控全局趋势（卫星）", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "单独用任何一个都有盲点：Boundary 太严 / Anchoring 被忽略 / Similarity 反应慢", options: { fontSize: 11, italic: true, color: "C7CED6", paraSpaceBefore: 6 } }], { x: 1.12, y: 5.0, w: 11.1, h: 1.3, fontFace: FONT, valign: "top" });
s.addNotes("三个机制形成递进的防线。Behavior Boundary 是最硬的——Agent 尝试调用不被允许的工具，直接拒绝，没有商量余地。这就像围栏：牛出不了围栏范围。Goal Anchoring 是中等强度的——周期性提醒 Agent 它的本职工作。这就像牧羊人的哨声。Context Similarity 是最软的——被动监控全局趋势。这就像卫星追踪。生产系统中你应该三个都用。");

// ---------- Slide 10: Drift Recovery ----------
s = contentSlide(p, 10, N, "漂移恢复：渐进式响应 — 从轻推到强停", "Drift · Graduated Recovery");
const lvls = [
  { t: "L1 · Inject Reminder", trig: "similarity < 0.7", act: "下一轮注入高优先级提醒，Agent 自我修正", succ: "70% 修正率", c: "E0A000" },
  { t: "L2 · Context Reset", trig: "L1 后 3 轮未回归", act: "Summarize progress + 移除噪音 + 重新注入 goal", succ: "丢失中间推理", c: C.ORANGE },
  { t: "L3 · Force Terminate", trig: "similarity < 0.4 / budget 80% 无进展", act: "立即停止 + checkpoint + 漂移报告 → 人类决策", succ: "task failure", c: C.RED },
];
lvls.forEach((l, i) => {
  const y = 1.75 + i * 1.1;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 3.0, h: 1.0, fill: { color: l.c } });
  s.addText([{ text: l.t, options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: l.trig, options: { fontSize: 10, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: 1.05, y: y + 0.08, w: 2.8, h: 0.85, fontFace: FONT, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.0, y, w: 6.5, h: 1.0, fill: { color: C.LIGHT } });
  s.addText(l.act, { x: 4.15, y, w: 6.3, h: 1.0, fontFace: FONT, fontSize: 11, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 10.6, y, w: 1.8, h: 1.0, fill: { color: "FBEAE5" } });
  s.addText(l.succ, { x: 10.7, y, w: 1.6, h: 1.0, fontFace: FONT, fontSize: 10, italic: true, color: l.c, bold: true, align: "center", valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.15, w: 11.5, h: 1.2, fill: { color: C.DARK } });
s.addText([{ text: "原则：渐进响应，不直接跳到 L3", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "L1 像\u201C会议中走神被叫名字拉回\u201D · L2 像\u201C清理乱房间\u201D · L3 像\u201C承认无法救药交给人类\u201D", options: { fontSize: 11.5, italic: true, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "记住：L3 不是失败 — 不终止导致的 $200 账单才是失败", options: { fontSize: 11.5, bold: true, color: C.ORANGE, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.3, w: 11.1, h: 1.0, fontFace: FONT, valign: "top" });
s.addNotes("L1 的 70% 成功率是实践经验值。大部分漂移是\u201C无意的\u201D——Agent 只是被最近的工具输出带偏了注意力，一个提醒就能拉回来。但 30% 的情况下提醒无效——特别是当 context 已经被大量无关信息污染时。这时候需要 L2——本质上是\u201C打扫房间\u201D：把不相关的东西全部清理掉。如果打扫了还不行，那就是 L3——承认这个 Agent 已经\u201C不可救药\u201D了，保存现场，交给人类。");

// ---------- Slide 11: Token Budget 3-level ----------
s = contentSlide(p, 11, N, "Token Budget：三级预算 + 渐进式压力响应", "Token Budget · 3 Levels");
const tb = [
  ["L1 · Per-Day Global", "10M tokens/day ≈ $30/day", "保护组织预算 · 触发 → 全停 + alert"],
  ["L2 · Per-Task", "500K tokens ≈ $1.50", "防 runaway · 触发 → graceful + partial result"],
  ["L3 · Per-Round", "继承自 S1 Context Budget", "防超长 output · 由 S1 管理"],
];
tb.forEach((t, i) => {
  const y = 1.75 + i * 0.7;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 3.4, h: 0.6, fill: { color: [C.RED, C.ORANGE, C.BLUE][i] } });
  s.addText(t[0], { x: 0.92, y, w: 3.4, h: 0.6, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.4, y, w: 3.0, h: 0.6, fill: { color: C.LIGHT } });
  s.addText(t[1], { x: 4.5, y, w: 2.8, h: 0.6, fontFace: MONO, fontSize: 10.5, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 7.5, y, w: 4.9, h: 0.6, fill: { color: "FBEAE5" } });
  s.addText(t[2], { x: 7.65, y, w: 4.7, h: 0.6, fontFace: FONT, fontSize: 10.5, color: C.GRAY, valign: "middle" });
});
s.addText("Progressive Pressure Response", { x: 0.92, y: 4.0, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const pp = [["80%", "Compress", "summarize 历史，释放空间", C.GREEN], ["90%", "autoDream", "关键信息写入外部记忆", "E0A000"], ["95%", "Reject New Tools", "只允许 finish/summary", C.ORANGE], ["99%", "Hard Stop", "无条件终止 + 状态总结", C.RED]];
pp.forEach((s2, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 4.45, w: 2.7, h: 1.5, fill: { color: s2[3] } });
  s.addText([{ text: s2[0], options: { bold: true, fontSize: 22, color: C.WHITE, breakLine: true } }, { text: s2[1], options: { bold: true, fontSize: 11.5, color: "FFFFFF", breakLine: true, paraSpaceBefore: 6 } }, { text: s2[2], options: { fontSize: 9.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.12, y: 4.55, w: 2.5, h: 1.35, fontFace: FONT, align: "center", valign: "top" });
});
s.addText("软着陆 → 激进压缩 → 最后通牒 → 断路器 · 类比：船舶进水的 4 级响应", { x: 0.92, y: 6.05, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 11.5, italic: true, color: C.GRAY, align: "center" });
s.addNotes("为什么三级？因为粒度不同。Per-Day 保护公司钱包；Per-Task 保护单次用户体验；Per-Round 保护单次 LLM 调用。渐进式压力响应是精髓——80% compress 是\u201C软着陆\u201D；90% autoDream 更激进；95% 是最后通牒；99% 是断路器。这就像一艘正在下沉的船：80% 排水，90% 关闭非关键舱室，95% 发 SOS，99% 全员弃船。");

// ---------- Slide 12: State Machine ----------
s = contentSlide(p, 12, N, "Agent 状态机：Control Plane 的骨架", "Control Plane State Machine");
const states = [
  { x: 1.0, y: 1.85, n: "IDLE", c: C.GRAY, term: true },
  { x: 3.5, y: 1.85, n: "INITIALIZING", c: C.BLUE },
  { x: 6.5, y: 1.85, n: "EXECUTING", c: C.ORANGE },
  { x: 9.5, y: 1.85, n: "COMPLETED", c: C.GREEN, term: true },
  { x: 9.5, y: 4.0, n: "FAILED", c: C.RED, term: true },
  { x: 6.5, y: 4.0, n: "PAUSED", c: "E0A000", optional: true },
];
states.forEach(st => {
  const w = st.n.length > 8 ? 2.4 : 1.7;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: st.x, y: st.y, w, h: 0.7, fill: { color: st.c }, line: { color: st.term ? C.DARK : (st.optional ? C.GRAY : st.c), width: st.term ? 3 : (st.optional ? 1.5 : 1), dashType: st.optional ? "dash" : "solid" }, rectRadius: 0.1 });
  s.addText(st.n, { x: st.x, y: st.y, w, h: 0.7, fontFace: FONT, fontSize: 11.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
});
s.addShape(p.shapes.LINE, { x: 2.7, y: 2.2, w: 0.8, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 5.9, y: 2.2, w: 0.6, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 8.9, y: 2.2, w: 0.6, h: 0, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 7.4, y: 2.55, w: 0, h: 1.45, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle", beginArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 8.2, y: 4.35, w: 1.3, h: 0, line: { color: C.RED, width: 1.5, endArrowType: "triangle", dashType: "dash" } });
s.addText("kill_signal", { x: 6.5, y: 4.7, w: 3, h: 0.3, fontFace: FONT, fontSize: 9, italic: true, color: C.RED });
codeBox(p, s, [
  { text: "# State Transitions", opt: { color: C.ORANGE, bold: true } },
  { text: "IDLE + user_message → INITIALIZING", opt: { color: "8FBFE8" } },
  { text: "INIT + ready → EXECUTING", opt: { color: "8FBFE8" } },
  { text: "EXEC + termination_met → COMPLETED", opt: { color: "8FD19E" } },
  { text: "EXEC + unrecoverable → FAILED", opt: { color: "E8736A" } },
  { text: "EXEC ↔ PAUSED (HITL injection point)", opt: { color: "E8A33D" } },
  { text: "ANY + kill_signal → FAILED", opt: { color: "E8736A" } },
], { x: 0.92, y: 5.05, w: 11.5, h: 1.3, fontSize: 10 });
s.addNotes("这个状态机看起来简单，但它是整个 Control Plane 的骨架。你在前面学到的所有控制机制——drift detection、budget enforcement、termination conditions——都映射到这个状态机的某个转换上。PAUSED 状态特别重要——它让你有机会在 Agent 执行中途介入。没有 PAUSED，你只能 Kill 然后从头重来。有了 PAUSED，你可以暂停 → 注入新指令 → Resume。");

// ---------- Slide 13: Pause/Resume ----------
s = contentSlide(p, 13, N, "实时控制操作：Pause / Resume / Intervene / Kill", "Pause/Resume/Intervention");
const ops = [
  { t: "Pause", icon: "‖", d: "完成当前 tool call → 进入 PAUSED · 保存完整 checkpoint", c: "E0A000" },
  { t: "Resume", icon: "▶", d: "verify state → re-inject goal reminder → 从 checkpoint 继续", c: C.GREEN },
  { t: "Intervene", icon: "↓", d: "运行中注入新指令（不暂停）· high-priority context", c: C.BLUE },
  { t: "Kill", icon: "■", d: "立即终止（不等当前 tool）· state snapshot for post-mortem", c: C.RED },
];
ops.forEach((o, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 2.7, h: 0.85, fill: { color: o.c } });
  s.addText([{ text: o.icon + "  ", options: { fontSize: 22, bold: true, color: C.WHITE } }, { text: o.t, options: { fontSize: 16, bold: true, color: "FFFFFF" } }], { x, y: 1.85, w: 2.7, h: 0.65, fontFace: FONT, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.6, w: 2.7, h: 1.85, fill: { color: C.LIGHT } });
  s.addText(o.d, { x: x + 0.12, y: 2.7, w: 2.5, h: 1.7, fontFace: FONT, fontSize: 10.5, color: C.INK, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.7, w: 11.5, h: 1.6, fill: { color: C.DARK } });
s.addText([{ text: "Agent 不是\u201C启动后就不管了\u201D的 batch job — 它是 live process", options: { bold: true, color: C.ORANGE, fontSize: 13.5, breakLine: true } }, { text: "Pause 关键：完成当前 tool 再暂停（避免文件写一半）", options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "Resume 关键：验证状态有效（暂停期间外部环境可能变化）", options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 4 } }, { text: "Intervene 关键：副驾驶式实时指导  ·  Kill 关键：紧急情况立即截停", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 4 } }], { x: 1.12, y: 4.85, w: 11.1, h: 1.4, fontFace: FONT, valign: "top" });
s.addNotes("这四个操作是用户与正在运行的 Agent 之间的交互接口。Pause 的关键细节是\u201C完成当前 tool call 再暂停\u201D——你不想在文件写到一半时暂停，那会导致文件损坏。Resume 的关键细节是\u201C验证状态有效性\u201D——如果暂停了 5 分钟，在这 5 分钟里其他人可能修改了 Agent 正在操作的文件。Intervene 是最有趣的——它让你像\u201C副驾驶\u201D一样实时指导 Agent。Kill 是最后手段——当你看到 Agent 正在执行 rm -rf 时，必须立即终止。");

// ---------- Slide 14: Part A Summary + Transition ----------
s = contentSlide(p, 14, N, "Part A 总结：Agent Loop 控制的四大支柱", "Part A · Summary + Transition");
const four = [
  { t: "5 Termination", role: "刹车系统", d: "保证 loop 一定停下", c: C.RED },
  { t: "Drift Detection", role: "方向盘", d: "保证朝正确目标前进", c: C.ORANGE },
  { t: "Token Budget", role: "油量表", d: "保证资源消耗可控", c: C.BLUE },
  { t: "State Machine", role: "仪表盘", d: "完整状态可见 + 实时操控", c: C.GREEN },
];
four.forEach((f, i) => {
  const x = 0.92 + i * 2.95;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 2.7, h: 1.4, fill: { color: f.c } });
  s.addText([{ text: f.t, options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: f.role, options: { fontSize: 13, italic: true, color: C.ORANGE, breakLine: true, paraSpaceBefore: 6 } }, { text: f.d, options: { fontSize: 10.5, color: "FFFFFF", paraSpaceBefore: 5 } }], { x: x + 0.12, y: 1.85, w: 2.5, h: 1.25, fontFace: FONT, align: "center", valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 3.4, w: 5.6, h: 1.5, fill: { color: C.LIGHT } });
s.addText([{ text: "✓ Part A 解决", options: { bold: true, color: C.GREEN, fontSize: 13, breakLine: true } }, { text: "灾难 1（Infinite Loop）→ Termination", options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 6 } }, { text: "灾难 2（Goal Drift）→ Drift Detection", options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 4 } }, { text: "灾难 4（Recursion）→ Budget per level", options: { fontSize: 11, color: C.INK, paraSpaceBefore: 4 } }], { x: 1.12, y: 3.55, w: 5.2, h: 1.3, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 3.4, w: 5.6, h: 1.5, fill: { color: "FBEAE5" } });
s.addText([{ text: "✗ Part A 假设了完美基础设施", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "现实：Provider 宕机 / 网络超时 / API 限流 / 错误级联", options: { fontSize: 11, color: C.INK, breakLine: true, paraSpaceBefore: 6 } }, { text: "灾难 3（Cascade Failure）还没解决", options: { fontSize: 11, bold: true, color: C.RED, paraSpaceBefore: 6 } }], { x: 7.02, y: 3.55, w: 5.2, h: 1.3, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.1, w: 11.5, h: 1.25, fill: { color: C.DARK } });
s.addText([{ text: "→ Part B: Fault Tolerance & Infrastructure", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "Provider Abstraction · Circuit Breaker · Fallback · Bulkhead · Retry · Timeout · Errors-as-Observations", options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "当地基摇晃时，如何让建筑不倒塌？", options: { fontSize: 12, italic: true, color: "C7CED6", paraSpaceBefore: 5 } }], { x: 1.12, y: 5.25, w: 11.1, h: 1.05, fontFace: FONT, valign: "top" });
s.addNotes("用 5 分钟做一个 clean 的 Part A 总结。让学员把前面学到的所有东西用一个框架串起来。然后做一个有力的 transition：到目前为止，我们假设了一个理想世界——LLM Provider 随叫随到、网络永远稳定。但现实是 OpenAI 每个月至少有一次 incident，Anthropic 也不例外。Part B 要教你的是：当地基摇晃时，如何让建筑不倒塌。休息 5 分钟后继续。");

// ---------- Slide 15: Provider Abstraction Paths ----------
s = contentSlide(p, 15, N, "Provider Abstraction — 深度绑定 vs 多模型路由", "Provider Abstraction · 两条路径");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.ORANGE } });
s.addText("A · Single-Model Binding（Claude Code）", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.3, w: 5.6, h: 2.1, fill: { color: C.LIGHT } });
s.addText([{ text: "深度集成 Anthropic API", options: { fontSize: 11.5, bold: true, color: C.INK, breakLine: true } }, ...["cache_control 标记 (90% 折扣)", "extended thinking", "native tool_use 格式"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 4 } })), { text: "代价：vendor lock-in", options: { fontSize: 10.5, italic: true, color: C.RED, paraSpaceBefore: 8 } }], { x: 1.1, y: 2.42, w: 5.3, h: 1.9, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.BLUE } });
s.addText("B · Multi-Model Routing（OpenCode）", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.3, w: 5.6, h: 2.1, fill: { color: C.LIGHT } });
s.addText([{ text: "统一抽象层 · 75+ providers", options: { fontSize: 11.5, bold: true, color: C.INK, breakLine: true } }, ...["OpenAI / Anthropic / Google / Ollama", "灵活切换 + 价格竞争", "故障时 cross-provider failover"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 4 } })), { text: "代价：只能用最大公约数功能", options: { fontSize: 10.5, italic: true, color: C.RED, paraSpaceBefore: 8 } }], { x: 7.0, y: 2.42, w: 5.3, h: 1.9, fontFace: FONT, valign: "top" });
codeBox(p, s, [
  { text: "# 推荐：混合方案", opt: { color: C.ORANGE, bold: true } },
  { text: "Primary:    Claude Sonnet  (深绑定 + cache + thinking)", opt: { color: "8FD19E" } },
  { text: "Fallback-1: Claude Haiku   (同 provider，保留 cache)", opt: { color: "8FBFE8" } },
  { text: "Fallback-2: GPT-4o-mini    (跨 provider via 抽象层)", opt: { color: "E8A33D" } },
], { x: 0.92, y: 4.6, w: 11.5, h: 1.7, fontSize: 10.5 });
s.addNotes("Provider Abstraction 是你在设计 Agent 系统时必须做的第一个架构决策。Claude Code 走了深度绑定——它能用 Anthropic 的 cache_control 标记精确控制缓存边界。OpenCode 走了多模型路由——你可以一键切到 GPT-4o 或本地模型。我推荐的混合方案：主路径深绑定（获得 90% 的 cache 折扣），但 fallback 通过抽象层走其他 provider。");

// ---------- Slide 16: Provider Decision Framework ----------
s = contentSlide(p, 16, N, "何时深绑定、何时多路由？", "Provider Abstraction · 决策框架");
const decGrid = [
  ["稳定性需求高 + 成本敏感低", "Multi-Route + 多 fallback", C.BLUE],
  ["稳定性需求低 + 成本敏感低", "Single-Bind（深度优化）", C.ORANGE],
  ["稳定性需求高 + 成本敏感高", "Hybrid（主深绑 + 抽象层 fallback）", C.GREEN],
  ["稳定性需求低 + 成本敏感高", "Multi-Route（按价格路由）", "2E4A63"],
];
decGrid.forEach((g, i) => {
  const x = 0.92 + (i % 2) * 5.95;
  const y = 1.75 + Math.floor(i / 2) * 1.0;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 0.85, fill: { color: g[2] } });
  s.addText([{ text: g[0], options: { bold: true, fontSize: 11, color: C.WHITE, breakLine: true } }, { text: g[1], options: { fontSize: 11.5, color: "FFFFFF", paraSpaceBefore: 5 } }], { x: x + 0.15, y: y + 0.08, w: 5.25, h: 0.7, fontFace: FONT, valign: "top" });
});
codeBox(p, s, [
  { text: "interface LLMProvider {", opt: {} },
  { text: "  complete(messages, tools, config): Promise<Response>", opt: { color: "8FD19E" } },
  { text: "  stream(messages, tools, config): AsyncIterator<StreamEvent>", opt: { color: "8FD19E" } },
  { text: "  estimateTokens(messages): number", opt: { color: "8FBFE8" } },
  { text: "  validateConfig(config): boolean", opt: { color: "8FBFE8" } },
  { text: "}", opt: {} },
], { x: 0.92, y: 3.85, w: 11.5, h: 1.95, fontSize: 10.5 });
s.addText("注意：切换 provider 不免费 — tool_use 格式不同 / token 计算不同 / 缓存不共享 / 重写适配", { x: 0.92, y: 6.0, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: C.RED, align: "center" });
s.addNotes("决策不是\u201C单绑定好\u201D或\u201C多路由好\u201D——是看你的约束条件。如果你的产品依赖 Claude 的 Artifacts 或 extended thinking，那深绑定是对的。如果你的 SLA 是 99.9% 但 Anthropic 每月有 1-2 次 incident，那你必须有 fallback。现实中大多数生产系统是混合模式：90% 流量走主路径，10% 是 fallback。");

// ---------- Slide 17: Circuit Breaker ----------
s = contentSlide(p, 17, N, "Circuit Breaker — 防止 Provider 故障雪崩", "Resilience · 三状态熔断器");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 11.5, h: 0.55, fill: { color: C.RED } });
s.addText("问题：Provider 宕机 → Agent 不断重试 → 延迟堆积 → 线程耗尽 → 服务崩溃", { x: 0.92, y: 1.75, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const cb = [
  { x: 1.5, y: 2.65, w: 2.6, n: "CLOSED", d: "正常通行", c: C.GREEN },
  { x: 9.2, y: 2.65, w: 2.6, n: "OPEN", d: "快速拒绝", c: C.RED },
  { x: 5.35, y: 4.5, w: 2.6, n: "HALF-OPEN", d: "试探放行", c: "E0A000" },
];
cb.forEach(b => {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: b.x, y: b.y, w: b.w, h: 0.95, fill: { color: b.c }, line: { color: b.c }, rectRadius: 0.15 });
  s.addText([{ text: b.n, options: { bold: true, fontSize: 14, color: C.WHITE, breakLine: true } }, { text: b.d, options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: b.x, y: b.y + 0.08, w: b.w, h: 0.8, fontFace: FONT, align: "center", valign: "top" });
});
s.addShape(p.shapes.LINE, { x: 4.1, y: 3.0, w: 5.1, h: 0, line: { color: C.RED, width: 2, endArrowType: "triangle" } });
s.addText("5 失败 / 50% 错误率", { x: 4.5, y: 2.6, w: 4.4, h: 0.3, fontFace: FONT, fontSize: 10, color: C.RED, italic: true, align: "center" });
s.addShape(p.shapes.LINE, { x: 9.2, y: 3.6, w: -1.5, h: 1.0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } });
s.addText("30s cooldown", { x: 7.7, y: 3.85, w: 1.5, h: 0.3, fontFace: FONT, fontSize: 10, color: C.GRAY, italic: true, align: "center" });
s.addShape(p.shapes.LINE, { x: 5.35, y: 4.85, w: -1.5, h: -1.85, line: { color: C.GREEN, width: 2, endArrowType: "triangle" } });
s.addText("探测成功", { x: 3.6, y: 3.7, w: 1.5, h: 0.3, fontFace: FONT, fontSize: 10, color: C.GREEN, italic: true, align: "center" });
s.addShape(p.shapes.LINE, { x: 7.95, y: 4.85, w: 1.7, h: -1.85, line: { color: C.RED, width: 2, endArrowType: "triangle", dashType: "dash" } });
s.addText("探测失败", { x: 8.2, y: 3.7, w: 1.5, h: 0.3, fontFace: FONT, fontSize: 10, color: C.RED, italic: true, align: "center" });
s.addText("每个 Provider 独立维护熔断状态  ·  Sonnet OPEN 不影响 Haiku CLOSED", { x: 0.92, y: 5.7, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 12, bold: true, color: C.INK, align: "center" });
s.addText("OPEN 30s → HALF-OPEN（一个探测请求）· 来自微服务的 Netflix Hystrix / Resilience4j 模式", { x: 0.92, y: 6.05, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 11, italic: true, color: C.GRAY, align: "center" });
s.addNotes("Circuit Breaker 防止了一个经典的级联故障模式。想象 Anthropic API 宕了，你的 Agent 每次请求都要等 60 秒超时才知道失败。10 个并发请求 × 60 秒 = 你的线程池被占满，其他健康的 provider 也无法被调用。Circuit Breaker 在检测到故障模式后立即\u201C断开\u201D——所有后续请求直接 fast-fail（毫秒级）。等故障恢复后，通过 HALF-OPEN 的探测机制逐步恢复流量。");

// ---------- Slide 18: Fallback Chain ----------
s = contentSlide(p, 18, N, "Fallback Chain — Provider 故障时的降级路径", "Resilience · Fallback Chain");
const fbc = [
  ["Primary", "Claude Sonnet 4", "full features + prompt caching", C.GREEN],
  ["Fallback-1", "Claude Haiku 4", "same provider, 同 cache", C.BLUE],
  ["Fallback-2", "GPT-4o-mini", "cross-provider, 新 cache, 格式转换", C.ORANGE],
  ["Hard Fail", "拒绝请求 + 告警", "排队等恢复", C.RED],
];
fbc.forEach((f, i) => {
  const y = 1.75 + i * 0.7;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 2.4, h: 0.6, fill: { color: f[3] } });
  s.addText(f[0], { x: 0.92, y, w: 2.4, h: 0.6, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 3.4, y, w: 3.4, h: 0.6, fill: { color: C.LIGHT } });
  s.addText(f[1], { x: 3.55, y, w: 3.2, h: 0.6, fontFace: MONO, fontSize: 11, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 6.85, y, w: 5.55, h: 0.6, fill: { color: "FBEAE5" } });
  s.addText(f[2], { x: 7.0, y, w: 5.4, h: 0.6, fontFace: FONT, fontSize: 10.5, color: C.GRAY, valign: "middle" });
  if (i < 3) s.addShape(p.shapes.LINE, { x: 2.12, y: y + 0.6, w: 0, h: 0.1, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.65, w: 11.5, h: 1.7, fill: { color: C.DARK } });
s.addText([{ text: "Fallback 的代价", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, ...["切换 provider = 丧失 prompt cache（cache 是 per-provider 的）", "不同 provider 的 tool_use 格式不同 → 需格式转换层", "弱模型 fallback：复杂任务可能失败（可接受的降级）"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }))], { x: 1.12, y: 4.8, w: 11.1, h: 1.5, fontFace: FONT, valign: "top" });
s.addNotes("Fallback Chain 是 Circuit Breaker 的下游——主路径熔断后流量去哪。设计 fallback 时要权衡：同 provider 的 fallback（Sonnet → Haiku）保留 cache，但如果是 Anthropic 全站宕机就不顶用。跨 provider 失去 cache + 需要格式转换，但能扛住单 provider 故障。生产推荐：3 级 fallback，Hard Fail 排队等恢复（不要让最后一级也失败导致请求丢失）。");

// ---------- Slide 19: Circuit Breaker 实现细节 ----------
s = contentSlide(p, 19, N, "Circuit Breaker 配置与错误分类", "Circuit Breaker · 实现细节");
codeBox(p, s, [
  { text: "providers:", opt: { color: C.ORANGE, bold: true } },
  { text: "  claude-sonnet:", opt: { color: "8FBFE8" } },
  { text: "    failure_threshold: 5         # 连续失败次数", opt: { color: "8FD19E" } },
  { text: "    error_rate_threshold: 0.5    # 30s 内错误率", opt: { color: "8FD19E" } },
  { text: "    error_rate_window: 30s", opt: { color: "8FD19E" } },
  { text: "    cooldown_initial: 30s        # 首次 OPEN", opt: { color: "8FD19E" } },
  { text: "    cooldown_multiplier: 2       # 每次恢复失败翻倍", opt: { color: "8FD19E" } },
  { text: "    cooldown_max: 300s", opt: { color: "8FD19E" } },
  { text: "  claude-haiku:", opt: { color: "8FBFE8" } },
  { text: "    failure_threshold: 3         # Fallback 更敏感", opt: { color: "8FD19E" } },
], { x: 0.92, y: 1.75, w: 6.5, h: 3.0, fontSize: 10 });
styledTable(p, s, [
  [hc("✓ 计入失败"), hc("✗ 不计入")],
  ["timeout", "400 (our bad request)"],
  ["500/502/503", "401 (our auth)"],
  ["529 (overloaded)", "422 (our validation)"],
  ["connection refused", "429 (rate limit)"],
], { x: 7.7, y: 1.75, w: 4.7, colW: [2.3, 2.4], rowH: 0.5, fontSize: 10.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 1.4, fill: { color: "FBEAE5" } });
s.addText([{ text: "429 Rate Limiting 单独处理（不触发熔断）", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "原因：429 是临时的、可预期的、自恢复的 — 用 exponential backoff + jitter", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 6 } }, { text: "Circuit breaker 针对系统性故障，不是临时限流", options: { fontSize: 11.5, italic: true, color: C.RED, paraSpaceBefore: 5 } }], { x: 1.12, y: 5.1, w: 11.1, h: 1.2, fontFace: FONT, valign: "top" });
s.addNotes("错误分类是 circuit breaker 实现中最容易犯的错。如果你把 400 Bad Request 也算作 provider 失败，那你的代码 bug 会触发熔断——明明 provider 是健康的。如果你把 429 也算进去，那正常的限流会导致熔断——接下来所有请求都 fast-fail，反而加剧了问题。只有真正的系统性故障（500/502/503/timeout/连接拒绝）才应该触发熔断。429 用 backoff 处理就好。");

// ---------- Slide 20: Bulkhead ----------
s = contentSlide(p, 20, N, "Bulkhead — 优先级资源隔离", "Resilience · Bulkhead Pattern");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.7, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("问题：批量后台任务可能耗尽并发配额，让用户交互请求排队", { x: 0.92, y: 1.7, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const bks = [
  ["Critical", "60%", "用户实时交互、紧急任务", C.RED],
  ["Normal", "30%", "后台任务、sub-agent", C.ORANGE],
  ["Low", "10%", "批处理、分析、autoDream 预热", C.GREEN],
];
bks.forEach((b, i) => {
  const y = 2.45 + i * 0.85;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 2.4, h: 0.7, fill: { color: b[3] } });
  s.addText(b[0], { x: 0.92, y, w: 2.4, h: 0.7, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 3.4, y, w: 1.8, h: 0.7, fill: { color: C.LIGHT } });
  s.addText(b[1], { x: 3.4, y, w: 1.8, h: 0.7, fontFace: FONT, fontSize: 18, bold: true, color: b[3], align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 5.3, y, w: 7.1, h: 0.7, fill: { color: "FBEAE5" } });
  s.addText(b[2], { x: 5.45, y, w: 6.95, h: 0.7, fontFace: FONT, fontSize: 11.5, color: C.INK, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.15, w: 11.5, h: 1.2, fill: { color: C.GREEN } });
s.addText([{ text: "即使 Low 队列堆满 100 个任务，Critical 始终有 60% 容量", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "类比：船舶水密舱壁 — 一个舱进水关门，其他舱不受影响", options: { fontSize: 11.5, italic: true, color: "FFFFFF", paraSpaceBefore: 6 } }, { text: "实现：独立请求队列 + per-queue 并发限制 + priority-based scheduling", options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: 1.12, y: 5.3, w: 11.1, h: 1.0, fontFace: FONT, valign: "top" });
s.addNotes("Bulkhead 的名字来自船舶的水密舱壁——一个舱进水了，关上隔离门，其他舱不受影响。在 Agent 系统中，如果你有后台任务（autoDream 在做记忆整合、sub-agent 在并行处理子任务），它们不应该影响到用户正在交互的主 Agent 的响应速度。即使 Low 优先级的队列排了 100 个任务，Critical 的 60% 配额保证用户请求秒级响应。");

// ---------- Slide 21: Retry + Timeout ----------
s = contentSlide(p, 21, N, "重试与超时 — 看似简单但最常做错", "Resilience · Retry + Timeout");
codeBox(p, s, [
  { text: "# 指数退避 + 抖动", opt: { color: C.ORANGE, bold: true } },
  { text: "delay = min(base × 2^attempt × (1 ± 0.3 random),", opt: { color: "8FD19E" } },
  { text: "            max_delay)", opt: { color: "8FD19E" } },
  { text: "# 例：1s → 2s → 4s → 8s ±30% 随机偏移", opt: { color: "8C9AA6" } },
  { text: "# 防 thundering herd", opt: { color: "8C9AA6" } },
  { text: "", opt: {} },
  { text: "MAX_RETRIES = 3   # 再多就是 circuit breaker 的事", opt: { color: "E8A33D" } },
  { text: "RETRY_ON  = [timeout, 429, 503]", opt: { color: "8FD19E" } },
  { text: "NEVER_RETRY = [400, 401, 422]   # 我们的错", opt: { color: "E8736A" } },
], { x: 0.92, y: 1.75, w: 6.5, h: 2.95, fontSize: 10.5 });
styledTable(p, s, [
  [hc("级别"), hc("默认值"), hc("超时后果")],
  [{ text: "Tool call", options: { bold: true } }, "30s", "Error-as-observation"],
  [{ text: "LLM inference", options: { bold: true } }, "60s", "Retry with fallback"],
  [{ text: "Task overall", options: { bold: true } }, "600s", "强制终止 + partial"],
  [{ text: "Session", options: { bold: true } }, "3600s", "绝对上限 + 清理"],
], { x: 7.7, y: 1.75, w: 4.7, colW: [1.6, 1.0, 2.1], rowH: 0.45, fontSize: 10.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 1.4, fill: { color: C.DARK } });
s.addText([{ text: "超时不是\u201C出错了\u201D，而是\u201C超过了我们愿意等的时间\u201D", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "Tool 超时 → 先作为 observation 告诉 Agent（让它决定重试还是换方案）", options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "LLM 超时 → S5 自动 retry with fallback model（不打扰 Agent loop）", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 5 } }], { x: 1.12, y: 5.08, w: 11.1, h: 1.2, fontFace: FONT, valign: "top" });
s.addNotes("Retry 和 timeout 看似是\u201C基础设施 101\u201D，但在 Agent 系统中它们与 errors-as-observations 模式交织，变得有趣。当 tool 超时了——30 秒内没返回——这是一个 error 还是需要 retry？答案是：先作为 observation 告诉 Agent（\u201Ctool timed out\u201D），让 Agent 决定。只有 LLM provider 级别的超时才由 S5 自动 retry with fallback。另一个常见错误：对 400 错误做重试。你的请求格式错了，重试 100 次结果也一样。");

// ---------- Slide 22: Errors-as-Observations ----------
s = contentSlide(p, 22, N, "Errors-as-Observations — 让 Agent 从失败中学习", "自愈模式");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.RED } });
s.addText("传统模式", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
codeBox(p, s, [
  { text: "error", opt: { color: "E8736A" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "exception", opt: { color: "E8736A" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "handler", opt: { color: "E8A33D" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "retry or crash", opt: { color: "E8736A" } },
], { x: 0.92, y: 2.3, w: 5.6, h: 2.0, fontSize: 11 });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.GREEN } });
s.addText("Agent 模式", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
codeBox(p, s, [
  { text: "error", opt: { color: "E8736A" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "ToolResult(is_error=true,", opt: { color: "8FBFE8" } },
  { text: "           content=\"file not found\")", opt: { color: "8FBFE8" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "next Think → Agent 推理替代方案", opt: { color: "8FD19E" } },
  { text: "  ↓", opt: { color: "8C9AA6" } },
  { text: "tries different path → success", opt: { color: "8FD19E" } },
], { x: 6.82, y: 2.3, w: 5.6, h: 2.0, fontSize: 10.5 });
s.addText("3 步自愈示例", { x: 0.92, y: 4.5, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const heal = [["1", "尝试方案 A", "失败：file not found", C.RED], ["2", "理解原因 → 尝试方案 B", "不同路径", C.ORANGE], ["3", "方案 B 成功", "任务完成（无人工干预）", C.GREEN]];
heal.forEach((h, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 4.9, w: 3.6, h: 1.2, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.OVAL, { x: x + 0.15, y: 5.0, w: 0.5, h: 0.5, fill: { color: h[3] } });
  s.addText(h[0], { x: x + 0.15, y: 5.0, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addText([{ text: h[1], options: { bold: true, fontSize: 11, color: C.INK, breakLine: true } }, { text: h[2], options: { fontSize: 9.5, color: h[3], paraSpaceBefore: 4 } }], { x: x + 0.75, y: 4.95, w: 2.7, h: 1.1, fontFace: FONT, valign: "top" });
});
s.addText("LLM 可以理解错误上下文并选择替代策略 — 这是 Agent 相比传统自动化的核心优势", { x: 0.92, y: 6.2, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 11.5, italic: true, color: C.GRAY, align: "center" });
s.addNotes("这可能是 Agent 系统中最优雅的设计模式之一。传统系统中，工具调用失败了你要么重试要么报错。但 Agent 有推理能力——你把错误信息作为一个 observation 喂给它，它能理解\u201C哦，这个文件不存在，让我检查一下路径对不对\u201D或者\u201C权限不够，我去问用户要权限\u201D。这就是 Agent 相比传统自动化的核心优势：它不需要你预先为每种错误编写处理逻辑——它自己推理出应对方案。");

// ---------- Slide 23: 自愈边界 ----------
s = contentSlide(p, 23, N, "何时不让 Agent\u201C自己处理\u201D — 自愈红线", "自愈 · Boundaries");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.GREEN } });
s.addText("✓ 可自愈", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.3, w: 5.6, h: 2.45, fill: { color: "E6F4EA" } });
s.addText([{ text: "可恢复错误", options: { bold: true, color: C.GREEN, fontSize: 12, breakLine: true } }, ...["File not found / wrong path", "Permission denied (可重试)", "Rate limited (等待)", "Tool result format error", "Network transient"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 5 } }))], { x: 1.1, y: 2.42, w: 5.3, h: 2.25, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.RED } });
s.addText("✗ 必须硬停", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.3, w: 5.6, h: 2.45, fill: { color: "FBEAE5" } });
s.addText([{ text: "不允许自愈", options: { bold: true, color: C.RED, fontSize: 12, breakLine: true } }, ...["安全违规 → S3 立即终止", "预算耗尽 → 无法生成下一轮", "系统级故障 (OOM, 磁盘满)", "级联失败 (同类 ≥5 次)", "Sandbox escape 尝试"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 5 } }))], { x: 7.0, y: 2.42, w: 5.3, h: 2.25, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.9, w: 11.5, h: 1.45, fill: { color: C.DARK } });
s.addText([{ text: "自愈 Guardrails", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, ...["max_consecutive_same_error: 3 → 升级（不让 Agent 反复撞墙）", "错误分类：feed 给 LLM 之前先分类 recoverable / non-recoverable", "成本感知：每次 error-retry 消耗 tokens，要计入 budget"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11, color: C.WHITE, paraSpaceBefore: 5 } }))], { x: 1.12, y: 5.05, w: 11.1, h: 1.25, fontFace: FONT, valign: "top" });
s.addNotes("自愈模式很强大但必须有边界。最危险的情况是：Agent 遇到安全违规后\u201C自愈\u201D——比如路径穿越被拦截后，它\u201C学会\u201D了用 symbolic link 绕过。这不是自愈，是 attack escalation。所以安全相关的错误绝不能进入 error-as-observation 循环——必须由 S3 硬终止。另一个常见问题：Agent 连续 5 次尝试同一个操作都失败——这时候问题是系统性的，\u201Ctry harder\u201D 没有意义。");

// ---------- Slide 24: DAG 多任务编排 ----------
s = contentSlide(p, 24, N, "复杂任务分解 — 从目标到依赖图", "Orchestration · DAG");
codeBox(p, s, [
  { text: "\"Build a REST API\" →", opt: { color: C.ORANGE, bold: true } },
  { text: "  [定义 Schema] → [生成 Models] → [写 Handlers] ─┐", opt: { color: "8FBFE8" } },
  { text: "                                                  ├→ [写 Tests]", opt: { color: "8FD19E" } },
  { text: "  [初始化项目] → [安装依赖] ──────────────────────┘", opt: { color: "8FBFE8" } },
  { text: "                                                       ↓", opt: { color: "8C9AA6" } },
  { text: "                                                  [跑 Tests]", opt: { color: "8FD19E" } },
], { x: 0.92, y: 1.75, w: 11.5, h: 2.0, fontSize: 10 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 3.95, w: 5.6, h: 1.0, fill: { color: C.RED } });
s.addText([{ text: "顺序执行", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "5 步 × 2min = 10 min", options: { fontSize: 14, bold: true, color: "FFFFFF", paraSpaceBefore: 5 } }], { x: 0.92, y: 4.05, w: 5.6, h: 0.9, fontFace: FONT, align: "center", valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 3.95, w: 5.6, h: 1.0, fill: { color: C.GREEN } });
s.addText([{ text: "并行执行（critical path）", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "3 步 × 2min = 6 min（节省 40%）", options: { fontSize: 14, bold: true, color: "FFFFFF", paraSpaceBefore: 5 } }], { x: 6.82, y: 4.05, w: 5.6, h: 0.9, fontFace: FONT, align: "center", valign: "top" });
s.addText("谁来做分解？", { x: 0.92, y: 5.1, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const decom = [["A · LLM 自动", "灵活但不可靠", C.RED], ["B · 预定义模板", "可靠但不灵活", C.ORANGE], ["C · 混合（推荐）", "模板 + LLM 调整", C.GREEN]];
decom.forEach((d, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 5.5, w: 3.6, h: 0.85, fill: { color: d[2] } });
  s.addText([{ text: d[0], options: { bold: true, fontSize: 12, color: C.WHITE, breakLine: true } }, { text: d[1], options: { fontSize: 10.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.15, y: 5.6, w: 3.3, h: 0.7, fontFace: FONT, align: "center", valign: "top" });
});
s.addNotes("复杂任务不是\u201C一步一步做完\u201D就行的——如果两个步骤之间没有依赖关系，它们应该并行执行以节省 wall-clock time。DAG 模型让你显式声明依赖关系，然后拓扑排序自动发现可并行的机会。关于\u201C谁来做分解\u201D——让 LLM 自己分解很灵活但不可靠，用固定模板可靠但不灵活。成熟的系统用混合方法：常见任务类型有预定义 DAG 模板，LLM 只需要在模板基础上微调。");

// ---------- Slide 25: 多 Agent 四种架构 ----------
s = contentSlide(p, 25, N, "Multi-Agent Patterns — 什么时候一个 Agent 不够", "Multi-Agent · 四种架构");
styledTable(p, s, [
  [hc("模式"), hc("结构"), hc("数据流"), hc("适用场景")],
  [{ text: "Coordinator", options: { bold: true, color: C.ORANGE } }, "1 指挥 + N worker", "星形（中心↔边缘）", "可并行分解的大任务（80% 场景）"],
  [{ text: "Pipeline", options: { bold: true, color: C.BLUE } }, "顺序流转 A→B→C", "线性", "线性工作流（研究→草稿→审查）"],
  [{ text: "Debate", options: { bold: true, color: C.RED } }, "Agent 间提议/反驳", "全连接", "设计决策、code review（高质量）"],
  [{ text: "Swarm", options: { bold: true, color: C.GREEN } }, "无中心，自组织", "广播", "探索性任务、大规模搜索"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.8, 2.8, 2.8, 4.1], rowH: 0.55, fontSize: 11.5 });
codeBox(p, s, [
  { text: "# Coordinator 模式（最常用）", opt: { color: C.ORANGE, bold: true } },
  { text: "User → Coordinator", opt: { color: "8FBFE8" } },
  { text: "         ├─→ Worker A (研究) ─→ result_A ─┐", opt: { color: "8FD19E" } },
  { text: "         ├─→ Worker B (编码) ─→ result_B ─┼─→ Synthesis → Response", opt: { color: "8FD19E" } },
  { text: "         └─→ Worker C (测试) ─→ result_C ─┘", opt: { color: "8FD19E" } },
  { text: "# 风险：Coordinator 是 SPOF + 瓶颈", opt: { color: "E8736A" } },
], { x: 0.92, y: 4.45, w: 11.5, h: 1.9, fontSize: 10 });
s.addNotes("选择哪种模式取决于任务结构。可并行分解 → Coordinator。线性流程 → Pipeline。需要质量保证的关键决策 → Debate。探索性搜索 → Swarm。实践中 Coordinator 是 80% 场景的选择——它简单、可控、好调试。Debate 模式虽然贵但在关键节点值得——比如架构设计、安全审计。一个有趣的实践：Claude Code 的 Agent tool 本质上就是 Coordinator 模式。");

// ---------- Slide 26: Multi-Agent Context 隔离 ----------
s = contentSlide(p, 26, N, "Sub-Agent 不是\u201C迷你版的父 Agent\u201D— 必须隔离", "Multi-Agent · Context 隔离");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.GREEN } });
s.addText("✓ Sub-agent 接收", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.3, w: 5.6, h: 1.85, fill: { color: "E6F4EA" } });
s.addText(["任务目标（你要做什么）", "必要输入数据（你需要什么）", "全局约束（你不能做什么）", "输出格式要求（返回什么格式）"].map(t => ({ text: "✓ " + t, options: { breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 6 } })), { x: 1.1, y: 2.42, w: 5.3, h: 1.7, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.RED } });
s.addText("✗ Sub-agent 不接收", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.3, w: 5.6, h: 1.85, fill: { color: "FBEAE5" } });
s.addText(["父 Agent 的完整对话历史", "其他 sub-agent 的中间状态", "系统级 secret（最小权限）", "无关的工具 schema"].map(t => ({ text: "✗ " + t, options: { breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 6 } })), { x: 7.0, y: 2.42, w: 5.3, h: 1.7, fontFace: FONT, valign: "top" });
codeBox(p, s, [
  { text: "# Budget 继承", opt: { color: C.ORANGE, bold: true } },
  { text: "Parent Budget: 100K", opt: { color: "8FBFE8" } },
  { text: "  ├─ Reserved for parent: 30K (coordination)", opt: { color: "8FD19E" } },
  { text: "  ├─ Worker A: 25K", opt: { color: "8FD19E" } },
  { text: "  ├─ Worker B: 25K", opt: { color: "8FD19E" } },
  { text: "  └─ Worker C: 20K", opt: { color: "8FD19E" } },
  { text: "# 子预算之和 ≤ 父预算 - 父保留", opt: { color: "E8A33D" } },
  { text: "# 权限继承：只能向下收窄，不能扩展", opt: { color: "E8736A" } },
], { x: 0.92, y: 4.3, w: 11.5, h: 2.05, fontSize: 10 });
s.addNotes("这是多 Agent 系统中最常犯的错误：把父 Agent 的整个对话历史 copy 给子 Agent。我见过一个系统，主 Agent 有 80K 的 context，它 spawn 了 5 个子 Agent，每个都接收了 80K 的历史。结果：5 × 80K = 400K tokens 的额外消耗，每个子任务多花 $2，大部分信息对子 Agent 完全无用。正确做法：只传任务描述（几百 tokens）+ 必要数据。");

// ---------- Slide 27: Multi-Agent 通信 ----------
s = contentSlide(p, 27, N, "Agent 之间怎么\u201C说话\u201D — 三种通信架构", "Multi-Agent · 通信模式");
const comm = [
  { t: "Message Passing", impl: "Actor / Queue / Event bus", feat: "异步、解耦、可跨进程", use: "Coordinator / Pipeline", c: C.BLUE },
  { t: "Shared State", impl: "共享内存 / DB / Redis", feat: "同步、耦合、同进程高效", use: "Blackboard / 紧密协作", c: C.ORANGE },
  { t: "Structured Output Protocol", impl: "JSON-RPC / ACP / schema", feat: "类型安全、可验证、协议层规范", use: "跨服务 / 跨团队", c: C.GREEN },
];
comm.forEach((co, i) => {
  const y = 1.75 + i * 1.2;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 3.4, h: 1.05, fill: { color: co.c } });
  s.addText([{ text: co.t, options: { bold: true, fontSize: 12, color: C.WHITE, breakLine: true } }, { text: co.impl, options: { fontFace: MONO, fontSize: 9.5, color: "E6EAEE", paraSpaceBefore: 5 } }], { x: 1.05, y: y + 0.08, w: 3.2, h: 0.9, fontFace: FONT, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.4, y, w: 4.5, h: 1.05, fill: { color: C.LIGHT } });
  s.addText(co.feat, { x: 4.55, y, w: 4.3, h: 1.05, fontFace: FONT, fontSize: 11, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.0, y, w: 3.4, h: 1.05, fill: { color: "FBEAE5" } });
  s.addText(co.use, { x: 9.15, y, w: 3.2, h: 1.05, fontFace: FONT, fontSize: 11, italic: true, color: co.c, bold: true, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.4, w: 11.5, h: 0.95, fill: { color: C.DARK } });
s.addText([{ text: "选择指南", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "同进程 + 松耦合 → Message Passing  ·  同进程 + 紧耦合 → Shared State  ·  跨进程 → SOP", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.55, w: 11.1, h: 0.75, fontFace: FONT, valign: "top" });
s.addNotes("通信模式的选择看起来是技术细节，但它决定了系统的可扩展性。Message Passing 最灵活——你可以把 worker 部署在不同机器上。Shared State 最高效但最脆弱——两个 Agent 同时写同一个 key 会产生竞态。在生产中，大多数多 Agent 系统用 Message Passing——因为它天然支持重试、可观测、容错。");

// ---------- Slide 28: Multi-Agent 失败处理 ----------
s = contentSlide(p, 28, N, "当子 Agent 失败时 — Partial Results + 优雅降级", "Multi-Agent · 失败处理");
const fails = [
  ["Timeout", "超时未返回 → 视为失败 / 默认值 / 跳过"],
  ["Budget Exhausted", "用完 token → 返回部分结果"],
  ["Error", "内部错误 → 错误信息供 coordinator 决策"],
  ["Quality Below Threshold", "完成但质量低 → 重试或换模型"],
];
fails.forEach((f, i) => {
  const y = 1.75 + i * 0.5;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 4.0, h: 0.42, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.1, h: 0.42, fill: { color: C.RED } });
  s.addText([{ text: f[0] + "  ", options: { bold: true, fontSize: 10.5, color: C.INK } }, { text: f[1], options: { fontSize: 9.5, color: C.GRAY } }], { x: 1.1, y, w: 3.8, h: 0.42, fontFace: FONT, valign: "middle" });
});
s.addText("Partial Results 策略", { x: 5.2, y: 1.75, w: 7, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const stra = [["A · Fail Fast", "任一失败 → 整体失败（强依赖链）", C.RED], ["B · Best Effort", "收集所有成功，忽略失败（独立并行）", C.GREEN], ["C · Retry + Fallback", "重试一次，仍失败则降级方案", C.ORANGE]];
stra.forEach((st, i) => {
  const y = 2.15 + i * 0.55;
  s.addShape(p.shapes.RECTANGLE, { x: 5.2, y, w: 7.2, h: 0.45, fill: { color: st[2] } });
  s.addText([{ text: st[0] + "   ", options: { bold: true, fontSize: 11.5, color: C.WHITE } }, { text: st[1], options: { fontSize: 10, color: "FFFFFF" } }], { x: 5.35, y, w: 6.95, h: 0.45, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.35, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("结果合成不是简单拼接：解决冲突、去重、确保一致性", { x: 0.92, y: 4.35, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.0, w: 11.5, h: 1.35, fill: { color: "FBEAE5" } });
s.addText([{ text: "防止递归爆炸", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "Max depth = 3（主 → sub → sub-sub）  ·  每层 budget = parent / (depth+1)（自然递减）", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 8 } }, { text: "超深度 → 强制在当前层完成，不再 spawn  ·  极少有任务真需要 > 3 层", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 5 } }], { x: 1.12, y: 5.15, w: 11.1, h: 1.15, fontFace: FONT, valign: "top" });
s.addNotes("多 Agent 系统最容易被忽视的问题是\u201C结果合成\u201D。你让 3 个 Agent 独立写代码，拼在一起发现类型不匹配、import 冲突、命名风格不一致。好的 coordinator 在分配任务时就应该给出统一的约束。另一个关键点：递归深度限制。我见过没有深度限制的系统——主 Agent spawn 子 Agent，子 Agent 又 spawn 子子 Agent，最终 5 层深度、32 个 Agent 并发运行、内存耗尽。设 max_depth=3 是经验值。");

// ---------- Slide 29: Claude Code Sub-Agent Case ----------
s = contentSlide(p, 29, N, "Case Study — Claude Code 的子 Agent 设计", "Multi-Agent · 真实案例");
codeBox(p, s, [
  { text: "# 主 Agent Context (200K window)", opt: { color: C.ORANGE, bold: true } },
  { text: "  - System prompt", opt: { color: "8FBFE8" } },
  { text: "  - Full conversation history", opt: { color: "8FBFE8" } },
  { text: "  - All tool schemas", opt: { color: "8FBFE8" } },
  { text: "", opt: {} },
  { text: "# 子 Agent Context (独立的 200K window)", opt: { color: C.ORANGE, bold: true } },
  { text: "  - 精简 system prompt (相关部分)", opt: { color: "8FD19E" } },
  { text: "  - 只有任务描述 (来自主 Agent prompt)", opt: { color: "8FD19E" } },
  { text: "  - 只有需要的 tool schemas", opt: { color: "8FD19E" } },
  { text: "  - 完全独立的 conversation history (从 0 开始)", opt: { color: "8FD19E" } },
], { x: 0.92, y: 1.75, w: 6.5, h: 3.2, fontSize: 10 });
s.addText([{ text: "关键设计决策", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } }, ...["子 Agent context 完全独立（不\u201C继承\u201D）", "返回 text summary（非结构化数据）", "权限继承可收窄（如 Explore agent 只 read）", "敏感操作仍需用户确认（不自动 approve）", "Worktree 隔离防文件冲突"].map(t => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 5 } }))], { x: 7.7, y: 1.75, w: 4.7, h: 3.2, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.1, w: 11.5, h: 1.25, fill: { color: C.DARK } });
s.addText([{ text: "Worktree 隔离 — 多 Agent 并行修改文件的解决方案", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "每个子 Agent 在独立 git worktree 工作 → 完成后 merge 回主分支", options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "代价：+200-500ms 设置 + 磁盘空间  ·  收益：完美的并行隔离", options: { fontSize: 11, italic: true, color: "C7CED6", paraSpaceBefore: 5 } }], { x: 1.12, y: 5.25, w: 11.1, h: 1.05, fontFace: FONT, valign: "top" });
s.addNotes("Claude Code 的子 Agent 设计是 Coordinator 模式的优秀实现。几个值得注意的设计决策：第一，子 Agent 的 context 完全独立——不是\u201C继承\u201D父 Agent 的 context，而是全新开始。这保证了隔离性。第二，返回值是 text summary 而非结构化数据——这给了子 Agent 灵活性。第三，worktree 隔离解决了多 Agent 并行修改文件的冲突问题。");

// ---------- Slide 30: Discussion ----------
s = contentSlide(p, 30, N, "Discussion — 你的场景适合什么模式？", "讨论环节 · 多 Agent 决策");
const scen = [
  { t: "场景 A · 文档生成系统", d: "数据收集 → 初稿 → 事实核查 → 润色，严格先后依赖", a: "Pipeline", c: C.BLUE },
  { t: "场景 B · 代码重构系统", d: "5 个独立微服务并行重构，最终需 API 兼容", a: "Coordinator + 统一约束 + 合成检查", c: C.ORANGE },
  { t: "场景 C · 架构设计助手", d: "微服务 vs monolith / SQL vs NoSQL 多维 trade-off", a: "Debate（Judge 综合）或单 Agent + CoT", c: C.RED },
];
scen.forEach((sc, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 3.6, h: 0.55, fill: { color: C.DARK } });
  s.addText(sc.t, { x: x + 0.1, y: 1.75, w: 3.4, h: 0.55, fontFace: FONT, fontSize: 12, bold: true, color: C.ORANGE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 3.6, h: 1.85, fill: { color: C.LIGHT } });
  s.addText(sc.d, { x: x + 0.15, y: 2.42, w: 3.3, h: 1.65, fontFace: FONT, fontSize: 11, color: C.INK, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x, y: 4.15, w: 3.6, h: 1.0, fill: { color: sc.c } });
  s.addText(sc.a, { x: x + 0.15, y: 4.15, w: 3.3, h: 1.0, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.4, w: 11.5, h: 0.95, fill: { color: "FBEAE5" } });
s.addText([{ text: "讨论引导（5 分钟）", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "① 你们系统中可用多 Agent 优化的场景？  ② 多 Agent 主要代价？（成本+复杂度+调试）  ③ 什么时候不该用？（单 Agent 够时）", options: { fontSize: 11, color: C.INK, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.55, w: 11.1, h: 0.75, fontFace: FONT, valign: "top" });
s.addNotes("这个讨论 5 分钟。场景 B 最有讨论价值——\u201C5 个独立模块\u201D听起来应该用 Coordinator，但\u201C确保 API 兼容性\u201D引入了耦合。如果不提前给约束，5 个 worker 可能各自定义不兼容的接口。这引出多 Agent 设计的核心挑战：你需要在隔离和协作之间找到平衡。太隔离 = 结果不一致；太耦合 = 失去并行的好处。");

// ---------- Slide 31: Cost Engineering ----------
s = contentSlide(p, 31, N, "Smart Model Routing — 用对的模型做对的事", "Cost · 模型路由与 Pareto");
styledTable(p, s, [
  [hc("复杂度"), hc("模型"), hc("价格 (in/out per MTok)"), hc("适用任务")],
  [{ text: "Simple", options: { bold: true, color: C.GREEN } }, "Haiku", "$0.25 / $1.25", "格式化、分类、简单问答"],
  [{ text: "Medium", options: { bold: true, color: C.ORANGE } }, "Sonnet", "$3 / $15", "代码生成、调试、分析"],
  [{ text: "Complex", options: { bold: true, color: C.RED } }, "Opus", "$15 / $75", "架构设计、多步推理、创意"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.6, 1.6, 3.2, 5.1], rowH: 0.55, fontSize: 11.5 });
s.addText("路由决策方法", { x: 0.92, y: 3.65, w: 11, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const routing = [["关键词启发式", "format → Haiku / debug → Sonnet / design → Opus"], ["消息长度", "<100 tokens → 简单 / >1000 tokens → 复杂"], ["训练分类器", "小模型对任务分类 → 路由到合适 tier"]];
routing.forEach((r, i) => {
  const y = 4.05 + i * 0.42;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 11.5, h: 0.35, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.1, h: 0.35, fill: { color: C.ORANGE } });
  s.addText([{ text: r[0] + "  ", options: { bold: true, fontSize: 11, color: C.INK } }, { text: r[1], options: { fontSize: 10.5, color: C.GRAY } }], { x: 1.1, y, w: 11.2, h: 0.35, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.5, w: 11.5, h: 0.85, fill: { color: C.DARK } });
s.addText([{ text: "Cost-Quality Pareto", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "定义最低质量阈值（90% success）→ 找满足阈值的最便宜模型  ·  Caching (50-90%) × Routing (40-60%) = 80%+ 总降本", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.65, w: 11.1, h: 0.65, fontFace: FONT, valign: "top" });
s.addNotes("模型路由是第二高 ROI 的成本优化（第一是 prompt caching）。逻辑很简单：你不会用 Opus 来做\u201C把这段文字翻译成 JSON\u201D 这种简单任务——Haiku 做得一样好，但便宜 60 倍。关键挑战是准确分类任务复杂度。先用启发式跑起来，收集数据后再训练分类器。注意 Pareto 的关键词是\u201C阈值\u201D——不是追求最高质量，而是满足质量下限后追求最低成本。");

// ---------- Slide 32: 设计检查清单 ----------
s = contentSlide(p, 32, N, "S5 Production Readiness — 10 项必检", "S5 设计检查清单");
const checks = [
  ["1", "终止条件", "5 种全部激活，任一触发即停"],
  ["2", "漂移检测", "至少实现 Goal Anchoring"],
  ["3", "Token Budget", "三级 + 80/90/95/99 阈值动作"],
  ["4", "Control Plane", "Pause/Resume/Intervene/Kill 全部可用"],
  ["5", "Provider Abstraction", "至少 1 级 fallback 配置"],
  ["6", "Circuit Breaker", "per-provider 独立 + 错误分类正确"],
  ["7", "Retry", "指数退避+抖动 + 只 retry 可恢复 + max 3"],
  ["8", "Timeout", "四级配置（tool/LLM/task/session）"],
  ["9", "Error-as-Observation", "max_consecutive guard ≤ 3"],
  ["10", "Cost 监控", "per-task / per-model 追踪 + 异常告警"],
];
checks.forEach((c, i) => {
  const x = 0.92 + (i % 2) * 5.95;
  const y = 1.75 + Math.floor(i / 2) * 0.5;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 0.42, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.OVAL, { x: x + 0.1, y: y + 0.05, w: 0.32, h: 0.32, fill: { color: C.ORANGE } });
  s.addText(c[0], { x: x + 0.1, y: y + 0.05, w: 0.32, h: 0.32, fontFace: FONT, fontSize: 10, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addText([{ text: c[1] + "  ", options: { bold: true, fontSize: 10.5, color: C.INK } }, { text: c[2], options: { fontSize: 9.5, color: C.GRAY } }], { x: x + 0.5, y, w: 5.0, h: 0.42, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.4, w: 11.5, h: 1.95, fill: { color: "FBEAE5" } });
s.addText([{ text: "最常缺失的两项", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "#6 Circuit breaker 错误分类（很多人把 429 也算进去）", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 8 } }, { text: "#9 Error-as-observation 没有 max consecutive guard（同错重试 20 次烧 $5 token）", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 5 } }, { text: "上线前逐项核对 — 这 10 项是 production minimum", options: { fontSize: 12, italic: true, bold: true, color: C.RED, paraSpaceBefore: 8 } }], { x: 1.12, y: 4.55, w: 11.1, h: 1.75, fontFace: FONT, valign: "top" });
s.addNotes("这 10 项是 S5 的 production readiness minimum。上线之前逐项核对。最常缺失的是 #6（circuit breaker 的错误分类——很多人把 429 也算进去了）和 #9（error-as-observation 没有 max consecutive guard——Agent 对同一个错误反复重试 20 次才被 max_iterations 终止，白白烧了 $5 token）。");

// ---------- Slide 33: 总结全景 ----------
s = contentSlide(p, 33, N, "一图总结 — Agent Control Plane 全景", "总结 · S5 全景");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.7, w: 11.5, h: 0.5, fill: { color: C.DARK } });
s.addText("S5: AGENT CONTROL PLANE", { x: 0.92, y: 1.7, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
const partA = [["Loop Control", "5 终止"], ["Drift Detect", "3 机制"], ["Token Budget", "3 级 / 4 阈值"]];
partA.forEach((p2, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 2.3, w: 3.6, h: 0.6, fill: { color: C.BLUE } });
  s.addText([{ text: p2[0] + "  ", options: { bold: true, fontSize: 11, color: C.WHITE } }, { text: p2[1], options: { fontSize: 10, color: "E6EAEE" } }], { x: x + 0.1, y: 2.3, w: 3.4, h: 0.6, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 3.0, w: 11.5, h: 0.55, fill: { color: C.ORANGE } });
s.addText("STATE MACHINE + CONTROL PLANE  ·  IDLE → INIT → EXEC → DONE/FAIL  +  Pause/Resume/Intervene/Kill", { x: 0.92, y: 3.0, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const partB = [["Provider", "Single + Multi + CB + Fallback"], ["Resilience", "Bulkhead + Retry + Timeout + EaO"], ["Orchestration", "DAG + 4 Multi-Agent + Routing"]];
partB.forEach((p2, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 3.65, w: 3.6, h: 1.55, fill: { color: C.GREEN } });
  s.addText([{ text: p2[0], options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: p2[1], options: { fontSize: 10, color: "FFFFFF", paraSpaceBefore: 8 } }], { x: x + 0.12, y: 3.78, w: 3.36, h: 1.3, fontFace: FONT, align: "center", valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.3, w: 11.5, h: 0.55, fill: { color: C.RED } });
s.addText("核心指标：task completion >90% · avg loop <15 · drift <2% · fallback <5% · cost within budget", { x: 0.92, y: 5.3, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addText("Mini-Lab 预告：max_iterations=3 观察终止 · 注入 drift 测检测 · 模拟 provider 故障看熔断", { x: 0.92, y: 5.95, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: C.GRAY, align: "center" });
s.addNotes("这就是 S5 的全景。上半部分管 Agent 自身的行为（别漂移、别超预算、别停不下来），下半部分管 Agent 依赖的基础设施（provider 宕了怎么办、网络断了怎么办、错误怎么自愈）。两者合在一起就是 Agent 的\u201C控制面\u201D——就像 Kubernetes 的 control plane 管理容器的生命周期一样，S5 管理 Agent loop 的生命周期。接下来的 Mini-Lab 让你亲手设置这些参数，观察 Agent 在不同约束下的行为变化。");

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
module.exports = {};

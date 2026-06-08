const { C, FONT, MONO, W, newDeck, darkSlide, contentSlide, bullets, styledTable, hc } = require("./aws_theme");
const p = newDeck("Harness Engineering — 01 Opening");
const N = 16;
let s;

// ---------- Slide 1: Cover ----------
s = darkSlide(p);
s.addText("HARNESS ENGINEERING", { x: 0.6, y: 1.7, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("构建生产级 AI Agent 系统的工程学", { x: 0.6, y: 2.25, w: 11.5, h: 1.6, fontFace: FONT, fontSize: 40, bold: true, color: C.WHITE, lineSpacingMultiple: 1.05 });
s.addText("LLM 与执行环境之间的工程层", { x: 0.62, y: 4.0, w: 11, h: 0.5, fontFace: FONT, fontSize: 18, color: "C7CED6" });
s.addShape(p.shapes.LINE, { x: 0.62, y: 5.15, w: 6.2, h: 0, line: { color: "47525E", width: 1 } });
s.addText([
  { text: "讲师：Harness Engineering 教研团队", options: { breakLine: true, fontSize: 13, color: "AEB7C0" } },
  { text: "2026 年", options: { fontSize: 13, color: "AEB7C0" } },
], { x: 0.62, y: 5.35, w: 8, h: 0.9, fontFace: FONT, paraSpaceAfter: 4 });
s.addText("01 · Opening", { x: 9.5, y: 6.7, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: "6B7682", align: "right" });
s.addNotes("欢迎各位。这门课叫 Harness Engineering——直译是“线束工程”。线束是什么？在航空领域，线束是连接引擎与驾驶舱的所有线缆和控制系统。引擎再强大，没有可靠的线束，飞机飞不起来。今天的 LLM 就是引擎，而我们要讲的，就是怎么把这台引擎变成一架能安全飞行的飞机。两天时间，我们从头构建这套工程体系。");

// ---------- Slide 2: Course Map ----------
s = contentSlide(p, 2, N, "两天课程结构", "Course Map");
styledTable(p, s, [
  [hc("时间"), hc("模块"), hc("核心系统")],
  ["Day 1 上午", "Opening + Context Assembly", "S1: 信息 → LLM"],
  ["Day 1 下午", "Tool Governance + Security", "S2: LLM → 外部世界 / S3: 约束与人类控制"],
  ["Day 2 上午", "Feedback & State", "S4: 观测 + 记忆 + 评估闭环"],
  ["Day 2 下午", "Entropy Management + Integration", "S5: 编排 + 容错 + 成本控制"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [2.0, 4.6, 4.9], rowH: 0.55, fontSize: 13 });
s.addText(bullets([
  "五大系统 (S1–S5) 是课程骨架",
  "每个系统：概念 → 源码分析 → 动手实践",
  "最终产出：一套可部署的 Agent Harness 框架",
]), { x: 0.92, y: 5.1, w: 11.5, h: 1.5, valign: "top" });
s.addNotes("先看全局地图。两天，五大系统，每个系统我们都会深入源码。这不是一个“理念课”——每个模块都有可运行的代码。到 Day 2 结束，你手上会有一套完整的 Harness 框架原型。先记住这张图，后面我们不断回来对照。");

// ---------- Slide 3: The Paradigm Shift ----------
s = contentSlide(p, 3, N, "范式跃迁：Prompt → Context → Harness", "The Paradigm Shift");
const stairs = [
  { t: "Prompt Engineering", y: "2022–2023", d: "单次输入质量", x: 0.92, w: 3.6, top: 4.2, col: C.GRAY },
  { t: "Context Engineering", y: "2024–2025", d: "信息组装与窗口管理", x: 4.72, w: 3.6, top: 3.4, col: C.BLUE },
  { t: "Harness Engineering", y: "2025–", d: "整个执行环境的工程化", x: 8.52, w: 3.9, top: 2.6, col: C.ORANGE },
];
stairs.forEach((b) => {
  s.addShape(p.shapes.RECTANGLE, { x: b.x, y: b.top, w: b.w, h: 6.5 - b.top, fill: { color: b.col }, line: { color: b.col } });
  s.addText([
    { text: b.y, options: { breakLine: true, fontSize: 11, color: "FFE9CC", bold: true } },
    { text: b.t, options: { breakLine: true, fontSize: 16, color: C.WHITE, bold: true, paraSpaceBefore: 3 } },
    { text: b.d, options: { fontSize: 12, color: "FFFFFF", paraSpaceBefore: 6 } },
  ], { x: b.x + 0.15, y: b.top + 0.15, w: b.w - 0.3, h: 6.3 - b.top, fontFace: FONT, valign: "top" });
});
s.addText("每一层都包含前一层：Context Engineering 是 Harness 的子系统 S1，覆盖范围逐级放大——输入、输出、约束、反馈、容错。", { x: 0.92, y: 1.65, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 14, color: C.INK, valign: "top" });
s.addNotes("2022 年大家在做什么？写 prompt。2024 年进化到 Context Engineering——怎么把正确的信息、在正确的时机、以正确的格式喂给模型。这是个巨大进步，但还不够。为什么？因为 Context Engineering 只管“输入侧”。模型输出之后呢？工具调用怎么治理？权限怎么控制？失败怎么恢复？成本怎么管理？这些问题合在一起，就是 Harness Engineering。它不是替代前两者，而是包含前两者——Context Engineering 是 Harness 的子系统 S1。");

// ---------- Slide 4: Probability Compounding ----------
s = contentSlide(p, 4, N, "99%¹⁰⁰ = 36.6% —— 为什么工程比模型更重要", "Probability Compounding");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 4.3, h: 3.0, fill: { color: C.DARK } });
s.addText([
  { text: "0.99", options: { fontSize: 60, bold: true, color: C.WHITE } },
  { text: "100", options: { fontSize: 22, bold: true, color: C.WHITE, superscript: true } },
], { x: 1.1, y: 2.1, w: 3.9, h: 1.2, fontFace: FONT, align: "center" });
s.addText("= 36.6%", { x: 1.1, y: 3.35, w: 3.9, h: 0.9, fontFace: FONT, fontSize: 40, bold: true, color: C.ORANGE, align: "center" });
styledTable(p, s, [
  [hc("单步成功率"), hc("10 步"), hc("50 步"), hc("100 步")],
  ["95%", "59.9%", "7.7%", { text: "0.6%", options: { color: C.RED, bold: true } }],
  ["99%", "90.4%", "60.5%", { text: "36.6%", options: { color: C.RED, bold: true } }],
  ["99.5%", "95.1%", "77.8%", "60.6%"],
  ["99.9%", "99.0%", "95.1%", { text: "90.5%", options: { color: C.GREEN, bold: true } }],
], { x: 5.5, y: 1.75, w: 6.9, colW: [2.1, 1.6, 1.6, 1.6], rowH: 0.55, align: "center" });
s.addText("Agent 是多步系统：每一步的微小改进，在复合效应下被巨幅放大。这就是 Harness Engineering 存在的根本原因。", { x: 0.92, y: 5.4, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 15, bold: true, color: C.INK, valign: "top" });
s.addNotes("这是整门课最重要的一张 slide。请记住这个数字：99% 的 100 次方等于 36.6%。什么意思？假设你的 Agent 每一步操作成功率是 99%——已经很高了对吧？但如果一个任务需要 100 步，整体成功率只有 36.6%。三分之一。这不是理论数字——一个复杂的代码生成任务，从理解需求、搜索代码、生成方案、编辑文件、运行测试到修复错误，轻松超过 100 步。所以问题不是“模型够不够聪明”，问题是“你的工程系统能不能把每一步的成功率从 99% 提升到 99.9%”。差 0.9 个百分点，100 步之后结果从 36.6% 变成 90.5%。这就是 Harness Engineering 的价值——它不是锦上添花，它决定系统能不能用。");

// ---------- Slide 5: Dark Code ----------
s = contentSlide(p, 5, N, "Dark Code —— 传统工程方法失效的新现实", "Dark Code");
s.addText("Dark Code：LLM 在运行时生成的行为，无法被预先审查——绕过了 review / test / CI 等所有前置检查。", { x: 0.92, y: 1.62, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 14, color: C.INK, valign: "top" });
// traditional flow (crossed)
const flow1 = ["Code", "Review", "Test", "Deploy"];
flow1.forEach((t, i) => { s.addShape(p.shapes.RECTANGLE, { x: 0.92 + i * 1.5, y: 2.35, w: 1.25, h: 0.55, fill: { color: C.LIGHT }, line: { color: C.LINE } }); s.addText(t, { x: 0.92 + i * 1.5, y: 2.35, w: 1.25, h: 0.55, fontFace: FONT, fontSize: 12, align: "center", valign: "middle", color: C.GRAY }); });
s.addText("✕  传统软件：部署前可控", { x: 7.1, y: 2.35, w: 5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.RED, valign: "middle" });
// agent flow
const flow2 = [{ t: "User", c: C.LIGHT, tc: C.GRAY }, { t: "LLM", c: C.BLUE, tc: C.WHITE }, { t: "[ Dark Code ]", c: C.DARK, tc: C.ORANGE }, { t: "Execution", c: C.LIGHT, tc: C.GRAY }];
flow2.forEach((b, i) => { s.addShape(p.shapes.RECTANGLE, { x: 0.92 + i * 1.5, y: 3.15, w: 1.35, h: 0.55, fill: { color: b.c }, line: { color: C.LINE } }); s.addText(b.t, { x: 0.92 + i * 1.5, y: 3.15, w: 1.35, h: 0.55, fontFace: FONT, fontSize: 11, bold: true, align: "center", valign: "middle", color: b.tc }); });
s.addText("Agent：行为在运行时实时生成", { x: 7.1, y: 3.15, w: 5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, valign: "middle" });
styledTable(p, s, [
  [hc("传统保障"), hc("对 Dark Code 的效果")],
  ["Code Review", "无效 —— 代码运行时才生成"],
  ["单元测试", "部分有效 —— 只能测已知路径"],
  ["CI/CD", "无效 —— 无法预测运行时行为"],
  ["静态分析", "无效 —— 没有静态代码可分析"],
], { x: 0.92, y: 4.05, w: 7.4, colW: [2.4, 5.0], rowH: 0.5, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 8.7, y: 4.05, w: 3.7, h: 2.5, fill: { color: C.ORANGE } });
s.addText([
  { text: "应对策略", options: { breakLine: true, fontSize: 13, bold: true, color: "5A3D00" } },
  { text: "Runtime Governance", options: { breakLine: true, fontSize: 20, bold: true, color: C.WHITE, paraSpaceBefore: 6 } },
  { text: "在执行的每一步施加约束（S2 + S3）", options: { fontSize: 13, color: "FFFFFF", paraSpaceBefore: 8 } },
], { x: 8.9, y: 4.35, w: 3.3, h: 2.0, fontFace: FONT, valign: "top" });
s.addNotes("我们做软件工程这么多年，有一套完善的质量保障体系：写代码、code review、跑测试、CI 通过、部署。但 Agent 系统里有个根本性问题——我叫它 Dark Code。LLM 生成的工具调用、代码片段、操作序列，都是运行时才产生的。你没法提前 review，没法提前测试，因为在运行之前它根本不存在。这就是为什么传统方法全部失效。我们需要的不是更好的测试，而是一套运行时治理体系——在每一步执行的瞬间进行约束和验证。这就是 S2 和 S3 要解决的问题。");

// ---------- Slide 6: The 80/20 Split ----------
s = contentSlide(p, 6, N, "模型 15-20% vs Harness 80-85%", "The 80/20 Split");
s.addChart(p.charts.DOUGHNUT, [{ name: "贡献", labels: ["Harness 80-85%", "模型 15-20%"], values: [82, 18] }], {
  x: 0.92, y: 1.8, w: 4.6, h: 3.9, chartColors: [C.ORANGE, C.BLUE], showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: FONT,
  showPercent: true, dataLabelColor: "FFFFFF", dataLabelFontSize: 12, dataLabelFontBold: true, holeSize: 55, showTitle: false,
});
s.addChart(p.charts.BAR, [{ name: "SWE-bench 通过率", labels: ["优化前", "优化 Harness 后"], values: [45, 90] }], {
  x: 5.8, y: 1.8, w: 6.6, h: 3.9, barDir: "col", chartColors: [C.BLUE, C.ORANGE], chartColorsOpacity: 100,
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.INK, dataLabelFontFace: FONT, dataLabelFontBold: true,
  valAxisMaxVal: 100, valAxisHidden: true, catAxisLabelColor: C.INK, catAxisLabelFontFace: FONT, catAxisLabelFontSize: 12,
  valGridLine: { style: "none" }, showLegend: false, showTitle: true, title: "同一模型 codex-1，仅改工程层", titleColor: C.GRAY, titleFontFace: FONT, titleFontSize: 12,
});
s.addText("结论：模型决定思维上限（能不能想出方案），Harness 决定可靠性（方案能不能稳定执行）。30-40 个百分点提升，纯工程贡献。", { x: 0.92, y: 6.0, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 14, bold: true, color: C.INK, valign: "top" });
s.addNotes("让数据说话。OpenAI 的 Codex 产品，用的是同一个模型 codex-1。最初在 SWE-bench 上大概 40-50% 的通过率。然后他们没有换模型，只优化了 Harness——怎么组装 context、怎么管理工具调用、怎么处理失败、怎么做 feedback loop。结果？飙升到接近 90%。30-40 个百分点的提升，纯靠工程。这就是为什么我说模型只占 15-20%，Harness 占 80-85%。模型决定了“能不能想出来”，Harness 决定了“想出来之后能不能做对、做稳、做到”。你们来这里两天，学的就是那 80-85%。");

// ---------- Slide 7: Five Systems Architecture ----------
s = contentSlide(p, 7, N, "Harness 五大系统全景", "Five Systems Architecture");
const OX = 0.92, OY = 1.7, OW = 11.5, OH = 5.05;
s.addShape(p.shapes.RECTANGLE, { x: OX, y: OY, w: OW, h: OH, fill: { color: C.DARK } });
s.addText("S5: Entropy Management  ·  编排 + 容错 + 成本控制（控制平面）", { x: OX + 0.2, y: OY + 0.12, w: OW - 0.4, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE });
const box = (x, w, t1, t2, fill, tc) => { s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.55, w, h: 1.1, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 }); s.addText([{ text: t1, options: { breakLine: true, fontSize: 13, bold: true, color: tc } }, { text: t2, options: { fontSize: 10, color: tc } }], { x, y: 2.6, w, h: 1.0, fontFace: FONT, align: "center", valign: "middle" }); };
box(1.5, 2.7, "S1", "Context Assembly", C.WHITE, C.INK);
box(5.3, 2.7, "LLM", "推理核心", C.BLUE, C.WHITE);
box(9.1, 2.7, "S2", "Tool Governance", C.WHITE, C.INK);
// S3 / S4 stacked below center
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.3, y: 4.0, w: 2.7, h: 0.85, fill: { color: C.WHITE }, line: { color: C.WHITE }, rectRadius: 0.06 });
s.addText([{ text: "S3", options: { breakLine: true, fontSize: 13, bold: true, color: C.INK } }, { text: "Security & Approval", options: { fontSize: 10, color: C.INK } }], { x: 5.3, y: 4.0, w: 2.7, h: 0.85, fontFace: FONT, align: "center", valign: "middle" });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.3, y: 5.15, w: 2.7, h: 0.85, fill: { color: C.WHITE }, line: { color: C.WHITE }, rectRadius: 0.06 });
s.addText([{ text: "S4", options: { breakLine: true, fontSize: 13, bold: true, color: C.INK } }, { text: "Feedback & State", options: { fontSize: 10, color: C.INK } }], { x: 5.3, y: 5.15, w: 2.7, h: 0.85, fontFace: FONT, align: "center", valign: "middle" });
const ar = (x, y, w, h, both) => s.addShape(p.shapes.LINE, { x, y, w, h, line: { color: C.ORANGE, width: 2, endArrowType: "triangle", beginArrowType: both ? "triangle" : "none" } });
ar(4.2, 3.1, 1.1, 0, true);  // S1<->LLM
ar(8.0, 3.1, 1.1, 0, true);  // LLM<->S2
s.addShape(p.shapes.LINE, { x: 6.65, y: 3.65, w: 0, h: 0.35, line: { color: C.ORANGE, width: 2, beginArrowType: "triangle", endArrowType: "triangle" } }); // LLM<->S3
s.addShape(p.shapes.LINE, { x: 6.65, y: 4.85, w: 0, h: 0.3, line: { color: C.ORANGE, width: 2, endArrowType: "triangle" } }); // S4->S3
s.addShape(p.shapes.LINE, { x: 1.85, y: 5.55, w: 3.45, h: 0, line: { color: "8C9AA6", width: 1.5, dashType: "dash" } }); // feedback horiz
s.addShape(p.shapes.LINE, { x: 1.85, y: 3.65, w: 0, h: 1.9, line: { color: "8C9AA6", width: 1.5, dashType: "dash", beginArrowType: "triangle" } }); // feedback up to S1
s.addText("反馈回路", { x: 2.5, y: 5.18, w: 2.3, h: 0.3, fontFace: FONT, fontSize: 9, italic: true, color: "AEB7C0" });
s.addText("输入侧", { x: 1.5, y: 3.7, w: 2.7, h: 0.3, fontFace: FONT, fontSize: 9, color: "8C9AA6", align: "center" });
s.addText("输出侧", { x: 9.1, y: 3.7, w: 2.7, h: 0.3, fontFace: FONT, fontSize: 9, color: "8C9AA6", align: "center" });
s.addNotes("这是整个课程的架构图，请拍照或记下来。五大系统，各司其职。S1 管输入——给模型组装什么信息。S2 管输出——模型调用的工具怎么治理。S3 管安全——什么操作必须被拦截或需要人工审批。这三个是“运行时三件套”，Agent 每走一步，S1、S2、S3 都会被触发一次。然后 S4 是反馈环路——执行结果回来了，怎么观测、怎么记忆、怎么评估，然后反馈给下一步的 S1。最后 S5 是控制平面——编排多步流程、处理失败、控制成本。S5 在最外层，管全局。两天课，我们逐一拆解每个系统的设计和实现。");

// ---------- Slide 8: Principle 1 — Constraint-First ----------
s = contentSlide(p, 8, N, "设计原则 #1 —— 约束优先", "Design Principle · Constraint-First");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.85, w: 4.3, h: 3.0, fill: { color: "FBEAE5" }, line: { color: C.RED, width: 1.5 } });
s.addText("CANNOT", { x: 0.92, y: 2.0, w: 4.3, h: 0.6, fontFace: FONT, fontSize: 22, bold: true, color: C.RED, align: "center" });
s.addText("约束空间（先画牢笼）", { x: 0.92, y: 2.6, w: 4.3, h: 0.4, fontFace: FONT, fontSize: 12, color: C.RED, align: "center" });
s.addShape(p.shapes.RECTANGLE, { x: 2.3, y: 3.5, w: 1.55, h: 1.0, fill: { color: "E6F4EA" }, line: { color: C.GREEN, width: 1.5 } });
s.addText([{ text: "CAN", options: { breakLine: true, fontSize: 14, bold: true, color: C.GREEN } }, { text: "能力", options: { fontSize: 10, color: C.GREEN } }], { x: 2.3, y: 3.6, w: 1.55, h: 0.8, fontFace: FONT, align: "center" });
s.addText(bullets([
  { text: "核心：先定义“不能做什么”，再定义“能做什么”", opt: { bold: true } },
  "Tool allowlist > blocklist（白名单优于黑名单）",
  "Default deny > Default allow",
  "文件系统：先 sandbox，再逐步放开路径",
  "网络：先全部禁止，再按需开放域名",
]), { x: 5.5, y: 1.85, w: 6.9, h: 2.6, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 5.5, y: 4.7, w: 6.9, h: 1.55, fill: { color: C.LIGHT } });
s.addText([{ text: "反例：", options: { bold: true, color: C.RED, fontSize: 13 } }, { text: "某 Agent 框架默认开放所有 shell 命令 → 模型 hallucinate 了 rm -rf /home/user/data → 用户数据被删除。约束优先本可避免。", options: { fontSize: 13, color: C.INK } }], { x: 5.7, y: 4.85, w: 6.5, h: 1.3, fontFace: FONT, valign: "top" });
s.addNotes("第一个设计原则：Constraint-First，约束优先。传统做产品是“我能做什么”，列功能清单。做 Harness 必须反过来——先定义“绝对不能做什么”。为什么？因为 Dark Code。你不知道 LLM 下一步要干什么，所以你必须先画好边界。白名单，default deny，sandbox first。这不是过度防御，这是唯一可行的策略。我见过一个案例：某 Agent 框架默认允许所有 shell 命令，结果模型 hallucinate 了一个 rm -rf /home/user/data，用户数据全没了。如果约束优先——shell 命令默认禁止，只开放白名单——这个事故根本不会发生。");

// ---------- Slide 9: Principle 2 — Verifiability ----------
s = contentSlide(p, 9, N, "设计原则 #2 —— 可验证性", "Design Principle · Verifiability");
const pyr = [{ t: "Reproducibility 能否重现", w: 3.2, c: C.ORANGE }, { t: "Evaluation 做得好不好", w: 4.6, c: C.BLUE }, { t: "Observability 发生了什么", w: 6.0, c: C.DARK }];
pyr.forEach((b, i) => { const cx = 0.92 + 3.0; const y = 1.95 + i * 1.15; s.addShape(p.shapes.RECTANGLE, { x: cx + (6.0 - b.w) / 2, y, w: b.w, h: 1.0, fill: { color: b.c } }); s.addText(b.t, { x: cx + (6.0 - b.w) / 2, y, w: b.w, h: 1.0, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" }); });
s.addText([
  { text: "行业现状（LangChain 调研）", options: { breakLine: true, fontSize: 13, bold: true, color: C.INK, paraSpaceAfter: 10 } },
  { text: "89%", options: { fontSize: 30, bold: true, color: C.BLUE } }, { text: "  有 observability", options: { breakLine: true, fontSize: 12, color: C.GRAY } },
  { text: "52%", options: { fontSize: 30, bold: true, color: C.ORANGE, paraSpaceBefore: 6 } }, { text: "  做 evaluation", options: { breakLine: true, fontSize: 12, color: C.GRAY } },
  { text: "37%", options: { fontSize: 30, bold: true, color: C.RED, paraSpaceBefore: 6 } }, { text: "  可验证性缺口", options: { fontSize: 12, color: C.GRAY } },
], { x: 10.3, y: 2.0, w: 2.6, h: 4.0, fontFace: FONT, valign: "top" });
s.addText("完整可验证性 = Observability + Evaluation + Reproducibility —— 能看到行为，更要知道行为对不对。", { x: 0.92, y: 6.15, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 14, bold: true, color: C.INK, valign: "top" });
s.addNotes("第二个原则：Verifiability，可验证性。Agent 做了什么，你必须能追溯。不只是“记了日志”——LangChain 的调研显示 89% 的团队有 observability，但只有 52% 做 evaluation。这中间有 37% 的缺口——你能看到 Agent 调用了什么工具、花了多少 token，但你不知道它做得对不对。可验证性需要三层：Observability 是“发生了什么”，Evaluation 是“做得好不好”，Reproducibility 是“能不能重现”。三层全做到，你才真正控制住了 Agent 的行为。S4 会深入讲这个体系。");

// ---------- Slide 10: Principle 3 — Progressive Trust ----------
s = contentSlide(p, 10, N, "设计原则 #3 —— 渐进信任", "Design Principle · Progressive Trust");
s.addChart(p.charts.LINE, [{ name: "信任/权限", labels: ["新会话", "成功1", "成功2", "成功3", "异常!", "收紧", "恢复"], values: [1, 2, 3, 4.2, 1.2, 2, 3] }], {
  x: 0.92, y: 1.85, w: 6.6, h: 4.0, lineSize: 3, lineSmooth: true, chartColors: [C.ORANGE], showLegend: false,
  valAxisHidden: true, catAxisLabelColor: C.GRAY, catAxisLabelFontFace: FONT, catAxisLabelFontSize: 10, valGridLine: { color: "EDEDED", size: 0.5 }, catGridLine: { style: "none" },
  showTitle: true, title: "权限随上下文动态升降", titleColor: C.GRAY, titleFontFace: FONT, titleFontSize: 12,
});
s.addText(bullets([
  { text: "权限是动态的，不是二元的（有/无）", opt: { bold: true } },
  "新会话：最小权限",
  "连续成功：逐步放开",
  "出现异常：立即收紧",
  "高风险操作：始终需要确认",
  { text: "类比驾照：实习期 + 扣分制 + 吊销机制", opt: { color: C.BLUE } },
]), { x: 7.8, y: 1.95, w: 4.6, h: 4.5, valign: "top" });
s.addNotes("第三个原则：Progressive Trust，渐进信任。权限不应该是“全开或全关”。想想驾照制度——你不是拿到驾照就可以开任何车。有实习期、有扣分、有吊销。Agent 也一样：刚开始对话，最小权限；连续执行成功，逐步放开；一旦出现异常行为——比如试图访问不相关的文件——立即收紧。这不是固定配置，这是运行时动态调整的。S3 会详细讲 Claude Code 是怎么实现这套 progressive trust 的——它的 permission system 就是这个原则的典型实现。");

// ---------- Slide 11: Principle 4 — Design for Failure ----------
s = contentSlide(p, 11, N, "设计原则 #4 —— 为失败而设计", "Design Principle · Design for Failure");
const fmodes = [["LLM 幻觉", "生成不存在的文件/函数/API"], ["工具执行失败", "超时、权限不足、资源不可用"], ["状态不一致", "部分完成、中间状态残留"], ["无限循环", "重复尝试无法成功的操作"]];
const fixes = [["Checkpoint / Rollback", "检查点与回滚"], ["Circuit Breaker", "熔断器"], ["Retry + backoff", "重试有上限"], ["Graceful degradation", "优雅降级"]];
s.addText("失败模式（常态，非意外）", { x: 0.92, y: 1.7, w: 5.6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.RED });
s.addText("工程应对", { x: 6.8, y: 1.7, w: 5.6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.GREEN });
fmodes.forEach((m, i) => { const y = 2.15 + i * 0.85; s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 5.6, h: 0.72, fill: { color: "FBEAE5" } }); s.addText([{ text: m[0] + "  ", options: { bold: true, color: C.INK } }, { text: m[1], options: { color: C.GRAY, fontSize: 11 } }], { x: 1.1, y, w: 5.3, h: 0.72, fontFace: FONT, fontSize: 13, valign: "middle" }); });
fixes.forEach((m, i) => { const y = 2.15 + i * 0.85; s.addShape(p.shapes.RECTANGLE, { x: 6.8, y, w: 5.6, h: 0.72, fill: { color: "E6F4EA" } }); s.addText([{ text: m[0] + "  ", options: { bold: true, color: C.INK } }, { text: m[1], options: { color: C.GRAY, fontSize: 11 } }], { x: 6.98, y, w: 5.3, h: 0.72, fontFace: FONT, fontSize: 13, valign: "middle" }); });
s.addText([{ text: "成本数据：", options: { bold: true, color: C.ORANGE, fontSize: 14 } }, { text: "合理的容错设计可带来 60-80% 的成本降低——无效重试和无限循环是最大的 token 浪费来源。", options: { fontSize: 14, color: C.INK } }], { x: 0.92, y: 5.95, w: 11.5, h: 0.8, fontFace: FONT, valign: "top" });
s.addNotes("最后一个原则：Design for Failure，为失败而设计。不是“出错了再想办法”，而是在架构层面假设每一步都会出错。LLM 会幻觉、工具会超时、状态会不一致、Agent 会陷入死循环——这些不是意外，这是常态。你的 Harness 必须内建恢复能力：checkpoint 让你能回滚，circuit breaker 让你能熔断，retry 让你能重试但有上限，graceful degradation 让你在部分失败时仍能给出有价值的结果。这里有个有趣的数据：合理的容错设计不仅提升可靠性，还能降低 60-80% 的成本——因为无效重试和无限循环是最大的 token 浪费来源。S5 会深入讲这些机制。");

// ---------- Slide 12: Three Reference Systems ----------
s = contentSlide(p, 12, N, "三大参考系统 —— 设计哲学对比", "Three Reference Systems");
styledTable(p, s, [
  [hc("维度"), hc("Claude Code"), hc("OpenCode"), hc("OpenAI Codex CLI")],
  ["设计哲学", { text: "交互优先", options: { color: C.BLUE, bold: true } }, { text: "开放优先", options: { color: C.GREEN, bold: true } }, { text: "协议优先", options: { color: C.ORANGE, bold: true } }],
  ["核心架构", "Async Generator + Streaming", "Multi-model + Plugin SDK", "Item / Turn / Thread"],
  ["优先级", "低延迟、流式体验", "多模型支持、社区生态", "结构一致性、可组合性"],
  ["开源协议", "Proprietary（部分开源）", "MIT", "MIT"],
  ["适用场景", "高频交互、实时反馈", "需要模型灵活切换", "需要严格结构化输出"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.7, 3.3, 3.25, 3.25], rowH: 0.6, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.85, w: 11.5, h: 0.8, fill: { color: C.DARK } });
s.addText("No best, only trade-offs —— 没有“最好”的系统，关键是你的场景需要什么哲学？", { x: 0.92, y: 5.85, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 15, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("这门课我们会反复参考三个系统。Claude Code——Anthropic 官方的，设计哲学是交互优先：async generator 架构、全程 streaming、极致低延迟。用户输入一个字就开始响应。OpenCode——开源社区的，设计哲学是开放优先：支持多种模型、插件化 SDK、MIT 协议，社区可以自由扩展。OpenAI Codex CLI——设计哲学是协议优先：Item/Turn/Thread 三层抽象，prefix consistency 保证 cache hit，一切都是结构化的。三种哲学，没有对错。这两天我们不是要“选一个”，而是理解每种选择背后的 trade-off。你做自己系统的时候，要想清楚你的用户最需要什么。");

// ---------- Slide 13: Five Systems Deep Dive Preview ----------
s = contentSlide(p, 13, N, "五大系统速览 —— 每个系统解决什么问题", "Deep Dive Preview");
const sys = [
  ["S1", "Context Assembly", "有限窗口内给 LLM 最有用的信息？", "Compaction · CLAUDE.md 层级 · 动态注入", C.BLUE],
  ["S2", "Tool Governance", "如何安全地让 LLM 操作真实世界？", "Tool schema · 参数验证 · 执行沙箱", C.ORANGE],
  ["S3", "Security & Approval", "哪些操作需要人类确认？如何不过度打扰？", "Permission model · risk scoring · approval flow", C.GREEN],
  ["S4", "Feedback & State", "执行结果如何反馈以改进后续决策？", "Observation · memory · evaluation pipeline", C.BLUE],
  ["S5", "Entropy Management", "如何让系统稳定、可控、经济地运行？", "Orchestration · circuit breaker · cost control", C.ORANGE],
];
sys.forEach((r, i) => { const y = 1.75 + i * 0.98; s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 0.85, h: 0.82, fill: { color: r[4] } }); s.addText(r[0], { x: 0.92, y, w: 0.85, h: 0.82, fontFace: FONT, fontSize: 20, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addShape(p.shapes.RECTANGLE, { x: 1.77, y, w: 10.65, h: 0.82, fill: { color: C.LIGHT } }); s.addText([{ text: r[1] + "   ", options: { bold: true, fontSize: 14, color: C.INK } }, { text: r[2], options: { fontSize: 12, color: C.GRAY, breakLine: true } }, { text: r[3], options: { fontSize: 11, color: r[4], italic: true } }], { x: 1.95, y, w: 10.3, h: 0.82, fontFace: FONT, valign: "middle" }); });
s.addNotes("快速过一遍五个系统各解决什么问题。S1——Context Assembly：窗口就那么大，怎么装最有用的信息？Claude Code 的 compaction 机制、CLAUDE.md 的多层级加载，都是经典方案。S2——Tool Governance：模型要调工具了，怎么确保安全？参数验证、沙箱执行、结果过滤。S3——Security：哪些操作太危险必须人来确认？怎么做到既安全又不过度打扰？S4——Feedback：执行完了，结果怎么回来？怎么让 Agent 从错误中学习？S5——Entropy Management：怎么防止系统跑飞？怎么控制成本？怎么编排复杂流程？每个系统我们都会深入源码级别。");

// ---------- Slide 14: The Engineering Levers ----------
s = contentSlide(p, 14, N, "六根工程杠杆 —— 60-80% 成本降低的来源", "The Engineering Levers");
const levers = [
  ["Context Compaction", "压缩历史对话，减少 token"],
  ["Prompt Caching", "prefix 一致命中缓存（降 90%）"],
  ["Tool Result Truncation", "截断过长的工具输出"],
  ["Intelligent Routing", "简单任务用小模型"],
  ["Circuit Breaking", "熔断无效循环，避免浪费"],
  ["Batch Processing", "合并可并行操作，减少调用"],
];
levers.forEach((l, i) => { const col = i % 3, row = Math.floor(i / 3); const x = 0.92 + col * 3.87, y = 1.95 + row * 1.9; s.addShape(p.shapes.RECTANGLE, { x, y, w: 3.6, h: 1.65, fill: { color: C.LIGHT } }); s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.12, h: 1.65, fill: { color: C.ORANGE } }); s.addText(String(i + 1), { x: x + 0.25, y: y + 0.15, w: 1, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: C.ORANGE }); s.addText([{ text: l[0], options: { breakLine: true, bold: true, fontSize: 14, color: C.INK } }, { text: l[1], options: { fontSize: 12, color: C.GRAY, paraSpaceBefore: 4 } }], { x: x + 0.25, y: y + 0.7, w: 3.2, h: 0.85, fontFace: FONT, valign: "top" }); });
s.addText("六根杠杆组合使用，可实现 60-80% 的成本降低——没有任何一根需要更换模型。", { x: 0.92, y: 5.95, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 14, bold: true, color: C.INK, valign: "top" });
s.addNotes("补充一个成本视角。很多人觉得 Agent 贵，token 烧钱。但 Harness Engineering 有六根成本杠杆，组合使用可以降低 60-80%。Prompt Caching 一项就能降 90%——前提是你的 context assembly 做对了，prefix 一致。Circuit Breaking 避免无限循环烧 token。Intelligent Routing 让简单操作走便宜的小模型。这些都是纯工程优化，不需要换模型。Day 2 的 S5 会详细讲每根杠杆怎么实现。");

// ---------- Slide 15: What We'll Build ----------
s = contentSlide(p, 15, N, "两天之后，你将拥有", "What We'll Build");
const col = (x, tag, tagc, items) => { s.addShape(p.shapes.RECTANGLE, { x, y: 1.8, w: 5.55, h: 0.6, fill: { color: tagc } }); s.addText(tag, { x, y: 1.8, w: 5.55, h: 0.6, fontFace: FONT, fontSize: 16, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addText(items.map((t) => ({ text: t, options: { bullet: { code: "2713" }, breakLine: true, fontFace: FONT, fontSize: 13, color: C.INK, paraSpaceAfter: 10 } })), { x: x + 0.1, y: 2.6, w: 5.4, h: 3.0, valign: "top" }); };
col(0.92, "Day 1 产出", C.BLUE, ["Context Assembly pipeline（compaction + 多源加载）", "Tool Governance 框架（schema + 验证 + 沙箱）", "Permission System（分级审批 + progressive trust）"]);
col(6.86, "Day 2 产出", C.ORANGE, ["Feedback Loop（observation → evaluation → memory）", "Entropy Manager（orchestration + circuit breaker + cost）", "集成的 Mini Agent Harness（五大系统协同）"]);
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.7, w: 11.49, h: 0.95, fill: { color: C.LIGHT } });
s.addText([{ text: "附加价值：", options: { bold: true, color: C.ORANGE } }, { text: "三大系统源码阅读笔记 · 可复用设计模式清单 · 系统成熟度自检表", options: { color: C.INK } }], { x: 1.1, y: 5.7, w: 11.1, h: 0.95, fontFace: FONT, fontSize: 13, valign: "middle" });
s.addNotes("两天结束之后你手上会有什么？不是一堆 slide 和笔记——是可运行的代码。Day 1 结束你有 context assembly pipeline、tool governance 框架、permission system。Day 2 结束你有 feedback loop、entropy manager，最后集成成一个 mini agent harness。这不是玩具——这些模式直接来自 Claude Code、OpenCode、Codex CLI 的真实实现。你回去之后可以直接用在自己的系统上。好，概览结束。接下来我们进入第一个系统——S1: Context Assembly。准备好了吗？");

// ---------- Slide 16: Transition to S1 ----------
s = darkSlide(p);
s.addText("NEXT", { x: 0.6, y: 1.7, w: 6, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("S1: Context Assembly System", { x: 0.6, y: 2.2, w: 12, h: 0.9, fontFace: FONT, fontSize: 34, bold: true, color: C.WHITE });
s.addText("核心问题：在有限的 context window 内，如何给 LLM 提供最大价值的信息？", { x: 0.62, y: 3.2, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 16, color: "C7CED6" });
s.addText([
  { text: "Context 的五种来源", options: { bullet: { code: "2022" }, breakLine: true } },
  { text: "CLAUDE.md 的多层级加载机制", options: { bullet: { code: "2022" }, breakLine: true } },
  { text: "Compaction 策略与实现", options: { bullet: { code: "2022" }, breakLine: true } },
  { text: "System Prompt 的工程化构建", options: { bullet: { code: "2022" } } },
], { x: 0.7, y: 4.1, w: 8, h: 2.0, fontFace: FONT, fontSize: 15, color: "E6EAEE", paraSpaceAfter: 8 });
s.addText("约 90 分钟（含实践）  ·  请打开你的开发环境", { x: 0.62, y: 6.4, w: 11, h: 0.4, fontFace: FONT, fontSize: 13, italic: true, color: C.ORANGE });
s.addNotes("概览到此结束。我们花了一个小时建立了全局认知：为什么需要 Harness Engineering（概率复合效应）、面对什么新挑战（Dark Code）、整体架构长什么样（五大系统）、设计原则是什么（约束优先、可验证、渐进信任、为失败设计）。接下来我们进入第一个系统：Context Assembly。这是 Harness 的“输入侧”——怎么在有限的窗口里给模型提供最大价值的信息。请打开你的开发环境，我们马上开始动手。");

p.writeFile({ fileName: "/Users/qcguang/Desktop/courses/HarnessEngineering/ppt_v3/01_opening.pptx" }).then(f => console.log("WROTE", f));

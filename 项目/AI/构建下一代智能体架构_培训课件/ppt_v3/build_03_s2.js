const { C, FONT, MONO, newDeck, darkSlide, contentSlide, bullets, styledTable, hc, setModule, codeBox } = require("./aws_theme");
setModule("03 S2 · Tool Governance");
const p = newDeck("Harness Engineering — 03 S2 Tool Governance");
const N = 36;
const OUT = "/Users/qcguang/Desktop/courses/HarnessEngineering/ppt_v3/03_S2_tool_governance.pptx";
let s;

// ---------- Slide 1: Cover ----------
s = darkSlide(p);
s.addText("S2 · TOOL GOVERNANCE", { x: 0.6, y: 1.6, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("工具治理系统", { x: 0.6, y: 2.15, w: 11.5, h: 0.95, fontFace: FONT, fontSize: 40, bold: true, color: C.WHITE });
s.addText("Agent 的手与脚 — 与物理世界交互的唯一通道", { x: 0.62, y: 3.15, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 18, color: "C7CED6" });
s.addShape(p.shapes.LINE, { x: 0.62, y: 4.05, w: 6.2, h: 0, line: { color: "47525E", width: 1 } });
s.addText([
  { text: "如果 LLM 是大脑，Tool System 就是手脚", options: { breakLine: true } },
  { text: "覆盖：工具抽象 · 执行流水线 · 权限模型 · 结构化输出解析 · MCP/ACP 协议", options: { breakLine: true } },
  { text: "承接：S1 组装 context → LLM 产出 tool_use → S2 接管全部执行生命周期", options: {} },
], { x: 0.62, y: 4.3, w: 12, h: 1.8, fontFace: FONT, fontSize: 15, color: "E6EAEE", paraSpaceAfter: 9 });
s.addText("80 min  ·  36 slides", { x: 9.5, y: 6.7, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: "6B7682", align: "right" });
s.addNotes("开场直接点题：上一个模块我们解决了“Agent 看到什么”的问题，这个模块我们解决“Agent 能做什么”的问题。LLM 再聪明，如果没有工具，它只能输出文字。工具系统赋予 Agent 改变世界的能力 — 但能力越大，治理需求越大。接下来 80 分钟，我们完整拆解一个生产级工具治理系统的设计。");

// ---------- Slide 2: 范式转变 ----------
s = contentSlide(p, 2, N, "范式转变 — 从确定性到非确定性", "传统调用 vs Agent 调用");
styledTable(p, s, [
  [hc("维度"), hc("传统 API 调用"), hc("Agent 工具调用")],
  ["调用目标", "编译时确定 (http.get(\"/api/users\"))", "运行时由 LLM 选择"],
  ["参数来源", "开发者硬编码或用户输入", "LLM 从自然语言推理生成"],
  ["调用顺序", "代码逻辑决定，可静态分析", "基于中间结果的动态规划"],
  ["可预测性", "确定性 — 同输入同输出", "非确定性 — 同 prompt 可能选不同工具"],
  ["错误来源", "bug（可复现）", "幻觉（概率性、难复现）"],
  ["治理方式", "代码审查 + 单元测试", "运行时拦截 + 权限系统 + schema 校验"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [1.6, 4.95, 4.95], rowH: 0.5, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.55, w: 11.5, h: 0.9, fill: { color: C.DARK } });
s.addText("关键洞察：传统软件的复杂度在编译时可控；Agent 的复杂度在运行时爆发。", { x: 0.92, y: 5.55, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 15, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("先建立认知冲突。问在座各位：你们写过多少年的 API 调用代码？那些调用在编译时就确定了目标、参数、顺序。现在想象一下，调用什么工具、传什么参数、以什么顺序执行，全部由一个概率模型在运行时决定。这不是小变化 — 这是软件工程基础假设的颠覆。传统软件工程花了 50 年建立确定性（类型系统、静态分析、形式化验证），Agent 在一夜之间把不确定性重新注入了系统核心。");

// ---------- Slide 3: 四大灾难 ----------
s = contentSlide(p, 3, N, "没有治理时会发生什么 — 四大灾难", "灾难场景");
const dis = [
  { t: "灾难 1 · 错误工具选择 → 删生产库", l: ["用户意图：“清理测试数据”", "Agent 选 bash_exec → rm -rf /data/production/"], r: "根因：tool description 不精确" },
  { t: "灾难 2 · MCP 超时 → 级联阻塞", l: ["server 响应 30s → 5min", "Agent 无限等待 → context 持续消耗 → 全挂起"], r: "根因：无超时 / circuit breaker" },
  { t: "灾难 3 · 幻觉参数 → 静默写错", l: ["传入 {mode:\"upsert\"}，schema 仅 insert/update", "未校验 → fallback update → 覆盖已有数据"], r: "根因：缺 input validation（strict）" },
  { t: "灾难 4 · 虚构工具 → 浪费 turn", l: ["调用 deploy_to_production（不存在）", "tool not found → 再试一个不存在的 → 循环"], r: "根因：工具列表未严格约束" },
];
dis.forEach((d, i) => { const x = 0.92 + (i % 2) * 5.95; const y = 1.85 + Math.floor(i / 2) * 2.2; s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 0.55, fill: { color: C.RED } }); s.addText(d.t, { x: x + 0.15, y, w: 5.4, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, valign: "middle" }); s.addShape(p.shapes.RECTANGLE, { x, y: y + 0.55, w: 5.55, h: 1.5, fill: { color: "FBEAE5" } }); s.addText([...d.l.map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceAfter: 5 } })), { text: d.r, options: { fontSize: 11.5, color: C.RED, bold: true } }], { x: x + 0.18, y: y + 0.68, w: 5.25, h: 1.3, fontFace: FONT, valign: "top" }); });
s.addText("这四个灾难分别对应流水线 Step 1 / 4 / 3 / 1 的缺失。", { x: 0.92, y: 6.35, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, align: "center" });
s.addNotes("每个场景停顿 10 秒让大家消化。这些听起来极端吗？实际上在早期 Agent 部署中，类似事故每周都在发生。场景 1 导致了 Claude Code 的 permission system；场景 2 推动了 timeout 机制成为标配；场景 3 让 strict validation 成为默认；场景 4 催生了 tool hallucination detection。工程系统的每一道防线，背后都是真实的事故教训。");

// ---------- Slide 4: 异构能力源 ----------
s = contentSlide(p, 4, N, "异构能力源的统一接口问题", "Tool 抽象的核心问题");
const sources = ["Bash 执行", "文件系统", "HTTP 请求", "数据库", "MCP Server", "子 Agent"];
sources.forEach((t, i) => { const x = 0.92 + i * 1.94; s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 1.8, h: 0.55, fill: { color: "6E8BA3" } }); s.addText(t, { x, y: 1.7, w: 1.8, h: 0.55, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addShape(p.shapes.LINE, { x: x + 0.9, y: 2.25, w: 0, h: 0.35, line: { color: C.GRAY, width: 1.2, endArrowType: "triangle" } }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.65, w: 11.5, h: 0.75, fill: { color: C.DARK } });
s.addText("统一接口层 — Everything is a Tool   ·   tool.call(input) → ToolResult", { x: 0.92, y: 2.65, w: 11.5, h: 0.75, fontFace: FONT, fontSize: 15, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addShape(p.shapes.LINE, { x: 6.65, y: 3.4, w: 0, h: 0.35, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.RECTANGLE, { x: 4.4, y: 3.8, w: 4.5, h: 0.55, fill: { color: C.BLUE } });
s.addText("Agent Core", { x: 4.4, y: 3.8, w: 4.5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.65, w: 5.6, h: 1.85, fill: { color: "FBEAE5" } });
s.addText([{ text: "没有统一接口的后果", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } },
  { text: "核心代码充斥 if(type==='bash')…else if…", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 6 } },
  { text: "新增工具类型 = 改核心调度 = 高风险变更", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 4 } },
  { text: "无法复用 timeout/truncation/permission 横切关注点", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 4 } }], { x: 1.12, y: 4.8, w: 5.2, h: 1.6, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 4.65, w: 5.6, h: 1.85, fill: { color: "EEF1F3" } });
s.addText([{ text: "设计目标", options: { bold: true, color: C.BLUE, fontSize: 13, breakLine: true } },
  { text: "类比 POSIX：everything is a file descriptor", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 6 } },
  { text: "Agent 只需知道 tool.call(input) → ToolResult", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 4 } },
  { text: "不关心底层是 bash / 远程 API / 子 Agent", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 4 } }], { x: 7.02, y: 4.8, w: 5.2, h: 1.6, fontFace: FONT, valign: "top" });
s.addNotes("类比 POSIX 对操作系统做的事情 — “everything is a file descriptor”。不管是磁盘文件、网络 socket、还是管道，对进程来说都是 fd。我们需要同样的抽象：“everything is a Tool”。不管底层是 bash 命令、远程 API、还是另一个 Agent，对 LLM 来说都是同一个接口：给 name + input，得到 ToolResult。这个抽象是整个工具治理系统的地基。");

// ---------- Slide 5: Tool 接口设计 ----------
s = contentSlide(p, 5, N, "Tool 接口设计 — 5 个必备方法 + 2 个可选方法", "Tool Interface");
codeBox(p, s, [
  { text: "interface Tool<I, O, P> {", opt: {} },
  { text: "  name: string;              // 唯一标识，LLM 选择依据", opt: { color: "8FD19E" } },
  { text: "  description: string;       // 这就是 prompt engineering", opt: { color: "8FD19E" } },
  { text: "  inputSchema: JSONSchema;   // Pydantic / Zod 生成", opt: { color: "8FD19E" } },
  { text: "  call(input, ctx): Promise<ToolResult<O>>;", opt: { color: "8FD19E" } },
  { text: "  checkPermissions(input, ctx): PermissionResult;", opt: { color: "8FD19E" } },
  { text: "  progress?(cb): void;       // 可选：进度报告", opt: { color: "8FBFE8" } },
  { text: "  stream?(input): AsyncGenerator<ToolResult<O>>;", opt: { color: "8FBFE8" } },
  { text: "}", opt: {} },
], { x: 0.92, y: 1.8, w: 7.0, h: 3.0, fontSize: 11.5 });
s.addText([
  { text: "必备（绿）", options: { bold: true, color: C.GREEN, breakLine: true, fontSize: 13 } },
  { text: "name · description · inputSchema · call · checkPermissions", options: { fontSize: 11.5, color: C.INK, breakLine: true, paraSpaceBefore: 4, paraSpaceAfter: 10 } },
  { text: "可选（蓝）", options: { bold: true, color: C.BLUE, breakLine: true, fontSize: 13 } },
  { text: "progress · stream（大输出工具）", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 4 } },
], { x: 8.2, y: 1.85, w: 4.2, h: 3.0, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.1, w: 11.5, h: 1.25, fill: { color: C.ORANGE } });
s.addText([{ text: "description IS prompt engineering   ", options: { bold: true, fontSize: 16, color: C.WHITE } }, { text: "改一个词，tool 被选中概率可变化 20%（file_read 改写后 65% → 92%）。Claude Code 的 Bash description 有 200+ 字，详述 when to use / when NOT to use。", options: { fontSize: 12.5, color: "FFFFFF" } }], { x: 1.12, y: 5.25, w: 11.1, h: 1.0, fontFace: FONT, valign: "middle" });
s.addNotes("重点讲 description。我展示一个真实数据：在某个 harness 的 A/B 测试中，把 file_read 工具的 description 从 “Read a file” 改成 “Read the contents of a file at the given path. Use this instead of bash cat for reading files — it's faster and handles encoding correctly.” 之后，LLM 正确选择 file_read 而非 bash cat 的比例从 65% 提升到 92%。这不是文档，这是控制 LLM 行为的杠杆。");

// ---------- Slide 6: 工具分类与风险 ----------
s = contentSlide(p, 6, N, "四类工具，四种治理策略", "Tool 分类与风险等级");
styledTable(p, s, [
  [hc("类型"), hc("典型示例"), hc("风险"), hc("核心威胁"), hc("治理重点")],
  [{ text: "Execution", options: { bold: true, color: C.RED } }, "bash, code_exec", { text: "Critical", options: { color: C.RED, bold: true } }, "可以做任何事（God tools）", "沙箱、白名单、每次审批、审计"],
  [{ text: "Network", options: { bold: true, color: "E0651A" } }, "http_fetch, webhook", { text: "High", options: { color: "E0651A", bold: true } }, "数据外泄、SSRF、rate limit", "域名白名单、限流、超时、auth"],
  [{ text: "Agent", options: { bold: true, color: C.ORANGE } }, "spawn_agent", { text: "Med-High", options: { color: C.ORANGE, bold: true } }, "递归失控、token 爆炸", "深度限制、budget 继承、权限收窄"],
  [{ text: "Domain", options: { bold: true, color: C.GREEN } }, "db_query, file_write", { text: "Medium", options: { color: C.GREEN, bold: true } }, "复杂依赖、不可逆副作用", "强校验、事务回滚、路径限制"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [1.5, 2.4, 1.5, 2.9, 3.2], rowH: 0.6, fontSize: 11.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 1.45, fill: { color: C.LIGHT } });
s.addText([{ text: "风险不是工具固有属性，而是 (工具 + 输入 + 上下文) 的函数", options: { bold: true, color: C.INK, fontSize: 14, breakLine: true } },
  { text: "同一个 bash：ls = 低风险；rm -rf / = 极高风险", options: { fontSize: 12.5, color: C.GRAY, breakLine: true, paraSpaceBefore: 8 } },
  { text: "Claude Code 的选择：允许 bash，但每次调用都需权限检查（除非在 allowlist 中）—— power vs safety 的经典 trade-off", options: { fontSize: 12.5, color: C.GRAY, paraSpaceBefore: 4 } }], { x: 1.12, y: 5.1, w: 11.1, h: 1.2, fontFace: FONT, valign: "top" });
s.addNotes("Execution 类工具是最强大也最危险的。Claude Code 允许 bash 是一个大胆的设计决策 — 因为禁用 bash 意味着 Agent 连 git status 都做不了。但代价是什么？每次 bash 调用都需要用户按一下 “Allow”（除非用户配置了 allowlist）。这是 security vs usability 的典型张力。后续 S3 会详细讨论如何通过 policy 配置来平衡这个 trade-off。");

// ---------- Slide 7: 六步执行流水线 ----------
s = contentSlide(p, 7, N, "Tool Execution Pipeline — 从 LLM 输出到结果持久化", "六步执行流水线");
const steps = [
  ["Step 1 · Discovery", "toolRegistry.get(name) · O(1) lookup", "防工具幻觉"],
  ["Step 2 · Permission", "checkPermissions() · Free/Ask/Approve/Deny", "防越权操作"],
  ["Step 3 · Validation", "validate(input, schema) · JSON Schema/Zod", "防幻觉参数"],
  ["Step 4 · Execution", "tool.call() · timeout 30s · 异常隔离", "防 hang / crash"],
  ["Step 5 · Result", "truncate + serialize · max 1MB", "防 context 溢出"],
  ["Step 6 · Persistence", "cache + history + trace", "可观测 + 可复用"],
];
steps.forEach((st, i) => { const y = 1.7 + i * 0.72; s.addShape(p.shapes.RECTANGLE, { x: 1.6, y, w: 8.0, h: 0.6, fill: { color: i === 3 ? C.ORANGE : (i < 3 ? C.DARK : C.BLUE) } }); s.addText([{ text: st[0] + "   ", options: { bold: true, fontSize: 12.5, color: C.WHITE } }, { text: st[1], options: { fontSize: 10.5, color: "E6EAEE" } }], { x: 1.78, y, w: 7.7, h: 0.6, fontFace: FONT, valign: "middle" }); s.addText(st[2], { x: 9.75, y, w: 2.6, h: 0.6, fontFace: FONT, fontSize: 11, color: C.RED, valign: "middle" }); if (i < 5) s.addShape(p.shapes.LINE, { x: 5.6, y: y + 0.6, w: 0, h: 0.12, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 6.15, w: 11.5, h: 0.55, fill: { color: C.DARK } });
s.addText("任何一步失败 → 立即返回 ToolResult { is_error: true }。不 crash，不 hang，不静默失败。", { x: 0.92, y: 6.15, w: 11.5, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("这是本模块的核心骨架。接下来几张 slides 我们逐步拆解每一步的细节。先记住整体结构：6 步串行，任何一步失败都走 error path，绝不 crash 整个 Agent。这个设计保证了 resilience — 工具系统可以出错，但 Agent 会话永远不会因为一次工具调用失败而终止。每一步的存在都有明确的理由：防止一种具体的灾难场景。");

// ---------- Slide 8: Step 1-2 ----------
s = contentSlide(p, 8, N, "找到工具 → 检查权限", "Step 1-2 · Discovery + Permission");
s.addText("Step 1 · Tool Discovery", { x: 0.92, y: 1.65, w: 11, h: 0.35, fontFace: FONT, fontSize: 14, bold: true, color: C.BLUE });
s.addText(bullets([
  "Map<string, Tool> — O(1) lookup by name",
  "启动时静态注册 + 运行时动态注册（MCP tools/list）",
  "name 不存在 → \"Tool not found. Available: [...]\"",
  "不用 fuzzy match：防 typo 意外调用相似工具",
], { fontSize: 12.5 }), { x: 0.92, y: 2.05, w: 11.5, h: 1.7, valign: "top" });
s.addText("Step 2 · Permission Check — 四级权限模型", { x: 0.92, y: 3.75, w: 11, h: 0.35, fontFace: FONT, fontSize: 14, bold: true, color: C.BLUE });
const doors = [["Free", "直接通过", C.GREEN], ["Ask-first", "每次弹窗", "E0A000"], ["Approve-once", "session 记住", C.ORANGE], ["Deny", "硬性拒绝", C.RED]];
doors.forEach((d, i) => { const x = 0.92 + i * 2.95; s.addShape(p.shapes.RECTANGLE, { x, y: 4.2, w: 2.7, h: 1.3, fill: { color: d[2] } }); s.addText([{ text: d[0], options: { bold: true, fontSize: 15, color: C.WHITE, breakLine: true } }, { text: d[1], options: { fontSize: 12, color: "FFFFFF", paraSpaceBefore: 6 } }], { x, y: 4.45, w: 2.7, h: 0.85, fontFace: FONT, align: "center", valign: "top" }); });
s.addText("检查依据三要素：tool metadata + input content + runtime context  ·  permission check 本身 < 1ms  ·  S2 执行 check（mechanism），S3 定义 policy（规则）", { x: 0.92, y: 5.7, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 12, color: C.INK, valign: "top" });
s.addNotes("Step 1 实现简单但至关重要 — 严格的 name match 是第一道防线。如果 LLM hallucinate 了一个不存在的工具名，这里就直接拦住了，而不是让它滑到后续步骤。Step 2 是用户体验的关键触点 — Claude Code 用户最常见的交互就是权限弹窗 “Allow Bash: git commit -m ...”。如何在安全和流畅之间取得平衡，是 harness 设计者最重要的判断。");

// ---------- Slide 9: Step 3 Validation ----------
s = contentSlide(p, 9, N, "参数校验 — 在执行前拦截一切非法输入", "Step 3 · Input Validation");
codeBox(p, s, [
  { text: "// LLM 输出", opt: { color: "8C9AA6" } },
  { text: "{ \"mode\": \"upsert\" }   // ✗ 不在 schema", opt: { color: "F2A93B" } },
  { text: "", opt: {} },
  { text: "// schema 约束", opt: { color: "8C9AA6" } },
  { text: "enum: [\"insert\", \"update\"]", opt: { color: "8FD19E" } },
  { text: "", opt: {} },
  { text: "// 校验结果（self-correction）", opt: { color: "8C9AA6" } },
  { text: "{ is_error: true, content:", opt: { color: "E8736A" } },
  { text: "  \"'mode' must be one of [insert,update]\" }", opt: { color: "E8736A" } },
], { x: 0.92, y: 1.8, w: 6.3, h: 3.2, fontSize: 11 });
s.addText(bullets([
  { text: "为何在 execution 之前？副作用不可逆，validation 是零成本软拦截", opt: { bold: true } },
  "校验：required / 类型 / enum / 数值范围 / 格式 / strict（多余字段报错）",
  "技术栈：JSON Schema · Zod · Pydantic",
  { text: "首次失败后 LLM 自我修正成功率 ~90%", opt: { bold: true, color: C.ORANGE } },
  { text: "黄金法则：validate BEFORE execute", opt: { bold: true, color: C.RED } },
], { fontSize: 12.5 }), { x: 7.5, y: 1.85, w: 4.9, h: 3.5, valign: "top" });
s.addNotes("回到开场的灾难场景 3：幻觉参数 “upsert” 导致数据损坏。如果有严格的 input validation + strict mode，那个不存在的参数值会被立即拦截，LLM 会收到明确的错误信息并在下一个 turn 自动修正。这一步的 ROI 极高 — 实现成本低（JSON Schema 验证库现成），效果显著（拦截 90%+ 的参数幻觉）。记住：validate BEFORE execute — 这是工具系统设计的黄金法则。");

// ---------- Slide 10: Step 4 Execution ----------
s = contentSlide(p, 10, N, "执行 — 超时保护、异常隔离、并发控制", "Step 4 · Execution");
const prot = [
  { t: "Timeout 超时保护", d: ["默认 30s（按工具配置）", "Promise.race([call, timeout])", "cancel → wait 5s → abort"], c: C.BLUE },
  { t: "Exception 异常隔离", d: ["try/catch 包裹一切", "异常 → ToolResult{is_error}", "stack trace 入日志，不给 LLM"], c: C.RED },
  { t: "Concurrency 并发", d: ["独立 call 并行执行", "同工具 max 5 / 全局 max 10", "串行 N×t → max(t)"], c: C.GREEN },
  { t: "Resource 资源限制", d: ["子进程 / 独立 context", "max output size", "chroot / 路径白名单"], c: C.ORANGE },
];
prot.forEach((pr, i) => { const x = 0.92 + (i % 2) * 4.3; const y = 1.8 + Math.floor(i / 2) * 2.1; s.addShape(p.shapes.RECTANGLE, { x, y, w: 4.0, h: 1.9, fill: { color: C.LIGHT } }); s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.12, h: 1.9, fill: { color: pr.c } }); s.addText([{ text: pr.t, options: { bold: true, fontSize: 13, color: C.INK, breakLine: true } }, ...pr.d.map((t) => ({ text: t, options: { fontSize: 11, color: C.GRAY, breakLine: true, paraSpaceBefore: 4 } }))], { x: x + 0.25, y: y + 0.12, w: 3.6, h: 1.7, fontFace: FONT, valign: "top" }); });
styledTable(p, s, [
  [hc("工具"), hc("超时")],
  ["file_read", "5s"], ["http_fetch", "30s"], ["bash", "120s"], ["agent_spawn", "300s"],
], { x: 9.5, y: 1.8, w: 2.9, colW: [1.7, 1.2], rowH: 0.78, fontSize: 12 });
s.addNotes("超时是最容易被忽视也最容易出事的机制。回想灾难场景 2：MCP server 变慢导致级联 hang。如果有 30s timeout，最坏情况就是一次工具调用失败返回 timeout error，Agent 可以选择重试或换一个方案。没有 timeout，整个 session 可能永远挂住，用户只能强制终止。并发执行是性能利器 — 当 LLM 同时请求读取 5 个文件时，串行需要 5 秒，并行只需 1 秒。");

// ---------- Slide 11: Step 5-6 ----------
s = contentSlide(p, 11, N, "结果截断、序列化、持久化", "Step 5-6 · Result + Persistence");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.8, w: 5.6, h: 2.0, fill: { color: C.LIGHT } });
s.addText([{ text: "Step 5 · Result Processing", options: { bold: true, color: C.BLUE, fontSize: 14, breakLine: true } },
  { text: "默认上限 1MB → 超过则截断 + “[truncated, …]”", options: { fontSize: 12, color: C.INK, breakLine: true, paraSpaceBefore: 8 } },
  { text: "在语义边界截断（行尾 / JSON 边界），非按字节切", options: { fontSize: 12, color: C.INK, breakLine: true, paraSpaceBefore: 4 } },
  { text: "统一格式 ToolResultBlock { content, is_error }", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 4 } }], { x: 1.12, y: 1.95, w: 5.2, h: 1.8, fontFace: FONT, valign: "top" });
s.addText("Step 6 · Persistence — 三个存储目标", { x: 0.92, y: 4.0, w: 11, h: 0.35, fontFace: FONT, fontSize: 14, bold: true, color: C.BLUE });
const store = [["History", "写入对话历史 → 下轮 context（最重要）", C.DARK], ["Cache", "幂等工具结果缓存，避免重复 I/O", C.ORANGE], ["Trace", "结构化日志 → 调试/审计（S4 数据源）", C.BLUE]];
store.forEach((st, i) => { const x = 0.92 + i * 3.87; s.addShape(p.shapes.RECTANGLE, { x, y: 4.45, w: 3.6, h: 1.3, fill: { color: st[2] } }); s.addText([{ text: st[0], options: { bold: true, fontSize: 15, color: C.WHITE, breakLine: true } }, { text: st[1], options: { fontSize: 11, color: "E6EAEE", paraSpaceBefore: 6 } }], { x: x + 0.15, y: 4.6, w: 3.3, h: 1.05, fontFace: FONT, valign: "top" }); });
s.addText("Metrics：tool_call_duration_ms (P50/P95/P99) · tool_success_rate · result_size_bytes（监控截断频率）", { x: 0.92, y: 5.95, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 11.5, color: C.GRAY, valign: "top" });
s.addText("Step 5", { x: 6.7, y: 1.8, w: 5, h: 0.3, fontFace: FONT, fontSize: 1, color: C.WHITE });
s.addNotes("Result truncation 看起来简单，但设计时要考虑几个细节：截断点是否在有效 JSON 中间？截断后 LLM 能否理解结果？最佳实践是在语义边界截断（行尾、JSON 对象边界），而不是粗暴按字节切断一个 JSON array 导致 parse error。另外，cache 机制要注意失效策略 — file_read 的缓存在文件被修改后必须失效。这些“小细节”在生产环境中决定了用户体验的好坏。");

// ---------- Slide 12: 三大保护机制 ----------
s = contentSlide(p, 12, N, "Timeout + Truncation + Exception Isolation — 不可协商的底线", "三大保护机制");
styledTable(p, s, [
  [hc("保护机制"), hc("防范问题"), hc("默认值"), hc("触发后行为"), hc("可配置")],
  [{ text: "Timeout", options: { bold: true, color: C.BLUE } }, "执行无限挂起", "30s", "cancel → abort → timeout error", "按工具"],
  [{ text: "Truncation", options: { bold: true, color: C.GREEN } }, "结果撑爆 context", "1MB", "截断 + “[truncated]” 标注", "按工具"],
  [{ text: "Exception Isolation", options: { bold: true, color: C.RED } }, "工具 crash 杀死 Agent", "N/A", "try/catch → is_error=true", "始终开启"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [2.5, 2.6, 1.2, 3.7, 1.5], rowH: 0.7, fontSize: 12 });
const shields = [["Timeout", "30s", C.BLUE], ["Truncation", "1MB", C.GREEN], ["Exception", "is_error", C.RED]];
shields.forEach((sh, i) => { const x = 2.3 + i * 3.2; s.addShape(p.shapes.RECTANGLE, { x, y: 4.65, w: 2.6, h: 1.05, fill: { color: sh[2] } }); s.addText([{ text: "🛡 " + sh[0], options: { bold: true, fontSize: 14, color: C.WHITE, breakLine: true } }, { text: sh[1], options: { fontSize: 16, bold: true, color: "FFFFFF", paraSpaceBefore: 4 } }], { x, y: 4.78, w: 2.6, h: 0.85, fontFace: FONT, align: "center", valign: "top" }); });
s.addText("设计哲学：Fail gracefully, never fail silently  ·  这三个是 Day 1 必须实现的 non-negotiable minimums。", { x: 0.92, y: 5.9, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, align: "center", valign: "top" });
s.addNotes("记住三个数字：30s、1MB、is_error=true。这是工具治理的 safety net。在你自己设计 harness 时，这三个是第一天就必须实现的 — 不是 v2、不是 nice-to-have、不是 tech debt。没有这三个机制就上线，等同于开着没有刹车的车上高速。即使你的 permission system 还没做好、schema validation 还不完善，只要这三道防线在，Agent 至少不会把整个系统搞崩。");

// ---------- Slide 13: Discussion ----------
s = contentSlide(p, 13, N, "Discussion — 哪一步缺失导致了事故？", "讨论环节 · 灾难诊断");
const sc = [
  { t: "场景 A", body: "Agent 被要求“重构 auth”，却调用 deploy_service 把未完成代码部署到 staging。工具存在、schema 对，但权限被图方便设成了 Free。", ans: "Step 2 Permission — 策略配置错误，deploy 不应是 Free", c: C.ORANGE },
  { t: "场景 B", body: "Agent 调用 db_query 传入 {sql:\"SELECT *\", limit:\"all\"}，返回 2GB 结果，context window 被撑爆，后续推理全失败。", ans: "Step 3 Validation + Step 5 Truncation — 双重失守", c: C.RED },
  { t: "场景 C", body: "Agent 要读配置，调用 read_config（实际是 read_file）。连续 4 次 tool-not-found，最终放弃告诉用户“无法完成”。", ans: "Step 1 Discovery — 缺编辑距离纠错 + available 列表", c: C.BLUE },
];
sc.forEach((c, i) => { const x = 0.92 + i * 3.87; s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 3.6, h: 0.5, fill: { color: C.DARK } }); s.addText(c.t, { x, y: 1.75, w: 3.6, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addShape(p.shapes.RECTANGLE, { x, y: 2.25, w: 3.6, h: 2.0, fill: { color: C.LIGHT } }); s.addText(c.body, { x: x + 0.15, y: 2.4, w: 3.3, h: 1.75, fontFace: FONT, fontSize: 11.5, color: C.INK, valign: "top" }); s.addShape(p.shapes.RECTANGLE, { x, y: 4.25, w: 3.6, h: 1.1, fill: { color: c.c } }); s.addText(c.ans, { x: x + 0.15, y: 4.35, w: 3.3, h: 0.9, fontFace: FONT, fontSize: 11.5, bold: true, color: C.WHITE, valign: "middle" }); });
s.addText("引导问题：① 你团队的 deploy 权限怎么管理？ ② 除 validation+truncation 还有哪些防线？ ③ 纠错阈值设多少？太低会误纠正吗？", { x: 0.92, y: 5.6, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 12, color: C.GRAY, valign: "top" });
s.addNotes("这个讨论环节有两个目的：一是检验学员是否真正理解了六步管线（不只是记住名字，而是能诊断缺失）；二是引出真实经验分享。给每个场景 1 分钟思考，然后邀请 2-3 人分享判断。场景 A 最有讨论价值——很多团队为了“先跑通”把危险工具设成 Free，上线后忘记收紧。场景 B 让大家意识到防线需要纵深——单一 step 失效时其他 step 能兜底。场景 C 引出后面幻觉检测的内容。整个讨论控制在 5 分钟以内。");

// ---------- Slide 14: Case Bash Tool ----------
s = contentSlide(p, 14, N, "Real-World Case — Claude Code 如何治理最危险的工具", "案例 · Bash Tool 设计");
codeBox(p, s, [
  { text: "Execute a bash command in the user's shell.", opt: {} },
  { text: "IMPORTANT:", opt: { color: C.ORANGE, bold: true } },
  { text: "- Prefer dedicated tools (Read, Edit, Write)", opt: { color: "8FD19E" } },
  { text: "- Quote file paths with spaces", opt: { color: "8FD19E" } },
  { text: "- Optional timeout up to 600000ms (10 min)", opt: { color: "8FD19E" } },
  { text: "- git: prefer new commit over amend", opt: { color: "8FD19E" } },
  { text: "When NOT to use:", opt: { color: C.ORANGE, bold: true } },
  { text: "- Reading files → use Read", opt: { color: "E8A33D" } },
  { text: "- Editing files → use Edit", opt: { color: "E8A33D" } },
], { x: 0.92, y: 1.8, w: 6.3, h: 3.4, fontSize: 11 });
const bcards = [["Permission", "默认 Ask-first · allowlist Bash(git *) 自动通过 · Deny 硬编码 rm -rf / 与 fork bomb（allow all 也拒绝）", C.RED], ["Timeout", "默认 120s（编译/测试较慢）· 可覆盖至 600000ms · SIGTERM → 5s → SIGKILL", C.BLUE], ["Truncation", "保留 head + tail（中间 [...truncated...]）· 各默认 50KB · 保留 tail 因编译错误在末尾", C.GREEN]];
bcards.forEach((b, i) => { const y = 1.8 + i * 1.18; s.addShape(p.shapes.RECTANGLE, { x: 7.5, y, w: 4.9, h: 1.05, fill: { color: C.LIGHT } }); s.addShape(p.shapes.RECTANGLE, { x: 7.5, y, w: 0.12, h: 1.05, fill: { color: b[2] } }); s.addText([{ text: b[0], options: { bold: true, fontSize: 13, color: C.INK, breakLine: true } }, { text: b[1], options: { fontSize: 10.5, color: C.GRAY, paraSpaceBefore: 3 } }], { x: 7.72, y: y + 0.08, w: 4.6, h: 0.9, fontFace: FONT, valign: "middle" }); });
s.addText("精髓：“When NOT to use” 比 “When to use” 更重要 · 用户可放松安全，但不能关闭安全（Deny 硬编码）。", { x: 0.92, y: 5.5, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 13, bold: true, color: C.INK, valign: "top" });
s.addNotes("这是教科书级别的工具治理设计。注意几个精妙之处：第一，description 中“When NOT to use”比“When to use”更重要——因为 LLM 的默认倾向是“如果能用就用 bash”（训练数据中 bash 出现频率极高），你需要明确告诉它“有更好的工具时不要用我”。第二，Deny 硬编码是最后一道防线——即使用户的 allowlist 配了 Bash(*)（allow all bash），fork bomb 和 rm -rf / 仍然被拦截。用户可以放松安全，但不能关闭安全。第三，truncation 保留 tail 而不只是 head——这个设计决策来自真实痛点：早期版本只保留 head，用户 run test 后看不到失败原因（在输出末尾）。");

// ---------- Slide 15: Edit vs Bash ----------
s = contentSlide(p, 15, N, "对比 — 安全但受限的 Tool 如何设计", "案例 · Edit Tool 差异化");
styledTable(p, s, [
  [hc("维度"), hc("Bash Tool"), hc("Edit Tool")],
  ["能力范围", "无限（can do anything）", "限定（只改文件内容）"],
  ["副作用", "不可预测", "可预测（内容变更）"],
  ["权限级别", "Ask-first / Deny", "Free(项目内) / Ask(项目外)"],
  ["前置检查", "Allowlist glob match", "路径校验 + 存在性检查"],
  ["回滚", "不可能", "可能（git / 备份）"],
  ["Timeout", "120s", "5s（纯 I/O）"],
], { x: 0.92, y: 1.7, w: 6.6, colW: [1.6, 2.6, 2.4], rowH: 0.5, fontSize: 11.5 });
s.addText("Tool 治理的风险矩阵", { x: 7.8, y: 1.7, w: 4.6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const quad = [["高能力·高风险 Bash", "Ask-first + Deny + 长超时", C.RED], ["高能力·低风险 Edit", "Free(项目内) + 前置检查", C.ORANGE], ["低能力·高风险 Delete", "Ask-first + 确认回显", "E0651A"], ["低能力·低风险 Read", "Free + 最少检查 + 最短超时", C.GREEN]];
quad.forEach((q, i) => { const x = 7.8 + (i % 2) * 2.35; const y = 2.15 + Math.floor(i / 2) * 1.5; s.addShape(p.shapes.RECTANGLE, { x, y, w: 2.25, h: 1.4, fill: { color: q[2] } }); s.addText([{ text: q[0], options: { bold: true, fontSize: 11, color: C.WHITE, breakLine: true } }, { text: q[1], options: { fontSize: 9.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.12, y: y + 0.1, w: 2.0, h: 1.2, fontFace: FONT, valign: "top" }); });
s.addText("设计原则：治理强度应与工具能力成正比 —— 不是“越安全越好”，而是“风险匹配”。Edit 前置：必须先 Read → old_string 唯一 → 在项目内。", { x: 0.92, y: 5.55, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "top" });
s.addNotes("通过 Bash 和 Edit 的对比，我想传达一个设计原则：治理强度应该与工具能力成正比。Bash 能做任何事——所以它的治理是最重的：每次审批 + 硬编码 deny + 最长超时。Edit 只能改文件内容——所以它的治理是适度的：Free 但有前置条件（必须先读过、修改位置必须唯一、路径必须在项目内）。Read 几乎无副作用——所以治理最轻：Free + 极短超时。这不是“越安全越好”的设计——过度安全会杀死可用性。是“风险匹配”的设计。");

// ---------- Slide 16: Structured Output 矛盾 ----------
s = contentSlide(p, 16, N, "从文本流到结构化数据 — 被低估的难题", "Structured Output Parsing · 核心矛盾");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.7, w: 3.4, h: 0.7, fill: { color: C.BLUE } });
s.addText("LLM text stream", { x: 0.92, y: 1.7, w: 3.4, h: 0.7, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.LINE, { x: 4.32, y: 2.05, w: 0.9, h: 0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } });
s.addShape(p.shapes.RECTANGLE, { x: 5.22, y: 1.7, w: 2.4, h: 0.7, fill: { color: C.ORANGE } });
s.addText("？ 转换器", { x: 5.22, y: 1.7, w: 2.4, h: 0.7, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.LINE, { x: 7.62, y: 2.05, w: 0.9, h: 0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } });
s.addShape(p.shapes.RECTANGLE, { x: 8.52, y: 1.7, w: 3.9, h: 0.7, fill: { color: C.DARK } });
s.addText("structured JSON: name + params", { x: 8.52, y: 1.7, w: 3.9, h: 0.7, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
codeBox(p, s, [
  { text: "```json {...} ```        // markdown fences", opt: { color: "E8A33D" } },
  { text: "{\"a\":1, \"b\":2,}          // trailing comma", opt: { color: "E8A33D" } },
  { text: "{\"cmd\":\"git st            // unclosed (streaming)", opt: { color: "E8A33D" } },
  { text: "Let me run: {\"cmd\":\"ls\"} // 混合文本", opt: { color: "E8A33D" } },
  { text: "\\u{1F600} vs 😀           // unicode escape", opt: { color: "E8A33D" } },
  { text: "{\"cmd\":\"echo \\\"hi\\\"\"}     // 嵌套引号", opt: { color: "E8A33D" } },
], { x: 0.92, y: 2.7, w: 6.6, h: 2.7, fontSize: 10.5 });
s.addText([{ text: "为何不能完全依赖 native structured output？", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  ...["不是所有 provider 都支持（开源/旧 API）", "Streaming 需要增量解析", "Fallback 场景需自定义逻辑", "错误恢复需 domain-specific 处理", "多模型支持：Claude/GPT/Gemini 格式不同"].map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 12, color: C.INK, paraSpaceBefore: 6 } }))], { x: 7.9, y: 2.7, w: 4.5, h: 3.6, fontFace: FONT, valign: "top" });
s.addNotes("这个话题在大多数 Agent 框架的文档中一笔带过，但在生产环境中它是 bug 的重灾区。你可能想：“不是有 native tool_use 格式吗？provider 已经帮我解析好了。”对，在理想路径上是的。但生产系统必须处理非理想路径：streaming 中途断开、provider 降级到 text-only 模式、或者你需要支持多家 LLM provider。Structured output parsing 是你的 harness 必须自己掌控的能力，不能完全外包给 provider。");

// ---------- Slide 17: 四步解析管线 ----------
s = contentSlide(p, 17, N, "从原始文本到可信结构 — 4-Step Parsing Pipeline", "结构化输出解析");
const psteps = [
  ["1 · Candidate Extraction", "regex 匹配 JSON · 剥离 markdown fences · 定位混合文本中的结构", "text → 0-N 候选"],
  ["2 · Cleaning", "去 trailing comma · 单→双引号 · 去注释 · 规范 unicode", "→ cleaned JSON"],
  ["3 · Strict JSON Parse", "JSON.parse / json.loads · 失败 → error recovery", "→ JS/Py object"],
  ["4 · Schema Validation", "Pydantic/Zod · required/types/enum/range/pattern", "→ typed object"],
];
psteps.forEach((st, i) => { const y = 1.8 + i * 0.86; s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 8.4, h: 0.72, fill: { color: [C.DARK, "2E4A63", C.BLUE, C.ORANGE][i] } }); s.addText([{ text: st[0] + "    ", options: { bold: true, fontSize: 12.5, color: C.WHITE } }, { text: st[1], options: { fontSize: 10.5, color: "E6EAEE" } }], { x: 1.1, y, w: 8.0, h: 0.72, fontFace: FONT, valign: "middle" }); s.addText(st[2], { x: 9.45, y, w: 3.0, h: 0.72, fontFace: MONO, fontSize: 10, color: C.GRAY, valign: "middle" }); if (i < 3) s.addShape(p.shapes.LINE, { x: 5.1, y: y + 0.72, w: 0, h: 0.14, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.5, w: 11.5, h: 0.85, fill: { color: C.LIGHT } });
s.addText([{ text: "生产实测：", options: { bold: true, color: C.INK } }, { text: "Step 1-2 解决 95% 格式问题 · Step 3 parse 失败率 <3% · Step 4 捕获 ~100% 语义错误", options: { color: C.INK } }], { x: 0.92, y: 5.5, w: 11.5, h: 0.85, fontFace: FONT, fontSize: 13, align: "center", valign: "middle" });
s.addNotes("四步看似简单，但每一步都是从大量生产 bug 中提炼出来的。Step 1 解决“JSON 藏在文本里”的问题 — LLM 喜欢用 markdown 包裹 JSON，或在 JSON 前加一段解释性文字。Step 2 解决“几乎是合法 JSON 但不完全是”的问题 — trailing comma 是最常见的，因为很多编程语言允许它但 JSON 标准不允许。Step 3 用标准库做 parse，不要自己写 JSON parser。Step 4 确保不仅格式合法，语义也合法。");

// ---------- Slide 18: Streaming + Error Recovery ----------
s = contentSlide(p, 18, N, "流式解析 + 错误恢复 — 生产级鲁棒性", "Streaming + Error Recovery");
s.addText([{ text: "Streaming：bracket stack tracking", options: { bold: true, color: C.BLUE, fontSize: 13, breakLine: true } },
  ...["{ → push · } → pop · 空栈 = JSON 完整可解析", "增量库：partial-json / simdjson", "三阶段优化：识别 name → 预备执行环境 → params 完整即执行", "收益：省 100-500ms cold start（bash 尤其明显）"].map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 12, color: C.INK, paraSpaceBefore: 6 } }))], { x: 0.92, y: 1.8, w: 6.0, h: 3.4, fontFace: FONT, valign: "top" });
s.addText("Error Recovery 重试链", { x: 7.4, y: 1.8, w: 5, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.RED });
const rec = [["首次 retry", "85%", C.GREEN], ["第二次 retry", "+10%", C.ORANGE], ["仍失败 → 人工", "5%", C.RED]];
rec.forEach((r, i) => { const y = 2.25 + i * 0.95; s.addShape(p.shapes.RECTANGLE, { x: 7.4, y, w: 5.0, h: 0.78, fill: { color: C.LIGHT } }); s.addShape(p.shapes.RECTANGLE, { x: 7.4, y, w: 1.1, h: 0.78, fill: { color: r[2] } }); s.addText(r[1], { x: 7.4, y, w: 1.1, h: 0.78, fontFace: FONT, fontSize: 15, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addText(r[0], { x: 8.65, y, w: 3.6, h: 0.78, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "middle" }); });
s.addText("结构化 error message 注入 context → LLM 重试。Max 2 retries，总成功率 ~95%。不要无限重试 —— 反模式。", { x: 0.92, y: 5.5, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 12.5, bold: true, color: C.INK, valign: "top" });
s.addNotes("Streaming parsing 是性能优化的关键。想想用户体验：如果你等 LLM 输出完整的 tool_use JSON 才开始处理，用户要多等 1-2 秒。但如果你在看到 tool name 的瞬间就开始准备执行环境（比如预先 spawn bash subprocess），等 params 完整后立即执行，用户感知到的延迟就少了几百毫秒。Error recovery 的 85% 首次修复率说明：LLM 看到明确的格式错误反馈后，绝大多数情况下能自我修正。但要设置 retry 上限 — 无限重试是反模式。");

// ---------- Slide 19: 幻觉三类型 ----------
s = contentSlide(p, 19, N, "Tool-Call Hallucination — 三种致命幻觉", "幻觉检测 · 三种类型");
styledTable(p, s, [
  [hc("类型"), hc("表现"), hc("检测难度"), hc("示例"), hc("根因")],
  [{ text: "工具名幻觉", options: { bold: true } }, "编造不存在的工具", { text: "低", options: { color: C.GREEN, bold: true } }, "execute_sql（实为 run_query）", "训练数据工具名混入"],
  [{ text: "参数幻觉", options: { bold: true } }, "编造不在 schema 的参数", { text: "中", options: { color: C.ORANGE, bold: true } }, "{timeout:30}（schema 无）", "基于函数名推测参数"],
  [{ text: "值幻觉", options: { bold: true } }, "参数名对但值是编造的", { text: "高", options: { color: C.RED, bold: true } }, "file:\"/src/utils/helper.ts\"（不存在）", "基于代码模式推测路径"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.8, 2.8, 1.3, 3.3, 2.3], rowH: 0.78, fontSize: 11.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 1.2, fill: { color: C.DARK } });
s.addText("S2 负责前两类的 L1 拦截（确定性、毫秒级）；值幻觉需要运行时验证（S3 / S4 协同）。幻觉不是“撒谎”——是概率推测。", { x: 0.92, y: 4.95, w: 11.5, h: 1.2, fontFace: FONT, fontSize: 14, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("幻觉不是模型在“撒谎”——它是在做概率推测。当你的系统里有一个 run_query 工具，模型可能基于训练数据中见过的类似系统，推测出一个 execute_sql。这不是恶意的，但结果同样致命——如果我们不拦截，就会走到 pipeline 的 discovery 阶段报 “tool not found”，浪费一轮。更危险的是参数幻觉：模型可能传了一个 schema 里不存在的参数，但 JSON 格式是合法的——如果你只做 JSON parse 不做 schema validation，这个错误会悄悄传递下去。");

// ---------- Slide 20: L1 Schema Validation ----------
s = contentSlide(p, 20, N, "L1 Defense — Schema 校验 + 编辑距离纠错", "幻觉检测 · L1");
codeBox(p, s, [
  { text: "Tool Call 到达", opt: {} },
  { text: "  → tool_name 是否存在于注册表？", opt: { color: "8FBFE8" } },
  { text: "    ├ 存在 → Schema 校验", opt: { color: "8FD19E" } },
  { text: "    │   required? 类型? enum? 范围?", opt: { color: "8FD19E" } },
  { text: "    └ 不存在 → 编辑距离纠错", opt: { color: "E8A33D" } },
  { text: "        dist≤2 & sim>0.85 → 自动纠正", opt: { color: "E8A33D" } },
  { text: "        dist>2 → 拒绝 + 返回可用列表", opt: { color: "E8A33D" } },
], { x: 0.92, y: 1.8, w: 6.6, h: 2.9, fontSize: 11 });
s.addText([{ text: "Edit Distance 纠错", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  { text: "Levenshtein + Jaro-Winkler", options: { fontSize: 12, color: C.GRAY, breakLine: true, paraSpaceBefore: 6 } },
  { text: "read_fil → “Did you mean read_file?” (dist=1) → 自动纠正", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 6 } }], { x: 7.9, y: 1.8, w: 4.5, h: 2.0, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 7.9, y: 3.9, w: 4.5, h: 1.5, fill: { color: C.ORANGE } });
s.addText([{ text: "~60%", options: { fontSize: 40, bold: true, color: C.WHITE, breakLine: true } }, { text: "L1 schema validation 拦截的工具调用幻觉", options: { fontSize: 12, color: "FFFFFF" } }], { x: 8.1, y: 4.05, w: 4.1, h: 1.2, fontFace: FONT, valign: "top" });
s.addText("实现成本极低（纯确定性字符串比较 + schema 校验，无 AI），ROI 极高。关键决策：typo 自动纠正，方向错则拒绝。", { x: 0.92, y: 5.6, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "top" });
s.addNotes("这个防线实现成本极低——纯确定性的字符串比较和 schema 校验，没有任何 AI 参与。但 ROI 极高：60% 的幻觉工具调用在这里就被终结。关键工程决策是“纠正还是拒绝”。如果只是 typo（edit distance 1-2），自动纠正更好——省了一次完整的 LLM 重试循环。但如果 distance 很大，说明模型可能完全走错了方向，这时候应该拒绝并给出可用列表，让它重新思考。");

// ---------- Slide 21: Input Gate 分工 ----------
s = contentSlide(p, 21, N, "Input Gate 设计 — S2 在幻觉防御中的定位", "幻觉检测 · 分工");
styledTable(p, s, [
  [hc("检测层"), hc("负责系统"), hc("检测内容"), hc("时机")],
  [{ text: "L1 结构校验", options: { bold: true, color: C.ORANGE } }, "S2", "工具名/参数名/类型/范围", "执行前"],
  [{ text: "L2 语义校验", options: { bold: true } }, "S3", "路径合法性/命令安全/权限合规", "执行前"],
  [{ text: "L3 事实校验", options: { bold: true } }, "S4", "文件存在/API 可达/数据过时", "执行中/后"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [2.2, 1.8, 5.0, 2.5], rowH: 0.72, fontSize: 12.5 });
const defense = [["S1", "格式合法（这是合法 JSON）", C.BLUE], ["S2", "结构语义（对目标工具有意义）", C.ORANGE], ["S3", "安全策略（允许这个操作吗）", C.DARK], ["执行", "", C.GREEN]];
defense.forEach((d, i) => { const x = 0.92 + i * 2.95; s.addShape(p.shapes.RECTANGLE, { x, y: 4.75, w: 2.6, h: 1.0, fill: { color: d[2] } }); s.addText([{ text: d[0], options: { bold: true, fontSize: 15, color: C.WHITE, breakLine: true } }, { text: d[1], options: { fontSize: 10, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: x + 0.12, y: 4.85, w: 2.36, h: 0.85, fontFace: FONT, align: "center", valign: "top" }); if (i < 3) s.addShape(p.shapes.LINE, { x: x + 2.6, y: 5.25, w: 0.35, h: 0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } }); });
s.addText("S2 的 L1 成本最低、速度最快 —— 纯确定性计算，毫秒级完成。S1 保证格式 + S2 保证语义 → 才进入执行。", { x: 0.92, y: 5.95, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 12, color: C.INK, valign: "top" });
s.addNotes("幻觉防御是跨系统协作的典型案例。S1 保证格式（“这是合法的 JSON”），S2 保证结构语义（“这个 JSON 对 read_file 工具有意义”），S3 保证安全策略（“允许读这个路径吗？”），S4 在运行时做事实验证（“这个文件真的存在吗？”）。每一层捕获不同类型的错误。S2 的 L1 是成本最低、速度最快的一道——纯确定性计算，毫秒级完成。");

// ---------- Slide 22: 四级权限 ----------
s = contentSlide(p, 22, N, "四级权限模型 — 从完全自由到完全禁止", "Permission Model");
styledTable(p, s, [
  [hc("级别"), hc("含义"), hc("用户体验"), hc("典型工具")],
  [{ text: "Free", options: { bold: true, color: C.GREEN } }, "无需检查，直接执行", "无感知", "read_file(项目内), list_tools"],
  [{ text: "Ask-first", options: { bold: true, color: "E0A000" } }, "每次执行前询问", "频繁弹窗", "write_file, run_bash"],
  [{ text: "Approve-once", options: { bold: true, color: C.ORANGE } }, "首次询问，session 记住", "首次弹窗", "git_commit, npm_install"],
  [{ text: "Deny", options: { bold: true, color: C.RED } }, "硬性禁止，无法覆盖", "被拒绝", "rm -rf, DROP TABLE(prod)"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [2.0, 3.2, 2.3, 4.0], rowH: 0.6, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 11.5, h: 1.3, fill: { color: C.LIGHT } });
s.addText([{ text: "级别决策依据", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  { text: "Tool 元数据（默认） → 项目配置（覆盖, .claude/settings.json） → 运行时上下文（动态升级）", options: { fontSize: 12, color: C.GRAY, breakLine: true, paraSpaceBefore: 6 } },
  { text: "示例：read_file 默认 Free，但 path 含 .. 或在 home 外 → 升级到 Ask-first", options: { fontSize: 12, color: C.ORANGE, bold: true, paraSpaceBefore: 4 } }], { x: 1.12, y: 5.1, w: 11.1, h: 1.05, fontFace: FONT, valign: "top" });
s.addNotes("四级模型的精髓在于“不是所有操作都同等危险”。读一个项目内的文件——几乎零风险，设成 Free 减少用户打扰。写文件——有风险但可控，Ask-first 让用户确认。npm install——第一次确认后 session 内无需重复，Approve-once。rm -rf——永远不应该自动执行，Deny。注意 Deny 不是“很难获批”，是“不可能获批”——即使用户说“我知道我在干什么”也不行。这是防止 social engineering 攻击的关键。");

// ---------- Slide 23: 动态升级与 S3 ----------
s = contentSlide(p, 23, N, "权限不是静态标签 — 运行时证据驱动升降级", "Permission · 动态升级与 S3");
s.addText(bullets([
  { text: "动态升级触发条件", opt: { bold: true } },
  "Tool result 含敏感模式（API key/password）→ 后续升级",
  "路径超出项目边界 → 升级到 Ask-first",
  "连续 3 次同工具失败 → 升级引入人工",
  "异常参数值（非典型操作）→ 升级",
], { fontSize: 12.5 }), { x: 0.92, y: 1.8, w: 6.0, h: 3.0, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 7.3, y: 1.8, w: 5.1, h: 1.3, fill: { color: C.ORANGE } });
s.addText([{ text: "S2 · 执行层", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "执行权限检查（前台保安：查通行证）", options: { fontSize: 11.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: 7.5, y: 1.95, w: 4.7, h: 1.0, fontFace: FONT, valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 7.3, y: 3.25, w: 5.1, h: 1.3, fill: { color: C.DARK } });
s.addText([{ text: "S3 · 策略层", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "定义权限规则（安保主管：制定规则）", options: { fontSize: 11.5, color: "E6EAEE", paraSpaceBefore: 4 } }], { x: 7.5, y: 3.4, w: 4.7, h: 1.0, fontFace: FONT, valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.1, w: 11.5, h: 1.2, fill: { color: C.LIGHT } });
s.addText([{ text: "信任不对称（有意设计）：", options: { bold: true, color: C.INK, fontSize: 14, breakLine: true } }, { text: "获得信任是慢的（10+ 次安全操作 → 可降级）；失去信任是瞬间的（1 次违规 → 立即升级）。", options: { fontSize: 13, color: C.GRAY, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.28, w: 11.1, h: 1.0, fontFace: FONT, valign: "top" });
s.addNotes("S2 和 S3 的关系类似于 Kubernetes 中 API Server 和 RBAC Policy 的关系。S2 是 enforcement point——它在 pipeline 中执行检查。但检查的规则从哪来？从 S3。为什么分开？因为策略和执行需要独立演进。你可以在不改 S2 代码的情况下通过配置文件调整策略（S3 的职责）。这种 separation of concerns 让系统更容易维护和审计。");

// ---------- Slide 24: 产品对比 ----------
s = contentSlide(p, 24, N, "Claude Code vs Cursor vs Windsurf — 权限交互三流派", "Permission · 产品对比");
const prods = [
  { t: "Claude Code", s: "显式审批派", d: ["每个 bash/write 弹终端确认", "y/a/N · allowlist 配永久 Free", "哲学：知情并同意每个副作用", "+ 审计清晰 − 频繁打断"], c: C.ORANGE },
  { t: "Cursor", s: "差异展示派", d: ["Apply 前展示完整 diff", "Accept/Reject 文件级", "哲学：审查结果而非过程", "+ 理解度高 − bash 无法 diff"], c: C.BLUE },
  { t: "Windsurf", s: "YOLO 可选派", d: ["默认 ask，提供 Act 全自动", "依赖 Docker sandbox 兜底", "哲学：环境隔离代替交互", "+ 流畅 − 审计困难"], c: C.GREEN },
];
prods.forEach((pr, i) => { const x = 0.92 + i * 3.87; s.addShape(p.shapes.RECTANGLE, { x, y: 1.75, w: 3.6, h: 0.7, fill: { color: pr.c } }); s.addText([{ text: pr.t, options: { bold: true, fontSize: 14, color: C.WHITE, breakLine: true } }, { text: pr.s, options: { fontSize: 11, color: "FFFFFF" } }], { x: x + 0.15, y: 1.8, w: 3.4, h: 0.6, fontFace: FONT, valign: "middle" }); s.addShape(p.shapes.RECTANGLE, { x, y: 2.45, w: 3.6, h: 2.4, fill: { color: C.LIGHT } }); s.addText(pr.d.map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontFace: FONT, fontSize: 11, color: C.INK, paraSpaceAfter: 7 } })), { x: x + 0.18, y: 2.6, w: 3.3, h: 2.15, valign: "top" }); });
s.addText("没有“最好”的设计，只有“最适合你场景”的：开发者本地 IDE → 显式审批/差异；CI/CD 无人值守 → Sandbox；多人协作 → 审批工作流。", { x: 0.92, y: 5.1, w: 11.5, h: 1.2, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "top" });
s.addNotes("权限系统不是技术问题——它是用户体验和安全性的 trade-off 决策。Claude Code 选择了“显式审批”，牺牲了一些流畅度换来了最高的可审计性——每个操作都有用户确认记录。Cursor 选择了“结果可视化”——你不需要理解命令是什么，只需要看 diff 合不合理。Windsurf 最激进——让你选全自动模式，但代价是你必须信任 sandbox 的隔离性。没有“最好”的设计，只有“最适合你场景”的设计。如果你在做一个面向金融行业的 Agent——显式审批+审计日志是监管要求。如果你在做开发者个人工具——YOLO 模式可能 perfectly fine。");

// ---------- Slide 25: Allowlist/Blocklist 配置 ----------
s = contentSlide(p, 25, N, "配置驱动权限 — 不改代码调整安全边界", "Permission · 配置实战");
codeBox(p, s, [
  { text: "{ \"permissions\": {", opt: {} },
  { text: "  \"allow\": [", opt: { color: "8FD19E" } },
  { text: "    \"Bash(git *)\", \"Bash(npm test)\",", opt: { color: "8FD19E" } },
  { text: "    \"Read(*)\", \"Write(src/**)\"", opt: { color: "8FD19E" } },
  { text: "  ],", opt: { color: "8FD19E" } },
  { text: "  \"deny\": [", opt: { color: "E8736A" } },
  { text: "    \"Bash(rm -rf *)\", \"Bash(sudo *)\",", opt: { color: "E8736A" } },
  { text: "    \"Write(.env*)\", \"Write(*.pem)\"", opt: { color: "E8736A" } },
  { text: "  ] } }", opt: { color: "E8736A" } },
], { x: 0.92, y: 1.8, w: 6.3, h: 3.0, fontSize: 11 });
s.addText([{ text: "Glob 与评估顺序", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  ...["* = 单层；** = 多层路径", "评估：deny → allow → default(Ask-first)", "deny 优先于 allow（安全默认）"].map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceBefore: 5 } })),
  { text: "三级覆盖", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true, paraSpaceBefore: 10 } },
  { text: "系统默认 < 项目(.claude) < 用户(~/.claude)；deny 取并集，个人不能绕过团队 deny", options: { fontSize: 11.5, color: C.INK, paraSpaceBefore: 5 } }], { x: 7.5, y: 1.8, w: 4.9, h: 3.6, fontFace: FONT, valign: "top" });
s.addText("可立即上手：把常用安全命令加到 allow list。核心原则：deny 优先于 allow —— 误放行危险操作 ≫ 误拦截安全操作。", { x: 0.92, y: 5.4, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 12.5, bold: true, color: C.INK, valign: "top" });
s.addNotes("这是学员回去之后立即能用的知识。如果你在用 Claude Code——打开你的 .claude/settings.json，把常用的安全命令加到 allow list 里，你的开发效率会立刻提升。但更重要的是如果你在设计自己的 harness，这个配置系统的设计决策：deny 优先于 allow——这是安全系统的基本原则。如果同一个命令同时匹配 allow 和 deny，deny 赢。因为误放行一个危险操作比误拦截一个安全操作严重得多。三级覆盖的设计让团队可以统一管理安全基线（项目级），同时允许个人定制（用户级），但个人永远不能绕过团队的 deny list。");

// ---------- Slide 26: MCP N×M ----------
s = contentSlide(p, 26, N, "MCP — AI 时代的 USB", "解决 N×M 问题");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.8, w: 5.6, h: 1.5, fill: { color: "FBEAE5" } });
s.addText([{ text: "问题：N × M 定制集成", options: { bold: true, color: C.RED, fontSize: 14, breakLine: true } }, { text: "N 框架 × M 工具，每对写适配代码，维护成本平方级上升", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 6 } }], { x: 1.12, y: 1.95, w: 5.2, h: 1.2, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.8, w: 5.6, h: 1.5, fill: { color: "E6F4EA" } });
s.addText([{ text: "MCP 解法：N + M", options: { bold: true, color: C.GREEN, fontSize: 14, breakLine: true } }, { text: "N 框架实现 MCP Client + M 工具实现 MCP Server，标准化协议", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 6 } }], { x: 7.02, y: 1.95, w: 5.2, h: 1.2, fontFace: FONT, valign: "top" });
const prim = [["Tools", "可调用函数（主用途）", "tools/list + tools/call"], ["Resources", "可读数据源（文件类）", "resources/list + read"], ["Prompts", "可复用提示模板", "prompts/list + get"]];
prim.forEach((pr, i) => { const x = 0.92 + i * 3.87; s.addShape(p.shapes.RECTANGLE, { x, y: 3.6, w: 3.6, h: 1.5, fill: { color: C.DARK } }); s.addText([{ text: pr[0], options: { bold: true, fontSize: 15, color: C.ORANGE, breakLine: true } }, { text: pr[1], options: { fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 5 } }, { text: pr[2], options: { fontSize: 10, color: "9AA9B5", fontFace: MONO, paraSpaceBefore: 5 } }], { x: x + 0.15, y: 3.75, w: 3.3, h: 1.25, fontFace: FONT, valign: "top" }); });
s.addText("生态：200+ 开源 MCP Server（Slack/GitHub/Notion/PostgreSQL/Stripe…） · Anthropic 发起，OpenAI / Google 已采用。", { x: 0.92, y: 5.4, w: 11.5, h: 0.8, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "top" });
s.addNotes("MCP 是 2024 年 Agent 工具生态最重要的标准化事件。在它出现之前，如果你想让 Agent 连 Slack + GitHub + 数据库，你要为每个都写定制代码。现在你实现一个 MCP Client，就能接入 200+ 个现成的 Server。反过来，如果你是工具提供方，实现一个 MCP Server 就能被所有 Agent 框架使用。USB 的类比非常贴切：曾经每个外设一种接口（打印机口、PS/2、串口），USB 统一了一切。MCP 在做同样的事情。");

// ---------- Slide 27: MCP Transport ----------
s = contentSlide(p, 27, N, "MCP 连接模型 — stdio vs Streamable HTTP", "MCP · Transport 与生命周期");
styledTable(p, s, [
  [hc("Transport"), hc("通信方式"), hc("适用场景"), hc("示例")],
  [{ text: "stdio", options: { bold: true } }, "子进程 stdin/stdout", "本地工具", "文件系统、Git、本地 DB"],
  [{ text: "Streamable HTTP", options: { bold: true } }, "HTTP 请求/响应 + SSE", "远程服务", "云 API、共享工具、SaaS"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [2.6, 3.2, 2.2, 3.5], rowH: 0.55, fontSize: 12 });
codeBox(p, s, [
  { text: "Client → Server: initialize (version, capabilities)", opt: { color: "8FBFE8" } },
  { text: "Server → Client: initialize_result (capabilities)", opt: { color: "8FD19E" } },
  { text: "Client → Server: tools/list", opt: { color: "8FBFE8" } },
  { text: "Server → Client: [tool definitions with schemas]", opt: { color: "8FD19E" } },
  { text: "Client → Server: tools/call (name, arguments)", opt: { color: "8FBFE8" } },
  { text: "Server → Client: result (content, is_error)", opt: { color: "8FD19E" } },
], { x: 0.92, y: 3.5, w: 11.5, h: 1.85, fontSize: 11.5 });
s.addText("Capability Negotiation：双方各自声明支持的原语/功能，只使用对方声明支持的部分 → 避免 runtime error。", { x: 0.92, y: 5.55, w: 11.5, h: 0.7, fontFace: FONT, fontSize: 12.5, color: C.INK, valign: "top" });
s.addNotes("两种 transport 的选择很简单。本地工具用 stdio——Agent 把 MCP server 作为子进程启动，通过 stdin/stdout 通信。零网络开销、延迟极低。远程工具用 HTTP——MCP server 作为独立服务运行，可以被多个 agent 共享。Capability negotiation 是个好设计——你不需要假设对方支持所有功能。如果 server 只提供 tools 不提供 resources，client 就不会尝试调 resources/list。避免了 runtime error。");

// ---------- Slide 28: MCP 报文 Walkthrough ----------
s = contentSlide(p, 28, N, "一次完整 MCP 交互的 JSON-RPC 报文", "MCP · 报文 Walkthrough");
codeBox(p, s, [
  { text: "// 1. Client → Server (初始化)", opt: { color: "8C9AA6" } },
  { text: "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",", opt: {} },
  { text: " \"params\":{\"protocolVersion\":\"2024-11-05\",...}}", opt: {} },
  { text: "// 3. Client → Server (发现工具)", opt: { color: "8C9AA6" } },
  { text: "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}", opt: {} },
  { text: "// 4. Server → Client (返回 schema)", opt: { color: "8C9AA6" } },
  { text: " result.tools[].inputSchema  // 标准 JSON Schema", opt: { color: "E8A33D" } },
  { text: "// 5. Client → Server (调用)", opt: { color: "8C9AA6" } },
  { text: "{\"method\":\"tools/call\",\"params\":{\"name\":", opt: {} },
  { text: "  \"create_pull_request\",\"arguments\":{...}}}", opt: { color: "8FD19E" } },
  { text: "// 6. Server → Client: {content:[...], isError:false}", opt: { color: "8C9AA6" } },
], { x: 0.92, y: 1.8, w: 7.4, h: 3.7, fontSize: 10.5 });
s.addText(bullets([
  "每条消息是独立 JSON 行（JSON-RPC 2.0）",
  "id 字段匹配请求/响应（支持并发）",
  "inputSchema 即标准 JSON Schema → Zod/Pydantic 校验",
  "schema 从 server 来，validation 在 client 做",
  "isError 决定 Agent 是否重试或换方案",
  "stdio：newline-delimited JSON；stderr 留给日志",
], { fontSize: 11.5 }), { x: 8.6, y: 1.8, w: 3.8, h: 3.7, valign: "top" });
s.addText("MCP 比 REST 更简洁 —— 没有 HTTP header、status code、content negotiation。JSON-RPC 的美在于极简。", { x: 0.92, y: 5.7, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 12.5, bold: true, color: C.INK, valign: "top" });
s.addNotes("我故意展示完整报文，因为很多人对 MCP 的理解停留在概念层。看到实际报文你会发现——它真的很简单。每条消息就是一个 JSON 对象，有 method、params、result。和你写过的 REST API 比，MCP 反而更简洁——没有 HTTP header、没有 status code、没有 content negotiation。JSON-RPC 的美在于极简。注意 Step 4 返回的 inputSchema——这就是你的 harness 拿去做 input validation 的依据。schema 从 server 来，validation 在 client 做。这种“schema 声明与校验分离”的设计让工具提供方和消费方可以独立演进。");

// ---------- Slide 29: MCP Schema 缓存与容错 ----------
s = contentSlide(p, 29, N, "MCP 工程化 — 缓存策略与故障处理", "MCP · Schema 缓存与容错");
const cache = [["L1 内存", "session 内 O(1)，TTL = session", C.DARK], ["L2 磁盘", "跨 session 持久化，TTL 24h / version", "2E4A63"], ["L3 分布式 Redis", "跨实例共享，多节点部署", C.BLUE]];
cache.forEach((c, i) => { const y = 1.8 + i * 0.95; const w = 7.0 - i * 1.4; s.addShape(p.shapes.RECTANGLE, { x: 0.92 + i * 0.7, y, w, h: 0.78, fill: { color: c[2] } }); s.addText([{ text: c[0] + "  ", options: { bold: true, fontSize: 12.5, color: C.WHITE } }, { text: c[1], options: { fontSize: 10.5, color: "E6EAEE" } }], { x: 1.12 + i * 0.7, y, w: w - 0.4, h: 0.78, fontFace: FONT, valign: "middle" }); });
s.addText("目标：cache hit > 95%，避免每轮 tools/list", { x: 0.92, y: 4.7, w: 7, h: 0.4, fontFace: FONT, fontSize: 12, italic: true, color: C.GRAY });
s.addText([{ text: "故障处理（每 server 独立 circuit breaker）", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  ...["Retry：临时错误 → 指数退避", "Server 切换：主不健康 → 备用", "本地降级：远程不可用 → 本地等效工具", "熔断：持续失败 → circuit breaker 快速失败", "健康检查：定期 ping / heartbeat"].map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, fontSize: 11.5, color: C.INK, paraSpaceBefore: 5 } }))], { x: 8.3, y: 1.8, w: 4.1, h: 4.3, fontFace: FONT, valign: "top" });
s.addNotes("Schema 缓存是一个经常被忽视的优化。每次 Agent loop 开始时如果都 tools/list，加上 tool schemas 可能有几十个工具、每个几百 token 的 description——光这个 RPC 就可能耗时几百毫秒。L1 内存缓存让 session 内的 schema 查询是 O(1)。L2 磁盘缓存让 session 间复用。L3 在多实例部署时避免每个实例冷启动。故障处理方面，注意每个 MCP server 有自己独立的 circuit breaker——一个 GitHub MCP 挂了不影响 Slack MCP 的使用。");

// ---------- Slide 30: MCP 5条规则 ----------
s = contentSlide(p, 30, N, "5 条 MCP 生产规则", "MCP · 生产集成最佳实践");
const rules = [
  ["Health Check", "定期 ping 检测故障，不等用户请求时才发现"],
  ["Credential 隔离", "MCP server 的 API key 与 Agent 主 credential 分离"],
  ["Saga 模式", "多工具操作需原子性时，设计补偿动作"],
  ["统一审计", "MCP tool calls 走与内置 tool 相同的 trace pipeline"],
  ["权限映射", "MCP 工具自动映射到 S3 四级权限模型（非默认 Free）"],
];
rules.forEach((r, i) => { const y = 1.75 + i * 0.72; s.addShape(p.shapes.OVAL, { x: 0.92, y, w: 0.55, h: 0.55, fill: { color: C.ORANGE } }); s.addText(String(i + 1), { x: 0.92, y, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 15, bold: true, color: C.WHITE, align: "center", valign: "middle" }); s.addText([{ text: r[0] + "   ", options: { bold: true, fontSize: 13, color: C.INK } }, { text: r[1], options: { fontSize: 12, color: C.GRAY } }], { x: 1.65, y, w: 10.7, h: 0.55, fontFace: FONT, valign: "middle" }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.5, w: 11.5, h: 0.85, fill: { color: C.RED } });
s.addText("反模式：给 MCP server “god mode” → 任何 MCP tool 无限制执行 → 安全灾难。正确：接入默认 Ask-first，评估后再降级。", { x: 0.92, y: 5.5, w: 11.5, h: 0.85, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("第 5 条是最常被违反的。很多团队接入 MCP server 后给了默认 Free 权限——“先跑通再说安全”。但一个 GitHub MCP server 可以 push force、delete branch、merge without review。如果它的权限是 Free，任何一次模型幻觉都可能导致不可逆操作。正确做法是：MCP 工具接入时默认 Ask-first，逐个评估后降级到 Free 或升级到 Deny。");

// ---------- Slide 31: ACP 定位 ----------
s = contentSlide(p, 31, N, "ACP — 把 Agent 嵌入任何编辑器", "Agent-Editor 通信标准");
s.addText("“LSP 之于语言服务器，ACP 之于 AI 编码 Agent”", { x: 0.92, y: 1.65, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 14, italic: true, color: C.GRAY });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.2, w: 3.4, h: 0.7, fill: { color: C.BLUE } });
s.addText("Editor (ACP Client)", { x: 0.92, y: 2.2, w: 3.4, h: 0.7, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.LINE, { x: 4.32, y: 2.55, w: 0.8, h: 0, line: { color: C.GRAY, width: 2, beginArrowType: "triangle", endArrowType: "triangle" } });
s.addShape(p.shapes.RECTANGLE, { x: 5.12, y: 2.2, w: 3.4, h: 0.7, fill: { color: C.ORANGE } });
s.addText("Agent (ACP Server)", { x: 5.12, y: 2.2, w: 3.4, h: 0.7, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.LINE, { x: 8.52, y: 2.55, w: 0.8, h: 0, line: { color: C.GRAY, width: 2, endArrowType: "triangle" } });
s.addShape(p.shapes.RECTANGLE, { x: 9.32, y: 2.2, w: 3.1, h: 0.7, fill: { color: C.DARK } });
s.addText("MCP → Tools", { x: 9.32, y: 2.2, w: 3.1, h: 0.7, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addText([{ text: "MCP vs ACP（互补）", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } },
  { text: "MCP = Agent 向外调用工具（Agent → Tools）", options: { fontSize: 12, color: C.INK, breakLine: true, paraSpaceBefore: 6 } },
  { text: "ACP = 编辑器与 Agent 通信（Editor → Agent）", options: { fontSize: 12, color: C.INK, paraSpaceBefore: 4 } }], { x: 0.92, y: 3.3, w: 6.0, h: 1.3, fontFace: FONT, valign: "top" });
s.addText(bullets([
  "Session 生命周期（create/resume/close）",
  "流式更新（thinking/tool_call/diff/plan）",
  "权限请求 session/request_permission",
  "文件系统 fs/read·write · 终端 terminal/*",
  "通信：JSON-RPC over stdio（主）/ HTTP（开发中）",
], { fontSize: 11.5 }), { x: 7.2, y: 3.3, w: 5.2, h: 2.9, valign: "top" });
s.addNotes("ACP 解决的问题和 MCP 互补。MCP 让 Agent 能调用工具，ACP 让编辑器能使用 Agent。类比：MCP 是 Agent 的“手”（操作外部世界），ACP 是 Agent 的“身体接口”（被宿主环境操控）。为什么这对我们重要？因为 Capstone Lab 中，你的 Gateway 就是一个 ACP Client——它通过 ACP 协议与 OpenCode Agent 通信，管理会话、接收流式更新、处理权限请求。");

// ---------- Slide 32: ACP 生态 ----------
s = contentSlide(p, 32, N, "ACP 生态现状 + 在本课程的角色", "ACP · 生态与 Capstone");
s.addText([{ text: "Editor (Client)：", options: { bold: true, color: C.INK } }, { text: "Zed · JetBrains · VS Code · Neovim · Emacs", options: { color: C.GRAY } }], { x: 0.92, y: 1.7, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12.5, valign: "top" });
s.addText([{ text: "Agent (Server)：", options: { bold: true, color: C.INK } }, { text: "Claude Code · OpenCode · Gemini CLI · Codex CLI · Goose · 50+", options: { color: C.GRAY } }], { x: 0.92, y: 2.15, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12.5, valign: "top" });
s.addText([{ text: "SDK：", options: { bold: true, color: C.INK } }, { text: "TypeScript · Rust · Python · Kotlin · Java  ·  ACP Registry（2026.01 上线）", options: { color: C.GRAY } }], { x: 0.92, y: 2.6, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12.5, valign: "top" });
styledTable(p, s, [
  [hc("ACP 能力"), hc("对应系统")],
  ["session/prompt + streaming", "S1 上下文"],
  ["Tool call reports", "S2 工具治理"],
  ["session/request_permission", "S3 安全审批"],
  ["Session resume + Plan", "S4 状态"],
  ["Stop reasons + modes", "S5 熵管理"],
], { x: 0.92, y: 3.2, w: 7.2, colW: [4.4, 2.8], rowH: 0.5, fontSize: 12 });
s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: 3.2, w: 3.9, h: 2.8, fill: { color: C.DARK } });
s.addText([{ text: "Capstone 角色", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "你的 Gateway = ACP Client（TS SDK）", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "OpenCode = ACP Server", options: { fontSize: 12, color: C.WHITE, breakLine: true, paraSpaceBefore: 5 } }, { text: "亲手体验 permission request 从 Agent → Gateway 策略层 → 前端 UI", options: { fontSize: 12, color: "C7CED6", paraSpaceBefore: 8 } }], { x: 8.7, y: 3.38, w: 3.5, h: 2.5, fontFace: FONT, valign: "top" });
s.addNotes("ACP 在 2025-2026 年的采用速度非常快——主要 IDE 和 主要 Agent 都已支持。对你的实际工作来说，如果你在做 Agent 产品，ACP 让你的 Agent 可以“即插即用”到任何支持 ACP 的编辑器中。在 Capstone Lab 中我们会直接用 ACP 协议把 Gateway 连到 OpenCode——你会亲手体验 permission request 如何从 Agent 发出、经过你的 Gateway 策略层、到达前端 UI。");

// ---------- Slide 33: Tool Selection ----------
s = contentSlide(p, 33, N, "Tool Selection — 工具数量决定选择策略", "工具选择智能");
const tsel = [["< 10 工具", "关键词匹配", "意图关键词 → match name+description · <1ms", C.GREEN], ["10–30 工具", "语义相似度", "embed 意图 ↔ description embedding · 处理同义改述", C.ORANGE], ["30+ 工具", "分类器 / 分层加载", "小模型分类任务 → 只加载子集 · hierarchical loading", C.RED]];
tsel.forEach((t, i) => { const y = 1.8 + i * 1.05; s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 2.4, h: 0.9, fill: { color: t[3] } }); s.addText([{ text: t[0], options: { bold: true, fontSize: 13, color: C.WHITE, breakLine: true } }, { text: t[1], options: { fontSize: 11, color: "FFFFFF", paraSpaceBefore: 3 } }], { x: 0.92, y: y + 0.08, w: 2.4, h: 0.75, fontFace: FONT, align: "center", valign: "middle" }); s.addShape(p.shapes.RECTANGLE, { x: 3.42, y, w: 9.0, h: 0.9, fill: { color: C.LIGHT } }); s.addText(t[2], { x: 3.6, y, w: 8.7, h: 0.9, fontFace: FONT, fontSize: 12, color: C.INK, valign: "middle" }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.1, w: 11.5, h: 1.2, fill: { color: C.ORANGE } });
s.addText([{ text: "description 的质量决定选择准确率（上限）", options: { bold: true, color: C.WHITE, fontSize: 14, breakLine: true } }, { text: "好的 description：做什么 / 什么时候用 / 什么时候不要用。算法再好，description 写烂也选不对。", options: { fontSize: 12.5, color: "FFFFFF", paraSpaceBefore: 6 } }], { x: 1.12, y: 5.25, w: 11.1, h: 1.0, fontFace: FONT, valign: "top" });
s.addNotes("工具选择智能容易被过度工程化。如果你只有 10 个工具——不需要 RAG、不需要分类器、不需要 embedding。简单的字符串匹配足够了。但如果你接入了 20 个 MCP server 总共 100+ 工具——这时候你需要要么分层加载（只给模型看相关子集），要么训练一个轻量分类器。最关键的一点：不管用什么选择策略，tool description 的质量是上限。description 写烂了，再好的算法也选不对。");

// ---------- Slide 34: 动态加载分层 ----------
s = contentSlide(p, 34, N, "不要把 100 个工具全塞进 Context", "工具选择 · 动态加载与分层");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.7, w: 11.5, h: 0.6, fill: { color: C.DARK } });
s.addText("问题：100 个工具的 schema ≈ 30-50K tokens → 吃掉 context budget 的 15-25%", { x: 0.92, y: 1.7, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const sols = [["shouldDefer（Claude Code）", "每个工具 shouldDefer(ctx):bool · 不在 git repo → Git 工具 defer"], ["分层加载（OpenCode）", "6 层：system→session→user→domain→builtin→dynamic · 默认仅 system+builtin"], ["Schema 摘要 vs 完整", "Discovery 用 {name, one-line} · Selection 后加载完整 schema · 省 80%+"]];
sols.forEach((sl, i) => { const x = 0.92 + i * 3.87; s.addShape(p.shapes.RECTANGLE, { x, y: 2.55, w: 3.6, h: 2.3, fill: { color: C.LIGHT } }); s.addShape(p.shapes.RECTANGLE, { x, y: 2.55, w: 3.6, h: 0.12, fill: { color: C.ORANGE } }); s.addText([{ text: "解法 " + (i + 1), options: { bold: true, color: C.ORANGE, fontSize: 12, breakLine: true } }, { text: sl[0], options: { bold: true, fontSize: 12.5, color: C.INK, breakLine: true, paraSpaceBefore: 4 } }, { text: sl[1], options: { fontSize: 11.5, color: C.GRAY, paraSpaceBefore: 6 } }], { x: x + 0.18, y: 2.8, w: 3.3, h: 2.0, fontFace: FONT, valign: "top" }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.2, w: 11.5, h: 0.95, fill: { color: C.GREEN } });
s.addText("全加载 50K tokens  →  按需加载 5-10K tokens   （这是 S1 Context Budget 原则在 S2 的具体体现）", { x: 0.92, y: 5.2, w: 11.5, h: 0.95, fontFace: FONT, fontSize: 14, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("这是 S1 Context Budget 原则在 S2 的具体体现。工具 schema 是 context 的第二大消费者（仅次于 system prompt）。如果你有 100 个工具全量加载，光 schema 就占了 50K tokens——在 200K 的窗口里四分之一就没了。而大多数时候，一个任务只需要 5-10 个工具。所以要按需加载。Claude Code 的 shouldDefer 很优雅——工具自己决定“当前场景是否需要我”。不在 git repo 里？Git 工具自动隐藏。不在 Node 项目里？npm 工具自动隐藏。");

// ---------- Slide 35: S2 接口 ----------
s = contentSlide(p, 35, N, "S2 在五大系统中的数据流", "系统接口");
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.5, y: 3.4, w: 2.3, h: 1.1, fill: { color: C.ORANGE }, line: { color: C.ORANGE }, rectRadius: 0.1 });
s.addText("S2\nTool Governance", { x: 5.5, y: 3.4, w: 2.3, h: 1.1, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
const sp2 = [
  { x: 5.5, y: 1.75, t: "S1 上游", d: "组装 context → LLM 输出 tool call → S2 接管", c: C.BLUE },
  { x: 9.7, y: 3.4, t: "S3 横向", d: "S2 执行 check（point），S3 提供 policy（规则）", c: C.DARK },
  { x: 5.5, y: 5.15, t: "S4 下游", d: "每次 tool call 发 trace event → 可观测/指标", c: C.GREEN },
  { x: 1.3, y: 3.4, t: "S5 横向 ↔", d: "budget check 决定是否允许新 call；circuit breaker", c: "2E4A63" },
];
sp2.forEach((k) => { s.addShape(p.shapes.RECTANGLE, { x: k.x, y: k.y, w: 2.3, h: 1.1, fill: { color: k.c } }); s.addText([{ text: k.t, options: { bold: true, fontSize: 12, color: C.WHITE, breakLine: true } }, { text: k.d, options: { fontSize: 9.5, color: "E6EAEE", paraSpaceBefore: 3 } }], { x: k.x + 0.12, y: k.y + 0.08, w: 2.06, h: 0.95, fontFace: FONT, valign: "middle" }); });
s.addShape(p.shapes.LINE, { x: 6.65, y: 2.85, w: 0, h: 0.55, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 7.8, y: 3.95, w: 1.9, h: 0, line: { color: C.GRAY, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 6.65, y: 4.5, w: 0, h: 0.65, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } });
s.addShape(p.shapes.LINE, { x: 3.6, y: 3.95, w: 1.9, h: 0, line: { color: C.GRAY, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
s.addText("完整链路：S1 结构化解析 → S2 幻觉检测 → S2 六步执行管线（input → validate → execute）。", { x: 0.92, y: 6.4, w: 11.5, h: 0.35, fontFace: FONT, fontSize: 11.5, italic: true, color: C.GRAY, align: "center" });
s.addNotes("S2 处在一个承上启下的核心位置。上游从 S1 接收经过结构化解析的 tool call；下游执行结果反馈给 S4 做监控和 S1 做下一轮 context。横向和 S3 配合做权限，和 S5 配合做预算控制。理解这些接口关系，你在设计系统时就知道模块间的 API 契约该怎么定义。");

// ---------- Slide 36: 总结全景 ----------
s = contentSlide(p, 36, N, "一图总结 — 从 LLM 输出到工具执行的完整链路", "总结");
const flow = [
  ["Structured Parsing (S1→S2)", "extract → clean → parse → validate", "成功率 >98%", C.DARK],
  ["Hallucination Detection (S2 L1)", "name check → schema → correction", "拦截率 ~60%", C.BLUE],
  ["Six-Step Execution Pipeline", "Discover→Permission→Validate→Execute→Result→Persist", "成功率 >99.5%", C.ORANGE],
];
flow.forEach((f, i) => { const y = 1.8 + i * 1.0; s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 8.4, h: 0.82, fill: { color: f[3] } }); s.addText([{ text: f[0] + "    ", options: { bold: true, fontSize: 12.5, color: C.WHITE } }, { text: f[1], options: { fontSize: 10.5, color: "E6EAEE" } }], { x: 1.1, y, w: 8.0, h: 0.82, fontFace: FONT, valign: "middle" }); s.addText(f[2], { x: 9.45, y, w: 3.0, h: 0.82, fontFace: FONT, fontSize: 12, bold: true, color: C.GREEN, valign: "middle" }); if (i < 2) s.addShape(p.shapes.LINE, { x: 5.1, y: y + 0.82, w: 0, h: 0.18, line: { color: C.GRAY, width: 1.5, endArrowType: "triangle" } }); });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.95, w: 7.0, h: 1.35, fill: { color: C.LIGHT } });
s.addText([{ text: "核心指标", options: { bold: true, color: C.INK, fontSize: 13, breakLine: true } }, { text: "Parse >98% · 幻觉拦截 >60% · 执行 >99.5% · P99 <5s · 权限检查 <5ms", options: { fontSize: 12, color: C.GRAY, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.1, w: 6.6, h: 1.1, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 8.1, y: 4.95, w: 4.3, h: 1.35, fill: { color: C.DARK } });
s.addText([{ text: "Mini-Lab 预告", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "注册自定义 tool · 改权限策略触发 Ask-first · 连接 MCP server 发起 tools/list", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 8.3, y: 5.1, w: 3.9, h: 1.1, fontFace: FONT, valign: "top" });
s.addNotes("这就是 S2 的全景。从 LLM 吐出一个 tool call 开始——先经过结构化解析确保格式正确，再经过幻觉检测确保内容有意义，最后进入六步执行管线完成实际操作。整个链路中每一环都有明确的拦截机制：格式错？解析修复。名字错？编辑距离纠正。参数错？Schema 拒绝。权限不够？Ask-first。执行超时？30s 保护。结果太大？1MB 截断。层层设防，确保只有合法、安全、有意义的操作才能真正执行。下一个 Mini-Lab 让你亲手体验这些机制。");

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
module.exports = {};

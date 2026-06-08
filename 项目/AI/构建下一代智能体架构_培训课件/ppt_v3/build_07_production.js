const { C, FONT, MONO, newDeck, darkSlide, contentSlide, bullets, styledTable, hc, setModule, codeBox } = require("./aws_theme");
setModule("07 · Production Engineering");
const p = newDeck("Harness Engineering — 07 Production Engineering");
const N = 11;
const OUT = "/Users/qcguang/Desktop/courses/HarnessEngineering/ppt_v3/07_production.pptx";
let s;

// ---------- Slide 1: Cover ----------
s = darkSlide(p);
s.addText("PRODUCTION ENGINEERING", { x: 0.6, y: 1.5, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: C.ORANGE, charSpacing: 4 });
s.addText("生产工程", { x: 0.6, y: 2.0, w: 11.5, h: 0.9, fontFace: FONT, fontSize: 38, bold: true, color: C.WHITE });
s.addText("从 Demo 到 Production 的最后一公里", { x: 0.62, y: 2.95, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 18, color: "C7CED6" });
s.addText("\u201C80% 的 Agent 项目死在了\u2018最后一公里\u2019 — 不是模型不好，是缺生产工程。\u201D", { x: 0.62, y: 3.5, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, italic: true, color: "8C9AA6" });
s.addShape(p.shapes.LINE, { x: 0.62, y: 4.15, w: 6.2, h: 0, line: { color: "47525E", width: 1 } });
s.addText([
  { text: "Configuration · Canary · Cost · Performance · Topology", options: { breakLine: true } },
  { text: "S1-S5 已构建完成 — 现在让它们\u201C上路\u201D", options: { breakLine: true } },
  { text: "横切工程层：让 Agent 系统从\u201C能用\u201D到\u201C可运营\u201D", options: {} },
], { x: 0.62, y: 4.35, w: 12, h: 1.7, fontFace: FONT, fontSize: 14, color: "E6EAEE", paraSpaceAfter: 8 });
s.addText("40 min  ·  11 slides", { x: 9.5, y: 6.7, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: "6B7682", align: "right" });
s.addNotes("问一个问题：\u201C你们做过的 Agent demo，有多少最终上了生产？\u201D 停顿 3 秒。业界数据是不到 20%。80% 的 Agent 项目死在了\u201C最后一公里\u201D——不是模型不够好，不是 prompt 写得差，而是缺少生产级的工程保障。接下来 40 分钟，我们讲五个关键维度：配置管理、金丝雀发布、成本优化、性能工程、部署拓扑。这些是让 Agent 系统从\u201C能用\u201D到\u201C可运营\u201D的必修课。");

// ---------- Slide 2: Config 4-layer ----------
s = contentSlide(p, 2, N, "三层配置架构 — Defaults → YAML → Env → Runtime", "Configuration · Three-Layer Architecture");
styledTable(p, s, [
  [hc("层级"), hc("来源"), hc("变更方式"), hc("生效速度")],
  [{ text: "L0 · Hardcoded Defaults", options: { bold: true, color: C.GRAY } }, "代码中的安全兜底", "改代码 + 部署", "分钟级"],
  [{ text: "L1 · Global YAML", options: { bold: true, color: C.BLUE } }, "config/agent.yaml in Git", "PR + merge", "分钟级"],
  [{ text: "L2 · Environment Variables", options: { bold: true, color: C.ORANGE } }, ".env / K8s ConfigMap", "重启 / 滚动更新", "秒级"],
  [{ text: "L3 · Runtime Parameters", options: { bold: true, color: C.RED } }, "API / Feature Flag / CLI", "即时生效", "毫秒级"],
], { x: 0.92, y: 1.7, w: 11.5, colW: [2.8, 3.6, 2.8, 2.3], rowH: 0.55, fontSize: 11.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.2, w: 5.6, h: 0.55, fill: { color: C.DARK } });
s.addText("合并规则：L3 > L2 > L1 > L0（CSS specificity）", { x: 0.92, y: 4.2, w: 5.6, h: 0.55, fontFace: MONO, fontSize: 12, bold: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 4.2, w: 5.6, h: 0.55, fill: { color: C.GREEN } });
s.addText("黄金法则：All config in Git", { x: 6.82, y: 4.2, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 13, bold: true, color: C.WHITE, align: "center", valign: "middle" });
codeBox(p, s, [
  { text: "# config/agent.yaml (L1)", opt: { color: "8C9AA6" } },
  { text: "model: claude-sonnet-4-20250514", opt: { color: "8FD19E" } },
  { text: "timeout_seconds: 30", opt: { color: "8FD19E" } },
  { text: "max_tokens: 4096", opt: { color: "8FD19E" } },
  { text: "tool_concurrency: 5", opt: { color: "8FD19E" } },
  { text: "budget:", opt: { color: "8FBFE8" } },
  { text: "  per_task_usd: 0.50", opt: { color: "E8A33D" } },
  { text: "  daily_cap_usd: 100", opt: { color: "E8A33D" } },
], { x: 0.92, y: 4.95, w: 11.5, h: 1.45, fontSize: 10.5 });
s.addNotes("第一个维度：配置管理。很多团队的配置散落在代码各处——这里一个常量，那里一个环境变量，还有些硬编码在 prompt 里。问学员：\u201C你能在不改代码、不重新部署的情况下，把模型从 Sonnet 切到 Haiku 吗？\u201D 如果答案是\u201C不能\u201D，说明配置管理有问题。三层架构的价值：开发时有安全默认值（L0），标准部署用 YAML（L1），不同环境用 env（L2），紧急时运行时热切（L3）。If it's not in Git, it doesn't exist.");

// ---------- Slide 3: Configurable vs Hardcoded ----------
s = contentSlide(p, 3, N, "可配置 vs. 不可配置 — 划清边界", "Configuration · 边界划分");
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.GREEN } });
s.addText("✓ 应该可配置（运维需要灵活性）", { x: 0.92, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 2.3, w: 5.6, h: 2.4, fill: { color: "E6F4EA" } });
s.addText(["Provider / Model selection", "Timeout 阈值", "Token budgets", "Tool policies (allow/deny/ask)", "Logging level", "Retry 策略", "Feature flags"].map(t => ({ text: "✓ " + t, options: { breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 4 } })), { x: 1.1, y: 2.42, w: 5.3, h: 2.25, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fill: { color: C.RED } });
s.addText("✗ 不应该可配置（稳定性 & 安全）", { x: 6.82, y: 1.75, w: 5.6, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: C.WHITE, align: "center", valign: "middle" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 2.3, w: 5.6, h: 2.4, fill: { color: "FBEAE5" } });
s.addText(["Safety constraints（安全约束）", "Audit logging（合规要求）", "Core permission model", "Encryption settings", "Business logic branching"].map(t => ({ text: "✗ " + t, options: { breakLine: true, fontSize: 11, color: C.INK, paraSpaceBefore: 6 } })), { x: 7.0, y: 2.42, w: 5.3, h: 2.25, fontFace: FONT, valign: "top" });
codeBox(p, s, [
  { text: "---", opt: { color: "8C9AA6" } },
  { text: "id: system-prompt-coding-agent", opt: { color: "8FD19E" } },
  { text: "version: 2.3.1", opt: { color: "E8A33D" } },
  { text: "author: engineering-team", opt: { color: "8FD19E" } },
  { text: "updated: 2026-05-20", opt: { color: "8FD19E" } },
  { text: "changelog: \"添加 safety: 禁止修改 /etc 目录\"", opt: { color: "8FBFE8" } },
  { text: "---", opt: { color: "8C9AA6" } },
  { text: "You are a coding assistant...", opt: { color: "E8A33D" } },
], { x: 0.92, y: 4.85, w: 11.5, h: 1.5, fontSize: 10 });
s.addNotes("一个常见 anti-pattern：把所有东西都做成可配置的。这会导致 configuration hell——排列组合爆炸，测试覆盖不了。Safety constraints 尤其不能配置化——你不会让运维人员通过改一个 YAML 就关掉安全限制。Prompt versioning 是经常被忽视的点：很多团队的 prompt 就是代码里一个字符串，改了都不知道谁改的。把它当代码管理，PR review，版本号，changelog，全套。");

// ---------- Slide 4: Canary 5-Stage ----------
s = contentSlide(p, 4, N, "金丝雀发布 — 五阶段渐进式上线", "Canary Rollout · Five Stages");
const stages = [
  ["Stage 1", "Internal Dogfood", "团队内部", "≥ 3 天", "无 P0/P1 bug", C.GRAY],
  ["Stage 2", "1% Users", "极小流量", "≥ 4 天", "错误率无显著上升", C.BLUE],
  ["Stage 3", "10% Users", "A/B 对比", "3-5 天", "统计显著性 > 95%", C.ORANGE],
  ["Stage 4", "50% Users", "完整 Eval", "3-5 天", "全量级评估通过", "C0631A"],
  ["Stage 5", "100% Users", "全量发布", "持续 7 天", "持续监控", C.GREEN],
];
stages.forEach((st, i) => {
  const y = 1.75 + i * 0.55;
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y, w: 1.3, h: 0.45, fill: { color: st[5] } });
  s.addText(st[0], { x: 0.92, y, w: 1.3, h: 0.45, fontFace: FONT, fontSize: 11, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 2.3, y, w: 2.6, h: 0.45, fill: { color: C.LIGHT } });
  s.addText(st[1], { x: 2.4, y, w: 2.4, h: 0.45, fontFace: FONT, fontSize: 11, bold: true, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 4.95, y, w: 2.0, h: 0.45, fill: { color: C.LIGHT } });
  s.addText(st[2], { x: 5.05, y, w: 1.85, h: 0.45, fontFace: FONT, fontSize: 10.5, color: C.GRAY, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 7.0, y, w: 1.7, h: 0.45, fill: { color: "FBEAE5" } });
  s.addText(st[3], { x: 7.05, y, w: 1.6, h: 0.45, fontFace: FONT, fontSize: 10.5, color: C.RED, bold: true, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 8.75, y, w: 3.65, h: 0.45, fill: { color: "E6F4EA" } });
  s.addText(st[4], { x: 8.85, y, w: 3.5, h: 0.45, fontFace: FONT, fontSize: 10.5, color: C.GREEN, bold: true, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.7, w: 11.5, h: 0.85, fill: { color: C.DARK } });
s.addText([{ text: "核心洞察：Deployment ≠ Release", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "Deploy daily（代码每天部署）  ·  Release when metrics are green（feature flag 控制曝光）", options: { fontSize: 12, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 4.85, w: 11.1, h: 0.7, fontFace: FONT, valign: "top" });
s.addText("Agent 系统的 bug 是\u201C删了用户代码\u201D，不是\u201C按钮颜色错了\u201D — 渐进发布尤其重要。", { x: 0.92, y: 5.7, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, italic: true, color: C.GRAY, align: "center" });
s.addNotes("很多 startup 觉得\u201C我们用户少，不需要灰度发布\u201D。但 Agent 系统不一样。传统软件的 bug 是\u201C按钮颜色错了\u201D，Agent 系统的 bug 是\u201C删了用户的代码仓库\u201D。内部 dogfood 3 天这个要求是硬性的。为什么从 1% 开始而不是 5%？因为如果出问题，1% 的爆炸半径是可控的。每个阶段都必须有明确的\u201C通过条件\u201D——不是\u201C感觉可以了就推进\u201D，而是指标说了算。");

// ---------- Slide 5: Auto-Rollback + Feature Flags ----------
s = contentSlide(p, 5, N, "自动回滚阈值 + Feature Flag 三种类型", "Canary · Auto-Rollback");
styledTable(p, s, [
  [hc("指标"), hc("阈值"), hc("检测窗口")],
  ["Success Rate 下降", { text: "> 5 percentage points", options: { color: C.RED, bold: true } }, "5 min sliding"],
  ["P99 Latency 增加", { text: "> 30%", options: { color: C.RED, bold: true } }, "10 min sliding"],
  ["Cost per Task 增加", { text: "> 20%", options: { color: C.RED, bold: true } }, "1 hour"],
  ["新增 CRITICAL 错误", { text: "≥ 1 occurrence", options: { color: C.RED, bold: true } }, "即时"],
], { x: 0.92, y: 1.75, w: 6.4, colW: [2.4, 2.5, 1.5], rowH: 0.5, fontSize: 11 });
s.addText("Feature Flag 三种类型", { x: 7.7, y: 1.75, w: 5, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.INK });
const flags = [["Boolean", "开/关二元 · Kill switch", C.RED], ["Percentage", "渐进放量 · 灰度发布", C.ORANGE], ["Dimension", "按维度 · 用户/地域/Plan", C.BLUE]];
flags.forEach((f, i) => {
  const y = 2.15 + i * 0.62;
  s.addShape(p.shapes.RECTANGLE, { x: 7.7, y, w: 4.7, h: 0.55, fill: { color: f[2] } });
  s.addText([{ text: f[0] + "  ", options: { bold: true, fontSize: 11.5, color: C.WHITE } }, { text: f[1], options: { fontSize: 10.5, color: "FFFFFF" } }], { x: 7.85, y, w: 4.5, h: 0.55, fontFace: FONT, valign: "middle" });
});
codeBox(p, s, [
  { text: "# Feature Flag 示例", opt: { color: C.ORANGE, bold: true } },
  { text: "new_prompt_v3: false                  # Boolean", opt: { color: "8FD19E" } },
  { text: "smart_routing: 10%                    # Percentage", opt: { color: "E8A33D" } },
  { text: "multi_tool: plan=enterprise AND       # Dimension", opt: { color: "8FBFE8" } },
  { text: "            region=us", opt: { color: "8FBFE8" } },
], { x: 0.92, y: 4.4, w: 11.5, h: 1.5, fontSize: 10.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 6.05, w: 11.5, h: 0.4, fill: { color: C.GREEN } });
s.addText("回滚不是失败，是系统在正常工作的证明", { x: 0.92, y: 6.05, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, italic: true, color: C.WHITE, align: "center", valign: "middle" });
s.addNotes("自动回滚是整个 canary 策略的安全网。这些阈值必须在上线前就定义好，写入代码而不是靠人记住。问学员：\u201C如果你的 Agent 系统突然成本翻倍了，你能在多少时间内发现并回滚？\u201D 如果答案是\u201C等到月底看账单\u201D——那就太晚了。Feature flag 的三种类型各有场景：Boolean 适合紧急下线，Percentage 适合新功能灰度，Dimension 适合给特定客户群优先体验。初期不需要 LaunchDarkly——一个 JSON 文件 + API endpoint 就够了。");

// ---------- Slide 6: Cost 6 Levers ----------
s = contentSlide(p, 6, N, "成本优化 — 六把高 ROI 扳手 → 60-80% 成本降幅", "Cost · Six High-ROI Levers");
styledTable(p, s, [
  [hc("#"), hc("杠杆"), hc("机制"), hc("节省"), hc("难度")],
  [{ text: "1", options: { align: "center", bold: true } }, { text: "Prompt Caching", options: { bold: true, color: C.RED } }, "system prompt + prefix 命中缓存", { text: "50-90%", options: { color: C.GREEN, bold: true } }, "★☆☆"],
  [{ text: "2", options: { align: "center", bold: true } }, { text: "Schema Caching", options: { bold: true, color: C.ORANGE } }, "tool definition 序列化一次", { text: "10-20%", options: { color: C.GREEN, bold: true } }, "★☆☆"],
  [{ text: "3", options: { align: "center", bold: true } }, { text: "Smart Model Routing", options: { bold: true, color: C.BLUE } }, "简单→Haiku, 复杂→Sonnet, 极难→Opus", { text: "40-60%", options: { color: C.GREEN, bold: true } }, "★★☆"],
  [{ text: "4", options: { align: "center", bold: true } }, { text: "Result Truncation", options: { bold: true, color: "C0631A" } }, "工具输出截断到关键信息", { text: "20-40%", options: { color: C.GREEN, bold: true } }, "★☆☆"],
  [{ text: "5", options: { align: "center", bold: true } }, { text: "Token Hard Limits", options: { bold: true, color: C.GRAY } }, "per-task / per-session 上限", { text: "防溢出", options: { color: C.GREEN, bold: true } }, "★☆☆"],
  [{ text: "6", options: { align: "center", bold: true } }, { text: "History Compression", options: { bold: true, color: "2E4A63" } }, "旧轮次压缩为摘要", { text: "30-50%", options: { color: C.GREEN, bold: true } }, "★★☆"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [0.5, 2.3, 5.2, 1.4, 2.1], rowH: 0.5, fontSize: 11 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.0, w: 5.6, h: 1.35, fill: { color: C.GREEN } });
s.addText([{ text: "综合效果", options: { bold: true, color: C.WHITE, fontSize: 13, breakLine: true } }, { text: "60-80%", options: { fontSize: 36, bold: true, color: C.WHITE, breakLine: true, paraSpaceBefore: 6 } }, { text: "总成本降幅 · 不需换模型", options: { fontSize: 11, color: "FFFFFF" } }], { x: 0.92, y: 5.1, w: 5.6, h: 1.2, fontFace: FONT, align: "center", valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 5.0, w: 5.6, h: 1.35, fill: { color: C.DARK } });
s.addText([{ text: "核心理念", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "花钱花在刀刃上 — 让每个 token 都承载高价值信息", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }, { text: "起步顺序：1 → 4 → 5 → 2 → 3 → 6", options: { fontSize: 11, italic: true, color: "C7CED6", paraSpaceBefore: 8 } }], { x: 7.0, y: 5.15, w: 5.3, h: 1.15, fontFace: FONT, valign: "top" });
s.addNotes("这是最让工程经理兴奋的一页。先问学员：\u201C你们现在每月的 LLM API 费用是多少？\u201D 然后告诉他们可能砍掉 60-80%——不是换便宜模型，而是纯工程优化。Prompt Caching 是最容易实现的，Anthropic 原生支持，只要你保证 system prompt 的 prefix 一致就能命中缓存。Smart Model Routing 是收益最大的——95% 的任务 Haiku 就能搞定。Result Truncation 最容易被忽视——git log 输出 10000 行塞进 context，既贵又没用。");

// ---------- Slide 7: Cost Monitoring ----------
s = contentSlide(p, 7, N, "成本监控 — 你不能优化你看不见的东西", "Cost · Monitoring Dashboard");
const quads = [
  ["📈 Daily Cost Trend", "折线图 + 预算线", C.BLUE],
  ["🥧 Cost by Task Type", "饼图：code/search/debug/other", C.ORANGE],
  ["📊 Cost by Model", "柱状图：Haiku/Sonnet/Opus", C.GREEN],
  ["🚨 Anomaly Alerts", "异常任务 / 异常用户列表", C.RED],
];
quads.forEach((q, i) => {
  const x = 0.92 + (i % 2) * 5.95;
  const y = 1.75 + Math.floor(i / 2) * 1.4;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 1.25, fill: { color: C.LIGHT } });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.14, h: 1.25, fill: { color: q[2] } });
  s.addText([{ text: q[0], options: { bold: true, fontSize: 14, color: q[2], breakLine: true } }, { text: q[1], options: { fontSize: 11, color: C.GRAY, paraSpaceBefore: 8 } }], { x: x + 0.25, y: y + 0.12, w: 5.2, h: 1.05, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.65, w: 11.5, h: 1.7, fill: { color: C.DARK } });
s.addText([{ text: "告警规则（逐级升级）", options: { bold: true, color: C.ORANGE, fontSize: 13, breakLine: true } }, { text: "单任务 > P95 历史值 → INFO（记录，不打扰）", options: { fontSize: 11, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "日成本达预算 80% → WARNING（通知负责人）", options: { fontSize: 11, color: C.WHITE, breakLine: true, paraSpaceBefore: 4 } }, { text: "日成本达预算 100% → CRITICAL + Hard Stop（暂停服务 + 告警）", options: { fontSize: 11, bold: true, color: C.RED, breakLine: true, paraSpaceBefore: 4 } }, { text: "单用户日消耗 > 阈值 → Throttle（限流该用户）", options: { fontSize: 11, color: C.WHITE, paraSpaceBefore: 4 } }], { x: 1.12, y: 4.8, w: 11.1, h: 1.5, fontFace: FONT, valign: "top" });
s.addNotes("很多团队上线后才发现\u201C某个用户一天花了 $500\u201D 或者\u201C某个功能的成本是预期的 10 倍\u201D。成本监控不是上线后才加的——Day 1 就应该有。成本归因特别重要：如果你不知道钱花在哪里，就无法做定向优化。Hard stop 机制是最后的安全网——宁可暂时拒绝服务，也不要让成本无限膨胀。我见过一个真实案例：Agent 陷入死循环，一个晚上烧了 $3000，第二天早上才发现。有 hard stop 就不会发生。");

// ---------- Slide 8: Performance Core Targets ----------
s = contentSlide(p, 8, N, "性能指标 — 用户能感知的才是真指标", "Performance · Core Targets");
const targets = [
  ["TTFT", "< 1s", "超过 1s 用户感到\u201C卡\u201D，触发重试", C.RED],
  ["P99 Task Completion", "< 30s", "交互式任务的耐心极限", C.ORANGE],
  ["Tool Concurrency", "并发执行", "3-5x speedup vs. 串行", C.BLUE],
  ["Streaming", "响应 > 2s 必启用", "感知延迟降低 50%+", C.GREEN],
];
targets.forEach((t, i) => {
  const x = 0.92 + (i % 2) * 5.95;
  const y = 1.75 + Math.floor(i / 2) * 1.4;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.55, h: 1.25, fill: { color: t[3] } });
  s.addText([{ text: t[0], options: { bold: true, fontSize: 14, color: C.WHITE, breakLine: true } }, { text: t[1], options: { fontSize: 18, bold: true, color: C.WHITE, breakLine: true, paraSpaceBefore: 4 } }, { text: t[2], options: { fontSize: 10.5, color: "FFFFFF", paraSpaceBefore: 4 } }], { x: x + 0.18, y: y + 0.1, w: 5.2, h: 1.1, fontFace: FONT, valign: "top" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.65, w: 11.5, h: 0.8, fill: { color: C.DARK } });
s.addText([{ text: "Perceived latency > Actual latency", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "Streaming 让用户\u201C看到进度\u201D → 心理等待时间缩短一半", options: { fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 4.78, w: 11.1, h: 0.65, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.6, w: 11.5, h: 0.8, fill: { color: "FBEAE5" } });
s.addText([{ text: "Streaming 是强制要求，不是可选优化", options: { bold: true, color: C.RED, fontSize: 13, breakLine: true } }, { text: "任何响应可能 > 2s 必须 streaming · SSE / WebSocket · 用户需看到 Agent\u201C在思考\u201D", options: { fontSize: 11, color: C.INK, paraSpaceBefore: 5 } }], { x: 1.12, y: 5.73, w: 11.1, h: 0.65, fontFace: FONT, valign: "top" });
s.addNotes("TTFT < 1s 是生死线。超过 1 秒，用户会点取消或重试——然后你花了双倍 token。Streaming 不是\u201Cnice to have\u201D——在 Agent 场景下是强制要求。可以做个简单演示：在终端里，一个命令等 5 秒后输出全部，另一个立即开始逐字输出。让学员体感差异——总时间可能一样，但体验天壤之别。Tool concurrency 很多框架没利用好：Agent 要读 5 个文件，没有依赖关系，为什么要等上一个读完才开始下一个？并发一下，5 秒变 1 秒。");

// ---------- Slide 9: Performance Optimization Levers ----------
s = contentSlide(p, 9, N, "性能优化五板斧（按优先级排序）", "Performance · Optimization Levers");
styledTable(p, s, [
  [hc("优先级"), hc("手段"), hc("效果"), hc("实施成本")],
  [{ text: "P0", options: { bold: true, color: C.GREEN, align: "center" } }, { text: "Streaming Response", options: { bold: true } }, { text: "感知延迟 -50%", options: { color: C.GREEN, bold: true } }, "极低（API 原生）"],
  [{ text: "P1", options: { bold: true, color: C.BLUE, align: "center" } }, { text: "Tool Concurrency", options: { bold: true } }, { text: "多工具延迟 3-5x ↓", options: { color: C.GREEN, bold: true } }, "低（依赖分析）"],
  [{ text: "P2", options: { bold: true, color: C.ORANGE, align: "center" } }, { text: "Prompt Caching", options: { bold: true } }, { text: "TTFT -40%, cost -90%", options: { color: C.GREEN, bold: true } }, "低（prefix 一致）"],
  [{ text: "P3", options: { bold: true, color: "C0631A", align: "center" } }, { text: "Smart Model Routing", options: { bold: true } }, { text: "简单任务延迟 -60%", options: { color: C.GREEN, bold: true } }, "中（需 classifier）"],
  [{ text: "P4", options: { bold: true, color: C.RED, align: "center" } }, { text: "Async Cache Warmup", options: { bold: true } }, { text: "下一步 TTFT → 0", options: { color: C.GREEN, bold: true } }, "高（需预测）"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.0, 3.2, 3.6, 3.7], rowH: 0.5, fontSize: 11.5 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.55, w: 11.5, h: 1.8, fill: { color: C.DARK } });
s.addText([{ text: "实施建议：先 P0 → P4 顺序", options: { bold: true, color: C.ORANGE, fontSize: 14, breakLine: true } }, { text: "P0 几乎零成本：API 加 stream:true，前端改渐进渲染", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 8 } }, { text: "P1 注意陷阱：操作同一资源的工具不能并发（竞争条件）→ 需依赖分析", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 4 } }, { text: "P2 前提：system prompt prefix 必须稳定一致，动态内容放后面", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.WHITE, breakLine: true, paraSpaceBefore: 4 } }, { text: "P3 收益最大：Haiku ~200ms vs Opus ~2s · 95% 任务不需要最强模型", options: { bullet: { code: "2022" }, fontSize: 11.5, color: C.WHITE, paraSpaceBefore: 4 } }], { x: 1.12, y: 4.7, w: 11.1, h: 1.6, fontFace: FONT, valign: "top" });
s.addNotes("按优先级排序很重要——很多团队一上来就搞复杂的 cache warmup，streaming 都没做好。建议学员按 P0→P4 顺序逐步实施。P0 几乎零成本：API 加个 stream:true，前端改成渐进渲染。P1 需要注意一个陷阱：如果两个工具操作同一个文件，并发会导致竞争条件，所以需要依赖分析——读读可以并发，读写不行，写写更不行。P2 的 prompt caching 有个前提：你的 system prompt 前缀必须稳定一致。");

// ---------- Slide 10: Deployment 3 Tiers ----------
s = contentSlide(p, 10, N, "部署拓扑 — 从单机到多区域", "Deployment Topology · Three Tiers");
styledTable(p, s, [
  [hc("Tier"), hc("用户规模"), hc("状态存储"), hc("扩展方式"), hc("适用场景")],
  [{ text: "Tier 1", options: { bold: true, color: C.GREEN } }, "< 100", "SQLite + 文件系统", "垂直扩展", "内部工具 / MVP"],
  [{ text: "Tier 2", options: { bold: true, color: C.ORANGE } }, "100-10K", "Redis + PostgreSQL", "水平扩展", "B2B SaaS / 中型产品"],
  [{ text: "Tier 3", options: { bold: true, color: C.RED } }, "10K+", "多区域独立集群", "区域扩展", "全球化产品"],
], { x: 0.92, y: 1.75, w: 11.5, colW: [1.2, 1.5, 3.3, 1.8, 3.7], rowH: 0.6, fontSize: 11 });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 3.85, w: 5.6, h: 1.5, fill: { color: "E6F4EA" } });
s.addText([{ text: "✓ 必须外部化（Tier 2+）", options: { bold: true, color: C.GREEN, fontSize: 12.5, breakLine: true } }, ...["Session state · Memory", "Task state · Audit logs", "Configuration"].map(t => ({ text: "• " + t, options: { breakLine: true, fontSize: 10.5, color: C.INK, paraSpaceBefore: 5 } }))], { x: 1.1, y: 4.0, w: 5.3, h: 1.3, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 6.82, y: 3.85, w: 5.6, h: 1.5, fill: { color: "FBEAE5" } });
s.addText([{ text: "可保持本地", options: { bold: true, color: C.ORANGE, fontSize: 12.5, breakLine: true } }, ...["Schema cache", "Working memory", "Temp files"].map(t => ({ text: "• " + t, options: { breakLine: true, fontSize: 10.5, color: C.INK, paraSpaceBefore: 5 } }))], { x: 7.0, y: 4.0, w: 5.3, h: 1.3, fontFace: FONT, valign: "top" });
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.55, w: 11.5, h: 0.8, fill: { color: C.DARK } });
s.addText([{ text: "黄金测试：\u201C如果这个实例突然崩溃，用户会丢失什么？\u201D → 那些需要外部化", options: { bold: true, color: C.ORANGE, fontSize: 12.5, breakLine: true } }, { text: "升级信号：1→2 单实例 > 70% 或需高可用 · 2→3 跨地域延迟或合规要求", options: { fontSize: 11, italic: true, color: C.WHITE, paraSpaceBefore: 6 } }], { x: 1.12, y: 5.65, w: 11.1, h: 0.7, fontFace: FONT, valign: "top" });
s.addNotes("不要过早优化！问学员预期用户量——90% 的团队 Tier 1 就够了。最常见的错误是\u201C我们将来可能有百万用户\u201D然后一开始就搞多区域部署，结果两年了还是 50 个内部用户。从 Tier 1 开始有个巨大好处：简单、快速迭代、状态全在一个地方好调试。当你真的需要 Tier 2 时再升级——前提是做好状态外部化。关键是这个升级路径要在设计时就想好：不要把状态耦合在进程内存里，那样升级时就是重写。");

// ---------- Slide 11: Production Readiness Checklist ----------
s = contentSlide(p, 11, N, "生产就绪清单 — 7 大类 · 上线前最后检查", "Production Readiness Checklist");
const ck7 = [
  ["1", "Config", "配置版本化？能否不改代码切模型？", "Git + PR 审核 + 热切换"],
  ["2", "Canary", "回滚条件预定义？自动还是手动？", "自动回滚阈值已配置并测试"],
  ["3", "Cost", "预算上限？异常可检测？", "Per-task cap + daily cap + 告警"],
  ["4", "Performance", "TTFT < 1s？Streaming 已实现？", "P95 TTFT < 1s + 全链路 streaming"],
  ["5", "Monitoring", "核心指标可见？告警配置？", "Dashboard + 4 级告警规则"],
  ["6", "Security", "Sandbox 配置？权限最小化？", "Tool policy + audit log"],
  ["7", "Evaluation", "Baseline 建立？回归检测？", "评估集 + 基线分数 + CI 集成"],
];
ck7.forEach((c, i) => {
  const y = 1.75 + i * 0.45;
  s.addShape(p.shapes.OVAL, { x: 0.92, y, w: 0.4, h: 0.4, fill: { color: C.ORANGE } });
  s.addText(c[0], { x: 0.92, y, w: 0.4, h: 0.4, fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE, align: "center", valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 1.45, y, w: 1.6, h: 0.4, fill: { color: C.DARK } });
  s.addText(c[1], { x: 1.55, y, w: 1.5, h: 0.4, fontFace: FONT, fontSize: 11, bold: true, color: C.ORANGE, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 3.15, y, w: 4.5, h: 0.4, fill: { color: C.LIGHT } });
  s.addText(c[2], { x: 3.25, y, w: 4.35, h: 0.4, fontFace: FONT, fontSize: 9.5, color: C.INK, valign: "middle" });
  s.addShape(p.shapes.RECTANGLE, { x: 7.75, y, w: 4.65, h: 0.4, fill: { color: "E6F4EA" } });
  s.addText(c[3], { x: 7.85, y, w: 4.5, h: 0.4, fontFace: FONT, fontSize: 9.5, color: C.GREEN, bold: true, valign: "middle" });
});
const goNoGo = [["🟢 7/7", "GO — 全量上线", C.GREEN], ["🟡 5-6/7", "Conditional Go — 限流 + 限期修复", "E0A000"], ["🔴 < 5/7", "No Go — 回去补课", C.RED]];
goNoGo.forEach((g, i) => {
  const x = 0.92 + i * 3.87;
  s.addShape(p.shapes.RECTANGLE, { x, y: 5.0, w: 3.6, h: 0.6, fill: { color: g[2] } });
  s.addText([{ text: g[0] + "  ", options: { bold: true, fontSize: 13, color: C.WHITE } }, { text: g[1], options: { fontSize: 10.5, color: "FFFFFF" } }], { x: x + 0.15, y: 5.0, w: 3.4, h: 0.6, fontFace: FONT, valign: "middle" });
});
s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 5.75, w: 11.5, h: 0.6, fill: { color: C.DARK } });
s.addText("\u201CProduction readiness is not a milestone — it's a muscle.\u201D", { x: 0.92, y: 5.75, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 14, bold: true, italic: true, color: C.ORANGE, align: "center", valign: "middle" });
s.addNotes("这是本模块的收束，也是整个课程\u201C工程化\u201D理念的集中体现。把这个 checklist 做成团队可以直接使用的模板——学员回去后可以立即对着表格审视自己的系统。强调 7/7 是理想状态，现实中很多团队是 3/7 就上了线，然后在生产中补课——代价是事故、是用户流失、是凌晨 3 点的告警电话。最后一句话总结整个模块：Production engineering 不是上线后才做的事，而是设计时就应该内建的能力。就像飞机的安全检查清单——不是飞机起飞后才看的，是起飞前必须过的。接下来进入 Capstone Lab。");

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
module.exports = {};

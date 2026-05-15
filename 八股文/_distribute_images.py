"""
Match source lecture note images to knowledge file ## sections by comparing
Q&A content against source section content. More robust than title-only keyword matching.
"""
import re
import math
from pathlib import Path
from collections import Counter

BASE = Path("/Users/haojie.liu/personalProjects/anki/八股文")

SOURCE_MAP = {
    "Redis/knowledge/数据结构/SDS字典跳表与对象编码/SDS字典跳表与对象编码.md": "Redis/Redis设计与实现（一） 数据结构 & 对象.md",
    "Redis/knowledge/数据结构/高级数据类型与使用场景/高级数据类型与使用场景.md": "Redis/Redis设计与实现（一） 数据结构 & 对象.md",
    "Redis/knowledge/数据库/过期删除与内存淘汰/过期删除与内存淘汰.md": "Redis/Redis设计与实现（二） 数据库（删除策略&过期淘汰策略）.md",
    "Redis/knowledge/IO模型/事件驱动与单线程模型/事件驱动与单线程模型.md": "Redis/Redis设计与实现（三） 服务器与客户端的交互（事件IO模型）.md",
    "Redis/knowledge/复制高可用/主从复制与PSYNC/主从复制与PSYNC.md": "Redis/Redis设计与实现（四） 主从复制.md",
    "Redis/knowledge/复制高可用/Sentinel哨兵/Sentinel哨兵.md": "Redis/Redis设计与实现（五） Sentinel哨兵.md",
    "Redis/knowledge/集群/Cluster槽与重分片/Cluster槽与重分片.md": "Redis/Redis设计与实现（六） 集群（分片）.md",
    "Redis/knowledge/集群/MOVED-ASK与HashTag/MOVED-ASK与HashTag.md": "Redis/Redis设计与实现（六） 集群（分片）.md",
    "Redis/knowledge/消息/PubSub与Stream/PubSub与Stream.md": "Redis/Redis设计与实现（七） 发布 & 订阅.md",
    "Redis/knowledge/事务与脚本/事务WATCH与Lua/事务WATCH与Lua.md": "Redis/Redis设计与实现（八） 事务.md",
    "Redis/knowledge/持久化/RDB与AOF/RDB与AOF.md": "Redis/Redis设计与实现（九） RDB和AOF持久化.md",
    "计算机网络/knowledge/网络基础/分层模型与网络性能/分层模型与网络性能.md": "计算机网络/计算机网络 网络概述（什么是互联网 & 互联网结构）.md",
    "计算机网络/knowledge/应用层/HTTP基础与缓存/HTTP基础与缓存.md": "计算机网络/计算机网络 应用层（上）.md",
    "计算机网络/knowledge/应用层/DNS解析/DNS解析.md": "计算机网络/计算机网络 应用层（上）.md",
    "计算机网络/knowledge/应用层/HTTP版本演进/HTTP版本演进.md": "计算机网络/计算机网络 应用层（下）.md",
    "计算机网络/knowledge/传输层/TCP与UDP对比/TCP与UDP对比.md": "计算机网络/计算机网络 传输层 TCP&UDP 可靠传输（上）.md",
    "计算机网络/knowledge/传输层/TCP可靠传输与滑动窗口/TCP可靠传输与滑动窗口.md": "计算机网络/计算机网络 传输层 TCP&UDP 可靠传输（上）.md",
    "计算机网络/knowledge/传输层/TCP流量控制与拥塞控制/TCP流量控制与拥塞控制.md": "计算机网络/计算机网络 传输层 TCP&UDP 可靠传输（下）.md",
    "计算机网络/knowledge/传输层/TCP连接管理/TCP连接管理.md": "计算机网络/计算机网络 传输层 TCP&UDP 可靠传输（下）.md",
    "计算机网络/knowledge/网络层/IP地址子网与NAT/IP地址子网与NAT.md": "计算机网络/计算机网络 网络层（数据平面）.md",
    "计算机网络/knowledge/网络层/ARP-ICMP与路由/ARP-ICMP与路由.md": "计算机网络/计算机网络 网络层（控制平面）.md",
    "计算机网络/knowledge/安全/HTTPS与TLS/HTTPS与TLS.md": "计算机网络/计算机网络 网络安全 HTTP & HTTPS URI解析全过程.md",
    "计算机网络/knowledge/安全/Web常见攻击/Web常见攻击.md": "计算机网络/计算机网络 网络安全 HTTP & HTTPS URI解析全过程.md",
    "计算机网络/knowledge/网络编程/epoll与高性能网络/epoll与高性能网络.md": "计算机网络/TCP IP网络编程 Linux下的网络编程.md",
    "计算机网络/knowledge/网络编程/Socket与IO多路复用/Socket与IO多路复用.md": "计算机网络/TCP IP网络编程 Linux下的网络编程.md",
    "计算机网络/knowledge/负载均衡/四层与七层负载均衡/四层与七层负载均衡.md": "综合/有关四层负载均衡与七层负载均衡的讨论.md",
}

EXTRA_SOURCES = {
    "计算机网络/knowledge/网络编程/Socket与IO多路复用/Socket与IO多路复用.md": [
        "计算机网络/TCP IP网络编程 理解网络编程和套接字.md",
        "计算机网络/TCP IP网络编程 实现基于TCP和UDP的服务器端 客户端.md",
    ],
}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HEADER_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def tokenize(text):
    """Extract meaningful Chinese/English tokens from text."""
    tokens = set()
    # Chinese: take bigrams for better matching
    cleaned = re.sub(r'[^一-鿿\w]', ' ', text.lower())
    words = cleaned.split()
    for w in words:
        if len(w) >= 2:
            tokens.add(w)
        if len(w) >= 3:
            tokens.add(w)
    # Chinese character bigrams
    chinese = re.findall(r'[一-鿿]+', text)
    for segment in chinese:
        for i in range(len(segment) - 1):
            tokens.add(segment[i:i+2])
        for i in range(len(segment) - 2):
            tokens.add(segment[i:i+3])
    return tokens


def parse_source_sections(source_path):
    """Parse a source lecture note into (title, level, images, body_text)."""
    text = source_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = []
    current_title = "<preamble>"
    current_level = 0
    current_images = []
    current_body = []

    for line in lines:
        header_match = HEADER_RE.match(line)
        if header_match:
            if current_images or current_body:
                sections.append((current_title, current_level, list(current_images), " ".join(current_body)))
            level = len(header_match.group(1))
            current_title = header_match.group(2).strip()
            current_level = level
            current_images = []
            current_body = []
            continue
        img_match = IMAGE_RE.search(line)
        if img_match:
            img_path = img_match.group(1)
            img_name = Path(img_path).name
            if img_name and not img_path.startswith("http") and "notion.so" not in img_path:
                current_images.append(img_name)
        # Always accumulate body text (skip image lines and empty lines for tokenization)
        clean = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', line)
        clean = re.sub(r'[#*>\[\]`|]', ' ', clean)
        if clean.strip():
            current_body.append(clean.strip())

    if current_images or current_body:
        sections.append((current_title, current_level, list(current_images), " ".join(current_body)))
    return sections


def get_qa_text(knowledge_path, section_name):
    """Extract Q&A text for a specific ## section from the knowledge file."""
    content = knowledge_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    in_section = False
    qa_lines = []
    for line in lines:
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            in_section = (m.group(1).strip() == section_name)
            continue
        if in_section:
            if re.match(r"^##\s+", line):
                break
            clean = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', line)
            clean = re.sub(r'[#*>\[\]`|]', ' ', clean)
            if clean.strip():
                qa_lines.append(clean.strip())
    return " ".join(qa_lines)


def cosine_similarity(tokens1, tokens2):
    """Compute Jaccard-like token overlap score."""
    if not tokens1 or not tokens2:
        return 0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0


def match_by_content(source_sections, ks_tokens):
    """Find best matching source sections for a given knowledge section token set."""
    best_score = 0
    best_images = []
    for src_title, src_level, src_images, src_body in source_sections:
        src_tokens = tokenize(src_title + " " + src_body)
        score = cosine_similarity(ks_tokens, src_tokens)
        if score > best_score:
            best_score = score
            best_images = list(src_images)
        elif score == best_score and score > 0:
            best_images.extend(src_images)
    seen = set()
    unique = []
    for img in best_images:
        if img not in seen:
            seen.add(img)
            unique.append(img)
    return unique, best_score


def distribute_images(knowledge_path, source_paths):
    """Match source images to knowledge sections by content similarity."""
    all_source_sections = []
    for sp in source_paths:
        if sp.exists():
            all_source_sections.extend(parse_source_sections(sp))
    if not all_source_sections:
        return "no_source_sections"

    content = knowledge_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    ks_names = []
    ks_starts = []
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            ks_names.append(m.group(1).strip())
            ks_starts.append(i)

    if not ks_names:
        return "no_sections"

    # Assign each source section to the best matching knowledge section
    # Precompute knowledge section tokens
    ks_all_tokens = {}
    for ks_name in ks_names:
        qa_text = get_qa_text(knowledge_path, ks_name)
        ks_all_tokens[ks_name] = tokenize(ks_name + " " + qa_text)

    # For each source section, find the best matching knowledge section
    ks_images = {name: [] for name in ks_names}
    used_source_images = set()

    for src_title, src_level, src_images, src_body in all_source_sections:
        if not src_images:
            continue
        src_tokens = tokenize(src_title + " " + src_body)
        best_ks = None
        best_score = 0.0
        for ks_name, ks_tokens in ks_all_tokens.items():
            score = cosine_similarity(ks_tokens, src_tokens)
            if score > best_score:
                best_score = score
                best_ks = ks_name
        # Require a minimum similarity (low threshold to catch more matches)
        if best_ks and best_score >= 0.005:
            for img in src_images:
                if img not in used_source_images:
                    ks_images[best_ks].append(img)
                    used_source_images.add(img)

    # Remove images from header
    header_end = ks_starts[0]
    new_header_lines = []
    for i in range(header_end):
        img_match = IMAGE_RE.search(lines[i])
        if not img_match:
            new_header_lines.append(lines[i])
        elif img_match and img_match.group(1).startswith("http"):
            new_header_lines.append(lines[i])

    while new_header_lines and new_header_lines[-1].strip() == "":
        new_header_lines.pop()

    new_lines = list(new_header_lines)
    for i, (ks_name, ks_start) in enumerate(zip(ks_names, ks_starts)):
        ks_end = ks_starts[i + 1] if i + 1 < len(ks_starts) else len(lines)
        section_lines = lines[ks_start:ks_end]

        q_line_idx = None
        for j, sl in enumerate(section_lines):
            if re.match(r"^Q:\s", sl):
                q_line_idx = j
                break

        section_images = ks_images.get(ks_name, [])
        # Filter out images already present in this section
        section_text = "\n".join(section_lines)
        section_images = [img for img in section_images if img not in section_text]
        if section_images and q_line_idx is not None:
            img_lines = [f"![image]({img})" for img in section_images]
            for img_line in reversed(img_lines):
                section_lines.insert(q_line_idx, img_line)

        new_lines.extend(section_lines)

    new_content = "\n".join(new_lines)
    if new_content != content:
        knowledge_path.write_text(new_content, encoding="utf-8")
        total_assigned = sum(len(v) for v in ks_images.values())
        return f"distributed {total_assigned} images"
    return "no_changes"


def main():
    total_distributed = 0
    total_no_change = 0
    total_skip = 0

    for knowledge_rel, source_rel in SOURCE_MAP.items():
        knowledge_path = BASE / knowledge_rel
        if not knowledge_path.exists():
            print(f"SKIP (no file): {knowledge_rel}")
            total_skip += 1
            continue

        source_path = BASE / source_rel
        extra_sources = []
        if knowledge_rel in EXTRA_SOURCES:
            for es in EXTRA_SOURCES[knowledge_rel]:
                extra_sources.append(BASE / es)
        source_paths = [source_path] + extra_sources

        name = f"{Path(knowledge_rel).parent.name}/{Path(knowledge_rel).name}"
        try:
            result = distribute_images(knowledge_path, source_paths)
            if result.startswith("distributed"):
                print(f"  {result}: {name}")
                total_distributed += 1
            elif result == "no_changes":
                print(f"  {result}: {name}")
                total_no_change += 1
            else:
                print(f"  {result}: {name}")
                total_skip += 1
        except Exception as e:
            print(f"  ERROR: {name} -> {e}")
            import traceback
            traceback.print_exc()

    print(f"\nDone: {total_distributed} distributed, {total_no_change} no changes, {total_skip} skip")


if __name__ == "__main__":
    main()

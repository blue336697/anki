#!/usr/bin/env python3
"""Map source lecture-note images to knowledge files based on heading context."""
import os, re
from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote

JAVA_DIR = Path("/Users/haojie.liu/personalProjects/anki/八股文/Java")

HEADING_ROUTE_MAP = {
    "Java集合相关总结（List Set Map）": {
        "ArrayList": "集合/ArrayList、LinkedList与CopyOnWriteArrayList",
        "LinkedList": "集合/ArrayList、LinkedList与CopyOnWriteArrayList",
        "CopyOnWriteArrayList": "集合/ArrayList、LinkedList与CopyOnWriteArrayList",
        "HashMap": "集合/HashMap原理",
        "HashSet": "集合/HashSet、LinkedHashSet与TreeSet",
        "LinkedHashSet": "集合/HashSet、LinkedHashSet与TreeSet",
        "TreeSet": "集合/HashSet、LinkedHashSet与TreeSet",
        "LinkedHashMap": "集合/LinkedHashMap与TreeMap",
        "TreeMap": "集合/LinkedHashMap与TreeMap",
        "Queue": "集合/Queue与Deque",
        "Deque": "集合/Queue与Deque",
        "集合框架": "集合/ArrayList、LinkedList与CopyOnWriteArrayList",
    },
    "Spring源码分析（IOC&AOP） SpringMVC源码分析（DispatcherServle": {
        "IOC": "Spring/01-Spring-IoC与AOP核心",
        "IoC": "Spring/01-Spring-IoC与AOP核心",
        "AOP": "Spring/01-Spring-IoC与AOP核心",
        "SpringMVC": "Spring/02-SpringMVC核心流程",
        "DispatcherServlet": "Spring/02-SpringMVC核心流程",
    },
    "JDK简要进化史（8~10）": {
        "JDK 8": "JDK演进/JDK8关键特性",
        "JDK8": "JDK演进/JDK8关键特性",
        "JDK 9": "JDK演进/JDK9-10模块化与工具",
        "JDK9": "JDK演进/JDK9-10模块化与工具",
        "JDK 10": "JDK演进/JDK9-10模块化与工具",
        "JDK10": "JDK演进/JDK9-10模块化与工具",
    },
    "Java多并发（一） 并发机制的底层原理（内存模型、重排序）": {
        "volatile": "并发/volatile与JMM",
        "内存模型": "并发/Java内存模型与重排序",
        "JMM": "并发/Java内存模型与重排序",
        "重排序": "并发/Java内存模型与重排序",
        "happens-before": "并发/Java内存模型与重排序",
    },
    "Java多并发（二） cas & synchronized & volatile的内存语义": {
        "CAS": "并发/CAS原理",
        "synchronized": "并发/synchronized与monitor",
        "volatile": "并发/volatile与JMM",
        "锁升级": "并发/锁升级与版本差异",
        "偏向锁": "并发/锁升级与版本差异",
        "轻量级锁": "并发/锁升级与版本差异",
        "重量级锁": "并发/锁升级与版本差异",
    },
    "Java多并发（五） JUC包下的并发容器（ConcurrentHashMap）& 并发工具类 &_": {
        "ConcurrentHashMap": "并发/ConcurrentHashMap",
        "CountDownLatch": "并发/JUC同步工具类",
        "CyclicBarrier": "并发/JUC同步工具类",
        "Semaphore": "并发/JUC同步工具类",
        "原子": "并发/原子类与LongAdder",
        "Atomic": "并发/原子类与LongAdder",
        "LongAdder": "并发/原子类与LongAdder",
        "ForkJoin": "并发/ForkJoinPool与工作窃取",
        "CompletableFuture": "并发/CompletableFuture异步编排",
    },
    "Java虚拟机 JVM知识点汇总及简述-＞运行时数据区(堆、方法区)篇（总结自尚硅谷JVM课程）": {
        "堆": "JVM/2_运行时数据区",
        "方法区": "JVM/2_运行时数据区",
        "元空间": "JVM/2_运行时数据区",
        "永久代": "JVM/2_运行时数据区",
    },
    "Java虚拟机 JVM知识点汇总及简述-＞运行时数据区(程序计数器、虚拟机栈、本地方法栈)篇（总结自": {
        "程序计数器": "JVM/2_运行时数据区",
        "虚拟机栈": "JVM/2_运行时数据区",
        "本地方法栈": "JVM/2_运行时数据区",
        "栈帧": "JVM/2_运行时数据区",
    },
    "Java虚拟机 JVM知识点汇总及简述-＞再谈类加载器和类加载过程": {
        "双亲委派": "JVM/6_类加载过程详解",
        "ClassLoader": "JVM/6_类加载过程详解",
        "破坏": "JVM/6_类加载过程详解",
        "SPI": "JVM/6_类加载过程详解",
    },
}

# 1:1 mappings (source name prefix -> single target)
SIMPLE_MAP = {
    "Java多并发（三） 线程间的通信（ThreadLoacl详解）": "并发/ThreadLocal与线程通信",
    "Java多并发（四） 锁（Lock接口 & AQS & ReentrantLock）": "并发/Lock与AQS",
    "Java多并发（六） 线程池的基本概述（阻塞队列）": "并发/线程池核心机制",
    "Java多并发（七） Executor框架（四种线程池详解）": "并发/Executor框架",
    "Java虚拟机 JVM最强知识点汇总及简述-＞JVM体系及类加载子系统篇（总结自尚硅谷JVM课程）": "JVM/1_JVM体系与类加载",
    "Java虚拟机 JVM知识点汇总及简述-＞运行时数据区(创建对象内部各种结构的配合、运行时数据区面试": "JVM/3_对象创建与内存布局",
    "Java虚拟机 JVM知识点汇总及简述-＞垃圾回收（一）：垃圾回收算法": "JVM/4_垃圾回收算法",
    "Java虚拟机 JVM知识点汇总及简述-＞垃圾回收（二）：垃圾回收器": "JVM/5_垃圾回收器",
    "Java虚拟机 JVM知识点汇总及简述-＞StringTable篇（总结自尚硅谷JVM课程）": "JVM/7_StringTable与字符串",
    "Java虚拟机 JVM知识点汇总及简述-＞JVM运行时参数及如何分析GC日志": "JVM/8_JVM运行时参数与GC日志",
    "Java虚拟机 JVM知识点汇总及简述-＞性能监控与调优": "JVM/9_性能监控与调优",
    "Java虚拟机 JVM知识点汇总及简述-＞字节码指令集与解析举例": "JVM/10_字节码指令集",
    "Java虚拟机 JVM知识点汇总及简述-＞Class文件结构": "JVM/1_JVM体系与类加载",
    "Spring及Java编码相关": "Spring/Spring事务与失效场景",
    "JDK简要进化史（11~17）": "JDK演进/JDK11-17重要变化",
    "FastJSON与JackJSON": "工具库/JSON序列化对比",
    "EasyExcel": "工具库/常用工具库要点",
    "Hutool等工具类": "工具库/常用工具库要点",
    "Lombok相关": "工具库/Lombok核心注解",
    "javassist相关": "工具库/常用工具库要点",
    "Feign": "工具库/Feign调用要点",
    "URule相关": "工具库/常用工具库要点",
    "NIO优化与Unix-Domain Socket": "Java基础/IO与NIO基础",
    "三种ThreadLocal的详细对比": "并发/ThreadLocal与线程通信",
    "Swagger相关": None,
    # JVM - sources in HEADING_ROUTE_MAP need fallback targets too
    "Java虚拟机 JVM知识点汇总及简述-＞运行时数据区(程序计数器、虚拟机栈、本地方法栈)篇（总结自": "JVM/2_运行时数据区",
    "Java虚拟机 JVM知识点汇总及简述-＞运行时数据区(堆、方法区)篇（总结自尚硅谷JVM课程）": "JVM/2_运行时数据区",
    "Java虚拟机 JVM知识点汇总及简述-＞再谈类加载器和类加载过程": "JVM/6_类加载过程详解",
    # Collections - heading-routed with fallback
    "Java集合相关总结（List Set Map）": "集合/ArrayList、LinkedList与CopyOnWriteArrayList",
    # Spring - heading-routed with fallback
    "Spring源码分析（IOC&AOP） SpringMVC源码分析（DispatcherServle": "Spring/01-Spring-IoC与AOP核心",
    # JDK - heading-routed with fallback
    "JDK简要进化史（8~10）": "JDK演进/JDK8关键特性",
    # Concurrency - heading-routed with fallback
    "Java多并发（一） 并发机制的底层原理（内存模型、重排序）": "并发/Java内存模型与重排序",
    "Java多并发（二） cas & synchronized & volatile的内存语义": "并发/CAS原理",
    "Java多并发（五） JUC包下的并发容器（ConcurrentHashMap）& 并发工具类 &_": "并发/ConcurrentHashMap",
    "深入理解Dubbo与实战（零）": "Dubbo/01-Dubbo架构与核心组件",
    "深入理解Dubbo与实战（一） Dubbo注册中心": "Dubbo/02-Dubbo注册中心",
    "深入理解Dubbo与实战（二） Dubbo扩展点加载机制": "Dubbo/03-Dubbo-SPI扩展机制",
    "深入理解Dubbo与实战（四） Dubbo远程调用": "Dubbo/04-Dubbo远程调用",
    "深入理解Dubbo与实战（五） Dubbo集群容错": "Dubbo/05-Dubbo集群容错与负载均衡",
    "深入理解Dubbo与实战（五·续） Dubbo集群容错——负载均衡": "Dubbo/05-Dubbo集群容错与负载均衡",
    "深入理解Dubbo与实战（三） Dubbo启停原理解析": "Dubbo/06-Dubbo服务暴露与引用",
    "深入理解Dubbo与实战（六） Dubbo扩展点 整体框架的总结": "Dubbo/06-Dubbo服务暴露与引用",
    "深入理解Dubbo与实战（七） Dubbo高级特性": "Dubbo/01-Dubbo架构与核心组件",
    "深入理解Dubbo与实战（八） Dubbo过滤器": "Dubbo/01-Dubbo架构与核心组件",
}


def find_heading_for_line(lines, img_line_idx):
    for i in range(img_line_idx - 1, -1, -1):
        line = lines[i].strip()
        m = re.match(r'^#{1,4}\s+(.+)', line)
        if m:
            return m.group(1).strip()
    return None


def main():
    mappings = []

    # Process SIMPLE_MAP (1:1 or heading-routed)
    for source_prefix, fallback_target in {**SIMPLE_MAP, **{k: None for k in HEADING_ROUTE_MAP if k not in SIMPLE_MAP}}.items():
        if fallback_target is None:
            continue
        # Find matching source dir (directory with images)
        source_dir = None
        for d in JAVA_DIR.iterdir():
            if d.is_dir() and d.name.startswith(source_prefix):
                source_dir = d
                break
        if not source_dir:
            continue

        # Find matching source md file
        md_files = list(JAVA_DIR.glob(f"{source_prefix}*.md"))
        if not md_files:
            continue

        md_file = md_files[0]
        lines = md_file.read_text(encoding='utf-8').split('\n')

        for i, line in enumerate(lines):
            m = re.search(r'!\[.*?\]\((.+)\)', line)
            if not m:
                continue
            img_path = unquote(m.group(1))
            basename = os.path.basename(img_path)

            heading = find_heading_for_line(lines, i)
            route = HEADING_ROUTE_MAP.get(source_prefix, {})
            target = None
            if route and heading:
                for keyword, t in route.items():
                    if keyword.lower() in heading.lower():
                        target = t
                        break
            if not target:
                target = fallback_target
            if target:
                mappings.append((source_dir, basename, target))

    # Print summary
    print(f"Total mappings: {len(mappings)}")
    by_target = defaultdict(list)
    for src_dir, img_name, target in mappings:
        by_target[target].append((src_dir, img_name))

    for target in sorted(by_target.keys()):
        items = by_target[target]
        print(f"\n{target} ({len(items)} images):")
        for src_dir, img_name in items:
            src = src_dir / img_name
            print(f"  {'✓' if src.exists() else '✗'} {img_name} <- {src_dir.name}")

    # Write mapping file
    with open("/tmp/java_image_map.txt", "w") as f:
        for src_dir, img_name, target in mappings:
            f.write(f"{src_dir}|{img_name}|{target}\n")

    print(f"\nMapping written to /tmp/java_image_map.txt")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 ceph-guide/ 下的四份长文 HTML 转换成博客文章页。

用法：
    python tools/build_posts.py

它做的事：
  1. 抽取源文档的 <style>、<nav class="toc"> 与 <main> 内容；
  2. 去掉源文档自带的 hero 横幅（改用博客统一的标题区）；
  3. 套上博客的站点头部 / 面包屑 / 页脚 / 系列导航；
  4. 输出到 posts/ 目录。

源文档样式以 <style> 形式内联注入（排在站点 CSS 之后），
因此文章内的表格、代码、卡片、SVG 配图保持原样，不会被站点样式冲掉。
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "tools", "source")   # 源文档放置目录（可选）
OUT_DIR = os.path.join(ROOT, "posts")

SERIES = [
    ("posts/ceph-principles.html", "① Ceph 原理详解：从寻址到数据均衡"),
    ("posts/ceph-deployment.html", "② Ceph 完整部署手册（手动 + Ansible）"),
    ("posts/ceph-operations.html", "③ Ceph 日常运维实战手册"),
    ("posts/ceph-tuning.html", "④ Ceph 性能瓶颈分析与调优"),
]

DOCS = [
    {
        "src": "Ceph原理详解.html",
        "out": "ceph-principles.html",
        "title": "Ceph 原理详解：从寻址到数据均衡",
        "sub": "五张 Map · CRUSH 寻址 · 强一致写入 · 数据均衡 · BlueStore · EC · 容量规划",
        "tags": ["Ceph", "分布式存储", "原理"],
        "date": "2026-09-14",
        "words": "约 3.2 万字",
    },
    {
        "src": "Ceph完整部署手册.html",
        "out": "ceph-deployment.html",
        "title": "Ceph 完整部署手册（手动 + Ansible）",
        "sub": "硬件与网络规划 · 手动部署七步法 · MDS/RGW/Dashboard · 扩缩容 · ceph-ansible 全量模板",
        "tags": ["Ceph", "部署", "Ansible"],
        "date": "2026-09-14",
        "words": "约 2.4 万字",
    },
    {
        "src": "Ceph日常运维实战手册.html",
        "out": "ceph-operations.html",
        "title": "Ceph 日常运维实战手册",
        "sub": "命令体系 · slow ops 排查 · PG 均衡 · 扩缩容换盘 · 巡检与故障速查",
        "tags": ["Ceph", "运维", "排障"],
        "date": "2026-09-14",
        "words": "约 1.6 万字",
    },
    {
        "src": "Ceph瓶颈分析与性能调优.html",
        "out": "ceph-tuning.html",
        "title": "Ceph 性能瓶颈分析与调优",
        "sub": "六大瓶颈层 · 时延分解 · mclock 隐性天花板 · 四段压测法 · 六套场景配方",
        "tags": ["Ceph", "性能", "调优"],
        "date": "2026-09-14",
        "words": "约 1.5 万字",
    },
]


def find_src(name):
    """在工作区常见位置找源文档。"""
    cands = [
        os.path.join(SRC_DIR, name),
        os.path.join(ROOT, "tools", "source", name),
        os.path.join(os.path.expanduser("~"), "WorkBuddy"),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    # 在工作区里递归找一遍
    base = os.path.join(os.path.expanduser("~"), "WorkBuddy")
    for dirpath, _, files in os.walk(base):
        if name in files:
            return os.path.join(dirpath, name)
    return None


def pick(pattern, text, name):
    m = re.search(pattern, text, re.S)
    if not m:
        sys.exit("  ✗ 无法抽取 %s：%s" % (name, pattern[:40]))
    return m.group(1)


def build(doc):
    path = find_src(doc["src"])
    if not path:
        print("  ! 跳过（未找到源文档）: %s" % doc["src"])
        return False
    src = open(path, encoding="utf-8").read()

    # 清掉编辑器注入的 data-page-node-id 属性（保持输出干净）
    src = re.sub(r'\s+data-page-node-id="[^"]*"', "", src)

    css = pick(r"<style>(.*?)</style>", src, "style")
    toc = pick(r'(<nav class="toc"[^>]*>.*?</nav>)', src, "toc")
    main = pick(r"<main[^>]*>(.*?)</main>", src, "main")

    # 去掉源文档自带的 hero 横幅（用博客统一标题区替代）
    main = re.sub(r'<header class="hero"[^>]*>.*?</header>', "", main, flags=re.S)
    # 去掉源文档页脚（博客已有统一页脚）
    main = re.sub(r'<div class="footer"[^>]*>.*?</div>', "", main, flags=re.S)

    tags_html = "".join('<span>#%s</span>' % t for t in doc["tags"])
    cur = "posts/" + doc["out"]
    series_html = "\n".join(
        '<li class="%s"><a href="../%s">%s</a></li>' % ("cur" if u == cur else "", u, t)
        for u, t in SERIES
    )

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · rensongqi</title>
<meta name="description" content="{sub}">
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="alternate" type="application/rss+xml" title="rensongqi · RSS" href="../feed.xml">
<style>
{css}
</style>
</head>
<body class="doc-page">

<header class="site-head">
  <div class="site-head__in">
    <a class="site-logo" href="../index.html">rensongqi</a>
    <nav class="site-nav">
      <a href="../index.html">首页</a>
      <a href="../archive.html">归档</a>
      <a href="../storage.html" class="is-active">存储</a>
      <a href="../about.html">关于</a>
    </nav>
  </div>
</header>

<div class="doc-crumb"><a href="../index.html">首页</a> / <a href="../storage.html">存储</a> / <span>{title}</span></div>

<div class="doc-title">
  <h1>{title}</h1>
  <div class="meta">{date} · {words} · 更新于 2026-09-14</div>
  <div class="doc-tags">{tags}</div>
</div>

<div class="layout">
{toc}
<main>
<p class="lead">{sub}</p>
{main}
<nav class="doc-series">
  <p class="lb">Ceph 四部曲</p>
  <ol>
{series}
  </ol>
</nav>
</main>
</div>

<footer class="site-foot">
  <div class="site-foot__in">
    <span>&copy; 2026 rensongqi</span>
    <span class="r">
      <a href="../feed.xml">RSS</a>
      <a href="../storage.html">存储专题</a>
      <a href="https://github.com/rensongqi/rensongqi.github.io">源码</a>
    </span>
  </div>
</footer>

<script src="../assets/js/main.js"></script>
</body>
</html>
""".format(
        title=doc["title"], sub=doc["sub"], css=css, toc=toc,
        main=main.strip(), tags=tags_html, series=series_html,
        date=doc["date"], words=doc["words"],
    )

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    out = os.path.join(OUT_DIR, doc["out"])
    open(out, "w", encoding="utf-8").write(page)
    print("  ✓ %-28s %8.0f KB   (源: %s)" % (doc["out"], len(page) / 1024, os.path.basename(path)))
    return True


if __name__ == "__main__":
    print("生成文章页 → posts/")
    ok = 0
    for d in DOCS:
        if build(d):
            ok += 1
    print("完成：%d/%d 篇" % (ok, len(DOCS)))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 posts/ 下长文文章页（ceph-*.html 与 3fs-*.html）的内嵌样式与目录结构，
统一成笔记文章页的风格（以 build_notes.py 生成的页面为基准）。

做法（每页）：
  1. 用「笔记页 CSS + Ceph 内容兼容样式」替换页内第一个 <style>（原页面专属样式）；
  2. 把目录 <nav class="toc"> 的平铺 <a>/<div class="part"> 结构
     转换为笔记页的 <ul><li> 结构（.part → li.part，.sub → li.l3）；
  3. 其余标记（面包屑 / 标题区 / 正文 / 系列导航 / 页脚 / SVG 样式块）原样保留。

用法：
    python tools/build_ceph.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_notes import CSS as NOTES_CSS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRIDGE = """
/* ── Ceph 长文内容兼容（保持笔记页极简风格） ── */
.doc-page main section{margin:36px 0 0;padding:0;background:none;border:0;border-radius:0}
.doc-page main section:first-of-type{margin-top:4px}
.doc-page main h2{border-bottom:1px solid var(--line);padding-bottom:10px;scroll-margin-top:70px}
.doc-page main h2 .num{display:inline-block;min-width:23px;text-align:center;padding:1px 7px;margin-right:9px;background:var(--accent);color:#fff;font-size:13px;line-height:20px;border-radius:6px;vertical-align:2px}
.doc-page main .note,.doc-page main .warn,.doc-page main .good,.doc-page main .tip{border:1px solid var(--line);border-left-width:3px;border-radius:var(--radius);padding:11px 15px;margin:16px 0;font-size:14.5px}
.doc-page main .note{background:#eef7f9;border-left-color:var(--accent)}
.doc-page main .warn{background:#fdf6e3;border-left-color:#b45309}
.doc-page main .good{background:#f0f9f1;border-left-color:#15803d}
.doc-page main .tip{background:#f5f2fc;border-left-color:#6d28d9}
.doc-page main .note b,.doc-page main .warn b,.doc-page main .good b,.doc-page main .tip b{color:inherit}
.doc-page main .grid2,.doc-page main .grid3{display:grid;gap:14px;margin:16px 0}
.doc-page main .grid2{grid-template-columns:1fr 1fr}
.doc-page main .grid3{grid-template-columns:repeat(3,1fr)}
@media (max-width:760px){.doc-page main .grid2,.doc-page main .grid3{grid-template-columns:1fr}}
.doc-page main .card{border:1px solid var(--line);border-radius:var(--radius);padding:12px 15px;background:var(--bg-soft)}
.doc-page main .card h5{margin:0 0 6px;font-size:14.5px}
.doc-page main .card p{margin:0;font-size:13.5px;color:var(--ink-soft)}
.doc-page main .kv{background:var(--bg-soft);border:1px dashed var(--line);border-radius:var(--radius);padding:10px 14px;margin:12px 0;font-size:13.5px}
.doc-page main .q{border:1px solid var(--line);border-radius:var(--radius);padding:12px 16px;margin:12px 0}
.doc-page main .q .qq{font-weight:600;color:var(--accent)}
.doc-page main svg{max-width:100%;height:auto}
.doc-page nav.toc li.part{font-size:11.5px;letter-spacing:.08em;color:var(--accent);font-weight:600;margin:13px 0 3px}
"""

TOC_ITEM_RE = re.compile(
    r'(<a (?:[^>]* )?href="#[^"]*"[^>]*>.*?</a>|<div class="part">.*?</div>)', re.S)


def transform_toc(html_text):
    m = re.search(r'<nav class="toc">(.*?)</nav>', html_text, re.S)
    if not m:
        return html_text
    inner = m.group(1)
    lis = []
    for item in TOC_ITEM_RE.finditer(inner):
        seg = item.group(1)
        if seg.startswith("<a "):
            cls = ' class="l3"' if 'class="sub"' in seg else ""
            lis.append("<li%s>%s</li>" % (cls, seg))
        else:  # part
            label = re.sub(r"</?div[^>]*>", "", seg).strip()
            lis.append('<li class="part">%s</li>' % label)
    new_nav = ('<nav class="toc"><p class="toc-lb">目录</p><ul>\n%s\n</ul></nav>'
               % "\n".join(lis))
    return html_text[:m.start()] + new_nav + html_text[m.end():]


def main():
    pages = sorted(
        os.path.join(ROOT, "posts", f) for f in os.listdir(os.path.join(ROOT, "posts"))
        if re.match(r"(?:ceph|3fs)-.*\.html$", f))
    if not pages:
        sys.exit("posts/ 下没有找到 ceph-/3fs-*.html")
    style = "<style>%s\n%s</style>" % (NOTES_CSS, BRIDGE)
    for path in pages:
        s = open(path, encoding="utf-8").read()
        # 1) 替换第一个 <style>（页面专属样式；第二个 SVG 样式块保留）
        s2, n = re.subn(r"<style>.*?</style>", lambda _: style, s, count=1, flags=re.S)
        # 2) 目录结构转换
        s2 = transform_toc(s2)
        open(path, "w", encoding="utf-8", newline="\n").write(s2)
        print("✓ %s（样式替换 %d 处）" % (os.path.basename(path), n))


if __name__ == "__main__":
    main()

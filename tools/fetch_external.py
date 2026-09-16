#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 notes-src 文章里引用的外链静态资源（图片 / yaml / json）下载到本地，
生成 tools/ext_assets.json 清单，build_notes.py 会把页面中的对应链接
重写为本地文件 —— 解决防盗链（简书/CSDN 图片）与外链失效（OSS yaml）问题。

用法：
    python tools/fetch_external.py           # 增量下载
    python tools/fetch_external.py --force   # 全部重新下载

跳过：github.com 的 blob/tree 页面链接（非文件本身）、需要登录态的域名。
"""

import hashlib
import json
import mimetypes
import os
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "notes-src")
OUT_DIR = os.path.join(ROOT, "assets", "attachments")
MANIFEST = os.path.join(ROOT, "tools", "ext_assets.json")

# 值得本地化的扩展名（图片 + 配置/数据文件）
KEEP_EXT = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
    ".yaml", ".yml", ".json", ".conf", ".cfg", ".txt",
}
# 需要登录态/确认无法下载的域名（直接跳过，保留外链）
BLOCK_HOST = {"internal-api-drive-stream.feishu.cn"}
LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) fetch-external/1.0"}

CT_EXT = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
    "image/gif": ".gif", "image/svg+xml": ".svg",
    "application/json": ".json", "text/yaml": ".yaml",
    "application/x-yaml": ".yaml", "text/plain": ".txt",
}


def want(url):
    if urlparse(url).hostname in BLOCK_HOST:
        return False
    if re.search(r"github\.com/(blob|tree)/", url):
        return False
    path = urlparse(url).path.lower()
    return os.path.splitext(path)[1] in KEEP_EXT


def local_name(url):
    """netloc_path 片段 + 短哈希，保留原始扩展名。"""
    u = urlparse(url)
    base = os.path.basename(u.path) or "download"
    stem, ext = os.path.splitext(base)
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", stem)[:60] or "file"
    h = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
    host = u.hostname.replace(".", "-")[:24]
    return "%s-%s-%s%s" % (stem, host, h, ext.lower())


def main():
    force = "--force" in sys.argv
    manifest = {}
    if os.path.isfile(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))

    urls = []
    for dirpath, _, files in os.walk(SRC_DIR):
        for name in files:
            if not name.endswith(".md"):
                continue
            raw = open(os.path.join(dirpath, name), encoding="utf-8").read()
            urls += LINK_RE.findall(raw)
    urls = sorted({u.rstrip(".,)'\"") for u in urls if want(u)})
    print("发现 %d 个外链资源" % len(urls))

    os.makedirs(OUT_DIR, exist_ok=True)
    ok = skip = fail = 0
    for url in urls:
        rel = "assets/attachments/" + local_name(url)
        dst = os.path.join(OUT_DIR, os.path.basename(rel))
        if not force and os.path.isfile(dst) and manifest.get(url) == rel:
            skip += 1
            continue
        try:
            req = Request(url, headers=UA)
            with urlopen(req, timeout=30) as r:
                data = r.read()
                ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            head = data[:300].lstrip().lower()
            if head.startswith((b"<!doctype html", b"<html")):
                print("  - 返回 HTML（疑似防盗链），放弃: %s" % url)
                fail += 1
                continue
            # 常见类型（aes192 等回应）按内容纠偏扩展名
            ext_here = CT_EXT.get(ctype, os.path.splitext(urlparse(url).path)[1].lower())
            if ext_here not in KEEP_EXT:
                print("  - 类型不符（%s），放弃: %s" % (ctype, url))
                fail += 1
                continue
            if ext_here != os.path.splitext(dst)[1].lower():
                rel = os.path.splitext(rel)[0] + ext_here
                dst = os.path.join(OUT_DIR, os.path.basename(rel))
            open(dst, "wb").write(data)
            manifest[url] = rel
            ok += 1
            print("  ✓ %-90s -> %s (%s)" % (url[:88], os.path.basename(rel), ctype))
        except Exception as e:
            print("  ✗ 下载失败: %s  [%s]" % (url, e))
            fail += 1

    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("完成：下载 %d，跳过（已存在）%d，失败 %d；清单 %d 条" % (ok, skip, fail, len(manifest)))


if __name__ == "__main__":
    main()

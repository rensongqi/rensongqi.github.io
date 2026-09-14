#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站内部链接检查：扫描所有 .html 中的 href/src，
凡站内相对链接（非 http(s)/mailto/#）都解析到本地路径验证存在性。

用法：
    python tools/check_links.py
退出码非 0 表示存在坏链。
"""

import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_SCHEMES = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def main():
    bad = []
    total = 0
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            text = open(path, encoding="utf-8").read()
            for m in re.finditer(r'\b(?:href|src)="([^"]+)"', text):
                url = m.group(1).strip()
                if not url or url.startswith("#") or SKIP_SCHEMES.match(url):
                    continue
                rel = unquote(url.split("#")[0].split("?")[0])
                if not rel:
                    continue
                total += 1
                target = os.path.normpath(os.path.join(dirpath, *rel.split("/")))
                # 目录链接（以 / 结尾）检查 index.html
                if url.endswith("/"):
                    target = os.path.join(target, "index.html")
                if not os.path.exists(target):
                    bad.append("%s:%d  %s" % (
                        os.path.relpath(path, ROOT).replace(os.sep, "/"),
                        text[:m.start()].count("\n") + 1, url))
    if bad:
        print("坏链 %d 条：" % len(bad))
        for b in bad[:60]:
            print("  " + b)
        sys.exit(1)
    print("OK：%d 条内部链接全部有效" % total)


if __name__ == "__main__":
    main()

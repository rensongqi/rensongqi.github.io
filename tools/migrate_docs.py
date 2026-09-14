#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 docs 仓库的内容迁移进博客仓库（一次性 + 可重复执行）。

    python tools/migrate_docs.py [docs 仓库路径]

默认源目录是 ../docs（与博客仓库同级）。

它做的事：
  1. 把六大类目录复制到 notes-src/<类别>/（cicd、dsa、go、interview、llm、ops）；
  2. resources/ 下的图片复制到 assets/images/notes/；
  3. 跳过仓库元文件（.git、LICENSE、.gitignore、根 README.md）；
  4. 跳过私钥等敏感文件（EXCLUDE 列表）；
  5. 文本文件中的敏感 token 替换为占位符（SANITIZE 表）。

重复执行会先清空 notes-src 与 assets/images/notes 再复制，保证两边一致。
"""

import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), "docs")

# docs 目录名 -> 博客分类 slug
CATEGORIES = {
    "cicd": "cicd",
    "data_structure": "dsa",
    "go": "go",
    "interview": "interview",
    "llm": "llm",
    "tools": "ops",
}

# 顶层跳过的文件/目录
SKIP_TOP = {".git", "LICENSE", ".gitignore", "README.md", "resources"}

# 敏感文件（相对 docs 根的路径）：私钥，不进公开博客
EXCLUDE = {
    os.path.join("go", "grpc", "key", "ca.key"),
    os.path.join("go", "grpc", "key", "client.key"),
    os.path.join("go", "grpc", "key", "server.key"),
    os.path.join("tools", "ssl_certs", "ssl_ecdsa_private_key.pem"),
}

# 需要脱敏的字符串（真实 token -> 占位符）
SANITIZE = {
    "88fc5e3f-5db7-4075-9914-8ae27b64fa62": "<your-consul-acl-token>",
}

TEXT_EXT = {
    ".md", ".yml", ".yaml", ".json", ".conf", ".cfg", ".j2", ".go",
    ".py", ".c", ".h", ".sh", ".lua", ".proto", ".txt", ".xml",
    ".mod", ".sum", ".ini", ".tpl", ".toml", ".hosts", "",
}


def is_text(path):
    return os.path.splitext(path)[1].lower() in TEXT_EXT or os.path.basename(path) == "hosts"


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if is_text(src):
        try:
            data = open(src, "r", encoding="utf-8").read()
        except (UnicodeDecodeError, ValueError):
            shutil.copy2(src, dst)
            return False
        hit = False
        for bad, good in SANITIZE.items():
            if bad in data:
                data = data.replace(bad, good)
                hit = True
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
        return hit
    shutil.copy2(src, dst)
    return False


def main():
    if not os.path.isdir(SRC):
        sys.exit("源目录不存在: %s" % SRC)

    notes_src = os.path.join(ROOT, "notes-src")
    img_dst = os.path.join(ROOT, "assets", "images", "notes")
    for d in (notes_src, img_dst):
        if os.path.isdir(d):
            shutil.rmtree(d)

    copied = skipped = sanitized = 0
    for top, slug in CATEGORIES.items():
        base = os.path.join(SRC, top)
        if not os.path.isdir(base):
            print("  ! 类别目录缺失，跳过: %s" % top)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            rel_dir = os.path.relpath(dirpath, base)
            for name in filenames:
                rel_docs = os.path.normpath(os.path.join(top, rel_dir, name))
                if rel_docs in EXCLUDE:
                    skipped += 1
                    print("  - 敏感文件跳过: %s" % rel_docs.replace(os.sep, "/"))
                    continue
                dst = os.path.join(notes_src, slug, rel_dir, name)
                if copy_file(os.path.join(dirpath, name), dst):
                    sanitized += 1
                    print("  ~ 已脱敏: %s" % rel_docs.replace(os.sep, "/"))
                copied += 1

    res = os.path.join(SRC, "resources")
    imgs = 0
    if os.path.isdir(res):
        for name in sorted(os.listdir(res)):
            f = os.path.join(res, name)
            if os.path.isfile(f):
                os.makedirs(img_dst, exist_ok=True)
                shutil.copy2(f, os.path.join(img_dst, name))
                imgs += 1

    print("完成：%d 个文件迁入 notes-src/，%d 张图片 → assets/images/notes/，"
          "%d 个敏感文件跳过，%d 个文件已脱敏" % (copied, imgs, skipped, sanitized))


if __name__ == "__main__":
    main()

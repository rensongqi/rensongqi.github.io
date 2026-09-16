#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 notes-src/ 下的 Markdown 笔记批量转换为博客文章页。

用法：
    python tools/build_notes.py

输入：notes-src/<cat>/**/*.md   （由 tools/migrate_docs.py 生成）
输出：
  posts/<cat>/**.html        笔记文章页（套站点外壳，含目录 / 同分类导航 / 面包屑）
  notes/index.html           笔记总览页（hub）
  notes/<cat>.html           六个分类页
  assets/js/main.js          在 __NOTES_BEGIN__/__NOTES_END__ 标记之间注入文章索引
  feed.xml                   重新生成 RSS（Ceph 长文 + 全部笔记）

链接处理：
  - md 里指向 ../../resources/x.jpg 的图片 → assets/images/notes/x.jpg
  - md 互相引用 [x](y.md) → 对应的 HTML 文章页
  - md 引用的其他本地文件（yaml/go/py 等）→ notes-src/ 下对应文件（可直接查看）
  - 外链原样保留
"""

import datetime
import html
import json
import os
import re
import string
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "notes-src")
IMG_DIR = os.path.join(ROOT, "assets", "images", "notes")
EXT_MANIFEST = os.path.join(ROOT, "tools", "ext_assets.json")
SITE = "https://rensongqi.github.io/"
DATE = "2026-09-16"
DATE_RSS = "Wed, 16 Sep 2026 00:00:00 GMT"

# 外链资源本地化清单（tools/fetch_external.py 生成）：URL -> 仓库内相对路径
EXT_ASSETS = {}
if os.path.isfile(EXT_MANIFEST):
    EXT_ASSETS = json.load(open(EXT_MANIFEST, encoding="utf-8"))


# ── Markdown 源规范化（贴近 GitHub/CommonMark 渲染习惯） ────
LIST_RE = re.compile(r"^([-*+]|\d+[.)])\s+")


def normalize_md(raw):
    """让 Python-Markdown 按 GitHub 的习惯渲染中文笔记：
    - 列表可以打断段落（前面补空行），否则 "- 项目" 会留在段落里变成纯文本；
    - 1~3 空格缩进的子列表统一为 4 空格（Python-Markdown 需要缩进到父级内容宽度），
      否则嵌套层级被拍平；
    - 不动代码围栏内的内容。
    """
    def ltype(s):
        """返回列表标记类型（'o' 有序 / '-' '*' '+'），非列表项返回 None。"""
        mm = LIST_RE.match(s.lstrip())
        return ("o" if re.match(r"^\d", mm.group(1)) else mm.group(1)) if mm else None

    out = []
    fence = False
    prev = ""
    for line in raw.splitlines():
        s = line.strip()
        fm = re.match(r"^(```+|~~~+)(\S.*)$", s)
        # 开围栏上的多词正文（如 ```ansible all -m ping）：合法 info 只能是
        # 单词/属性串（bear="\S+word"$、含 =、{ 起始、引号起始）；否则作者把内容
        # 挤在了开围栏行上，python-markdown 会不识别，导致后续围栏整体错位 ——
        # 拆成「空开围栏 + 内容行」（不影响配对与状态机）
        if fm and not fence:
            rest = fm.group(2)
            if (re.search(r"[ \t]", fm.group(2)) and "=" not in rest
                    and not rest.lstrip().startswith(("{", '"', "'"))):
                line = fm.group(1)
                inline_content = rest
            else:
                inline_content = None
        else:
            inline_content = None
        if re.match(r"^(```|~~~)", s):
            # 围栏打断段落：开围栏前一行非空且不是围栏 → 补空行（GitHub 行为）
            if not fence and prev.strip() and not re.match(r"^(```|~~~)", prev.strip()):
                out.append("")
            fence = not fence
            out.append(line)
            if inline_content is not None:
                out.append(inline_content)
            prev = line
            continue
        if fence:
            out.append(line)
            continue
        # 1~3 空格缩进的列表项 → 4 空格（更深缩进保持不动，视为代码块）
        m4 = re.match(r"^ {1,3}(\S.*)$", line)
        if m4 and LIST_RE.match(m4.group(1)):
            line = "    " + m4.group(1)
        # 列表打断段落：前行非空、前行不是同类列表、前行不是标题/表行
        # （前行允许带 1~3 空格缩进；引用块后的顶格列表同样补空行）
        if (line[0:1] != " " and ltype(line) and prev and prev.strip()
                and ltype(prev) != ltype(line)
                and not prev.lstrip().startswith(("#", "|"))):
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out) + ("\n" if raw.endswith("\n") else "")

# 分类：slug -> (显示名, 简介)
CATS = {
    "go": ("Go 语言", "Go 语言的语法、并发、容器、泛型、gorm 与 gRPC 实践笔记。"),
    "dsa": ("数据结构", "经典数据结构与排序算法的 Go 实现与要点笔记。"),
    "interview": ("面试", "面试高频考点整理：Go 底层、Linux、MySQL、Redis、Docker 与网络。"),
    "cicd": ("CI/CD", "CI/CD 流水线与部署实践：Argo CD、Jenkins Pipeline 与共享库。"),
    "llm": ("LLM", "大模型相关工具的本地部署与使用记录。"),
    "ops": ("运维工具", "工作中沉淀的运维笔记：监控、日志、数据库、K8s、Linux 系统与各类工具的部署排障。"),
}
CAT_ORDER = ["go", "dsa", "interview", "cicd", "llm", "ops"]

# 子目录名显示化别名（用于分组标题与标签）
HUMAN = {
    "argo": "Argo CD", "jenkins": "Jenkins", "pipeline": "Pipeline",
    "array": "数组", "binary_tree": "二叉树", "link_list": "链表", "queue": "队列",
    "sort": "排序", "bit_ops": "位运算", "go": "Go", "grpc": "gRPC",
    "docker": "Docker", "linux": "Linux", "mysql": "MySQL", "network": "网络",
    "redis": "Redis", "ollama": "Ollama",
    "ansible": "Ansible", "automation_jobs": "自动化任务", "api_gateway": "API 网关",
    "canal": "Canal", "consul": "Consul", "database": "数据库", "mongo": "MongoDB",
    "pgsql": "PostgreSQL", "elk": "ELK", "es": "Elasticsearch", "filebeat": "Filebeat",
    "kafka": "Kafka", "logstash": "Logstash", "git": "Git", "gitlab": "GitLab",
    "harbor": "Harbor", "k8s": "Kubernetes", "ld_preload": "LD_PRELOAD",
    "logrotate": "Logrotate", "lsyncd": "Lsyncd", "minio": "MinIO", "nacos": "Nacos",
    "nfpm": "nfpm", "openresty": "OpenResty", "openssl": "OpenSSL", "passbolt": "Passbolt",
    "prometheus": "Prometheus", "node_exporter": "Node Exporter",
    "blackbox_exporter": "Blackbox Exporter", "dcgm_exporter": "DCGM Exporter",
    "elasticsearch_exporter": "Elasticsearch Exporter", "kafka_exporter": "Kafka Exporter",
    "rdma": "RDMA", "seaweedfs": "SeaweedFS", "tikv": "TiKV", "ssl_certs": "SSL 证书",
    "sync_images": "镜像同步", "thanos": "Thanos", "tunasync": "TUNA 镜像同步",
    "vault": "Vault", "vdbench": "Vdbench", "windows": "Windows",
    "check_header": "Check Header", "lua-resty-feishu-auth": "飞书认证 (lua-resty-feishu-auth)",
}

# ── 标题选择 ────────────────────────────────────────────────
# 泛化到不能当文章标题的词（精确匹配，区分大小写不敏感）
GENERIC = {
    "概述", "简介", "介绍", "说明", "前言", "目录", "背景", "总结", "首页",
    "readme", "about", "usage", "install", "installation", "intro",
    "introduction", "overview", "quickstart", "quick start", "getting started",
    "home", "index", "describe", "description", "参考", "参考文章", "references",
    "注意事项", "架构说明", "架构图", "常用命令",
}
# 章节式前缀：「1 xxx」「1.1 xxx」「2、xxx」「一、xxx」「第x种方式：」
NUMBERED_RE = re.compile(r"^(\d+\.?)+[、.．\s]\s*|^[一二三四五六七八九十]+[、.．]\s*|^第[一二三四五六七八九十\d]+[种章节部分]")
# 纯数字 / IP 地址
IP_RE = re.compile(r"^[\d.]+$")
# 明显是小节而不是文档题的后缀
WEAK_END_RE = re.compile(r"(部署|配置|使用|安装|介绍|说明|下载|参考|命令|目录|deploy|usage|install)$", re.I)
# 动词开头且很短的小节名（「制作镜像」类），长描述句（「使用Tikv作为Filer的store」）不受影响
NO_TITLE_START_RE = re.compile(r"^(制作|运行|启动|对接|安装|下载|初始化|部署|配置)")
# 文件名词的缩写还原
UPPER = {
    "tcp": "TCP", "udp": "UDP", "ip": "IP", "http": "HTTP", "https": "HTTPS",
    "ssl": "SSL", "tls": "TLS", "ssh": "SSH", "dns": "DNS", "ldap": "LDAP",
    "ad": "AD", "ca": "CA", "os": "OS", "api": "API", "cli": "CLI", "sdk": "SDK",
    "ci": "CI", "cd": "CD", "ai": "AI", "llm": "LLM", "gorm": "GORM",
    "grpc": "gRPC", "rbac": "RBAC", "gc": "GC", "gmp": "GMP", "ipc": "IPC",
    "lvm": "LVM", "raid": "RAID", "ssd": "SSD", "k8s": "K8s", "elk": "ELK",
    "es": "ES", "mysql": "MySQL", "pgsql": "PostgreSQL", "redis": "Redis",
    "mongo": "MongoDB", "ollama": "Ollama", "apisix": "APISIX", "istio": "Istio",
    "argo": "Argo", "fio": "fio", "jwt": "JWT", "oauth": "OAuth", "sql": "SQL",
    "json": "JSON", "xml": "XML", "yaml": "YAML", "uuid": "UUID", "rdma": "RDMA",
    "openssl": "OpenSSL", "openresty": "OpenResty", "minio": "MinIO",
    "tikv": "TiKV", "seaweedfs": "SeaweedFS", "logstash": "Logstash",
    "gitlab": "GitLab", "kubesphere": "KubeSphere", "golang": "Go",
    "kibana": "Kibana", "nginx": "Nginx", "ubuntu": "Ubuntu",
    "centos": "CentOS", "debian": "Debian", "grafana": "Grafana",
    "harbor": "Harbor", "jenkins": "Jenkins", "nacos": "Nacos",
    "thanos": "Thanos", "vault": "Vault", "consul": "Consul",
    "ansible": "Ansible", "canal": "Canal", "docker": "Docker", "lua": "Lua",
}
CONN = {"by", "and", "or", "of", "the", "in", "on", "to", "for", "with", "vs", "via"}


def headings_of(raw):
    """正文标题（跳过代码围栏）。"""
    hs, fence = [], False
    for line in raw.splitlines():
        s = line.strip()
        if re.match(r"^(```|~~~)", s):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^#{1,3}\s+(.+?)\s*#*\s*$", s)
        if m:
            t = strip_md(m.group(1))
            if t:
                hs.append(t)
    return hs


def norm_key(s):
    return re.sub(r"[\s\-_.:：\d()（）]+", "", s).lower()


def heading_score(h, skip_norms, is_first, is_readme):
    """0=无效 1=弱 2=可当文章标题。纯拉丁标题最多为弱（多为命令/小节名）。"""
    key = norm_key(h)
    if not key or h.lower().strip() in GENERIC:
        return 0
    if key in skip_norms:                       # 与文件名/目录名相同，没有信息量
        return 0
    if NUMBERED_RE.match(h) or IP_RE.match(h):  # 章节号 / 数字 / IP
        return 0
    if NO_TITLE_START_RE.match(h) and len(h) <= 6:  # 短动作短语是小节不是题目
        return 0
    if WEAK_END_RE.search(h):                   # 以「部署/安装/使用…」结尾的多为小节
        return 1
    cjk = len(re.findall(r"[一-鿿]", h))
    if not cjk:
        return 1
    need = 6 if is_readme else (4 if is_first else 6)
    return 2 if cjk >= need else 1


def name_title(stem):
    """文件名 → 标题（缩写还原大小写）。"""
    out = []
    for i, tok in enumerate(re.split(r"[-_\s]+", stem)):
        if not tok:
            continue
        low = tok.lower()
        if low in UPPER:
            out.append(UPPER[low])
        elif i and low in CONN:
            out.append(low)
        else:
            out.append(tok[:1].upper() + tok[1:])
    return " ".join(out) or "笔记"


def pick_title(raw, stem, segs, cat):
    """标题决策：只看首个有效标题，其余按 README=目录主题 / 普通文件=文件名 兜底。"""
    is_readme = stem.lower() == "readme"
    skip = {norm_key(stem)} | {norm_key(s) for s in segs}
    hs = headings_of(raw)
    scores = [heading_score(h, skip, i == 0, is_readme) for i, h in enumerate(hs)]

    first, first_sc = (hs[0], scores[0]) if hs else ("", 0)
    if is_readme:
        # README：首标题足够具体就用，否则以目录主题命名
        if first_sc >= 1 and len(re.findall(r"[一-鿿]", first)) >= 3:
            return first
        if segs and segs[-1] in HUMAN:
            return HUMAN[segs[-1]]
        for h, sc in zip(hs, scores):
            if sc >= 1:
                return h
        return human(segs[-1]) if segs else CATS[cat][0]

    # 普通文件：只有首标题可以覆盖文件名（且要足够具体）
    if first_sc == 2:
        return first
    # 文件名兜底；嵌套目录时补上级主题，除非标题已含该主题词
    t = name_title(stem)
    if segs:
        parent = human(segs[-1])
        pl = re.sub(r"[\s()（）\-_.]+", " ", parent).lower().split()
        tl = t.lower()
        if (not any(w and w in tl for w in pl) and parent not in t
                and segs[-1].lower() not in tl.replace("-", " ")):
            t = "%s · %s" % (parent, t)
    return t


# ── 小工具 ──────────────────────────────────────────────────

def human(seg):
    if seg in HUMAN:
        return HUMAN[seg]
    return re.sub(r"[-_]+", " ", seg).strip().title() or "综合"


def slugify(seg):
    s = seg.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "note"


def read(path):
    return open(path, "r", encoding="utf-8").read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def relposix(target, start):
    return os.path.relpath(target, start).replace(os.sep, "/")


def strip_md(s):
    s = re.sub(r"!\[[^]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*`~#>]", "", s)   # 保留下划线（LD_PRELOAD 等标识符）
    return html.unescape(s).strip()


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def count_words(text):
    cjk = len(re.findall(r"[一-鿿]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", re.sub(r"[一-鿿]", " ", text)))
    n = cjk + latin
    if n >= 10000:
        return "约 %.1f 万字" % (n / 10000.0)
    return "约 %d 字" % max(10, int(round(n / 10.0) * 10))


# ── 收集笔记 ────────────────────────────────────────────────

def collect():
    posts = {}
    for cat in CAT_ORDER:
        base = os.path.join(SRC_DIR, cat)
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            for name in sorted(files):
                if not name.lower().endswith(".md"):
                    continue
                src = os.path.join(dirpath, name)
                rel = os.path.relpath(src, base)                       # 相对分类目录
                parts = [slugify(p) for p in rel[:-3].split(os.sep)]   # 去掉 .md
                if parts[-1] == "readme":
                    parts = parts[:-1] + ["index"]                     # README → index.html
                out_rel = "/".join([cat] + parts) + ".html"            # 相对 posts/
                raw = read(src)
                segs = rel[:-3].split(os.sep)[:-1]                     # 子目录段
                stem = os.path.splitext(name)[0]
                posts[os.path.join(src)] = {
                    "cat": cat,
                    "src": src,
                    "rel": rel.replace(os.sep, "/"),
                    "out": os.path.join(ROOT, "posts", *out_rel.split("/")),
                    "url": "posts/" + out_rel,
                    "title": pick_title(raw, stem, segs, cat),
                    "raw": raw,
                    "group": human(segs[0]) if segs else "综合",
                    "tags": [CATS[cat][0]] + [human(s) for s in segs][:2],
                    "words": count_words(raw),
                }
    return list(posts.values())


# ── 链接 / 图片重写 ─────────────────────────────────────────

def make_rewriter(post, by_src):
    src_dir = os.path.dirname(post["src"])
    out_dir = os.path.dirname(post["out"])

    def to_target(path):
        """把 md 相对路径解析成仓库内绝对路径（不存在则 None）。"""
        p = os.path.normpath(os.path.join(src_dir, *path.split("/")))
        return p if os.path.isfile(p) else None

    def repl(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I) or url.startswith("#"):
            # 外链资源本地化（防盗链 / 外链已失效的静态资源）
            loc = EXT_ASSETS.get(url) or EXT_ASSETS.get(url.split("#")[0])
            if loc:
                return '%s="%s"' % (attr, relposix(os.path.join(ROOT, loc), out_dir))
            return m.group(0)
        path, _, frag = url.partition("#")
        if not path:
            return m.group(0)
        # 指向 resources 图片
        if "resources/" in path.replace("\\", "/"):
            name = os.path.basename(path.split("resources/")[-1])
            target = os.path.join(IMG_DIR, name)
            new = relposix(target, out_dir)
            if os.path.isfile(target):
                return '%s="%s"' % (attr, new)
        target = to_target(path)
        if target is None:
            return m.group(0)  # 文件不存在（如被排除的敏感文件），保留原样
        # md 互链 → 对应文章页
        if path.lower().endswith(".md"):
            hit = by_src.get(os.path.join(target))
            if hit:
                new = relposix(hit["out"], out_dir)
                return '%s="%s%s"' % (attr, new, ("#" + frag) if frag else "")
        # 其他本地文件 → notes-src 下的原件
        return '%s="%s%s"' % (attr, relposix(target, out_dir), ("#" + frag) if frag else "")

    return lambda body: re.sub(r'\b(href|src)="([^"]+)"', repl, body)


# ── HTML 生成 ───────────────────────────────────────────────

CSS = """
.doc-page .layout{display:grid;grid-template-columns:200px minmax(0,760px);gap:48px;max-width:1060px;margin:0 auto;padding:26px 24px 24px}
.doc-page .layout.no-toc{display:block;max-width:808px}
.doc-page nav.toc{position:sticky;top:76px;align-self:start;max-height:calc(100vh - 108px);overflow:auto;padding-left:16px;border-left:1px solid var(--line)}
.doc-page nav.toc .toc-lb{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);margin:0 0 8px}
.doc-page nav.toc ul{list-style:none;margin:0;padding:0}
.doc-page nav.toc li{margin:5px 0;font-size:13.5px;line-height:1.6}
.doc-page nav.toc li.l3{padding-left:14px}
.doc-page nav.toc a{color:var(--ink-soft);border:0;display:block}
.doc-page nav.toc a:hover{color:var(--accent)}
.doc-page main{min-width:0;padding-bottom:8px}
.doc-page main h1{font-size:23px;font-weight:600;margin:36px 0 12px}
.doc-page main h2{font-size:21px;font-weight:600;margin:42px 0 12px;letter-spacing:-.01em}
.doc-page main h3{font-size:17px;font-weight:600;margin:30px 0 8px;color:var(--accent)}
.doc-page main h4{font-size:15.5px;font-weight:600;margin:24px 0 6px}
.doc-page main p{margin:13px 0}
.doc-page main ul,.doc-page main ol{padding-left:22px;margin:12px 0}
.doc-page main li{margin:6px 0}
.doc-page main blockquote{margin:20px 0;padding:2px 0 2px 16px;border-left:2px solid var(--line);color:var(--ink-soft)}
.doc-page main code{font-family:var(--mono);font-size:.88em;background:var(--bg-soft);padding:2px 5px;border-radius:var(--radius);color:#b45309}
.doc-page main pre{background:var(--bg-soft);border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px;overflow-x:auto;font-size:13px;line-height:1.7;margin:16px 0}
.doc-page main pre code{background:none;padding:0;color:var(--ink)}
.doc-page main table{width:100%;border-collapse:collapse;font-size:15px;margin:20px 0}
.doc-page main th,.doc-page main td{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}
.doc-page main th{background:var(--bg-soft);font-weight:600}
.doc-page main img{display:block;max-width:100%;margin:18px auto;border:1px solid var(--line);border-radius:var(--radius)}
.doc-page main hr{margin:36px 0}
.doc-page nav.doc-attach{margin:30px 0 0;padding:14px 18px;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg-soft)}
.doc-page nav.doc-attach .lb{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);margin:0 0 8px}
.doc-page nav.doc-attach ul{list-style:none;margin:0;padding:0}
.doc-page nav.doc-attach li{display:flex;justify-content:space-between;gap:16px;margin:5px 0;font-size:13.5px}
.doc-page nav.doc-attach .dir{color:var(--ink-soft)}
.doc-page nav.doc-attach .sz{color:var(--ink-mute);font-size:12px;white-space:nowrap}
@media (max-width:1020px){
  .doc-page .layout{display:block;max-width:808px}
  .doc-page nav.toc{display:none}
}
"""

NAV = """<header class="site-head">
  <div class="site-head__in">
    <a class="site-logo" href="${prefix}index.html">rensongqi</a>
    <nav class="site-nav">
      <a href="${prefix}index.html">首页</a>
      <a href="${prefix}archive.html"${active_archive}>归档</a>
      <a href="${prefix}storage.html"${active_storage}>存储</a>
      <a href="${prefix_notes_attrib}">${active_notes}笔记</a>
      <a href="${prefix}about.html"${active_about}>关于</a>
    </nav>
  </div>
</header>"""

FOOT = """<footer class="site-foot">
  <div class="site-foot__in">
    <span>&copy; 2026 rensongqi</span>
    <span class="r">
      <a href="${prefix}feed.xml">RSS</a>
      <a href="${prefix}notes/">笔记</a>
      <a href="https://github.com/rensongqi/rensongqi.github.io">源码</a>
    </span>
  </div>
</footer>"""


def nav_html(prefix, active):
    def on(name):
        return ' class="is-active"' if name == active else ""
    return string.Template(NAV).substitute(
        prefix=prefix,
        prefix_notes_attrib=prefix + "notes/",
        active_notes=' class="is-active"' if active == "notes" else "",
        active_archive=on("archive"), active_storage=on("storage"),
        active_about=on("about"),
    ).replace('>${active_notes}笔记<'.replace("${active_notes}",
           ' class="is-active"' if active == "notes" else ""), '>笔记<')


def render_nav(prefix, active):
    # 简化：直接拼
    def on(n):
        return ' class="is-active"' if n == active else ""
    return (
        '<header class="site-head">\n  <div class="site-head__in">\n'
        '    <a class="site-logo" href="%sindex.html">rensongqi</a>\n'
        '    <nav class="site-nav">\n'
        '      <a href="%sindex.html"%s>首页</a>\n'
        '      <a href="%sarchive.html"%s>归档</a>\n'
        '      <a href="%sstorage.html"%s>存储</a>\n'
        '      <a href="%snotes/"%s>笔记</a>\n'
        '      <a href="%sabout.html"%s>关于</a>\n'
        '    </nav>\n  </div>\n</header>'
        % (prefix, prefix, on("home"), prefix, on("archive"),
           prefix, on("storage"), prefix, on("notes"), prefix, on("about"))
    )


def render_foot(prefix):
    return string.Template(FOOT).substitute(prefix=prefix)


def build_toc(md):
    try:
        tokens = md.toc_tokens
    except AttributeError:
        return "", 0
    items = []

    def walk(toks, level):
        for t in toks:
            items.append((min(level, 3), t.get("id", ""), t.get("name", "")))
            walk(t.get("children", []), level + 1)

    walk(tokens, 2)
    items = [(l, i, n) for l, i, n in items if i and n]
    if len(items) < 2:
        return "", 0
    lis = "".join(
        '<li class="l%d"><a href="#%s">%s</a></li>' % (l, i, html.escape(n))
        for l, i, n in items
    )
    return ('<nav class="toc"><p class="toc-lb">目录</p><ul>%s</ul></nav>' % lis), len(items)


def human_size(n):
    if n >= 1024 * 1024:
        return "%.1f MB" % (n / 1024.0 / 1024.0)
    return "%.1f KB" % (n / 1024.0) if n >= 1024 else "%d B" % n


def attachments_html(post, out_dir, by_src):
    """文章同目录的附件（yaml/conf/go/sh 等）与含 README 的子目录，
    以便文章中提到的配置文件可以直接点击查看。"""
    sib_dir = os.path.dirname(post["src"])
    try:
        names = sorted(os.listdir(sib_dir))
    except OSError:
        return ""
    lis = []
    for name in names:
        p = os.path.join(sib_dir, name)
        if os.path.isfile(p):
            if name.lower().endswith(".md"):
                continue  # md 本身就是文章页
            href = relposix(p, out_dir)
            lis.append('<li><a href="%s">%s</a><span class="sz">%s</span></li>'
                       % (html.escape(href), html.escape(name), human_size(os.path.getsize(p))))
        elif os.path.isdir(p) and name != ".git":
            # 子目录：有 README 且已生成文章页 → 链到该文章页
            rd = by_src.get(os.path.join(p, "README.md")) or by_src.get(os.path.join(p, "readme.md"))
            if rd:
                lis.append('<li><a href="%s">%s/</a><span class="sz">子目录</span></li>'
                           % (relposix(rd["out"], out_dir), html.escape(name)))
            else:
                lis.append('<li><span class="dir">%s/</span><span class="sz">子目录</span></li>'
                           % html.escape(name))
    if not lis:
        return ""
    return ('<nav class="doc-attach">\n  <p class="lb">本目录附件</p>\n  <ul>\n%s\n  </ul>\n</nav>'
            % "\n".join("    " + li for li in lis))


def build_post(post, rewrite, related, by_src):
    src = post["src"]
    raw = read(src)
    md = markdown.Markdown(extensions=["pymdownx.superfences", "tables", "toc", "sane_lists"])
    body = md.convert(normalize_md(raw))

    # 去掉与标题重复的第一个 H1
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if m and strip_tags(m.group(1)).replace(" ", "") == post["title"].replace(" ", ""):
        body = body[:m.start()] + body[m.end():]

    body = rewrite(body)
    # 飞书外链图片需要登录态无法公开访问，替换为说明文字（保留上下文段落）
    body = re.sub(
        r"<img [^>]*feishu\.cn[^>]*/?>",
        '<em>（原内嵌流程图为飞书文档图片，因外链失效已移除）</em>',
        body)
    toc, n_head = build_toc(md)

    # 摘要：第一个自然段
    desc = ""
    pm = re.search(r"<p>(.*?)</p>", body, re.S)
    if pm:
        desc = strip_tags(pm.group(1))
        desc = re.sub(r"\s+", " ", desc).strip()[:100]

    out_dir = os.path.dirname(post["out"])
    prefix = relposix(ROOT, out_dir) + "/"
    attach = attachments_html(post, out_dir, by_src)
    tags_html = "".join("<span>#%s</span>" % html.escape(t) for t in dict.fromkeys(post["tags"]))
    rel_html = "\n".join(
        '<li class="%s"><a href="%s">%s</a></li>'
        % ("cur" if r is post else "", relposix(r["out"], out_dir), html.escape(r["title"]))
        for r in related
    )

    page = string.Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title_e · rensongqi</title>
<meta name="description" content="$desc_e">
<link rel="stylesheet" href="${prefix}assets/css/style.css">
<link rel="alternate" type="application/rss+xml" title="rensongqi · RSS" href="${prefix}feed.xml">
<style>$css</style>
</head>
<body class="doc-page">

$nav

<div class="doc-crumb"><a href="${prefix}index.html">首页</a> / <a href="${prefix}notes/">笔记</a> / <a href="${prefix}notes/$cat.html">$label</a> / <span>$title_e</span></div>

<div class="doc-title">
  <h1>$title_e</h1>
  <div class="meta">$date · $words · 源自 notes-src/$cat/$rel</div>
  <div class="doc-tags">$tags</div>
</div>

<div class="layout$toc_cls">
$toc
<main>
$body
$attach
<nav class="doc-series">
  <p class="lb">$label · 同分类笔记</p>
  <ol>
$related
  </ol>
</nav>
</main>
</div>

$foot

<script src="${prefix}assets/js/main.js"></script>
</body>
</html>
""").substitute(
        title_e=html.escape(post["title"]),
        desc_e=html.escape(desc or post["title"]),
        prefix=prefix, css=CSS,
        nav=render_nav(prefix, "notes"),
        cat=post["cat"], label=CATS[post["cat"]][0],
        date=DATE, words=post["words"], rel=post["rel"],
        tags=tags_html,
        toc_cls="" if toc else " no-toc", toc=toc,
        body=body.strip(), attach=attach,
        related=rel_html,
        foot=render_foot(prefix),
    )
    write(post["out"], page)
    post["desc"] = desc or post["title"]


def cat_page(cat, posts):
    label, blurb = CATS[cat]
    prefix = "../"
    groups = {}
    for p in posts:
        groups.setdefault(p["group"], []).append(p)
    blocks = []
    for g in sorted(groups):
        items = sorted(groups[g], key=lambda p: (not p["url"].endswith("/index.html"), p["title"]))
        lis = "".join(
            '<li><time datetime="%s">%s</time><a class="t" href="%s">%s</a>'
            '<a class="tag" href="../archive.html">#%s</a></li>'
            % (DATE, DATE, "../" + p["url"], html.escape(p["title"]), html.escape(label))
            for p in items
        )
        blocks.append(
            '<section class="block">\n'
            '  <div class="block__head"><h2>%s</h2><a class="more">%d 篇</a></div>\n'
            '  <ul class="posts">\n%s\n  </ul>\n</section>' % (html.escape(g), len(items), lis)
        )
    page = string.Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$label · 笔记 · rensongqi</title>
<meta name="description" content="$blurb_e">
<link rel="stylesheet" href="${prefix}assets/css/style.css">
<link rel="alternate" type="application/rss+xml" title="rensongqi · RSS" href="${prefix}feed.xml">
</head>
<body>

$nav

<main class="wrap">

  <section class="hero">
    <h1>$label</h1>
    <p>$blurb_e</p>
    <div class="meta">$n 篇 · 更新于 $date · <a href="../notes/">全部笔记</a></div>
  </section>

$blocks

</main>

$foot

<script src="${prefix}assets/js/main.js"></script>
</body>
</html>
""").substitute(
        label=label, blurb_e=html.escape(blurb), prefix=prefix,
        nav=render_nav(prefix, "notes"), n=len(posts), date=DATE,
        blocks="\n\n".join(blocks), foot=render_foot(prefix),
    )
    write(os.path.join(ROOT, "notes", cat + ".html"), page)


def hub_page(by_cat):
    prefix = "../"
    cards = []
    for cat in CAT_ORDER:
        posts = by_cat.get(cat, [])
        label, blurb = CATS[cat]
        cards.append(
            '<a class="module" href="%s.html">\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '        <span class="n">%d 篇</span>\n'
            '      </a>' % (cat, html.escape(label), html.escape(blurb), len(posts))
        )
    total = sum(len(v) for v in by_cat.values())
    page = string.Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>笔记 · rensongqi</title>
<meta name="description" content="工作笔记总览：Go、数据结构、面试、CI/CD、LLM 与运维工具。">
<link rel="stylesheet" href="${prefix}assets/css/style.css">
<link rel="alternate" type="application/rss+xml" title="rensongqi · RSS" href="${prefix}feed.xml">
</head>
<body>

$nav

<main class="wrap">

  <section class="hero">
    <h1>笔记</h1>
    <p>工作中遇到的问题与知识点沉淀，从原来的 docs 仓库整体搬迁而来，按六个分类组织。精修的长文专题见<a href="../storage.html">存储</a>。</p>
    <div class="meta">共 $total 篇 · 更新于 $date</div>
  </section>

  <section class="block">
    <div class="block__head"><h2>分类</h2></div>
    <div class="modules">
      $cards
    </div>
  </section>

</main>

$foot

<script src="${prefix}assets/js/main.js"></script>
</body>
</html>
""").substitute(
        prefix=prefix, nav=render_nav(prefix, "notes"),
        total=total, date=DATE,
        cards="\n      ".join(cards), foot=render_foot(prefix),
    )
    write(os.path.join(ROOT, "notes", "index.html"), page)


def patch_main_js(posts):
    path = os.path.join(ROOT, "assets", "js", "main.js")
    text = read(path)
    if "/*__NOTES_BEGIN__*/" not in text:
        sys.exit("  ✗ main.js 缺少 __NOTES_BEGIN__ 标记，请先手动加入")
    entries = []
    for p in posts:
        entries.append("  " + json.dumps({
            "title": p["title"], "url": p["url"], "date": DATE,
            "module": CATS[p["cat"]][0],
            "tags": list(dict.fromkeys(p["tags"])),
            "words": p["words"], "desc": p["desc"],
        }, ensure_ascii=False))
    block = "\n" + ",\n".join(entries) + ",\n"
    text = re.sub(
        r"/\*__NOTES_BEGIN__\*/.*?/\*__NOTES_END__\*/",
        "/*__NOTES_BEGIN__*/%s\n  /*__NOTES_END__*/" % block.rstrip("\n"),
        text, flags=re.S,
    )
    write(path, text)


def write_feed(posts):
    items = []
    head = read(os.path.join(ROOT, "feed.xml"))
    for m in re.finditer(r"    <item>.*?</item>\n", head, re.S):
        items.append(m.group(0))  # 保留 Ceph 长文的既有条目
    for p in posts:
        items.append("""    <item>
      <title>%s</title>
      <link>%s%s</link>
      <guid isPermaLink="true">%s%s</guid>
      <pubDate>%s</pubDate>
      <description>%s</description>
      <category>%s</category>
    </item>
""" % (html.escape(p["title"]), SITE, p["url"], SITE, p["url"],
            DATE_RSS, html.escape(p["desc"]), html.escape(CATS[p["cat"]][0])))
    feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>rensongqi · 个人笔记</title>
    <link>%s</link>
    <description>个人技术笔记 —— 分布式存储、后端工程与实践记录。</description>
    <language>zh-CN</language>
    <lastBuildDate>%s</lastBuildDate>
    <atom:link href="%sfeed.xml" rel="self" type="application/rss+xml"/>

%s
  </channel>
</rss>
""" % (SITE, DATE_RSS, SITE, "\n".join(items))
    write(os.path.join(ROOT, "feed.xml"), feed)


def main():
    posts = collect()
    if not posts:
        sys.exit("notes-src/ 下没有找到 md 文件，请先运行 tools/migrate_docs.py")

    by_src = {p["src"]: p for p in posts}
    by_cat = {}
    for p in posts:
        by_cat.setdefault(p["cat"], []).append(p)

    for cat_posts in by_cat.values():
        cat_posts.sort(key=lambda p: (not p["url"].endswith("/index.html"), p["url"]))
        related = []
        for p in cat_posts:
            for r in cat_posts:
                if r is not p and len([x for x in related if True]) < 0:
                    pass
        # 同分类导航：README 在前，按路径排序，最多 12 条
        for p in cat_posts:
            rel = [r for r in cat_posts if r is not p][:11]
            rel.append(p)
            rel = [r for r in cat_posts if r in rel]  # 保持全局顺序
            rewrite = make_rewriter(p, by_src)
            build_post(p, rewrite, rel, by_src)
        cat_page(cat_posts[0]["cat"], cat_posts)

    hub_page(by_cat)
    ordered = [p for c in CAT_ORDER for p in by_cat.get(c, [])]
    patch_main_js(ordered)
    write_feed(ordered)
    print("完成：%d 篇笔记 → posts/，%d 个分类页 + 笔记 hub → notes/，索引与 feed.xml 已更新"
          % (len(posts), len(by_cat)))


if __name__ == "__main__":
    main()

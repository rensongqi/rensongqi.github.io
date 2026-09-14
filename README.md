# rensongqi.github.io

个人技术博客。纯静态站点，无构建、无框架、无追踪。

<https://rensongqi.github.io>

## 风格

极简：系统字体、大留白、发丝线、单一强调色（`#0e7490`），正文宽度 720px。文章配图全部为内联 SVG。

## 目录结构

```
.
├── index.html              首页
├── archive.html            归档（含关键词搜索）
├── storage.html            专题：存储
├── about.html              关于
├── 404.html
├── feed.xml                RSS
├── posts/                  文章
│   ├── ceph-principles.html    ① Ceph 原理详解
│   ├── ceph-deployment.html    ② Ceph 部署手册
│   ├── ceph-operations.html    ③ Ceph 运维手册
│   └── ceph-tuning.html        ④ Ceph 性能调优
├── assets/
│   ├── css/style.css       全站样式
│   └── js/main.js          文章索引 + 搜索 + 阅读进度
├── tools/
│   ├── build_posts.py      把长文转换成文章页的脚本
│   └── source/             长文原始稿
└── .nojekyll               跳过 Jekyll，直接托管静态文件
```

## 本地预览

```bash
python -m http.server 8000
# 打开 http://localhost:8000
```

## 新增一篇文章

1. 写好 HTML（或把长文原稿放进 `tools/source/`，在 `tools/build_posts.py` 的 `DOCS` 里加一条，然后 `python tools/build_posts.py`）；
2. 在 `assets/js/main.js` 顶部的 `window.POSTS` 数组里加一条（标题、URL、日期、模块、标签、字数、摘要）——首页、归档、搜索都从这里读；
3. 在 `feed.xml` 里加一个 `<item>`；
4. 属于"存储"专题的话，在 `storage.html` 里补上条目。

普通文章页模板（最简）：

```html
<body>
<header class="site-head">…</header>
<main class="wrap"><article class="prose">
  <h1>标题</h1>
  <p class="post-meta">2026-09-14 · 阅读约 5 分钟</p>
  正文…
</article></main>
<footer class="site-foot">…</footer>
<script src="assets/js/main.js"></script>
</body>
```

## 发布

站点根目录即 `main` 分支，推送后 GitHub Pages 自动生效：

```bash
git add .
git commit -m "add: ceph storage series"
git push origin main
```

首次使用需在仓库 Settings → Pages 确认 Source 为 `Deploy from a branch` / `main` / `/ (root)`。

## 许可

文章与插图 © rensongqi，转载请注明出处。

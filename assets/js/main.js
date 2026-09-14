/* 文章索引 —— 搜索、归档、RSS 都从这个数组生成。新增文章只需在这里加一条。 */
window.POSTS = [
  {
    title: "Ceph 原理详解：从寻址到数据均衡",
    url: "posts/ceph-principles.html",
    date: "2026-09-14",
    module: "存储",
    tags: ["Ceph", "分布式存储", "原理"],
    words: "约 3.2 万字",
    desc: "17 章 12 图，讲透 Ceph 的分布式原理：五张 Map、File→Object→PG→OSD 寻址三部曲、CRUSH 与 straw2、强一致写入、Recovery 与 Backfill、数据均衡原理、BlueStore、EC 与容量规划。"
  },
  {
    title: "Ceph 完整部署手册（手动 + Ansible）",
    url: "posts/ceph-deployment.html",
    date: "2026-09-14",
    module: "存储",
    tags: ["Ceph", "部署", "Ansible"],
    words: "约 2.4 万字",
    desc: "21 章 4 图：硬件与网络规划、系统初始化、db/wal 磁盘布局、手动部署七步法、MDS/CephFS/RGW/Dashboard、扩容换盘缩容，以及 ceph-ansible 全量变量模板与运维 playbook。"
  },
  {
    title: "Ceph 日常运维实战手册",
    url: "posts/ceph-operations.html",
    date: "2026-09-14",
    module: "存储",
    tags: ["Ceph", "运维", "排障"],
    words: "约 1.6 万字",
    desc: "命令体系与命名规律、ceph -s 逐行解读、slow ops 五层定位法与六个真实案例、PG 均衡实战、扩容缩容换盘、日周月巡检表与一键巡检脚本、24 条故障速查。"
  },
  {
    title: "Ceph 性能瓶颈分析与调优",
    url: "posts/ceph-tuning.html",
    date: "2026-09-14",
    module: "存储",
    tags: ["Ceph", "性能", "调优"],
    words: "约 1.5 万字",
    desc: "六大瓶颈层剖析、3 副本随机写时延分解、写放大链条、网络与 CPU 定量规划、mclock 隐性 IOPS 天花板、四段压测定位法、六层参数表与六套场景化配方。"
  }
];

/* ── 搜索（归档页）───────────────────────────── */
(function () {
  var input = document.getElementById("q");
  var list = document.getElementById("list");
  if (!input || !list) return;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function render(items) {
    if (!items.length) {
      list.innerHTML = '<li><span class="t">没有匹配的文章</span></li>';
      return;
    }
    list.innerHTML = items.map(function (p) {
      return '<li><time datetime="' + p.date + '">' + p.date + "</time>" +
        '<a class="t" href="' + p.url + '">' + esc(p.title) + "</a>" +
        '<a class="tag" href="storage.html">#' + esc(p.module) + "</a></li>";
    }).join("");
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (!q) return render(window.POSTS.slice());
    render(window.POSTS.filter(function (p) {
      return (p.title + " " + p.desc + " " + p.tags.join(" ") + " " + p.module)
        .toLowerCase().indexOf(q) > -1;
    }));
  }

  input.addEventListener("input", run);
  render(window.POSTS.slice());

  var hint = document.getElementById("hint");
  if (hint) hint.textContent = "共 " + window.POSTS.length + " 篇";
})();

/* ── 阅读进度 + 返回顶部 ─────────────────────── */
(function () {
  var bar = document.createElement("div");
  bar.className = "progress";
  document.body.appendChild(bar);

  var top = document.createElement("button");
  top.className = "to-top";
  top.setAttribute("aria-label", "返回顶部");
  top.innerHTML = "&#8593;";
  document.body.appendChild(top);

  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var pct = max > 0 ? (h.scrollTop || document.body.scrollTop) / max * 100 : 0;
    bar.style.width = pct + "%";
    if (h.scrollTop > 400) top.classList.add("show");
    else top.classList.remove("show");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  top.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  onScroll();
})();

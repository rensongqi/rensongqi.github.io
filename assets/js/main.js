/* 文章索引 —— 搜索、归档、RSS 都从这个数组生成。
   前 4 篇 Ceph 长文手工维护；其余笔记由 tools/build_notes.py 自动生成，
   位于 __NOTES_BEGIN__ / __NOTES_END__ 标记之间，请勿手改。 */

/* 分类名 → 分类页地址（归档/搜索结果的 tag 链接用） */
window.MODULE_URL = {
  "存储": "storage.html",
  "Go 语言": "notes/go.html",
  "数据结构": "notes/dsa.html",
  "面试": "notes/interview.html",
  "CI/CD": "notes/cicd.html",
  "LLM": "notes/llm.html",
  "运维工具": "notes/ops.html"
};

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
  },
  {
    title: "3FS 性能排查实战：一次 C-state 引发的全员减速",
    url: "posts/3fs-troubleshooting.html",
    date: "2026-09-17",
    module: "存储",
    tags: ["3FS", "RDMA", "性能", "排障"],
    words: "约 1.1 万字",
    desc: "GPU 集群 3FS 读写延迟批量升高：fio 量化、ping/RDMA 分层定位、十二项配置逐项排除、火焰图与 perf top 锁定 CPU 侧，根因为 C1/C2 C-state 未禁用（每次中断多付 170μs 唤醒费），含修复持久化与速查清单。"
  },
  /*__NOTES_BEGIN__*/
  {"title": "gRPC", "url": "posts/go/grpc/index.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言", "gRPC"], "words": "约 1190 字", "desc": "下边创建一个简单的server端和client端，实现两者之间的交互"},
  {"title": "Go 语言", "url": "posts/go/index.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 40 字", "desc": "主要记录了go语言中底层的一些知识，包括内存管理、逃逸分析、垃圾回收和一些常见包的使用及分析"},
  {"title": "Channel", "url": "posts/go/channel.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 250 字", "desc": "Channel"},
  {"title": "Container List", "url": "posts/go/container-list.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 920 字", "desc": "container/list是一个双向链表。该结构具有链表的所有功能。"},
  {"title": "Generics", "url": "posts/go/generics.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 410 字", "desc": "go泛型示例"},
  {"title": "GORM", "url": "posts/go/gorm.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 580 字", "desc": "二者区别在于谁主谁从 下述代码中user表是源，company关联源中的字段名，简而言之通过先查user-->commpany 最终的主表记录从user出发"},
  {"title": "Sync", "url": "posts/go/sync.html", "date": "2026-09-16", "module": "Go 语言", "tags": ["Go 语言"], "words": "约 800 字", "desc": "经常会看到以下了代码："},
  {"title": "数组", "url": "posts/dsa/array/index.html", "date": "2026-09-16", "module": "数据结构", "tags": ["数据结构", "数组"], "words": "约 100 字", "desc": "当一个数组中的大部分元素为[0]，或者其它相同的值时，可以使用稀疏数组来保存该数组"},
  {"title": "二叉树", "url": "posts/dsa/binary-tree/index.html", "date": "2026-09-16", "module": "数据结构", "tags": ["数据结构", "二叉树"], "words": "约 1770 字", "desc": "在数据结构中，树的定义如下："},
  {"title": "链表", "url": "posts/dsa/link-list/index.html", "date": "2026-09-16", "module": "数据结构", "tags": ["数据结构", "链表"], "words": "约 660 字", "desc": "为了比较好的对单链表进行增删改查的操作，要给单链表设置一个空的头结点，主要用来标识链表头，这个节点本身不存放数据。"},
  {"title": "队列", "url": "posts/dsa/queue/index.html", "date": "2026-09-16", "module": "数据结构", "tags": ["数据结构", "队列"], "words": "约 130 字", "desc": "（1）队列本身是有序列表，使用数组来存储队列的数据，则应声明maxSize表示队列的最大容量 （2）因为队列的输出、输入是分别从前后端来处理，因此需要两个变量front和rear分别标记队列前后端的下"},
  {"title": "排序", "url": "posts/dsa/sort/index.html", "date": "2026-09-16", "module": "数据结构", "tags": ["数据结构", "排序"], "words": "约 2310 字", "desc": "排序是将一组数据，依照指定的顺序进行排列的过程，常见的排序有如下几种"},
  {"title": "Golang面试题", "url": "posts/interview/go/index.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 6140 字", "desc": "1、golang 中 make 和 new 的区别？"},
  {"title": "面试", "url": "posts/interview/index.html", "date": "2026-09-16", "module": "面试", "tags": ["面试"], "words": "约 20 字", "desc": "记录一些在面试中可能会被问到的一些面试题"},
  {"title": "遇到过比较深刻的问题记录", "url": "posts/interview/linux/index.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Linux"], "words": "约 1410 字", "desc": "Centos dmz网络问题"},
  {"title": "MySQL", "url": "posts/interview/mysql/index.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "MySQL"], "words": "约 3280 字", "desc": "MySQL 常见面试题"},
  {"title": "一致性Hash", "url": "posts/interview/redis/index.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Redis"], "words": "约 1170 字", "desc": "以Redis集群为例，集群中有三台节点，我们的数据以hash格式存储，当client访问某一个数据的时候，集群会随机调度一个集群节点响应client，这里就牵扯到一致性hash算法。"},
  {"title": "Docker Shim", "url": "posts/interview/docker/docker-shim.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Docker"], "words": "约 490 字", "desc": "Docker Shim"},
  {"title": "Go · Coding", "url": "posts/interview/go/coding.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 200 字", "desc": "Go · Coding"},
  {"title": "Go · Escape Analysis", "url": "posts/interview/go/escape-analysis.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 610 字", "desc": "golang逃逸分析技术本质上就是在堆和栈区中做选择。编辑器会追踪变量在代码块上的作用域，变量会携带有一组校验数据，用来证明它的整个生命周期是否在运行时完全可知。如果变量通过了这些校验，那么它就可以在"},
  {"title": "Go · GC", "url": "posts/interview/go/gc.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 2600 字", "desc": "编写 Go 代码不需要像写 C/C++ 那样手动的 malloc和 free内存，因为 malloc 操作由 Go 编译器的逃逸分析机制帮我们加上了，而 free 动作则是有 GC 机制来完成。"},
  {"title": "Goroutine Safety", "url": "posts/interview/go/goroutine-safety.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 210 字", "desc": "对slice加锁，进行保护"},
  {"title": "依赖注入", "url": "posts/interview/go/injection.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 540 字", "desc": "Golang 依赖注入（Dependency Injection, DI）是一种设计模式，它用于将依赖关系（即一个组件需要的外部对象）从组件内部的创建过程剥离出来，而是在外部构造并传递给该组件。这种方"},
  {"title": "Go · Memory Management", "url": "posts/interview/go/memory-management.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Go"], "words": "约 1640 字", "desc": "malloc：内存分配（memory allocation）"},
  {"title": "进程间通信", "url": "posts/interview/linux/ipc.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Linux"], "words": "约 2330 字", "desc": "汇总一下关于进程间通信（IPC）的知识。"},
  {"title": "Linux 处理僵尸进程", "url": "posts/interview/linux/zombie.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "Linux"], "words": "约 1610 字", "desc": "僵尸进程： 一个子进程在其父进程没有调用wait()或waitpid()的情况下退出。这个子进程就是僵尸进程。如果其父进程还存在而一直不调用wait，则该僵尸进程将无法回收，等到其父进程退出后该进程将"},
  {"title": "网络 · TCP IP UDP", "url": "posts/interview/network/tcp-ip-udp.html", "date": "2026-09-16", "module": "面试", "tags": ["面试", "网络"], "words": "约 220 字", "desc": "（1）tcp面向字节流，有连接，有三次握手和四次断开，且支持双向数据传输（全双工） （2）tcp有流量控制、滑动窗口、拥塞控制（慢开始，拥塞避免，快重传，快恢复。发送方维持一个拥塞窗口，大小取决于网络"},
  {"title": "Argo CD", "url": "posts/cicd/argo/index.html", "date": "2026-09-16", "module": "CI/CD", "tags": ["CI/CD", "Argo CD"], "words": "约 1220 字", "desc": "获取token"},
  {"title": "Jenkins", "url": "posts/cicd/jenkins/index.html", "date": "2026-09-16", "module": "CI/CD", "tags": ["CI/CD", "Jenkins"], "words": "约 190 字", "desc": "修改插件下载为清华源"},
  {"title": "Pipeline Usages", "url": "posts/cicd/jenkins/pipeline/pipeline-usages.html", "date": "2026-09-16", "module": "CI/CD", "tags": ["CI/CD", "Jenkins", "Pipeline"], "words": "约 900 字", "desc": "用if也可以实现条件判断"},
  {"title": "Pipeline · Share Library", "url": "posts/cicd/jenkins/pipeline/share-library.html", "date": "2026-09-16", "module": "CI/CD", "tags": ["CI/CD", "Jenkins", "Pipeline"], "words": "约 470 字", "desc": "一个仓库放pipeline，另一个仓库放代码库"},
  {"title": "通过Ollama管理本地大模型", "url": "posts/llm/ollama/index.html", "date": "2026-09-16", "module": "LLM", "tags": ["LLM", "Ollama"], "words": "约 200 字", "desc": "运行ollama"},
  {"title": "自动化任务", "url": "posts/ops/ansible/automation-jobs/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Ansible", "自动化任务"], "words": "约 120 字", "desc": "Ansible 自动化任务"},
  {"title": "Canal", "url": "posts/ops/canal/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Canal"], "words": "约 640 字", "desc": "基于Canal实现mysql到mysql之间的数据实时备份"},
  {"title": "Consul", "url": "posts/ops/consul/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Consul"], "words": "约 70 字", "desc": "注意需要使用到 ibm-spectrum-scale-csi-lt csi, 先确保该csi已安装,如未安装请使用其它存储"},
  {"title": "MongoDB", "url": "posts/ops/database/mongo/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "MongoDB"], "words": "约 760 字", "desc": "mongodb-rs.yaml"},
  {"title": "MySQL", "url": "posts/ops/database/mysql/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "MySQL"], "words": "约 2790 字", "desc": "初始化"},
  {"title": "PostgreSQL", "url": "posts/ops/database/pgsql/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "PostgreSQL"], "words": "约 450 字", "desc": "修改standby.signal"},
  {"title": "Redis", "url": "posts/ops/database/redis/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "Redis"], "words": "约 670 字", "desc": "初始化"},
  {"title": "三节点ES集群(带密码校验)", "url": "posts/ops/elk/es/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Elasticsearch"], "words": "约 1070 字", "desc": "先部署一个不开启安全验证的容器"},
  {"title": "ELK", "url": "posts/ops/elk/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK"], "words": "约 1090 字", "desc": "ELK"},
  {"title": "Kafka", "url": "posts/ops/elk/kafka/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Kafka"], "words": "约 220 字", "desc": "需要注意的是，基于Kraft的Kafka创建进入容器之后不能像使用zookeeper那样创建topic，具体原因可参考文章：https://github.com/wurstmeister/kafka-"},
  {"title": "修改logstash配置", "url": "posts/ops/elk/logstash/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Logstash"], "words": "约 400 字", "desc": "修改启动内存参数"},
  {"title": "Git", "url": "posts/ops/git/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Git"], "words": "约 960 字", "desc": "这种是本地有新的修改，解决办法就是提交修改或者删除文件 若是清理可按照如下操作"},
  {"title": "GitLab", "url": "posts/ops/gitlab/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "GitLab"], "words": "约 360 字", "desc": "500人以内 4c8g"},
  {"title": "Harbor", "url": "posts/ops/harbor/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Harbor"], "words": "约 140 字", "desc": "Harbor"},
  {"title": "基于LD_PRELOAD的读文件拦截", "url": "posts/ops/ld-preload/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "LD_PRELOAD"], "words": "约 720 字", "desc": "基于LD_PRELOAD实现在用户态拦截应用程序的读请求，从文件的属性中获取该文件所在目标s3等位置信息，从s3获取数据信息，并返回给客户端程序"},
  {"title": "压缩nginx日志", "url": "posts/ops/logrotate/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Logrotate"], "words": "约 70 字", "desc": "通配匹配子目录"},
  {"title": "Lsyncd", "url": "posts/ops/lsyncd/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Lsyncd"], "words": "约 60 字", "desc": "Lsyncd"},
  {"title": "MinIO", "url": "posts/ops/minio/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "MinIO"], "words": "约 480 字", "desc": "mc下载"},
  {"title": "Nacos", "url": "posts/ops/nacos/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Nacos"], "words": "约 740 字", "desc": "/data/nacos/env"},
  {"title": "nfpm是一款构建deb或rpm安装包工具", "url": "posts/ops/nfpm/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "nfpm"], "words": "约 300 字", "desc": "官方文档: https://nfpm.goreleaser.com/usage/"},
  {"title": "OpenResty", "url": "posts/ops/openresty/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "OpenResty"], "words": "约 3070 字", "desc": "layer7.conf"},
  {"title": "Check Header", "url": "posts/ops/openresty/lua/check-header/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "OpenResty", "Lua"], "words": "约 60 字", "desc": "对Basic auth的用户和密码进行校验"},
  {"title": "飞书认证 (lua-resty-feishu-auth)", "url": "posts/ops/openresty/lua/lua-resty-feishu-auth/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "OpenResty", "Lua"], "words": "约 660 字", "desc": "适用于 OpenResty / ngx_lua 的基于飞书组织架构的登录认证"},
  {"title": "密码管理工具", "url": "posts/ops/passbolt/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Passbolt"], "words": "约 60 字", "desc": "推荐本地安装"},
  {"title": "Blackbox Exporter", "url": "posts/ops/prometheus/blackbox-exporter/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus", "Blackbox Exporter"], "words": "约 120 字", "desc": "docker-compose.yml"},
  {"title": "DCGM Exporter", "url": "posts/ops/prometheus/dcgm-exporter/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus", "DCGM Exporter"], "words": "约 300 字", "desc": "DCGM Exporter"},
  {"title": "Elasticsearch Exporter", "url": "posts/ops/prometheus/elasticsearch-exporter/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus", "Elasticsearch Exporter"], "words": "约 80 字", "desc": "docker-compose.yml"},
  {"title": "基于Prometheus的监控流程", "url": "posts/ops/prometheus/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus"], "words": "约 600 字", "desc": "目前市面上有很多exporter（包括node-exporter、dcgm_exporter、infiniband_exporter、mysql_exporter、等等），这些exporter一般都是"},
  {"title": "Kafka Exporter", "url": "posts/ops/prometheus/kafka-exporter/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus", "Kafka Exporter"], "words": "约 50 字", "desc": "docker-compose.yml"},
  {"title": "Node Exporter", "url": "posts/ops/prometheus/node-exporter/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Prometheus", "Node Exporter"], "words": "约 110 字", "desc": "https://github.com/prometheus/node_exporter/blob/master/collector/infiniband_linux.go#L73"},
  {"title": "RDMA", "url": "posts/ops/rdma/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "RDMA"], "words": "约 930 字", "desc": "Installation dependency"},
  {"title": "SeaweedFS", "url": "posts/ops/seaweedfs/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SeaweedFS"], "words": "约 1010 字", "desc": "计算需要创建多少volume，有两种方式，一种是自动分配卷数量，另一种是手动分配。"},
  {"title": "使用Tikv作为Filer 的store", "url": "posts/ops/seaweedfs/tikv/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SeaweedFS", "TiKV"], "words": "约 1130 字", "desc": "由于redis内存型数据库，随着数据量的增长占用内存也越多，需要另一种kv数据库来支持"},
  {"title": "请求公网证书", "url": "posts/ops/ssl-certs/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SSL 证书"], "words": "约 30 字", "desc": "可以使用acme.sh脚本或lego sdk来请求生成公网证书"},
  {"title": "镜像同步", "url": "posts/ops/sync-images/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "镜像同步"], "words": "约 320 字", "desc": "自动同步公网docker镜像，包含gcr.io、quay.io、docker.io、registry.k8s.io镜像至内网gitlab镜像仓库"},
  {"title": "Thanos", "url": "posts/ops/thanos/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Thanos"], "words": "约 2980 字", "desc": "Thanos架构图："},
  {"title": "TUNA 镜像同步", "url": "posts/ops/tunasync/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "TUNA 镜像同步"], "words": "约 70 字", "desc": "TUNA 镜像同步"},
  {"title": "Vault", "url": "posts/ops/vault/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Vault"], "words": "约 430 字", "desc": "参考文章： vault-in-kubernetes"},
  {"title": "Vdbench", "url": "posts/ops/vdbench/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Vdbench"], "words": "约 1910 字", "desc": "vdbench是一个I/O工作负载生成器，通常用于验证数据完整性和度量直接附加（或网络连接）存储性能。它可以运行在windows、linux环境，可用于测试文件系统或块设备基准性能。"},
  {"title": "Windows", "url": "posts/ops/windows/index.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Windows"], "words": "约 1000 字", "desc": "xcopy"},
  {"title": "Ansible", "url": "posts/ops/ansible/ansible.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Ansible"], "words": "约 3000 字", "desc": "Ansible是一种IT自动化工具。它可以配置系统，部署软件以及协调更高级的IT任务，例如持续部署，滚动更新。Ansible适用于管理企业IT基础设施，从具有少数主机的小规模到数千个实例的企业环境。A"},
  {"title": "API Gateway Compare", "url": "posts/ops/api-gateway/api-gateway-compare.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "API 网关"], "words": "约 610 字", "desc": "API网关作为流量的入口，统一处理来自客户端（用户端）的请求，让请求更加快速、准确和安全的得到处理。"},
  {"title": "APISIX", "url": "posts/ops/api-gateway/apisix.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "API 网关"], "words": "约 1080 字", "desc": "Centos7 安装APISIX"},
  {"title": "MongoDB · Manage", "url": "posts/ops/database/mongo/manage.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "MongoDB"], "words": "约 1130 字", "desc": "所有数据库角色： readAnyDatabase、readWriteAnyDatabase、userAdminAnyDatabase、 dbAdminAnyDatabase"},
  {"title": "MySQL · Master Slave", "url": "posts/ops/database/mysql/master-slave.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "MySQL"], "words": "约 450 字", "desc": "进入master容器，查看 file 和 pos 数据"},
  {"title": "mysqldump备份及还原", "url": "posts/ops/database/mysql/mysqldump.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "数据库", "MySQL"], "words": "约 200 字", "desc": "锁表导出指定库"},
  {"title": "Index相关操作", "url": "posts/ops/elk/es/api.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Elasticsearch"], "words": "约 670 字", "desc": "使用 Index Template 设定默认分片数"},
  {"title": "elasticsearch冷热数据分离", "url": "posts/ops/elk/es/hot-warm.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Elasticsearch"], "words": "约 1630 字", "desc": "三个节点均需要执行"},
  {"title": "Elasticsearch · Optimization", "url": "posts/ops/elk/es/optimization.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Elasticsearch"], "words": "约 2370 字", "desc": "1 集群规划优化实践"},
  {"title": "Kafka · Deploy", "url": "posts/ops/elk/kafka/deploy.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "ELK", "Kafka"], "words": "约 1740 字", "desc": "监控："},
  {"title": "Access K8s API by Curl", "url": "posts/ops/k8s/access-k8s-api-by-curl.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Kubernetes"], "words": "约 220 字", "desc": "devops_admin_token.yaml"},
  {"title": "Kubernetes · Client Go Usage", "url": "posts/ops/k8s/client-go-usage.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Kubernetes"], "words": "约 960 字", "desc": "client-go是一个调用kubernetes集群资源对象API的客户端，即通过client-go实现对kubernetes集群中资源对象（包括deployment、service、ingress、"},
  {"title": "K8s RBAC Usage", "url": "posts/ops/k8s/k8s-rbac-usage.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Kubernetes"], "words": "约 2520 字", "desc": "RBAC(Role-Based Access Control) 基于角色的访问控制，顾名思义就是通过给角色赋予相应的权限，从而使得该角色具有访问相关资源的权限，而在K8s中这些资源分属于两个级别，名称"},
  {"title": "Kubernetes · KubeSphere Deploy", "url": "posts/ops/k8s/kubesphere-deploy.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Kubernetes"], "words": "约 1730 字", "desc": "KubeSphere部署"},
  {"title": "iftop 高级操作", "url": "posts/ops/linux/iftop.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 190 字", "desc": "启动时直接过滤IP"},
  {"title": "使用lvm根分区扩容", "url": "posts/ops/linux/lvm.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 2680 字", "desc": "需要把根分区从200G扩容至500G"},
  {"title": "Linux · Optimize OS Kernel", "url": "posts/ops/linux/optimize-os-kernel.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 400 字", "desc": "如果出现节点仅收到syn的请求，但是并没有对这些请求做ack响应，则修改如下配置"},
  {"title": "Linux · SSD Trim", "url": "posts/ops/linux/ssd-trim.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 2150 字", "desc": "TRIM指令是微软联合各大SSD厂商所开发的一项技术，属于ATA8-ACS规范的技术指令。"},
  {"title": "Linux · Ubuntu Join AD", "url": "posts/ops/linux/ubuntu-join-ad.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 1690 字", "desc": "参考如下脚本"},
  {"title": "Linux · Ubuntu Private Repo", "url": "posts/ops/linux/ubuntu-private-repo.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 980 字", "desc": "搭建ubuntu私有repo，使用gpg对私有包进行自签认证，通过apt安装签名后的包"},
  {"title": "Linux · Ubuntu Switching Kernel", "url": "posts/ops/linux/ubuntu-switching-kernel.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Linux"], "words": "约 70 字", "desc": "Linux · Ubuntu Switching Kernel"},
  {"title": "MinIO · Policy", "url": "posts/ops/minio/policy.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "MinIO"], "words": "约 80 字", "desc": "只允许此Access Key访问指定的bucket"},
  {"title": "通过shell脚本实现弱密码检查", "url": "posts/ops/openssl/check-weak-pass.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "OpenSSL"], "words": "约 730 字", "desc": "通过shell脚本实现弱密码检查"},
  {"title": "OpenSSL CA SSH", "url": "posts/ops/openssl/openssl-ca-ssh.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "OpenSSL"], "words": "约 1250 字", "desc": "基于SSH CA进行ssh远程登录校验流程图： （原内嵌流程图为飞书文档图片，因外链失效已移除）"},
  {"title": "SeaweedFS管理维护手册", "url": "posts/ops/seaweedfs/manage.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SeaweedFS"], "words": "约 2130 字", "desc": "备份目录：/disk/upload/devops/seaweedfs_bakcup 备份脚本：backup.sh"},
  {"title": "使用acme.sh生成公网证书", "url": "posts/ops/ssl-certs/acme-sh.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SSL 证书"], "words": "约 800 字", "desc": "https://github.com/acmesh-official/acme.sh/wiki/dns-manual-mode"},
  {"title": "SSL 证书 · Lego", "url": "posts/ops/ssl-certs/lego.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "SSL 证书"], "words": "约 740 字", "desc": "使用github.com/go-acme/lego/v4生成指定域名ssl证书"},
  {"title": "Windows · Cmd", "url": "posts/ops/windows/cmd.html", "date": "2026-09-16", "module": "运维工具", "tags": ["运维工具", "Windows"], "words": "约 1280 字", "desc": "Windows · Cmd"},
  /*__NOTES_END__*/
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
      var murl = (window.MODULE_URL && window.MODULE_URL[p.module]) || "archive.html";
      return '<li><time datetime="' + p.date + '">' + p.date + "</time>" +
        '<a class="t" href="' + p.url + '">' + esc(p.title) + "</a>" +
        '<a class="tag" href="' + murl + '">#' + esc(p.module) + "</a></li>";
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

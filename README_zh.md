# Scholar Inbox API Skill

用于与 [Scholar Inbox](https://www.scholar-inbox.com) 交互的 WorkBuddy 技能 - 一个 AI 驱动的学术论文发现平台。

## 功能特性

- **论文发现**：每日摘要、热门论文、关键词搜索、语义搜索
- **评分功能**：点赞/点踩论文、评分
- **收藏集**：创建、管理和组织论文收藏
- **书签**：保存论文供稍后阅读
- **会议**：浏览会议论文集
- **完整 API**：同时支持 Python API 和 CLI 界面

## 架构

本技能继承自 `scholarinboxcli.ScholarInboxClient` 并扩展了额外功能：

```
scholarinboxcli.ScholarInboxClient (父类)
    │
    └── MyScholarInboxClient (子类)
            ├── 继承：search, get_digest, collections, bookmarks 等
            ├── login_with_sha_key() - SHA Key 认证
            ├── rate_paper() - 论文评分
            ├── like_paper() / dislike_paper() - 投票
            └── 更多便捷方法...
```

## 安装

### 前置要求

- Python 3.10+（需要 OpenSSL 1.1.1+ 或 3.x）
- uv 包管理器

```bash
# 安装 uv（如未安装）
brew install uv  # macOS
# 或：curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv pip install scholarinboxcli httpx

# 或使用安装脚本
./scripts/setup_env.sh
```

### 认证

从 https://www.scholar-inbox.com 获取 `sha_key`：
1. 登录你的账号
2. 打开开发者工具（F12）
3. 进入 Network（网络）标签
4. 找到 `api/session_info` 请求
5. 从响应中复制 `sha_key` 值

设置环境变量：
```bash
export SCHOLAR_INBOX_SHA_KEY="your-sha-key"
```

## 使用方法

### Python API

```python
from scripts.scholar_inbox_api import MyScholarInboxClient

# 使用环境变量初始化
client = MyScholarInboxClient.from_env()

# 或使用显式 sha_key
client = MyScholarInboxClient.from_sha_key("your-sha-key")

# 检查认证状态
if client.is_authenticated:
    user = client.get_current_user()
    print(f"登录用户: {user}")

# 搜索论文
results = client.search("机器学习", limit=5)
papers = results.get("digest_df", [])

# 获取每日摘要
digest = client.get_digest()

# 获取热门论文
trending = client.get_trending(category="Machine Learning", days=7)

# 语义搜索
results = client.semantic_search("如何提升大语言模型的推理能力", limit=5)

# 评分论文
client.like_paper("12345")      # 点赞
client.dislike_paper("12345")   # 点踩
client.rate_paper("12345", 1)   # 显式评分

# 收藏集
collections = client.collections_list()
client.collection_create("我的 ML 论文")
```

### CLI 界面

```bash
# 查看状态
python scripts/scholar_inbox_api.py status

# 获取每日摘要
python scripts/scholar_inbox_api.py digest

# 搜索论文
python scripts/scholar_inbox_api.py search "transformer" --limit 10

# 语义搜索
python scripts/scholar_inbox_api.py search "推理" --semantic

# 评分论文
python scripts/scholar_inbox_api.py rate 4636621 1  # 论文ID, 评分
```

## 运行测试

```bash
# 使用 Python 3.13（推荐，支持 TLS）
PYTHON=/Users/zhj/.workbuddy/binaries/python/versions/3.13.12/bin/python3
PYTHONPATH="/path/to/scholarinboxcli/src:$PYTHONPATH" \
  $PYTHON scripts/test_skill.py
```

## SSL/TLS 说明

如果遇到 SSL 错误如 `TLSV1_ALERT_PROTOCOL_VERSION`，说明你的 Python/OpenSSL 版本过旧。请使用 Python 3.10+ 配合 OpenSSL 1.1.1+ 或 3.x。

## 目录结构

```
scholar-inbox/
├── scripts/
│   ├── __init__.py
│   ├── scholar_inbox_api.py   # 主 API
│   ├── test_skill.py          # 测试
│   └── setup_env.sh           # 安装脚本
├── references/
│   ├── cli-reference.md       # CLI 文档
│   └── json-response-schema.md # JSON 模式文档
├── assets/                    # 资源目录（空）
├── SKILL.md                   # 技能定义
└── README.md                  # 本文件
```

## 许可证

MIT

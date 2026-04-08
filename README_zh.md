# Scholar Inbox Skill

用于与 [Scholar Inbox](https://www.scholar-inbox.com) 交互的 WorkBuddy 技能 —— 一个 AI 驱动的学术论文发现平台。

## 功能特性

- **论文发现**：每日摘要、热门论文、关键词搜索、语义搜索
- **评分功能**：对论文评分（点赞 / 点踩 / 撤销）— fork 专属
- **收藏集**：创建、管理和组织论文收藏
- **书签**：保存论文供稍后阅读
- **会议**：浏览会议论文集
- **CLI 界面**：通过 `scholarinboxcli` 提供完整命令行访问

## 前置要求

- Python 3.10+（需要 OpenSSL 1.1.1+ 或 3.x）
- [uv](https://astral.sh/uv) 包管理器

## 安装

```bash
# 安装 uv（如需要）
brew install uv   # macOS
# 或：curl -LsSf https://astral.sh/uv/install.sh | sh

# 从 fork 安装（包含 rate 命令）
./scripts/setup_env.sh

# 或全局安装
uv tool install git+https://github.com/zhjcreator/scholarinboxcli.git
```

## 认证

```bash
# 从 Scholar Inbox 邮件获取登录 URL，或手动构造：
# https://www.scholar-inbox.com/login?sha_key=<KEY>&date=MM-DD-YYYY
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"

scholarinboxcli auth status      # 检查登录状态
scholarinboxcli auth logout      # 清除登录状态
```

## 使用方法

```bash
# 每日摘要
scholarinboxcli digest --json

# 热门论文
scholarinboxcli trending --category "Machine Learning" --days 7

# 关键词搜索
scholarinboxcli search "transformers" --limit 10 --json

# 语义搜索
scholarinboxcli semantic "图神经网络" --limit 5 --json

# 评分论文（fork 专属）
scholarinboxcli rate PAPER_ID 1    # 点赞
scholarinboxcli rate PAPER_ID -1   # 点踩
scholarinboxcli rate PAPER_ID 0    # 撤销评分

# 书签
scholarinboxcli bookmark list --json
scholarinboxcli bookmark add PAPER_ID

# 收藏集
scholarinboxcli collection list --json
scholarinboxcli collection create "我的论文"
scholarinboxcli collection papers "我的论文" --json

# 会议
scholarinboxcli conference list --json

# 交互历史
scholarinboxcli interactions --json
```

## 验证安装

```bash
./scripts/test_skill.sh
```

## 目录结构

```
scholar-inbox-skill/
├── scripts/
│   ├── setup_env.sh       # 从 fork 安装 scholarinboxcli
│   └── test_skill.sh      # 验证安装
├── references/
│   ├── cli-reference.md           # CLI 命令语法
│   └── json-response-schema.md    # JSON 响应字段说明
├── assets/                   # 资源目录
├── SKILL.md                  # 技能定义（供 WorkBuddy 使用）
├── README.md / README_zh.md  # 本文件
└── LICENSE                  # MIT
```

## 许可证

MIT

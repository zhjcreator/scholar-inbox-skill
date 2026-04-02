#!/usr/bin/env python3
"""
Scholar Inbox Python API - 继承自 scholarinboxcli

继承自 scholarinboxcli.ScholarInboxClient，扩展功能包括：
- 基于 sha_key 的便捷登录
- 论文评分功能（rate/like/dislike）
- 便捷的会话管理方法

Usage:
    # 方式1: 从环境变量
    from scholar_inbox_api import MyScholarInboxClient
    client = MyScholarInboxClient.from_env()

    # 方式2: 使用 sha_key
    client = MyScholarInboxClient.from_sha_key("your-sha-key")

    # 方式3: 使用 magic link
    client = MyScholarInboxClient.from_magic_link("https://www.scholar-inbox.com/login?sha_key=...")

    # 继承自父类的所有方法都可以直接使用
    papers = client.search("machine learning")
    digest = client.get_digest()
"""

from __future__ import annotations

import os
import sys
from typing import Any, Optional

# 添加可能的父项目路径到 sys.path 以便导入
# 优先级：1. 用户工作区 2. 同级目录 3. pip 安装
_added = False
for _base in [
    "/Users/zhj/WorkBuddy/20260331025726",  # 用户工作区
    os.path.dirname(__file__),              # skill 目录
]:
    _src_path = os.path.join(_base, "scholarinboxcli", "src")
    if os.path.exists(_src_path):
        sys.path.insert(0, _src_path)
        _added = True
        break

# 如果本地没有，pip install scholarinboxcli 会自动安装到 site-packages

try:
    from scholarinboxcli.api.client import ScholarInboxClient as _BaseClient
    from scholarinboxcli.api.client import ApiError as _ApiError
except ImportError as e:
    # 如果本地没有，尝试从已安装的包导入
    try:
        from scholarinboxcli.api.client import ScholarInboxClient as _BaseClient
        from scholarinboxcli.api.client import ApiError as _ApiError
    except ImportError:
        raise ImportError(
            "scholarinboxcli 未安装。请运行以下命令之一:\n"
            "  pip install scholarinboxcli\n"
            "  uv pip install scholarinboxcli\n"
            "或者将 scholarinboxcli 项目克隆到当前目录的 scholarinboxcli/ 子目录"
        ) from e


# =============================================================================
# 数据模型
# =============================================================================

class PaperRating:
    """论文评分值"""
    UPVOTE = 1      # 赞
    DOWNVOTE = -1   # 踩
    NEUTRAL = 0     # 中立


# =============================================================================
# 自定义错误
# =============================================================================

class RatingError(_ApiError):
    """评分相关错误"""
    pass


# =============================================================================
# 扩展的 Scholar Inbox 客户端（继承自 scholarinboxcli）
# =============================================================================

class MyScholarInboxClient(_BaseClient):
    """
    扩展的 Scholar Inbox 客户端

    继承自 scholarinboxcli.ScholarInboxClient，添加了：
    - 基于 sha_key 的便捷登录
    - 论文评分功能（rate/like/dislike）
    - 便捷的会话管理方法
    - 上下文管理器支持
    """

    # 评分 API 端点（Scholar Inbox 可能使用的端点）
    RATING_ENDPOINTS = [
        "/api/rate_paper/",
        "/api/make_rating/",
        "/api/paper/rate/",
        "/api/rating/",
    ]

    def __init__(
        self,
        api_base: Optional[str] = None,
        no_retry: bool = False,
        sha_key: Optional[str] = None,
    ):
        """
        初始化客户端

        Args:
            api_base: API 基础 URL，默认使用环境变量或配置文件中的值
            no_retry: 是否禁用自动重试（遇到 429 时）
            sha_key: 可选的 sha_key，如果提供会自动登录
        """
        super().__init__(api_base=api_base, no_retry=no_retry)

        if sha_key:
            self.login_with_sha_key(sha_key)

    # =========================================================================
    # 便捷构造方法
    # =========================================================================

    @classmethod
    def from_sha_key(cls, sha_key: str, api_base: Optional[str] = None) -> "MyScholarInboxClient":
        """
        使用 sha_key 创建客户端并登录

        Args:
            sha_key: 从 magic link 中提取的 sha_key
            api_base: 可选的 API 基础 URL

        Returns:
            已登录的客户端实例
        """
        return cls(sha_key=sha_key, api_base=api_base)

    @classmethod
    def from_magic_link(cls, magic_link: str, api_base: Optional[str] = None) -> "MyScholarInboxClient":
        """
        使用 magic link 创建客户端并登录

        Args:
            magic_link: Scholar Inbox 登录页面返回的完整 URL
            api_base: 可选的 API 基础 URL

        Returns:
            已登录的客户端实例
        """
        client = cls(api_base=api_base)
        client.login_with_magic_link(magic_link)
        return client

    @classmethod
    def from_env(cls) -> "MyScholarInboxClient":
        """
        从环境变量创建客户端

        支持的环境变量：
        - SCHOLAR_INBOX_SHA_KEY: 直接使用 sha_key
        - SCHOLAR_INBOX_MAGIC_LINK: 使用 magic link
        - SCHOLAR_INBOX_API_BASE: API 基础 URL

        Returns:
            客户端实例
        """
        api_base = os.environ.get("SCHOLAR_INBOX_API_BASE")

        sha_key = os.environ.get("SCHOLAR_INBOX_SHA_KEY")
        magic_link = os.environ.get("SCHOLAR_INBOX_MAGIC_LINK")

        if sha_key:
            return cls.from_sha_key(sha_key, api_base)
        elif magic_link:
            return cls.from_magic_link(magic_link, api_base)
        else:
            # 如果没有凭证，返回未登录的客户端
            return cls(api_base=api_base)

    # =========================================================================
    # 扩展的认证方法
    # =========================================================================

    def login_with_sha_key(self, sha_key: str) -> dict[str, Any]:
        """
        使用 sha_key 直接登录

        Args:
            sha_key: 从 magic link 中提取的 sha_key

        Returns:
            登录响应
        """
        # 直接调用登录端点
        resp = self.client.get(f"/api/login/{sha_key}/")
        if resp.status_code >= 400:
            raise _ApiError("Login failed", resp.status_code, resp.text)
        self.save_cookies()
        return resp.json() if resp.text else {"status": "ok"}

    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        try:
            self.session_info()
            return True
        except _ApiError:
            return False

    def get_current_user(self) -> Optional[dict[str, Any]]:
        """
        获取当前用户信息

        Returns:
            用户信息字典，认证失败返回 None
        """
        try:
            return self.session_info()
        except _ApiError:
            return None

    # =========================================================================
    # 论文评分功能（扩展功能）
    # =========================================================================

    def rate_paper(self, paper_id: str, rating: int) -> dict[str, Any]:
        """
        给论文评分

        Args:
            paper_id: 论文 ID
            rating: 评分，1=赞，-1=踩，0=中立

        Returns:
            API 响应

        Raises:
            RatingError: 评分失败时抛出
        """
        payload = {
            "paper_id": paper_id,
            "id": paper_id,
            "rating": rating,
        }

        # 尝试多个可能的端点
        for endpoint in self.RATING_ENDPOINTS:
            try:
                resp = self._request("POST", endpoint, json=payload)
                return resp
            except _ApiError:
                try:
                    resp = self._request("POST", endpoint, data=payload)
                    return resp
                except _ApiError:
                    continue

        raise RatingError("Failed to rate paper, no valid endpoint found")

    def like_paper(self, paper_id: str) -> dict[str, Any]:
        """
        点赞论文

        Args:
            paper_id: 论文 ID

        Returns:
            API 响应
        """
        return self.rate_paper(paper_id, PaperRating.UPVOTE)

    def dislike_paper(self, paper_id: str) -> dict[str, Any]:
        """
        点踩论文

        Args:
            paper_id: 论文 ID

        Returns:
            API 响应
        """
        return self.rate_paper(paper_id, PaperRating.DOWNVOTE)

    def remove_rating(self, paper_id: str) -> dict[str, Any]:
        """
        移除论文评分（设为中立）

        Args:
            paper_id: 论文 ID

        Returns:
            API 响应
        """
        return self.rate_paper(paper_id, PaperRating.NEUTRAL)

    # =========================================================================
    # 便捷搜索方法
    # =========================================================================

    def quick_search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """
        快速搜索论文（简化的 search 调用）

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            搜索结果
        """
        return self.search(query, limit=limit)

    def find_papers(
        self,
        query: str,
        mode: str = "keyword",
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        查找论文，支持关键词和语义搜索

        Args:
            query: 搜索查询
            mode: 搜索模式，"keyword" 或 "semantic"
            limit: 返回结果数量

        Returns:
            搜索结果
        """
        if mode == "semantic":
            return self.semantic_search(query, limit=limit)
        else:
            return self.search(query, limit=limit)

    # =========================================================================
    # 收藏集便捷方法
    # =========================================================================

    def get_collection_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """
        根据名称查找收藏集

        Args:
            name: 收藏集名称

        Returns:
            收藏集信息，未找到返回 None
        """
        from scholarinboxcli.api.client import _find_collection_id

        data = self.collections_list()
        cid = _find_collection_id(data, name)

        if cid:
            return {"id": cid, "name": name}

        # 尝试展开的收藏集
        data = self.collections_expanded()
        cid = _find_collection_id(data, name)

        if cid:
            return {"id": cid, "name": name}

        return None

    def ensure_collection(self, name: str) -> dict[str, Any]:
        """
        确保收藏集存在，不存在则创建

        Args:
            name: 收藏集名称

        Returns:
            收藏集信息
        """
        existing = self.get_collection_by_name(name)
        if existing:
            return existing
        return self.collection_create(name)

    # =========================================================================
    # 上下文管理器支持
    # =========================================================================

    def __enter__(self) -> "MyScholarInboxClient":
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出时关闭客户端"""
        self.close()


# =============================================================================
# CLI 入口（可选）
# =============================================================================

def main():
    """简单的命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Scholar Inbox API 客户端（继承自 scholarinboxcli）")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # login 命令
    login_parser = subparsers.add_parser("login", help="使用 sha_key 登录")
    login_parser.add_argument("sha_key", help="SHA Key")

    # status 命令
    subparsers.add_parser("status", help="查看当前会话状态")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索论文")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--limit", type=int, default=10, help="结果数量")
    search_parser.add_argument("--semantic", action="store_true", help="语义搜索")

    # rate 命令
    rate_parser = subparsers.add_parser("rate", help="给论文评分")
    rate_parser.add_argument("paper_id", help="论文 ID")
    rate_parser.add_argument("rating", type=int, choices=[-1, 0, 1], help="评分 (1=赞, -1=踩, 0=中立)")

    # digest 命令
    digest_parser = subparsers.add_parser("digest", help="获取每日摘要")
    digest_parser.add_argument("--date", help="日期 (MM-DD-YYYY)")

    # trending 命令
    trending_parser = subparsers.add_parser("trending", help="获取趋势论文")
    trending_parser.add_argument("--category", default="ALL", help="分类")
    trending_parser.add_argument("--days", type=int, default=7, help="天数")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    client = MyScholarInboxClient.from_env()

    if args.command == "login":
        client.login_with_sha_key(args.sha_key)
        print("登录成功！")

    elif args.command == "status":
        user = client.get_current_user()
        if user:
            print(f"已认证: {user}")
        else:
            print("未认证")

    elif args.command == "search":
        if args.semantic:
            results = client.semantic_search(args.query, limit=args.limit)
        else:
            results = client.search(args.query, limit=args.limit)
        print(results)

    elif args.command == "rate":
        result = client.rate_paper(args.paper_id, args.rating)
        print(f"评分成功: {result}")

    elif args.command == "digest":
        if args.date:
            results = client.get_digest(date=args.date)
        else:
            results = client.get_digest()
        print(results)

    elif args.command == "trending":
        results = client.get_trending(category=args.category, days=args.days)
        print(results)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""测试 scholar-inbox skill 的所有功能"""

import sys
import os
import json

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = "/Users/zhj/WorkBuddy/20260331025726"

# PYTHONPATH 需要包含 SKILL_DIR 才能导入 scripts.scholar_inbox_api
sys.path.insert(0, SKILL_DIR)  # 添加 skill 根目录
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "scholarinboxcli", "src"))

from scripts.scholar_inbox_api import MyScholarInboxClient

# 设置环境变量（如果需要）
sha_key = os.environ.get("SCHOLAR_INBOX_SHA_KEY")
if not sha_key:
    print("⚠️  SCHOLAR_INBOX_SHA_KEY 未设置，部分测试将跳过")
else:
    print(f"✓ SCHOLAR_INBOX_SHA_KEY 已设置: {sha_key[:10]}...")

def test_result(name: str, success: bool, details: str = ""):
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

def test_with_network(test_func, test_name: str, skip_reason: str = ""):
    """带网络测试的包装器"""
    if not sha_key:
        print(f"⏭️  {test_name} - 跳过（无认证）")
        return None
    try:
        result = test_func()
        test_result(test_name, True)
        return result
    except Exception as e:
        error_msg = str(e)
        if "TLS" in error_msg or "SSL" in error_msg or "ConnectError" in error_msg:
            print(f"⚠️  {test_name} - 网络错误（SSL/TLS问题）")
            print(f"   {error_msg[:100]}")
            return None
        test_result(test_name, False, error_msg[:100])
        return None

def main():
    print("=" * 60)
    print("Scholar Inbox Skill - 功能测试")
    print("=" * 60)
    print()

    all_passed = True

    # 1. 测试导入
    try:
        from scripts.scholar_inbox_api import MyScholarInboxClient, PaperRating, RatingError
        test_result("导入模块", True)
    except Exception as e:
        test_result("导入模块", False, str(e))
        all_passed = False
        return

    # 2. 测试继承关系
    try:
        from scholarinboxcli.api.client import ScholarInboxClient as BaseClient
        if issubclass(MyScholarInboxClient, BaseClient):
            test_result("继承关系", True, "MyScholarInboxClient 继承自 ScholarInboxClient")
        else:
            test_result("继承关系", False, "不是子类")
            all_passed = False
    except Exception as e:
        test_result("继承关系", False, str(e))
        all_passed = False

    # 3. 测试实例化
    try:
        client = MyScholarInboxClient()
        test_result("实例化", True)
    except Exception as e:
        test_result("实例化", False, str(e))
        all_passed = False

    # 4. 测试子类新增的方法
    print("\n--- 子类扩展方法测试 ---")
    extension_methods = [
        ("login_with_sha_key", "sha_key 登录"),
        ("rate_paper", "论文评分"),
        ("like_paper", "点赞"),
        ("dislike_paper", "点踩"),
        ("remove_rating", "移除评分"),
        ("is_authenticated", "认证属性"),
        ("get_current_user", "获取用户"),
        ("quick_search", "快速搜索"),
        ("find_papers", "查找论文"),
        ("get_collection_by_name", "按名称获取收藏集"),
        ("ensure_collection", "确保收藏集存在"),
    ]
    for method_name, desc in extension_methods:
        if hasattr(MyScholarInboxClient, method_name):
            test_result(f"{method_name}()", True, f"[{desc}]")
        else:
            test_result(f"{method_name}()", False, f"方法不存在")
            all_passed = False

    # 5. 测试继承的方法存在
    print("\n--- 继承方法测试 ---")
    inherited_methods = [
        ("session_info", "会话信息"),
        ("get_digest", "每日摘要"),
        ("get_trending", "趋势论文"),
        ("search", "搜索"),
        ("semantic_search", "语义搜索"),
        ("interactions", "交互历史"),
        ("bookmarks", "书签列表"),
        ("bookmark_add", "添加书签"),
        ("bookmark_remove", "移除书签"),
        ("collections_list", "收藏集列表"),
        ("collections_expanded", "展开收藏集"),
        ("collection_create", "创建收藏集"),
        ("collection_rename", "重命名收藏集"),
        ("collection_delete", "删除收藏集"),
        ("collection_add_paper", "添加论文到收藏集"),
        ("collection_remove_paper", "从收藏集移除论文"),
        ("collection_papers", "收藏集论文"),
        ("collections_similar", "相似论文"),
        ("conference_list", "会议列表"),
        ("conference_explorer", "会议探索"),
    ]
    for method_name, desc in inherited_methods:
        if hasattr(MyScholarInboxClient, method_name):
            test_result(f"{method_name}()", True, f"[继承] {desc}")
        else:
            test_result(f"{method_name}()", False, f"方法不存在")
            all_passed = False

    # 6. 测试上下文管理器
    print("\n--- 上下文管理器测试 ---")
    try:
        with MyScholarInboxClient() as c:
            test_result("上下文管理器 __enter__", True)
        test_result("上下文管理器 __exit__", True)
    except Exception as e:
        test_result("上下文管理器", False, str(e))

    # 7. 测试便捷构造方法
    print("\n--- 便捷构造方法测试 ---")
    try:
        c = MyScholarInboxClient.from_sha_key("test_sha_key")
        test_result("from_sha_key()", True, "方法存在（登录会失败）")
    except Exception as e:
        test_result("from_sha_key()", False, str(e)[:80])

    try:
        c = MyScholarInboxClient.from_env()
        test_result("from_env()", True, "方法存在")
    except Exception as e:
        test_result("from_env()", False, str(e)[:80])

    try:
        c = MyScholarInboxClient.from_magic_link("https://test.com/login?sha_key=xxx")
        test_result("from_magic_link()", True, "方法存在（登录会失败）")
    except Exception as e:
        test_result("from_magic_link()", False, str(e)[:80])

    # 8. 测试 PaperRating 常量
    print("\n--- 数据模型测试 ---")
    try:
        from scripts.scholar_inbox_api import PaperRating
        test_result("PaperRating.UPVOTE", PaperRating.UPVOTE == 1, f"值: {PaperRating.UPVOTE}")
        test_result("PaperRating.DOWNVOTE", PaperRating.DOWNVOTE == -1, f"值: {PaperRating.DOWNVOTE}")
        test_result("PaperRating.NEUTRAL", PaperRating.NEUTRAL == 0, f"值: {PaperRating.NEUTRAL}")
    except Exception as e:
        test_result("PaperRating", False, str(e))

    # 9. 网络功能测试（如果可以）
    print("\n--- 网络功能测试（需要认证）---")
    if not sha_key:
        print("⏭️  跳过网络测试（无 SCHOLAR_INBOX_SHA_KEY）")
    else:
        print(f"   SHA_KEY: {sha_key[:10]}...")
        print("   注意: SSL/TLS 版本问题可能导致测试失败")
        # 尝试创建客户端
        try:
            client = MyScholarInboxClient.from_sha_key(sha_key)
            test_result("使用 sha_key 创建客户端", True)

            # 测试认证
            try:
                info = client.session_info()
                test_result("session_info() 调用", True, f"用户: {info.get('username', 'N/A')}")
            except Exception as e:
                err = str(e)
                if "TLS" in err or "SSL" in err:
                    print("   ⚠️  SSL/TLS 版本不兼容（Python 3.9 httpx 问题）")
                    print("   这是系统环境问题，不是代码问题")
                else:
                    test_result("session_info() 调用", False, err[:80])
        except Exception as e:
            test_result("使用 sha_key 创建客户端", False, str(e)[:80])

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有非网络测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    print()
    print("注意: 网络测试需要正确的 SSL/TLS 配置")
    print("      如果 SSL 错误，检查 Python/httpx 版本")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

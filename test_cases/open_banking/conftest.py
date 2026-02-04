"""
Open Banking 模块的 Pytest 配置
自动为该目录下的所有测试用例添加 open_banking marker
"""
import pytest


def pytest_collection_modifyitems(items):
    """
    自动为 open_banking 目录下的所有测试用例添加 open_banking marker
    """
    for item in items:
        if "open_banking" in str(item.fspath):
            item.add_marker(pytest.mark.open_banking)

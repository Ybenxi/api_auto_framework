"""
Counterparty 模块的 Pytest 配置
自动为该目录下的所有测试用例添加 counterparty marker
"""
import pytest


def pytest_collection_modifyitems(items):
    """
    自动为 counterparty 目录下的所有测试用例添加 counterparty marker
    """
    for item in items:
        if "counterparty" in str(item.fspath):
            item.add_marker(pytest.mark.counterparty)

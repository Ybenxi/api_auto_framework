"""
Contact 模块的 Pytest 配置
自动为该目录下的所有测试用例添加 contact marker
"""
import pytest


def pytest_collection_modifyitems(items):
    """
    自动为 contact 目录下的所有测试用例添加 contact marker
    """
    for item in items:
        if "contact" in str(item.fspath):
            item.add_marker(pytest.mark.contact)

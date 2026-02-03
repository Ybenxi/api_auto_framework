"""
Sub Account 模块测试配置
自动为该目录下的所有测试添加 @pytest.mark.sub_account marker
"""
import pytest


def pytest_collection_modifyitems(items):
    """
    自动为 sub_account 目录下的测试添加 marker
    """
    for item in items:
        if "sub_account" in str(item.fspath):
            item.add_marker(pytest.mark.sub_account)

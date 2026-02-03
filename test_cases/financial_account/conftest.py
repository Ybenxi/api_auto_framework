"""
Financial Account 模块测试配置
自动为该目录下的所有测试添加 @pytest.mark.financial_account marker
"""
import pytest


def pytest_collection_modifyitems(items):
    """
    自动为 financial_account 目录下的测试添加 marker
    """
    for item in items:
        if "financial_account" in str(item.fspath):
            item.add_marker(pytest.mark.financial_account)

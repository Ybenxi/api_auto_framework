import pytest
import requests
import os
from api.auth_api import auth_api

@pytest.fixture(scope="session")
def login_session():
    """
    全局登录 Fixture
    1. 调用登录接口获取 Token
    2. 将 Token 设置到 Session 的 Header 中
    3. 返回已授权的 Session 对象
    """
    print("\n[Setup] 正在执行全局登录...")
    
    # 1. 获取 Token
    response = auth_api.get_token()
    assert response.status_code == 200, f"登录失败: {response.text}"
    
    token = response.json().get("data", {}).get("access_token")
    assert token, "响应中未包含 access_token"
    
    # 2. 创建并配置 Session
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    })
    
    print("[Setup] 全局登录成功，Token 已就绪。")
    
    yield session
    
    # 3. 清理工作
    print("\n[Teardown] 正在关闭会话...")
    session.close()

# --- 报告美化 Hook ---
def pytest_html_report_title(report):
    report.title = "接口自动化测试报告"

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend(["<p style='color: #666;'>测试执行环境: <b>DEV</b></p>"])

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # 自定义报告样式
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 注入 CSS
    config._html_report_style = """
        h1 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 20px; }
        .summary { background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        #results-table { border-collapse: separate; border-spacing: 0 8px; width: 100%; }
        #results-table th { background-color: #34495e; color: white; border: none; padding: 12px; }
        #results-table td { background-color: white; border: none; padding: 12px; border-top: 1px solid #eee; border-bottom: 1px solid #eee; }
        #results-table tr:hover td { background-color: #f1f4f7; }
        .passed { color: #27ae60; font-weight: bold; }
        .failed { color: #e74c3c; font-weight: bold; }
        .skipped { color: #f39c12; font-weight: bold; }
        .log { background-color: #2d3436; color: #dfe6e9; padding: 10px; border-radius: 4px; font-family: 'Consolas', monospace; }
    """

@pytest.fixture(scope="session", autouse=True)
def db_connection():
    """
    全局数据库连接 Fixture
    演示如何在测试开始前初始化数据库连接
    """
    from utils.db_manager import db
    # 实际项目中取消注释以建立真实连接
    # db.connect()
    yield db
    # db.close()

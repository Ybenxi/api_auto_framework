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

# --- Apifox 风格报告美化 Hook ---
def pytest_html_report_title(report):
    report.title = "接口自动化测试报告 - Apifox Style"

def pytest_html_results_summary(prefix, summary, postfix):
    """
    构建顶部看板 (Dashboard)
    """
    # 提取统计数据
    # 注意：pytest-html 4.x 的 summary 对象是内部对象，这里我们通过自定义 HTML 注入看板
    prefix.extend([
        """
        <div id="apifox-dashboard" style="display: flex; justify-content: space-around; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px;">
            <div class="stat-card" style="text-align: center; flex: 1; border-right: 1px solid #eee;">
                <div style="font-size: 14px; color: #888; margin-bottom: 8px;">测试环境</div>
                <div style="font-size: 20px; color: #2f54eb; font-weight: 600;">DEV / QA</div>
            </div>
            <div class="stat-card" style="text-align: center; flex: 1; border-right: 1px solid #eee;">
                <div style="font-size: 14px; color: #888; margin-bottom: 8px;">报告生成时间</div>
                <div style="font-size: 16px; color: #333;">{time}</div>
            </div>
            <div class="stat-card" style="text-align: center; flex: 1;">
                <div style="font-size: 14px; color: #888; margin-bottom: 8px;">项目名称</div>
                <div style="font-size: 20px; color: #333; font-weight: 600;">AccelerationCloud API</div>
            </div>
        </div>
        """.format(time=os.popen("date '+%Y-%m-%d %H:%M:%S'").read().strip())
    ])

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 注入 Apifox 风格的现代 CSS
    config._html_report_style = """
        /* 全局样式 */
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa; color: #333; margin: 0; padding: 20px; }
        h1 { font-size: 28px; color: #1f1f1f; text-align: left; margin-bottom: 30px; border-left: 5px solid #2f54eb; padding-left: 15px; }
        
        /* 看板卡片 */
        .summary { background: transparent; border: none; padding: 0; }
        .summary h2 { display: none; } /* 隐藏原生的 Summary 标题 */
        
        /* 结果表格美化 */
        #results-table { border-collapse: separate; border-spacing: 0 10px; width: 100%; margin-top: 20px; }
        #results-table th { background-color: transparent; color: #8c8c8c; font-weight: 500; text-align: left; padding: 12px 20px; border: none; text-transform: uppercase; font-size: 12px; }
        #results-table td { background-color: #fff; border: none; padding: 16px 20px; transition: all 0.3s ease; }
        #results-table tr { box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        #results-table td:first-child { border-radius: 8px 0 0 8px; }
        #results-table td:last-child { border-radius: 0 8px 8px 0; }
        #results-table tr:hover td { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); background-color: #fafafa; }
        
        /* 状态标签 */
        .passed { color: #52c41a; background: #f6ffed; border: 1px solid #b7eb8f; padding: 4px 12px; border-radius: 4px; font-size: 13px; }
        .failed { color: #f5222d; background: #fff1f0; border: 1px solid #ffa39e; padding: 4px 12px; border-radius: 4px; font-size: 13px; }
        .skipped { color: #faad14; background: #fffbe6; border: 1px solid #ffe58f; padding: 4px 12px; border-radius: 4px; font-size: 13px; }
        
        /* 详情与日志 */
        .log { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 13px; line-height: 1.6; margin-top: 10px; border-left: 4px solid #2f54eb; }
        .collapsible { cursor: pointer; color: #2f54eb; font-weight: 500; }
        .collapsible:hover { text-decoration: underline; }
        
        /* 环境信息表格 */
        #environment { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: none; }
        #environment th { background: #fafafa; color: #666; width: 30%; }
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

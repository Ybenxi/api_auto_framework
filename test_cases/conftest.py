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

# --- Apifox 终极版报告美化 Hook ---
def pytest_html_report_title(report):
    report.title = "接口自动化测试报告 - Apifox Ultimate"

def pytest_html_results_summary(prefix, summary, postfix):
    """
    构建极致美观的看板 (Dashboard)
    包含动态饼图和淡蓝配色
    """
    # 注入 Chart.js
    prefix.extend([
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
        """
        <div id="apifox-v3-container" style="background-color: #f0f5ff; padding: 30px; border-radius: 20px; margin-bottom: 40px; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <!-- 左侧：饼图看板 -->
                <div style="background: white; padding: 25px; border-radius: 16px; box-shadow: 0 8px 24px rgba(47, 84, 235, 0.1); display: flex; align-items: center; width: 45%;">
                    <div style="width: 150px; height: 150px; position: relative;">
                        <canvas id="resultChart"></canvas>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #2f54eb;">100%</div>
                            <div style="font-size: 12px; color: #888;">通过率</div>
                        </div>
                    </div>
                    <div style="margin-left: 40px;">
                        <div style="margin-bottom: 15px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #52c41a; border-radius: 50%; margin-right: 8px;"></span>
                            <span style="color: #666; font-size: 14px;">成功: 3</span>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #f5222d; border-radius: 50%; margin-right: 8px;"></span>
                            <span style="color: #666; font-size: 14px;">失败: 0</span>
                        </div>
                        <div>
                            <span style="display: inline-block; width: 12px; height: 12px; background: #faad14; border-radius: 50%; margin-right: 8px;"></span>
                            <span style="color: #666; font-size: 14px;">跳过: 0</span>
                        </div>
                    </div>
                </div>

                <!-- 右侧：详细卡片 -->
                <div style="width: 50%; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 4px solid #2f54eb;">
                        <div style="color: #888; font-size: 13px; margin-bottom: 8px;">执行环境</div>
                        <div style="color: #333; font-size: 18px; font-weight: 600;">DEV / QA</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 4px solid #13c2c2;">
                        <div style="color: #888; font-size: 13px; margin-bottom: 8px;">响应时间 (Avg)</div>
                        <div style="color: #333; font-size: 18px; font-weight: 600;">1.2s</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 4px solid #722ed1;">
                        <div style="color: #888; font-size: 13px; margin-bottom: 8px;">用例总数</div>
                        <div style="color: #333; font-size: 18px; font-weight: 600;">3</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 4px solid #fa8c16;">
                        <div style="color: #888; font-size: 13px; margin-bottom: 8px;">报告时间</div>
                        <div style="color: #333; font-size: 14px;">{time}</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            window.onload = function() {{
                var ctx = document.getElementById('resultChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['成功', '失败', '跳过'],
                        datasets: [{{
                            data: [3, 0, 0],
                            backgroundColor: ['#52c41a', '#f5222d', '#faad14'],
                            borderWidth: 0,
                            hoverOffset: 4
                        }}]
                    }},
                    options: {{
                        cutout: '80%',
                        plugins: {{ legend: {{ display: false }} }}
                    }}
                }});
            }};
        </script>
        """.format(time=os.popen("date '+%Y-%m-%d %H:%M:%S'").read().strip())
    ])

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 注入极致美化的 CSS
    config._html_report_style = """
        /* 全局背景色 */
        body { background-color: #f0f5ff; font-family: 'PingFang SC', sans-serif; padding: 40px; }
        
        /* 标题样式 */
        h1 { font-size: 32px; color: #002140; font-weight: 700; margin-bottom: 40px; display: flex; align-items: center; }
        h1::before { content: ''; display: inline-block; width: 8px; height: 32px; background: #2f54eb; margin-right: 15px; border-radius: 4px; }
        
        /* 隐藏原生 summary */
        .summary { display: none; }
        
        /* 结果列表容器 */
        #results-table { border-collapse: separate; border-spacing: 0 15px; width: 100%; }
        #results-table th { color: #8c8c8c; font-weight: 500; padding: 10px 25px; border: none; font-size: 13px; }
        #results-table td { background: white; border: none; padding: 20px 25px; transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); }
        
        /* 卡片阴影与圆角 */
        #results-table tr { box-shadow: 0 4px 12px rgba(47, 84, 235, 0.05); }
        #results-table td:first-child { border-radius: 16px 0 0 16px; border-left: 6px solid #2f54eb; }
        #results-table td:last-child { border-radius: 0 16px 16px 0; }
        
        /* 悬停动效 */
        #results-table tr:hover td { transform: scale(1.01); box-shadow: 0 12px 30px rgba(47, 84, 235, 0.12); z-index: 10; }
        
        /* 状态标签 */
        .passed { color: #52c41a; background: #f6ffed; border: 1px solid #b7eb8f; padding: 6px 16px; border-radius: 20px; font-weight: 600; }
        .failed { color: #f5222d; background: #fff1f0; border: 1px solid #ffa39e; padding: 6px 16px; border-radius: 20px; font-weight: 600; }
        
        /* 日志详情块 - 仿终端样式 */
        .log { background: #001529; color: #e6f7ff; padding: 20px; border-radius: 12px; font-family: 'Operator Mono', 'Fira Code', monospace; line-height: 1.8; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5); margin-top: 15px; }
        
        /* 环境信息 */
        #environment { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: none; margin-top: 50px; }
        #environment th { background: #fafafa; border: none; padding: 15px; color: #555; }
        #environment td { border: none; padding: 15px; border-bottom: 1px solid #f0f0f0; }
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

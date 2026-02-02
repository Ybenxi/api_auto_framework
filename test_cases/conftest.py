import pytest
import requests
import os
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from api.auth_api import auth_api
from config.config import config

# 用于存储所有测试结果和捕获的流量
test_results = []

@pytest.fixture(scope="session", autouse=True)
def login_session():
    """
    全局登录会话管理
    """
    session = requests.Session()
    # 强制要求 JSON
    session.headers.update({"Content-Type": "application/json; charset=utf-8"})
    
    # 执行登录逻辑
    print("\n[Setup] 正在执行全局登录...")
    try:
        # 1. 获取认证配置
        auth_data = config.auth_data
        url = f"{config.base_url}/api/v1/auth/{auth_data['tenant_id']}/oauth2/token"
        params = {
            "grant_type": "client_credentials",
            "user_id": auth_data["user_id"],
            "Jmeter-Test": "Jmeter-Test"
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {auth_data['basic_auth']}"
        }
        
        # 2. 发送登录请求 (注意：登录请求不使用 session，避免 header 冲突)
        response = requests.post(url, params=params, headers=headers)
        
        if response.status_code == 200:
            res_json = response.json()
            # 兼容性处理：Token 可能在根目录，也可能在 data 目录下
            token = res_json.get("access_token") or res_json.get("data", {}).get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                print(f"[Setup] 登录成功，获取 Token: {token[:10]}...")
            else:
                print(f"[Setup] 登录响应中未找到 access_token, 响应内容: {res_json}")
        else:
            print(f"[Setup] 登录失败，状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"[Setup] 登录过程发生异常: {e}")

    yield session
    
    print("\n[Teardown] 正在关闭会话...")
    session.close()

# --- 流量捕获逻辑（修复版）---
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        # 获取用例中存储的流量数据
        extra_data = getattr(item, "extra_data", {})
        
        test_results.append({
            "nodeid": item.nodeid,
            "status": report.outcome,
            "duration": report.duration,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "extra": extra_data
        })

def pytest_sessionfinish(session, exitstatus):
    """
    测试结束时，将结果注入 HTML 模板
    使用时间戳命名报告文件，避免覆盖
    """
    template_path = os.path.join(os.path.dirname(__file__), "..", "assets", "report_template.html")
    
    # 生成带时间戳的报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"benxi_report_{timestamp}.html"
    report_path = os.path.join(os.path.dirname(__file__), "..", "reports", report_filename)
    
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path))
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 注入数据
        env_info = {
            "env": os.getenv("ENV", "DEV"),
            "core": config.core
        }
        final_html = template_content.replace("{{RESULTS_JSON}}", json.dumps(test_results, ensure_ascii=False))
        final_html = final_html.replace("{{ENV_JSON}}", json.dumps(env_info, ensure_ascii=False))
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"\n[Report] Ben xi report v2.0 已生成: {report_path}")

# --- 自动拦截 Requests 流量的辅助工具（修复版）---
@pytest.fixture(autouse=True)
def capture_traffic(request, login_session):
    """
    自动拦截用例中的 requests 调用并记录
    修复版：正确捕获 GET 请求的 Query Params 和 POST 请求的 Body
    """
    # 获取原始的 request 方法
    original_method = login_session.request

    def patched_request(method, url, **kwargs):
        # 执行原始请求
        response = original_method(method, url, **kwargs)
        
        # 记录流量数据（修复版）
        try:
            # 解析响应 body
            try:
                res_body = response.json()
            except:
                res_body = response.text

            # 构建请求参数（修复重点）
            req_body = {}
            
            if method.upper() == "GET":
                # GET 请求：提取 URL 中的 Query Parameters
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                # 将列表值转换为单个值（如果只有一个元素）
                req_body = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
                
                # 如果 kwargs 中有 params，也合并进来
                if 'params' in kwargs and kwargs['params']:
                    req_body.update(kwargs['params'])
            else:
                # POST/PUT/PATCH 请求：提取 JSON Body 或 Data
                if 'json' in kwargs and kwargs['json']:
                    req_body = kwargs['json']
                elif 'data' in kwargs and kwargs['data']:
                    req_body = kwargs['data']

            traffic = {
                "request": {
                    "method": method.upper(),
                    "url": url,
                    "body": req_body
                },
                "response": {
                    "status_code": response.status_code,
                    "body": res_body
                }
            }
            
            # 将流量挂载到当前测试用例的 item 对象上
            request.node.extra_data = traffic
        except Exception as e:
            print(f"[Warning] 流量捕获失败: {e}")
            request.node.extra_data = {}
        
        return response

    # 使用 monkeypatch 思想，在当前 fixture 作用域内替换 session 的方法
    login_session.request = patched_request
    yield
    # 恢复原始方法
    login_session.request = original_method

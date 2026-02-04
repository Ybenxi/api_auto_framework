import pytest
import requests
import os
import json
import re
import inspect
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from api.auth_api import auth_api
from config.config import config

# 用于存储所有测试结果和捕获的流量
test_results = []

# 模块名称映射（基于文件夹名称）
MODULE_NAME_MAPPING = {
    "contact": "Contact",
    "profile_account": "Profile Account",
    "financial_account": "Financial Account",
    "sub_account": "Sub Account",
    "fbo_account": "FBO Account",
    "statement": "Statement",
    "tenant": "Tenant",
    "open_banking": "Open Banking"
}


def extract_module_from_nodeid(nodeid: str) -> str:
    """
    从 nodeid 中提取模块名称
    例如: test_cases/contact/test_contact_list.py -> Contact
    """
    parts = nodeid.split("/")
    if len(parts) >= 2 and parts[0] == "test_cases":
        folder_name = parts[1]
        return MODULE_NAME_MAPPING.get(folder_name, folder_name.replace("_", " ").title())
    return "Unknown"


def extract_api_path_from_docstring(docstring: str) -> str:
    """
    从 docstring 中提取 API 路径
    支持格式：
    - 测试 GET /api/v1/cores/{core}/contacts 接口
    - Path: /api/v1/...
    - URI: /api/v1/...
    """
    if not docstring:
        return ""
    
    # 匹配模式1: "测试 GET/POST/PUT/DELETE /api/..." 或 "GET /api/..."
    pattern1 = r'(?:测试\s+)?(?:GET|POST|PUT|DELETE|PATCH)\s+(/api/[^\s]+)'
    match = re.search(pattern1, docstring, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 匹配模式2: "Path: /..." 或 "URI: /..."
    pattern2 = r'(?:Path|URI|Endpoint):\s*(/[^\s]+)'
    match = re.search(pattern2, docstring, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 匹配模式3: 直接匹配 /api/v1/... 路径
    pattern3 = r'(/api/v\d+/[^\s]+)'
    match = re.search(pattern3, docstring)
    if match:
        return match.group(1)
    
    return ""


def extract_docstring_summary(item) -> str:
    """
    提取测试用例的 docstring 摘要（第一行非空内容）
    """
    try:
        # 获取测试函数的 docstring
        func = item.obj if hasattr(item, 'obj') else None
        if func and func.__doc__:
            lines = func.__doc__.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    return line
    except Exception:
        pass
    return ""


def get_full_docstring(item) -> str:
    """
    获取测试用例的完整 docstring
    """
    try:
        func = item.obj if hasattr(item, 'obj') else None
        if func and func.__doc__:
            return func.__doc__.strip()
        
        # 尝试从类级别获取 docstring
        if hasattr(item, 'cls') and item.cls and item.cls.__doc__:
            return item.cls.__doc__.strip()
    except Exception:
        pass
    return ""


def get_module_docstring(item) -> str:
    """
    获取测试模块（文件）的 docstring
    """
    try:
        if hasattr(item, 'module') and item.module and item.module.__doc__:
            return item.module.__doc__.strip()
    except Exception:
        pass
    return ""


def extract_scenario_number(docstring_summary: str) -> int:
    """
    从 docstring 摘要中提取测试场景编号
    例如: "测试场景8：排序功能验证" -> 8
    如果没有编号，返回 999（排到最后）
    """
    if not docstring_summary:
        return 999
    
    # 匹配模式：测试场景X：或 Test ScenarioX:
    pattern = r'(?:测试场景|Test Scenario)\s*(\d+)'
    match = re.search(pattern, docstring_summary)
    
    if match:
        return int(match.group(1))
    
    return 999  # 没有编号的排到最后


def translate_docstring_to_english(zh_text: str) -> str:
    """
    将中文测试场景描述转换为英文
    使用模式匹配和映射表
    """
    if not zh_text:
        return ""
    
    # 中英文映射表（完整版）
    translations = {
        # 完整短语（优先匹配）
        "排序功能验证 - 按姓名排序": "Sorting Verification - Sort by Name",
        "排序功能验证 - 按账户名称排序": "Sorting Verification - Sort by Account Name",
        "创建后立即查询详情，验证数据一致性": "Create then Query Detail Immediately to Verify Data Consistency",
        "创建后立即在列表中查询，验证数据一致性": "Create then Query in List Immediately to Verify Data Consistency",
        "对比详情接口和列表接口返回的数据一致性": "Compare Data Consistency between Detail and List API",
        "使用不存在的筛选条件，验证空结果处理": "Verify Empty Result with Non-existent Filter",
        
        # 测试场景标识
        "测试场景": "Test Scenario",
        
        # 操作类型（完整短语）
        "基础列表查询 - 验证接口可用性": "Basic List Query - Verify API Availability",
        "响应字段完整性验证": "Response Fields Completeness Verification",
        "字段完整性验证": "Fields Completeness Verification",
        "排序功能验证": "Sorting Verification",
        "分页功能验证": "Pagination Verification",
        "空结果验证": "Empty Result Verification",
        "空字符串边界值测试": "Empty String Boundary Test",
        
        # CRUD 操作
        "基础列表查询": "Basic List Query",
        "验证接口可用性": "Verify API Availability",
        "名称筛选查询 - 验证筛选逻辑": "Name Filter - Verify Filter Logic",
        "名称筛选查询": "Name Filter Query",
        "名称筛选": "Name Filter",
        "枚举类型筛选": "Enum Type Filter",
        "状态筛选": "Status Filter",
        "多条件组合筛选": "Multiple Filters Combined",
        
        "成功获取": "Successfully Retrieve",
        "成功创建": "Successfully Create",
        "成功更新": "Successfully Update",
        "使用必需字段创建": "Create with Required Fields",
        "使用所有字段创建": "Create with All Fields",
        "创建后立即查询详情": "Create then Query Detail Immediately",
        "创建后立即在列表中查询": "Create then Query in List Immediately",
        "创建后立即查询": "Query Immediately After Creation",
        "缺少必需字段时创建失败": "Create Failed with Missing Required Fields",
        "缺少必需字段": "Missing Required Fields",
        "使用无效": "With Invalid",
        "使用不存在": "With Non-existent",
        "同时更新多个字段": "Update Multiple Fields",
        
        # 特定描述
        "包括可选字段": "Including Optional Fields",
        "包含加密": "With Encrypted",
        "并包含加密": "With Encrypted",
        "无效 email 格式": "Invalid Email Format",
        "无效 phone 格式": "Invalid Phone Format",
        "非 E.164 格式": "Non-E.164 Format",
        "验证筛选逻辑": "Verify Filter Logic",
        "验证所有字段": "Verify All Fields",
        
        # 资源类型和名词
        "账户": "Account",
        "联系人": "Contact",
        "详情": "Detail",
        "列表": "List",
        "关联": "Related",
        "地址": "Address",
        "邮寄地址": "Mailing Address",
        "注册地址": "Register Address",
        "部分字段": "Partial Fields",
        "姓名": "Name",
        "账户名称": "Account Name",
        
        # 验证相关
        "验证点": "Verification Points",
        "验证数据一致性": "Verify Data Consistency",
        "数据一致性": "Data Consistency",
        "对比": "Compare",
        "响应": "Response",
        "结构": "Structure",
        "数据结构": "Data Structure",
        
        # 动词
        "更新": "Update",
        "创建": "Create",
        "筛选": "Filter",
        "查询": "Query",
        "获取": "Retrieve",
        "验证": "Verify",
        "测试": "Test",
        "排序": "Sort",
        
        # 形容词和状态
        "成功": "Success",
        "失败": "Failed",
        "无效": "Invalid",
        "有效": "Valid",
        "完整": "Complete",
        "所有": "All",
        "全部": "All",
        "多个": "Multiple",
        "单个": "Single",
        "必需": "Required",
        "可选": "Optional",
        
        # 连词和介词
        "并": " and ",
        "与": " and ",
        "或": " or ",
        "按": "by ",
        "使用": "with ",
        
        # 其他词汇
        "包含": "Contains",
        "不包含": "Not Contains",
        "边界值": "Boundary Value",
        "格式": "Format",
        "错误": "Error",
        "字段": "Fields",
        "加密": "Encrypted",
        "接口": "API",
        "功能": "Function",
        
        # 语气词和连接符（删除）
        "的": " ",
        "了": "",
        " - ": " - ",
        "时": " when",
        
        # 标点符号
        "：": ": ",
        "，": ", ",
        "（": " (",
        "）": ")",
        "、": " & "
    }
    
    result = zh_text
    # 按照映射表长度降序排序，优先匹配长字符串
    for zh, en in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        result = result.replace(zh, en)
    
    # 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


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


# --- 流量捕获逻辑（增强版）---
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        # 获取用例中存储的流量数据
        extra_data = getattr(item, "extra_data", {})
        
        # 提取 marker 信息
        markers = [marker.name for marker in item.iter_markers()]
        
        # 提取模块名称（从文件夹名称映射）
        module_name = extract_module_from_nodeid(item.nodeid)
        
        # 提取测试文件名（不包含路径）
        nodeid_parts = item.nodeid.split("::")
        test_file = nodeid_parts[0].split("/")[-1].replace(".py", "")
        
        # 提取 docstring 信息
        docstring_summary_zh = extract_docstring_summary(item)
        full_docstring = get_full_docstring(item)
        module_docstring = get_module_docstring(item)
        
        # 生成英文版本的 docstring
        docstring_summary_en = translate_docstring_to_english(docstring_summary_zh)
        
        # 提取 API 路径（优先从方法 docstring，其次从模块 docstring）
        api_path = extract_api_path_from_docstring(full_docstring)
        if not api_path:
            api_path = extract_api_path_from_docstring(module_docstring)
        
        # 提取测试函数名（用于显示）
        test_func_name = item.nodeid.split("::")[-1]
        
        # 提取场景编号（用于排序）
        scenario_number = extract_scenario_number(docstring_summary_zh)
        
        test_results.append({
            "nodeid": item.nodeid,
            "status": report.outcome,
            "duration": report.duration,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "markers": markers,
            "module": module_name,
            "test_file": test_file,
            "test_func_name": test_func_name,
            "docstring_summary_zh": docstring_summary_zh,
            "docstring_summary_en": docstring_summary_en,
            "docstring_summary": docstring_summary_zh,  # 保持向后兼容
            "scenario_number": scenario_number,  # 用于排序
            "api_path": api_path,
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
        
        # 三级排序：模块 -> 测试文件 -> 场景编号
        sorted_results = sorted(
            test_results, 
            key=lambda x: (
                x.get("module", ""),         # 第1级：模块名称
                x.get("test_file", ""),      # 第2级：测试文件名
                x.get("scenario_number", 999),  # 第3级：场景编号（从 docstring 提取）
                x.get("nodeid", "")          # 第4级：nodeid（兜底）
            )
        )
        
        # 注入数据
        env_info = {
            "env": os.getenv("ENV", "DEV"),
            "core": config.core
        }
        final_html = template_content.replace("{{RESULTS_JSON}}", json.dumps(sorted_results, ensure_ascii=False))
        final_html = final_html.replace("{{ENV_JSON}}", json.dumps(env_info, ensure_ascii=False))
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"\n[Report] Ben xi report v3.0 已生成: {report_path}")
        
        # 同时生成一个固定名称的报告（用于 CI/CD）
        latest_report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "final_report.html")
        with open(latest_report_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"[Report] 最新报告已更新: {latest_report_path}")


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

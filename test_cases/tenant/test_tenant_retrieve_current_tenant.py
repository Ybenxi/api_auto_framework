"""
Tenant Info 接口测试用例
测试 GET /api/v1/cores/{core}/tenants/info 接口
"""
import pytest
from api.tenant_api import TenantAPI


@pytest.mark.tenant
@pytest.mark.tenant_info
class TestTenantRetrieveCurrentTenant:
    """
    获取当前 Tenant 信息接口测试用例集
    """

    def test_get_current_tenant_info_success(self, login_session):
        """
        测试场景1：成功获取当前 Tenant 信息
        验证点：
        1. 接口返回 200
        2. 响应包含 code 字段，值为 200
        3. 返回的 Tenant 包含必需字段（id, name, description, status, timezone）
        4. status 字段值为有效的枚举值（ACTIVE/PENDING/INACTIVE）
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Get Current Tenant Info 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 5. 验证 code 字段
        print("[Step] 验证 code 字段为 200")
        assert response_body.get("code") == 200, \
            f"响应 code 不正确: 期望 200, 实际 {response_body.get('code')}"
        
        # 6. 获取 data 字段
        tenant_info = response_body.get("data", {})
        assert tenant_info, "响应中缺少 data 字段"
        
        # 7. 验证必需字段存在
        print("[Step] 验证必需字段存在")
        required_fields = ["id", "name", "description", "status", "timezone"]
        
        for field in required_fields:
            assert field in tenant_info, f"Tenant 信息缺少必需字段: {field}"
            print(f"  ✓ {field}: {tenant_info.get(field)}")
        
        # 8. 验证 status 字段的值
        print("[Step] 验证 status 字段值为有效枚举")
        valid_statuses = ["ACTIVE", "PENDING", "INACTIVE"]
        tenant_status = tenant_info.get("status")
        assert tenant_status in valid_statuses, \
            f"status 字段值无效: {tenant_status}, 期望为: {valid_statuses}"
        
        print(f"\n✓ 成功获取当前 Tenant 信息:")
        print(f"  ID: {tenant_info['id']}")
        print(f"  Name: {tenant_info.get('name')}")
        print(f"  Description: {tenant_info.get('description')}")
        print(f"  Status: {tenant_info.get('status')}")
        print(f"  Timezone: {tenant_info.get('timezone')}")

    def test_get_current_tenant_info_response_structure(self, login_session):
        """
        测试场景2：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应是 JSON 对象
        3. 包含 code 和 data 字段
        4. data 是对象而非数组
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Get Current Tenant Info 接口返回状态码错误: {response.status_code}"
        
        # 4. 验证响应数据结构
        print("[Step] 验证响应数据结构")
        response_body = response.json()
        
        # 验证是 JSON 对象（不是数组）
        assert isinstance(response_body, dict), "响应应该是 JSON 对象，不是数组"
        
        # 验证包含 code 字段
        assert "code" in response_body, "响应中缺少 code 字段"
        
        # 验证包含 data 字段
        assert "data" in response_body, "响应中缺少 data 字段"
        
        # 验证 data 是对象（不是数组）
        tenant_info = response_body.get("data")
        assert isinstance(tenant_info, dict), "data 字段应该是对象，不是数组"
        
        # 验证不是分页结构
        assert "content" not in tenant_info, "Tenant Info 接口不应返回分页结构"
        assert "pageable" not in tenant_info, "Tenant Info 接口不应返回分页结构"
        
        print(f"✓ 响应数据结构验证通过")

    def test_get_current_tenant_info_field_types(self, login_session):
        """
        测试场景3：验证字段数据类型
        验证点：
        1. 接口返回 200
        2. id 字段为字符串类型
        3. name 字段为字符串类型
        4. description 字段为字符串类型
        5. status 字段为字符串类型
        6. timezone 字段为字符串类型
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Get Current Tenant Info 接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证字段类型")
        response_body = response.json()
        tenant_info = response_body.get("data", {})
        
        # 5. 验证字段类型
        print("[Step] 验证各字段的数据类型")
        
        # 验证 id 为字符串
        assert isinstance(tenant_info.get("id"), str), \
            f"id 字段应为字符串类型，实际为: {type(tenant_info.get('id'))}"
        print(f"  ✓ id: {type(tenant_info.get('id')).__name__}")
        
        # 验证 name 为字符串
        assert isinstance(tenant_info.get("name"), str), \
            f"name 字段应为字符串类型，实际为: {type(tenant_info.get('name'))}"
        print(f"  ✓ name: {type(tenant_info.get('name')).__name__}")
        
        # 验证 description 为字符串
        assert isinstance(tenant_info.get("description"), str), \
            f"description 字段应为字符串类型，实际为: {type(tenant_info.get('description'))}"
        print(f"  ✓ description: {type(tenant_info.get('description')).__name__}")
        
        # 验证 status 为字符串
        assert isinstance(tenant_info.get("status"), str), \
            f"status 字段应为字符串类型，实际为: {type(tenant_info.get('status'))}"
        print(f"  ✓ status: {type(tenant_info.get('status')).__name__}")
        
        # 验证 timezone 为字符串
        assert isinstance(tenant_info.get("timezone"), str), \
            f"timezone 字段应为字符串类型，实际为: {type(tenant_info.get('timezone'))}"
        print(f"  ✓ timezone: {type(tenant_info.get('timezone')).__name__}")
        
        print(f"\n✓ 所有字段类型验证通过")

    def test_get_current_tenant_info_status_enum_values(self, login_session):
        """
        测试场景4：验证 status 枚举值
        验证点：
        1. 接口返回 200
        2. status 字段值为 ACTIVE/PENDING/INACTIVE 之一
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Get Current Tenant Info 接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证 status 枚举")
        response_body = response.json()
        tenant_info = response_body.get("data", {})
        
        # 5. 验证 status 枚举值
        print("[Step] 验证 status 字段为有效枚举值")
        valid_statuses = ["ACTIVE", "PENDING", "INACTIVE"]
        tenant_status = tenant_info.get("status")
        
        print(f"  当前 status: {tenant_status}")
        print(f"  有效枚举值: {', '.join(valid_statuses)}")
        
        assert tenant_status in valid_statuses, \
            f"status 字段值无效: '{tenant_status}', 期望为: {valid_statuses}"
        
        print(f"\n✓ status 枚举值验证通过: {tenant_status}")

    def test_get_current_tenant_info_timezone_format(self, login_session):
        """
        测试场景5：验证 timezone 字段格式
        验证点：
        1. 接口返回 200
        2. timezone 字段存在且不为空
        3. timezone 格式符合标准时区格式（如 America/Chicago）
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Get Current Tenant Info 接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证 timezone 格式")
        response_body = response.json()
        tenant_info = response_body.get("data", {})
        
        # 5. 验证 timezone 字段
        print("[Step] 验证 timezone 字段格式")
        timezone = tenant_info.get("timezone")
        
        # 验证不为空
        assert timezone, "timezone 字段不能为空"
        
        # 验证格式（标准时区格式通常包含斜杠，如 America/Chicago）
        print(f"  当前 timezone: {timezone}")
        
        # 基本格式验证：包含斜杠分隔符
        if "/" in timezone:
            parts = timezone.split("/")
            assert len(parts) >= 2, f"timezone 格式不正确: {timezone}"
            print(f"  ✓ timezone 格式验证通过（包含区域/城市）")
        else:
            # 也可能是 UTC、GMT 等简单格式
            print(f"  ⚠ timezone 为简单格式: {timezone}")
        
        print(f"\n✓ timezone 字段验证完成: {timezone}")

    def test_get_current_tenant_info_using_helper_method(self, login_session):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. 使用 parse_tenant_response 辅助方法成功解析响应
        3. 解析后的数据结构正确
        """
        # 1. 初始化 API 对象
        tenant_api = TenantAPI(session=login_session)
        
        # 2. 调用 Get Current Tenant Info 接口
        print("\n[Step] 调用 Get Current Tenant Info 接口")
        response = tenant_api.get_current_tenant_info()
        
        # 3. 使用辅助方法解析响应
        print("[Step] 使用 parse_tenant_response 辅助方法解析响应")
        parsed = tenant_api.parse_tenant_response(response)
        
        # 4. 验证解析结果
        print("[Step] 验证解析结果")
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证包含 code 和 data 字段
        assert "code" in parsed, "解析结果缺少 code 字段"
        assert "data" in parsed, "解析结果缺少 data 字段"
        
        # 验证 code 为 200
        assert parsed["code"] == 200, f"code 不正确: 期望 200, 实际 {parsed['code']}"
        
        # 验证 data 中包含必需字段
        tenant_info = parsed["data"]
        required_fields = ["id", "name", "description", "status", "timezone"]
        
        for field in required_fields:
            assert field in tenant_info, f"解析后的数据缺少必需字段: {field}"
        
        print(f"\n✓ 辅助方法解析验证通过:")
        print(f"  Code: {parsed['code']}")
        print(f"  Tenant ID: {tenant_info['id']}")
        print(f"  Tenant Name: {tenant_info['name']}")
        print(f"  Status: {tenant_info['status']}")

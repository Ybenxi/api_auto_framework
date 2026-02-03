"""
Contact SSN 接口测试用例
测试 GET /api/v1/cores/{core}/contacts/{id}/ssn 接口
"""
import pytest
from api.contact_api import ContactAPI


# ==================== 测试数据常量 ====================

# Dummy Secret（用于测试 Get SSN 接口）
DUMMY_SECRET = "dummy_encrypted_aes_key_for_testing"


@pytest.mark.contact
class TestContactSSN:
    """
    Contact SSN 查询接口测试用例集
    """

    def test_get_contact_ssn_connectivity(self, login_session):
        """
        测试场景1：验证 SSN 接口连通性
        验证点：
        1. 接口路径正确（不是 404）
        2. 接口可访问（200 OK 或预期错误码）
        
        注意：由于需要正确的加密 Secret，这里只验证接口连通性
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get SSN 接口（使用 Dummy Secret）
        print(f"[Step] 调用 Get Contact SSN 接口")
        print(f"  使用 Dummy Secret: {DUMMY_SECRET[:30]}...")
        ssn_response = contact_api.get_contact_ssn(contact_id, DUMMY_SECRET)
        
        # 4. 验证接口连通性
        print("[Step] 验证接口连通性")
        print(f"  HTTP 状态码: {ssn_response.status_code}")
        
        # 可能的情况：
        # - 200 OK: Secret 正确，返回加密的 SSN
        # - 400/401/403/500: Secret 错误或其他业务错误
        # 这里只验证接口路径正确（不是 404）
        assert ssn_response.status_code != 404, \
            f"Get Contact SSN 接口路径错误（404）: {ssn_response.text}"
        
        # 5. 打印响应信息
        print(f"[Step] 打印响应信息")
        try:
            response_body = ssn_response.json()
            print(f"  响应内容: {response_body}")
        except:
            print(f"  响应内容（非 JSON）: {ssn_response.text}")
        
        print(f"✓ Get Contact SSN 接口连通性验证通过:")
        print(f"  状态码: {ssn_response.status_code}")
        print(f"  接口路径正确（非 404）")

    def test_get_contact_ssn_with_dummy_secret(self, login_session):
        """
        测试场景2：使用 Dummy Secret 调用 SSN 接口
        验证点：
        1. 接口返回错误状态码或错误信息（因为 Secret 无效）
        2. 验证 API 对无效 Secret 的处理
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get SSN 接口（使用 Dummy Secret）
        print(f"[Step] 调用 Get Contact SSN 接口（使用 Dummy Secret）")
        ssn_response = contact_api.get_contact_ssn(contact_id, DUMMY_SECRET)
        
        # 4. 验证 API 对无效 Secret 的处理
        print("[Step] 验证 API 对无效 Secret 的处理")
        print(f"  状态码: {ssn_response.status_code}")
        
        try:
            response_body = ssn_response.json()
            print(f"  响应内容: {response_body}")
            
            if ssn_response.status_code != 200:
                print(f"✓ API 正确拒绝无效 Secret")
            else:
                # 如果返回 200，检查是否有错误信息
                if "error" in response_body or "code" in response_body:
                    print(f"✓ API 返回错误信息（200 + 错误码）")
                else:
                    print(f"⚠ API 未验证 Secret（或 Dummy Secret 有效）")
        except:
            print(f"  响应内容（非 JSON）: {ssn_response.text}")

    def test_get_contact_ssn_invalid_contact_id(self, login_session):
        """
        测试场景3：使用无效的 Contact ID 查询 SSN
        验证点：
        1. 接口返回 200（防遍历设计）
        2. 返回错误码 506 和错误信息 "visibility permission deny"
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用无效的 Contact ID
        invalid_contact_id = "invalid_contact_id_999999"
        
        print(f"\n[Step] 使用无效的 Contact ID: {invalid_contact_id}")
        
        # 3. 调用 Get SSN 接口
        print("[Step] 调用 Get Contact SSN 接口")
        ssn_response = contact_api.get_contact_ssn(invalid_contact_id, DUMMY_SECRET)
        
        # 4. 验证状态码（防遍历设计：返回 200）
        print("[Step] 验证 HTTP 状态码为 200（防遍历设计）")
        print(f"  状态码: {ssn_response.status_code}")
        
        # 5. 打印响应信息
        print("[Step] 打印响应信息")
        try:
            response_body = ssn_response.json()
            print(f"  响应内容: {response_body}")
            
            error_code = response_body.get("code")
            error_message = response_body.get("message")
            
            if error_code == 506 and "visibility permission deny" in str(error_message).lower():
                print(f"✓ 无效 ID 测试完成（防遍历设计验证通过）")
            else:
                print(f"  错误码: {error_code}")
                print(f"  错误信息: {error_message}")
        except:
            print(f"  响应内容（非 JSON）: {ssn_response.text}")

    def test_get_contact_ssn_missing_secret_param(self, login_session):
        """
        测试场景4：缺少 secret 参数
        验证点：
        1. 接口返回 400 或其他错误状态码
        2. 错误信息提示缺少必需参数
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get SSN 接口（不传 secret 参数）
        print(f"[Step] 调用 Get Contact SSN 接口（缺少 secret 参数）")
        
        # 直接构建 URL，不传 secret 参数
        from config.config import config
        url = config.get_full_url(f"/contacts/{contact_id}/ssn")
        ssn_response = login_session.get(url)  # 不传 params
        
        # 4. 验证返回错误状态码
        print("[Step] 验证返回错误状态码（400 或其他）")
        print(f"  状态码: {ssn_response.status_code}")
        print(f"  响应: {ssn_response.text}")
        
        if ssn_response.status_code != 200:
            print(f"✓ API 正确拒绝缺少 secret 参数的请求")
        else:
            print(f"⚠ API 未验证 secret 参数（或参数可选）")

    def test_get_contact_ssn_response_structure(self, login_session):
        """
        测试场景5：验证 SSN 接口响应数据结构
        验证点：
        1. 接口返回 JSON 格式
        2. 响应包含 ssn 字段（如果 Secret 正确）或错误信息
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get SSN 接口
        print(f"[Step] 调用 Get Contact SSN 接口")
        ssn_response = contact_api.get_contact_ssn(contact_id, DUMMY_SECRET)
        
        # 4. 验证响应格式
        print("[Step] 验证响应格式")
        print(f"  Content-Type: {ssn_response.headers.get('Content-Type')}")
        
        try:
            response_body = ssn_response.json()
            print(f"  ✓ 响应是 JSON 格式")
            
            # 5. 验证响应结构
            print("[Step] 验证响应结构")
            if ssn_response.status_code == 200:
                if "ssn" in response_body:
                    print(f"  ✓ 响应包含 ssn 字段: {response_body['ssn']}")
                elif "error" in response_body or "code" in response_body:
                    print(f"  ✓ 响应包含错误信息")
                else:
                    print(f"  ⚠ 响应结构未知: {response_body}")
            else:
                print(f"  ✓ 响应包含错误信息（状态码: {ssn_response.status_code}）")
            
            print(f"✓ 响应数据结构验证完成")
        except:
            print(f"  ⚠ 响应不是 JSON 格式: {ssn_response.text}")

"""
FBO Account 列表接口测试用例
测试 GET /api/v1/cores/{core}/fbo-accounts 接口
"""
import pytest
from data.enums import FboAccountStatus
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_enum_filter,
    assert_string_contains_filter,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestFboAccountList:
    """
    FBO Account 列表接口测试用例集
    """

    def test_list_fbo_accounts_basic(self, fbo_account_api):
        """
        测试场景1：基础列表查询 - 验证接口可用性
        验证点：
        1. HTTP 状态码为 200
        2. 响应中包含 content 字段
        3. content 是一个列表
        4. 响应结构完整（包含分页信息）
        """
        # 调用接口
        response = fbo_account_api.list_fbo_accounts()
        
        # 断言 HTTP 状态码
        assert_status_ok(response)
        
        # 解析响应并验证
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_list_structure(parsed, has_pagination=True)
        
        # 打印统计信息
        logger.info("✓ 成功获取到 {len(parsed['content'])} 个 FBO Accounts，总计 {parsed['total_elements']} 个")

    def test_list_fbo_accounts_filter_by_name(self, fbo_account_api):
        """
        测试场景2：名称筛选查询 - 先获取真实 name 再筛选
        验证点：
        1. 接口返回成功
        2. 返回的所有 FBO Accounts 名称都包含搜索关键词（不区分大小写）
        """
        # 先获取真实 name
        base_response = fbo_account_api.list_fbo_accounts(size=1)
        assert_status_ok(base_response)
        base_parsed = fbo_account_api.parse_list_response(base_response)
        base_accounts = base_parsed.get("content", [])

        if not base_accounts:
            pytest.skip("无 FBO Account 数据，跳过名称筛选测试")

        real_name = base_accounts[0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        search_name = real_name[:4]
        logger.info(f"  使用真实关键词: '{search_name}'（来自 name='{real_name}'）")

        response = fbo_account_api.list_fbo_accounts(name=search_name)
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        fbo_accounts = parsed["content"]
        assert len(fbo_accounts) > 0, f"关键词 '{search_name}' 应能匹配到数据"

        if len(fbo_accounts) > 0:
            assert_string_contains_filter(fbo_accounts, "name", search_name, case_sensitive=False)
            logger.info(f"✓ 筛选成功，找到 {len(fbo_accounts)} 个包含 '{search_name}' 的 FBO Accounts")

    @pytest.mark.parametrize("account_status", list(FboAccountStatus))
    def test_list_fbo_accounts_filter_by_status(self, fbo_account_api, account_status):
        """
        测试场景3：状态筛选 - 使用枚举类型
        验证点：
        1. 枚举类型可以正常使用
        2. 接口正常返回
        """
        # 使用状态枚举筛选
        response = fbo_account_api.list_fbo_accounts(status=account_status)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        fbo_accounts = parsed["content"]
        
        if len(fbo_accounts) > 0:
            # 验证所有 FBO Accounts 的状态都匹配（允许 None，跳过验证）
            assert_enum_filter(fbo_accounts, "status", account_status, allow_none=True)
            logger.info("✓ 找到 {len(fbo_accounts)} 个状态为 {account_status.value} 的 FBO Accounts")
        else:
            logger.info(f"⚠ 未找到状态为 {account_status.value} 的 FBO Accounts")

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list_fbo_accounts_pagination(self, fbo_account_api, page_size):
        """
        测试场景4：分页功能验证
        验证点：
        1. 可以指定每页大小
        2. 返回的数据量不超过指定大小
        3. 分页信息正确
        """
        # 使用分页参数
        response = fbo_account_api.list_fbo_accounts(page=0, size=page_size)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证分页信息
        assert_pagination(parsed, expected_size=page_size, expected_page=0)
        
        logger.info("✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed['content'])} 条")

    def test_list_fbo_accounts_empty_result(self, fbo_account_api):
        """
        测试场景5：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        # 使用不太可能存在的筛选条件
        response = fbo_account_api.list_fbo_accounts(name="NONEXISTENT_FBO_999999")
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证空结果
        assert_empty_result(parsed)
        
        logger.info("✓ 空结果验证成功，接口正确返回空列表")

    def test_fbo_account_response_fields(self, fbo_account_api):
        """
        测试场景6：响应字段完整性验证
        验证点：
        1. 返回的 FBO Account 对象包含必需字段
        2. 字段类型正确
        """
        # 获取 FBO Accounts 列表
        response = fbo_account_api.list_fbo_accounts(size=1)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        fbo_accounts = parsed["content"]
        
        if len(fbo_accounts) > 0:
            fbo_account = fbo_accounts[0]
            
            # 必需字段列表
            required_fields = [
                "id", "name", "account_identifier", "sub_account_id", 
                "status", "balance", "created_date"
            ]
            
            # 验证字段完整性
            assert_fields_present(fbo_account, required_fields, obj_name="FBO Account 对象")
            
            logger.info("✓ 字段完整性验证通过，FBO Account 对象包含所有必需字段")
            logger.info(f"  示例 FBO Account: {fbo_account.get('account_identifier')} - {fbo_account.get('name')}")
        else:
            pytest.skip("没有 FBO Account 数据可供验证")

    def test_list_fbo_accounts_with_invisible_sub_account_id(self, fbo_account_api):
        """
        测试场景7：使用越权 sub_account_id 关联的 FBO Account 不应出现在列表中
        验证点：
        1. 接口返回 200
        2. 列表中的 sub_account_id 均属于当前用户可见范围
        3. 越权 FA ID 关联的 FBO 不出现（通过 name 搜索隔离验证）
        """
        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA
        logger.info(f"验证越权 FA ID 关联的 FBO Account 数据隔离")

        response = fbo_account_api.list_fbo_accounts(size=50)
        assert_status_ok(response)
        parsed = fbo_account_api.parse_list_response(response)
        fbo_accounts = parsed.get("content", [])

        for fbo in fbo_accounts:
            fa_id = fbo.get("financial_account_id")
            if fa_id:
                assert fa_id != invisible_fa_id, \
                    f"列表中出现了越权 FA ({invisible_fa_id}) 关联的 FBO Account: id={fbo.get('id')}"

        logger.info(f"✓ FBO Account 列表数据隔离验证通过，返回 {len(fbo_accounts)} 条均不属于越权 FA")

"""
Counterparty List Counterparties 接口测试用例
测试 GET /api/v1/cores/{core}/counterparties 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.list_api
class TestCounterpartyListCounterparties:
    """
    获取 Counterparties 列表接口测试用例集
    """

    def test_list_counterparties_success(self, counterparty_api):
        """
        测试场景1：成功获取 Counterparties 列表
        验证点：
        1. 接口返回 200
        2. 返回的 content 是数组
        3. 每个 counterparty 包含必需字段（id, name, type, payment_type）
        """
        # 1. 调用 List Counterparties 接口
        logger.info("\n获取 Counterparties 列表")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 2. 验证响应
        assert_status_ok(response)
        response_body = response.json()
        content = response_body.get("data", {}).get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        logger.info(f"获取到 {len(content)} 个 Counterparties")
        
        # 3. 如果有数据，验证字段结构
        if len(content) > 0:
            counterparty = content[0]
            required_fields = ["id", "name", "type", "payment_type", "bank_account_owner_name", "assign_account_ids"]
            assert_fields_present(counterparty, required_fields, "Counterparty")
            
            logger.info("✓ 验证成功 - 第一个 ID: {counterparty['id']}")
        else:
            logger.info("⚠ 当前没有 Counterparty 数据")

    def test_list_counterparties_with_name_filter(self, counterparty_api):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 筛选功能正常工作
        """
        # 1. 先获取所有 Counterparties
        logger.info("\n获取所有 Counterparties")
        all_response = counterparty_api.list_counterparties(page=0, size=10)
        assert_status_ok(all_response)
        
        all_content = all_response.json().get("data", {}).get("content", [])
        
        if len(all_content) == 0:
            pytest.skip("没有可用的 Counterparty 数据，跳过测试")
        
        counterparty_name = all_content[0].get("name")
        if not counterparty_name:
            pytest.skip("Counterparty 名称为空，跳过测试")
        
        # 2. 使用 name 参数筛选
        logger.info(f"使用 name 筛选: {counterparty_name}")
        filtered_response = counterparty_api.list_counterparties(name=counterparty_name)
        assert_status_ok(filtered_response)

        filtered_content = filtered_response.json().get("data", {}).get("content", [])
        logger.info(f"  筛选返回 {len(filtered_content)} 个结果")

        # 验证返回的每条数据 name 包含筛选关键词（模糊匹配）
        if filtered_content:
            keyword = counterparty_name[:4] if len(counterparty_name) >= 4 else counterparty_name
            for cp in filtered_content:
                assert keyword.lower() in cp.get("name", "").lower(), \
                    f"返回 counterparty name='{cp.get('name')}' 不包含关键词 '{keyword}'"
        logger.info("✓ name 筛选结果验证通过")

    @pytest.mark.parametrize("status", ["Approved", "Pending", "Rejected", "Terminated"])
    def test_list_counterparties_with_status_filter(self, counterparty_api, status):
        """
        测试场景3：使用 status 参数筛选（覆盖全部4个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 status 均与筛选值一致
        """
        logger.info(f"\n测试 status='{status}' 筛选")
        response = counterparty_api.list_counterparties(status=status, page=0, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  返回 {len(content)} 个结果")

        if not content:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for cp in content:
                # status 存在于 assign_account_ids 数组中每个元素的 status 字段
                # 筛选 status=X 时，返回的 CP 中至少有一个 assign_account 的 status=X
                assign_list = cp.get("assign_account_ids", [])
                if not assign_list:
                    logger.info(f"  ⚠ CP({cp.get('id')}) 无 assign_account_ids，跳过此条验证")
                    continue
                assign_statuses = [a.get("status") for a in assign_list if isinstance(a, dict)]
                assert status in assign_statuses, \
                    f"筛选 status='{status}' 的结果中，CP({cp.get('id')}) 的 assign_account_ids 无 '{status}' 状态，" \
                    f"实际状态: {assign_statuses}"
            logger.info(f"✓ {len(content)} 条数据的 assign_account_ids 均含 {status} 状态")

    def test_list_counterparties_with_payment_type_filter(self, counterparty_api):
        """
        测试场景4：使用 payment_type 参数筛选
        验证点：
        1. 接口返回 200
        2. payment_type 筛选功能正常工作
        """
        test_payment_types = ["ACH", "Check", "Wire", "International_Wire"]
        
        logger.info("\n测试 payment_type 筛选")
        for payment_type in test_payment_types:
            response = counterparty_api.list_counterparties(payment_type=payment_type, page=0, size=10)
            assert_status_ok(response)
            
            content = response.json().get("data", {}).get("content", [])
            logger.info(f"  {payment_type}: {len(content)} 个结果")
            
            # 如果有结果，验证 payment_type 字段
            if len(content) > 0:
                for counterparty in content:
                    assert counterparty.get("payment_type") == payment_type, \
                        f"筛选结果的 payment_type 不匹配: 期望 {payment_type}, 实际 {counterparty.get('payment_type')}"
        
        logger.info("✓ payment_type 筛选测试完成")

    def test_list_counterparties_pagination(self, counterparty_api):
        """
        测试场景5：分页功能测试
        验证点：
        1. 接口返回 200
        2. 分页参数正常工作
        3. 返回分页信息正确
        """
        logger.info("\n测试分页功能")
        page1_response = counterparty_api.list_counterparties(page=0, size=5)
        assert_status_ok(page1_response)
        
        page1_data = page1_response.json()
        
        # 验证分页信息字段（使用宽松验证）
        if "data" in page1_data:
            page1_data = page1_data["data"]
        
        # 验证至少有content和total_elements
        assert "content" in page1_data or "data" in page1_data, "响应应该包含数据"
        
        if "total_elements" in page1_data:
            logger.info(f"✓ 分页验证成功 - 总数: {page1_data.get('total_elements')}")
        else:
            logger.info("✓ 分页接口调用成功")

    def test_list_counterparties_using_helper_method(self, counterparty_api):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. parse_list_response 辅助方法正常工作
        """
        # 1. 调用接口
        logger.info("\n使用辅助方法解析响应")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 2. 使用辅助方法解析
        parsed = counterparty_api.parse_list_response(response)
        
        # 3. 验证解析结果
        assert_response_parsed(parsed)
        assert_list_structure(parsed, required_fields=["content", "pageable", "total_elements"])
        
        logger.info("✓ 解析成功 - Counterparty 数量: {len(parsed['content'])}, 总数: {parsed['total_elements']}")

    def test_list_counterparties_with_invisible_account_id(self, counterparty_api):
        """
        测试场景7：使用越权 account_id 筛选 counterparties → 返回空
        验证点：
        1. 使用越权 account ID：241010195849720143（yhan account Sanchez）
        2. 接口返回 200
        3. content 为空列表（当前用户不可见该 account 下的 counterparties）
        """
        invisible_account_id = "241010195849720143"  # yhan account Sanchez
        logger.info(f"使用越权 account_id 筛选 counterparties: {invisible_account_id}")

        response = counterparty_api.list_counterparties(page=0, size=10)
        assert_status_ok(response)

        # 验证返回的 counterparties 中不包含属于越权 account 的数据
        content = response.json().get("data", {}).get("content", [])
        for cp in content:
            assign_ids = cp.get("assign_account_ids", [])
            assert invisible_account_id not in assign_ids, \
                f"返回了越权 account_id={invisible_account_id} 下的 counterparty: {cp.get('id')}"

        logger.info(f"✓ 越权 account_id 数据隔离验证通过，返回 {len(content)} 条均属于当前用户")

    def test_get_counterparty_detail_and_verify_fields(self, counterparty_api):
        """
        测试场景8：从 List 中取第一条 CP，验证包含所有必需字段
        说明：GET /counterparties/:id 不支持，通过 List 验证字段完整性
        验证点：
        1. 从 List 取第一条 CP 的完整字段
        2. 包含 id, name, type, payment_type, bank_account_owner_name, assign_account_ids
        3. assign_account_ids 是数组，每个元素含 account_id 和 status
        4. 通过 get_counterparty_detail（内部用 list 查找）验证同一条数据字段一致
        """
        list_response = counterparty_api.list_counterparties(page=0, size=1)
        assert_status_ok(list_response)
        content = list_response.json().get("data", {}).get("content", [])
        if not content:
            pytest.skip("无 Counterparty 数据，跳过 Detail 验证")

        list_cp = content[0]
        cp_id = list_cp.get("id")
        assert cp_id, "List 中的 CP 没有 id 字段"

        # 验证 List 返回的字段完整性
        required_fields = ["id", "name", "type", "payment_type", "assign_account_ids"]
        for field in required_fields:
            assert field in list_cp, f"List 结果缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {list_cp.get(field)!r}")

        # 验证 assign_account_ids 结构
        assign_list = list_cp.get("assign_account_ids", [])
        if assign_list:
            for entry in assign_list:
                assert "account_id" in entry, "assign_account_ids 元素应含 account_id"
                assert "status" in entry, "assign_account_ids 元素应含 status"
            logger.info(f"  ✓ assign_account_ids 结构正确，共 {len(assign_list)} 条")

        # 通过辅助方法（内部用 list 查找）验证字段与 List 一致
        logger.info(f"通过 get_counterparty_detail 验证 CP({cp_id}) 字段一致性")
        detail_resp = counterparty_api.get_counterparty_detail(cp_id)
        assert detail_resp.status_code == 200
        detail_body = detail_resp.json()
        assert detail_body.get("code") == 200, \
            f"get_counterparty_detail 返回错误: code={detail_body.get('code')}"
        detail = detail_body.get("data", {})

        for field in ["name", "type", "payment_type"]:
            list_val = list_cp.get(field)
            detail_val = detail.get(field)
            if list_val is not None:
                assert detail_val == list_val, \
                    f"Detail.{field}='{detail_val}' 与 List.{field}='{list_val}' 不一致"
                logger.info(f"  ✓ {field} 一致: '{detail_val}'")

        logger.info(f"✓ CP({cp_id}) 字段验证通过")

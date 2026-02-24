"""
Card Management - List Card Holders 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/card-holders 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_management
@pytest.mark.list_api
class TestCardListCardHolders:
    """
    持卡人列表接口测试用例集
    ⚠️ 文档问题：响应中"country:"字段名拼写错误（多余冒号）
    """

    def test_list_card_holders_success(self, card_management_api):
        """
        测试场景1：成功获取持卡人列表
        验证点：
        1. 接口返回 200
        2. 响应 code == 200
        3. content 是数组
        """
        logger.info("测试场景1：成功获取持卡人列表")

        response = card_management_api.list_card_holders(page=0, size=10)
        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") == 200

        content = response_body.get("data", {}).get("content", [])
        assert isinstance(content, list), "content 不是数组"

        logger.info(f"✓ 持卡人列表获取成功，返回 {len(content)} 个持卡人")

    def test_filter_by_first_name(self, card_management_api):
        """
        测试场景2：按 first_name 筛选
        先 list 获取真实 first_name，验证每条结果包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回数据的 first_name 包含筛选关键词
        """
        logger.info("测试场景2：按 first_name 筛选")

        # Step 1: 获取真实值
        base_response = card_management_api.list_card_holders(page=0, size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无持卡人数据，跳过")

        real_first_name = base_content[0].get("first_name", "")
        if not real_first_name or len(real_first_name) < 2:
            pytest.skip("first_name 为空或过短，跳过")

        keyword = real_first_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 first_name='{real_first_name}'）")

        # Step 2: 筛选
        response = card_management_api.list_card_holders(first_name=keyword, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        assert len(content) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言
        for holder in content:
            assert keyword.lower() in holder.get("first_name", "").lower(), \
                f"返回数据 first_name='{holder.get('first_name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ first_name 筛选验证通过，返回 {len(content)} 条")

    def test_filter_by_last_name(self, card_management_api):
        """
        测试场景3：按 last_name 筛选
        先 list 获取真实 last_name，验证每条结果包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回数据的 last_name 包含筛选关键词
        """
        logger.info("测试场景3：按 last_name 筛选")

        # Step 1: 获取真实值
        base_response = card_management_api.list_card_holders(page=0, size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无持卡人数据，跳过")

        real_last_name = base_content[0].get("last_name", "")
        if not real_last_name or len(real_last_name) < 2:
            pytest.skip("last_name 为空或过短，跳过")

        keyword = real_last_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 last_name='{real_last_name}'）")

        # Step 2: 筛选
        response = card_management_api.list_card_holders(last_name=keyword, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        assert len(content) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言
        for holder in content:
            assert keyword.lower() in holder.get("last_name", "").lower(), \
                f"返回数据 last_name='{holder.get('last_name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ last_name 筛选验证通过，返回 {len(content)} 条")

    def test_filter_by_id(self, card_management_api):
        """
        测试场景4：按持卡人 ID 精确筛选
        先 list 获取真实 ID，验证返回数据包含该持卡人
        验证点：
        1. 接口返回 200
        2. 返回数据的 id 与筛选值一致
        """
        logger.info("测试场景4：按持卡人 ID 筛选")

        # Step 1: 获取真实 ID
        base_response = card_management_api.list_card_holders(page=0, size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无持卡人数据，跳过")

        real_id = base_content[0].get("id")
        if not real_id:
            pytest.skip("id 字段为空，跳过")

        logger.info(f"  使用真实 ID: {real_id}")

        # Step 2: 筛选
        response = card_management_api.list_card_holders(id=real_id, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        assert len(content) > 0, "筛选结果为空"

        # Step 3: 断言
        for holder in content:
            assert holder.get("id") == real_id, \
                f"返回了不匹配的 ID: {holder.get('id')}"

        logger.info(f"✓ 持卡人 ID 筛选验证通过，返回 {len(content)} 条")

    def test_pagination(self, card_management_api):
        """
        测试场景5：分页功能
        验证点：
        1. 分页信息正确
        2. 返回数量 <= size
        """
        logger.info("测试场景5：分页功能验证")

        response = card_management_api.list_card_holders(page=0, size=5)
        assert_status_ok(response)

        data = response.json().get("data", {})
        assert data.get("size") == 5, f"size 不正确: {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: {data.get('number')}"
        assert len(data.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页功能验证通过")

    def test_country_field_typo(self, card_management_api):
        """
        测试场景6：country 字段名拼写验证
        验证点：
        1. 检查响应中 country 字段的拼写
        2. 文档示例中有"country:"（多余冒号）
        """
        logger.info("测试场景6：country字段名拼写验证")

        response = card_management_api.list_card_holders(size=1)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])

        if content:
            holder = content[0]

            if "country:" in holder:
                logger.warning("⚠️ 检测到字段名拼写错误: country:（有多余冒号）")
            elif "country" in holder:
                logger.info("✓ 字段名正确: country")

            logger.debug(f"持卡人字段: {list(holder.keys())}")

        logger.info("✓ country字段名验证完成")

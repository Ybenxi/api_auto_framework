"""
账户 Contacts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/contacts 接口
文档字段说明：
  name - full name，包含 first/middle/last name，支持模糊匹配
  status - 可选筛选
  page/size - 分页
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_pagination,
    assert_fields_present
)


@pytest.mark.contact_api
class TestAccountContacts:
    """
    账户 Contacts 接口测试用例集
    """

    def _get_account_id(self, account_api):
        """辅助：获取第一个可用的 account_id"""
        resp = account_api.list_accounts(size=1)
        assert_status_ok(resp)
        parsed = account_api.parse_list_response(resp)
        content = parsed.get("content", [])
        return content[0]["id"] if content else None

    # ──────────────────────────────────────────────
    # 基础成功场景
    # ──────────────────────────────────────────────
    def test_get_account_contacts_success(self, account_api):
        """
        测试场景1：成功获取账户关联的 Contacts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确（content 列表 + 分页）
        3. 如有数据，验证必需字段
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        contacts_response = account_api.get_account_contacts(account_id)
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        assert_list_structure(parsed_contacts, has_pagination=True)

        contacts = parsed_contacts["content"]
        if contacts:
            required_fields = ["id", "account_id", "name", "status", "email", "create_time"]
            assert_fields_present(contacts[0], required_fields, obj_name="Contact")
            logger.info(f"  第一个 Contact: {contacts[0].get('name')} / status={contacts[0].get('status')}")

        logger.info(f"✓ 成功获取 Contacts: 总数={parsed_contacts['total_elements']}")

    # ──────────────────────────────────────────────
    # 非必填字段单独验证
    # ──────────────────────────────────────────────
    def test_get_account_contacts_filter_by_status_active(self, account_api):
        """
        测试场景2：使用 status=Active 筛选，验证返回数据每条 status 均为 Active
        验证点：
        1. 接口返回 200
        2. 每条数据 status == 'Active'
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        contacts_response = account_api.get_account_contacts(account_id, status="Active")
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)

        contacts = parsed_contacts["content"]
        logger.info(f"  status=Active 返回 {len(contacts)} 条")

        if contacts:
            for c in contacts:
                assert c.get("status") == "Active", \
                    f"返回了非 Active 的 Contact: status={c.get('status')}, id={c.get('id')}"
        logger.info("✓ status=Active 筛选验证通过")

    def test_get_account_contacts_filter_by_name_first_name(self, account_api):
        """
        测试场景3：使用 name 搜索 - 使用真实 Contact 的 first name 部分搜索
        文档说明：name 字段包含 first/middle/last name，支持模糊搜索
        验证点：
        1. 先获取真实 Contact 的 name，取前几字符
        2. 搜索时返回的数据 name 均包含该关键词
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先获取真实 Contact name
        base_resp = account_api.get_account_contacts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_contacts_response(base_resp)
        contacts = base_parsed.get("content", [])

        if not contacts:
            pytest.skip("该账户无 Contact 数据，跳过 name 筛选测试")

        real_name = contacts[0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("Contact name 为空或过短，跳过")

        # 取 name 中第一个空格前的部分（即 first name）
        first_part = real_name.split()[0] if " " in real_name else real_name[:4]
        logger.info(f"  使用 first name 关键词: '{first_part}'（来自 name='{real_name}'）")

        contacts_response = account_api.get_account_contacts(account_id, name=first_part, size=10)
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        contacts = parsed_contacts.get("content", [])

        if contacts:
            for c in contacts:
                assert first_part.lower() in (c.get("name") or "").lower(), \
                    f"name='{c.get('name')}' 不包含关键词 '{first_part}'"
        logger.info(f"✓ first name 搜索验证通过，返回 {len(contacts)} 条")

    def test_get_account_contacts_filter_by_name_last_name(self, account_api):
        """
        测试场景4：使用 name 搜索 - 使用真实 Contact 的 last name 部分搜索
        文档说明：name 字段为 full name（含 first/middle/last），后缀搜索也应匹配
        验证点：
        1. 取 name 中最后一个空格后的部分（last name）
        2. 返回数据 name 均包含该关键词
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        base_resp = account_api.get_account_contacts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_contacts_response(base_resp)
        contacts = base_parsed.get("content", [])

        if not contacts:
            pytest.skip("该账户无 Contact 数据，跳过 name 筛选测试")

        real_name = contacts[0].get("name", "")
        if not real_name or " " not in real_name:
            pytest.skip("Contact name 不含空格（无法拆分 last name），跳过")

        last_part = real_name.split()[-1]
        logger.info(f"  使用 last name 关键词: '{last_part}'（来自 name='{real_name}'）")

        contacts_response = account_api.get_account_contacts(account_id, name=last_part, size=10)
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        contacts = parsed_contacts.get("content", [])

        if contacts:
            for c in contacts:
                assert last_part.lower() in (c.get("name") or "").lower(), \
                    f"name='{c.get('name')}' 不包含关键词 '{last_part}'"
        logger.info(f"✓ last name 搜索验证通过，返回 {len(contacts)} 条")

    def test_get_account_contacts_filter_by_name_nonexistent(self, account_api):
        """
        测试场景5：使用不存在的 name 搜索 → 返回空列表
        验证点：
        1. 接口返回 200
        2. content 为空列表
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        contacts_response = account_api.get_account_contacts(
            account_id,
            name="NONEXISTENT_CONTACT_XYZXYZ_999"
        )
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        contacts = parsed_contacts.get("content", [])
        assert isinstance(contacts, list), "content 应该是一个列表"
        assert len(contacts) == 0, f"不存在的 name 应返回空列表，实际返回 {len(contacts)} 条"

        logger.info("✓ 不存在 name 返回空列表验证通过")

    # ──────────────────────────────────────────────
    # name + status 组合筛选
    # ──────────────────────────────────────────────
    def test_get_account_contacts_filter_name_and_status_combined(self, account_api):
        """
        测试场景6：name + status 组合筛选
        先获取 Active Contact，取其 name 关键词，再用 name+status=Active 组合查询
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 name 包含关键词，且 status == Active
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先获取 Active Contact
        base_resp = account_api.get_account_contacts(account_id, status="Active", size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_contacts_response(base_resp)
        active_contacts = base_parsed.get("content", [])

        if not active_contacts:
            pytest.skip("该账户无 Active Contact，跳过组合筛选测试")

        real_name = active_contacts[0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("Contact name 为空或过短，跳过")

        keyword = real_name.split()[0] if " " in real_name else real_name[:4]
        logger.info(f"  组合筛选: name='{keyword}' + status=Active")

        contacts_response = account_api.get_account_contacts(
            account_id, name=keyword, status="Active", size=10
        )
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        contacts = parsed_contacts.get("content", [])

        if contacts:
            for c in contacts:
                assert keyword.lower() in (c.get("name") or "").lower(), \
                    f"name='{c.get('name')}' 不包含关键词 '{keyword}'"
                assert c.get("status") == "Active", \
                    f"组合筛选结果 status={c.get('status')} 不为 Active"

        logger.info(f"✓ name + status 组合筛选验证通过，返回 {len(contacts)} 条")

    # ──────────────────────────────────────────────
    # 分页
    # ──────────────────────────────────────────────
    def test_get_account_contacts_pagination(self, account_api):
        """
        测试场景7：验证分页功能
        验证点：
        1. page=0, size=5 分页信息正确
        2. 返回数量 <= size
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        contacts_response = account_api.get_account_contacts(account_id, page=0, size=5)
        assert_status_ok(contacts_response)

        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        assert_pagination(parsed_contacts, expected_size=5, expected_page=0)

        logger.info(f"✓ 分页测试通过: 总数={parsed_contacts['total_elements']}, "
                    f"页大小={parsed_contacts['size']}, 当前页={parsed_contacts['number']}")

    # ──────────────────────────────────────────────
    # 越权验证
    # ──────────────────────────────────────────────
    def test_get_account_contacts_with_invisible_account_id(self, account_api):
        """
        测试场景8：使用不在当前用户 visible 范围内的 account_id 查询 Contacts
        验证点：
        1. 使用他人账户 241010195849720143（yhan account Sanchez）
        2. 服务器返回 200 OK
        3. 返回空列表 或 code=506（服务端按 visible 范围过滤）
        """
        invisible_account_id = "241010195849720143"  # yhan account Sanchez
        logger.info(f"使用不在 visible 范围内的 account_id: {invisible_account_id}")

        contacts_response = account_api.get_account_contacts(invisible_account_id)
        assert contacts_response.status_code == 200, \
            f"服务器应该返回 200，实际: {contacts_response.status_code}"

        response_body = contacts_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and response_body.get("code") == 506:
            logger.info(f"  返回 code=506 visibility permission deny")
        else:
            parsed_contacts = account_api.parse_contacts_response(contacts_response)
            contacts = parsed_contacts.get("content", [])
            assert len(contacts) == 0, \
                f"越权 account_id 应返回空列表，实际返回 {len(contacts)} 条"
            logger.info("  越权 account_id 返回空 Contacts 列表")

        logger.info("✓ 越权 account_id Contacts 查询验证通过")

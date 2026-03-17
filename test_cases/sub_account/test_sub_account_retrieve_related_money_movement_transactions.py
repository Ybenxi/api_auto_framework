"""
Sub Account Related Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/transactions 接口
对应文档标题: Retrieve Related Money Movement Transactions
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.transactions_api
class TestSubAccountRetrieveRelatedMoneyMovementTransactions:
    """
    Sub Account 相关交易查询接口测试用例集
    """

    def _get_sa_id(self, sa_api):
        """辅助：获取第一个可用的 Sub Account ID"""
        resp = sa_api.list_sub_accounts(page=0, size=1)
        assert resp.status_code == 200
        parsed = sa_api.parse_list_response(resp)
        subs = parsed.get("content", [])
        if not subs:
            return None
        return subs[0].get("id")

    def test_retrieve_related_transactions_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 相关的 Money Movement Transactions
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用交易接口返回 200
        3. 必需字段存在
        4. 验证交易属于该 Sub Account（隔离性验证）
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=2)
        assert list_response.status_code == 200

        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行测试")

        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")

        txn_response = sa_api.get_related_transactions(sub_account_id, page=0, size=10)
        assert txn_response.status_code == 200, \
            f"接口返回状态码错误: {txn_response.status_code}"

        parsed_txn = sa_api.parse_list_response(txn_response)
        assert not parsed_txn.get("error"), f"响应解析失败: {parsed_txn.get('message')}"

        transactions = parsed_txn.get("content", [])
        logger.info(f"  总交易数: {parsed_txn['total_elements']}, 返回 {len(transactions)} 条")

        if transactions:
            txn = transactions[0]
            required_fields = ["id", "status", "transaction_type", "payment_type"]
            for field in required_fields:
                assert field in txn, f"交易记录缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {txn.get(field)}")

            # sub_account_id 一致性验证
            if "sub_account_id" in txn:
                for t in transactions:
                    assert t.get("sub_account_id") == sub_account_id, \
                        f"交易 sub_account_id={t.get('sub_account_id')} 与请求 {sub_account_id} 不一致"
                logger.info(f"  ✓ 所有交易 sub_account_id 一致")
            elif len(sub_accounts) >= 2:
                # 隔离性验证：两个 Sub Account 的交易不重叠
                sa2_id = sub_accounts[1].get("id")
                txn2_resp = sa_api.get_related_transactions(sa2_id, page=0, size=10)
                parsed_txn2 = sa_api.parse_list_response(txn2_resp)
                sa1_ids = {t["id"] for t in transactions if "id" in t}
                sa2_ids = {t["id"] for t in parsed_txn2.get("content", []) if "id" in t}
                overlap = sa1_ids & sa2_ids
                assert not overlap, f"两个 Sub Account 的交易有重叠，不应该: {overlap}"
                logger.info(f"  ✓ 隔离性验证通过：SA1={len(sa1_ids)}条, SA2={len(sa2_ids)}条, 无重叠")

        logger.info("✓ 获取交易成功")

    @pytest.mark.parametrize("status", [
        "Reviewing", "Cancelled", "Completed", "Processing", "Failed"
    ])
    def test_retrieve_related_transactions_with_status_filter(self, login_session, status):
        """
        测试场景2：使用 status 筛选交易（覆盖全部5个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 status 均与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        logger.info(f"使用 status='{status}' 筛选交易")
        txn_response = sa_api.get_related_transactions(sa_id, status=status, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = sa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if not transactions:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for txn in transactions:
                assert txn.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {txn.get('status')}"
            logger.info(f"✓ {len(transactions)} 条交易均为 {status} 状态")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_retrieve_related_transactions_with_transaction_type_filter(self, login_session, transaction_type):
        """
        测试场景3：使用 transaction_type 筛选交易（覆盖全部2个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 transaction_type 均与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        logger.info(f"使用 transaction_type='{transaction_type}' 筛选交易")
        txn_response = sa_api.get_related_transactions(sa_id, transaction_type=transaction_type, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = sa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if not transactions:
            logger.info(f"  ⚠️ transaction_type='{transaction_type}' 无数据，跳过筛选值验证")
        else:
            for txn in transactions:
                assert txn.get("transaction_type") == transaction_type, \
                    f"筛选结果包含非 {transaction_type}: {txn.get('transaction_type')}"
            logger.info(f"✓ {len(transactions)} 条交易均为 {transaction_type} 类型")

    @pytest.mark.parametrize("payment_type", [
        "ACH", "Wire", "Check", "Internal_Pay", "Instant_Pay", "Account_Transfer"
    ])
    def test_retrieve_related_transactions_with_payment_type_filter(self, login_session, payment_type):
        """
        测试场景4：使用 payment_type 筛选交易（覆盖全部6个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 payment_type 均与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        logger.info(f"使用 payment_type='{payment_type}' 筛选交易")
        txn_response = sa_api.get_related_transactions(sa_id, payment_type=payment_type, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = sa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if not transactions:
            logger.info(f"  ⚠️ payment_type='{payment_type}' 无数据，跳过筛选值验证")
        else:
            for txn in transactions:
                assert txn.get("payment_type") == payment_type, \
                    f"筛选结果包含非 {payment_type}: {txn.get('payment_type')}"
            logger.info(f"✓ {len(transactions)} 条交易均为 {payment_type} 类型")

    def test_retrieve_related_transactions_with_transaction_id_filter(self, login_session):
        """
        测试场景5：使用 transaction_id 精确筛选
        先 list 获取真实 transaction_id，再筛选，验证返回的就是那条交易
        验证点：
        1. 接口返回 200
        2. 返回的交易 id 与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        # Step 1: 获取真实 transaction_id
        base_resp = sa_api.get_related_transactions(sa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = sa_api.parse_list_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if not base_txns:
            pytest.skip(f"Sub Account {sa_id} 无交易数据，跳过 transaction_id 筛选测试")

        real_txn_id = base_txns[0].get("id")
        if not real_txn_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_txn_id}")

        # Step 2: 精确筛选
        txn_response = sa_api.get_related_transactions(sa_id, transaction_id=real_txn_id, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = sa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])

        assert len(transactions) > 0, f"transaction_id='{real_txn_id}' 筛选结果为空"
        for txn in transactions:
            assert txn.get("id") == real_txn_id, \
                f"筛选结果包含不匹配的 id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(transactions)} 条")

    def test_retrieve_related_transactions_pagination(self, login_session):
        """
        测试场景6：验证交易列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        txn_response = sa_api.get_related_transactions(sa_id, page=0, size=5)
        assert txn_response.status_code == 200

        parsed_txn = sa_api.parse_list_response(txn_response)

        assert parsed_txn["size"] == 5, f"size 不正确: {parsed_txn['size']}"
        assert parsed_txn["number"] == 0, f"number 不正确: {parsed_txn['number']}"
        assert len(parsed_txn.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总交易数: {parsed_txn['total_elements']}")
        logger.info(f"  每页大小: {parsed_txn['size']}, 当前页: {parsed_txn['number']}")
        logger.info(f"  实际返回: {len(parsed_txn.get('content', []))} 条")

    def test_retrieve_related_transactions_with_invisible_sub_account_id(self, login_session):
        """
        测试场景7：使用不在当前用户 visible 范围内的 sub_account_id 查询交易
        验证点：
        1. 使用他人账户关联的 sub_account_id（不属于当前用户）
        2. 服务器返回 200 OK（统一错误处理设计）
        3. 返回空列表 或 code != 200（服务端按 visible 范围过滤）
        """
        sa_api = SubAccountAPI(session=login_session)

        invisible_sa_id = "241010195849720143"  # yhan account（不属于当前用户）
        logger.info(f"使用不在 visible 范围内的 Sub Account ID: {invisible_sa_id}")

        txn_response = sa_api.get_related_transactions(invisible_sa_id, page=0, size=10)

        assert txn_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {txn_response.status_code}"

        response_body = txn_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  返回业务错误码: code={response_body.get('code')}, msg={response_body.get('error_message')}")
        else:
            parsed_txn = sa_api.parse_list_response(txn_response)
            assert len(parsed_txn.get("content", [])) == 0, \
                f"越权 Sub Account ID 应返回空交易列表，实际有 {len(parsed_txn.get('content', []))} 条"
            logger.info("  越权 Sub Account ID 返回空交易列表")

        logger.info("✓ 越权 Sub Account ID 交易查询验证通过")

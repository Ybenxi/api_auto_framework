"""
Financial Account Related Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/transactions 接口
对应文档标题: Retrieve Related Money Movement Transactions
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


def _get_fa_id_with_transactions(fa_api: FinancialAccountAPI, page_size: int = 20):
    """
    遍历 FA 列表，找到第一个有 Money Movement Transactions 数据的 FA ID。
    返回 (fa_id, first_transaction) 或 (None, None)。
    """
    list_resp = fa_api.list_financial_accounts(page=0, size=page_size)
    if list_resp.status_code != 200:
        return None, None

    accounts = fa_api.parse_list_response(list_resp).get("content", [])
    for acc in accounts:
        fa_id = acc.get("id")
        if not fa_id:
            continue
        txn_resp = fa_api.get_related_transactions(fa_id, page=0, size=1)
        if txn_resp.status_code != 200:
            continue
        txns = fa_api.parse_list_response(txn_resp).get("content", [])
        if txns:
            logger.info(f"  找到有交易数据的 FA: {fa_id}（交易总数 via 分页元数据）")
            return fa_id, txns[0]

    return None, None


@pytest.mark.financial_account
@pytest.mark.transactions_api
class TestFinancialAccountRetrieveRelatedMoneyMovementTransactions:
    """
    Financial Account 相关交易查询接口测试用例集
    """

    def test_retrieve_related_transactions_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的 Money Movement Transactions
        验证点：
        1. 使用已知有交易数据的 FA ID（避免循环遍历导致大量 API 调用）
        2. 接口返回 200，total_elements > 0
        3. 必需字段存在
        4. 隔离性验证：返回的交易属于该 FA
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # 直接使用已知有交易数据的 FA ID，避免 _get_fa_id_with_transactions 循环遍历
        # 注：_get_fa_id_with_transactions 会对每个 FA 都发一次请求，FA 多时产生大量 API 调用
        KNOWN_FA_WITH_TXNS = "251212054048470568"  # 已验证：有 ACH/Wire 等交易记录
        fa_id = KNOWN_FA_WITH_TXNS

        logger.info(f"使用有数据的 Financial Account ID: {fa_id}")

        txn_response = fa_api.get_related_transactions(fa_id, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)
        assert not parsed_txn.get("error")

        transactions = parsed_txn.get("content", [])
        if not transactions:
            pytest.skip(f"FA {fa_id} 暂无交易数据，跳过验证")
        logger.info(f"  总交易数: {parsed_txn['total_elements']}, 返回 {len(transactions)} 条")

        # 必需字段验证
        txn = transactions[0]
        required_fields = ["id", "status", "transaction_type", "payment_type"]
        for field in required_fields:
            assert field in txn, f"交易记录缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {txn.get(field)}")

        # financial_account_id 一致性
        if "financial_account_id" in txn:
            for t in transactions:
                assert t.get("financial_account_id") == fa_id, \
                    f"交易 financial_account_id={t.get('financial_account_id')} 与请求 {fa_id} 不一致"
            logger.info("  ✓ 所有交易 financial_account_id 一致")

        logger.info("✓ 获取交易成功")

    @pytest.mark.parametrize("status", [
        "Reviewing", "Cancelled", "Completed", "Processing", "Failed"
    ])
    def test_retrieve_related_transactions_with_status_filter(self, login_session, status):
        """
        测试场景2：使用 status 筛选交易（覆盖全部5个枚举值）
        验证点：
        1. 使用有数据的 FA
        2. 接口返回 200
        3. 返回的每条交易 status 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_transactions(fa_api)
        if not fa_id:
            pytest.skip("未找到有交易数据的 Financial Account")

        logger.info(f"使用 status='{status}' 筛选交易（FA: {fa_id}）")
        txn_response = fa_api.get_related_transactions(fa_id, status=status, page=0, size=10)
        assert txn_response.status_code == 200

        transactions = fa_api.parse_list_response(txn_response).get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if not transactions:
            logger.info(f"  ⚠️ status='{status}' 在此 FA 中无数据，跳过筛选值验证")
        else:
            for txn in transactions:
                assert txn.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {txn.get('status')}, id={txn.get('id')}"
            logger.info(f"✓ {len(transactions)} 条交易均为 {status} 状态")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_retrieve_related_transactions_with_transaction_type_filter(self, login_session, transaction_type):
        """
        测试场景3：使用 transaction_type 筛选交易（覆盖全部2个枚举值）
        验证点：
        1. 使用有数据的 FA
        2. 接口返回 200
        3. 返回的每条交易 transaction_type 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_transactions(fa_api)
        if not fa_id:
            pytest.skip("未找到有交易数据的 Financial Account")

        logger.info(f"使用 transaction_type='{transaction_type}' 筛选（FA: {fa_id}）")
        txn_response = fa_api.get_related_transactions(fa_id, transaction_type=transaction_type, page=0, size=10)
        assert txn_response.status_code == 200

        transactions = fa_api.parse_list_response(txn_response).get("content", [])
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
        1. 使用有数据的 FA
        2. 接口返回 200
        3. 返回的每条交易 payment_type 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_transactions(fa_api)
        if not fa_id:
            pytest.skip("未找到有交易数据的 Financial Account")

        logger.info(f"使用 payment_type='{payment_type}' 筛选（FA: {fa_id}）")
        txn_response = fa_api.get_related_transactions(fa_id, payment_type=payment_type, page=0, size=10)
        assert txn_response.status_code == 200

        transactions = fa_api.parse_list_response(txn_response).get("content", [])
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
        先从有数据的 FA 中取真实 transaction_id，再用它筛选，验证返回的就是那条交易
        验证点：
        1. 接口返回 200
        2. 返回的交易 id 与筛选值精确一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_txn = _get_fa_id_with_transactions(fa_api)
        if not fa_id or not first_txn:
            pytest.skip("未找到有交易数据的 Financial Account")

        real_txn_id = first_txn.get("id")
        if not real_txn_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"使用真实 transaction_id: {real_txn_id}（FA: {fa_id}）")

        txn_response = fa_api.get_related_transactions(fa_id, transaction_id=real_txn_id, page=0, size=10)
        assert txn_response.status_code == 200

        transactions = fa_api.parse_list_response(txn_response).get("content", [])

        assert len(transactions) > 0, f"transaction_id='{real_txn_id}' 筛选结果为空"
        for txn in transactions:
            assert txn.get("id") == real_txn_id, \
                f"筛选结果包含不匹配的 transaction_id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(transactions)} 条")

    def test_retrieve_related_transactions_with_date_range(self, login_session):
        """
        测试场景6：使用 start_date/end_date 日期范围筛选
        从有数据的 FA 中取真实交易日期，验证筛选结果的日期均在范围内
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 create_date 在筛选范围内
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_txn = _get_fa_id_with_transactions(fa_api)
        if not fa_id or not first_txn:
            pytest.skip("未找到有交易数据的 Financial Account")

        created_date = first_txn.get("create_date") or first_txn.get("created_date", "")
        date_str = created_date[:10] if created_date and len(created_date) >= 10 else "2024-01-01"
        logger.info(f"使用日期范围: {date_str} ~ {date_str}（FA: {fa_id}）")

        txn_response = fa_api.get_related_transactions(
            fa_id, start_date=date_str, end_date=date_str, page=0, size=10
        )
        assert txn_response.status_code == 200

        transactions = fa_api.parse_list_response(txn_response).get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if transactions:
            for txn in transactions:
                txn_date = txn.get("create_date") or txn.get("created_date", "")
                if txn_date and len(txn_date) >= 10:
                    assert txn_date[:10] == date_str, \
                        f"返回交易日期 '{txn_date[:10]}' 不在筛选日期 '{date_str}' 范围内"
            logger.info(f"✓ 日期范围筛选验证通过，所有 {len(transactions)} 条数据日期匹配")
        else:
            logger.warning(f"  ⚠️ 日期 {date_str} 范围内无数据（可能同日无多条，属正常）")

        logger.info("✓ 日期筛选测试完成")

    def test_retrieve_related_transactions_with_invisible_fa_id(self, login_session):
        """
        测试场景7：使用越权 FA ID 查询交易 → 返回空或拒绝
        验证点：
        1. 使用越权 FA ID：241010195850134683（ACTC Yhan FA）
        2. 服务器返回 200
        3. 返回空列表 或 code=506
        """
        fa_api = FinancialAccountAPI(session=login_session)

        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA
        logger.info(f"使用越权 FA ID 查询交易: {invisible_fa_id}")

        txn_response = fa_api.get_related_transactions(invisible_fa_id, page=0, size=10)
        assert txn_response.status_code == 200

        response_body = txn_response.json()
        if isinstance(response_body, dict) and response_body.get("code") == 506:
            logger.info("  返回 code=506 visibility permission deny")
        else:
            parsed_txn = fa_api.parse_list_response(txn_response)
            assert len(parsed_txn.get("content", [])) == 0, \
                f"越权 FA ID 应返回空列表，实际返回 {len(parsed_txn.get('content', []))} 条"
            logger.info("  越权 FA ID 返回空交易列表")

        logger.info("✓ 越权 FA ID 交易查询验证通过")

    def test_retrieve_related_transactions_pagination(self, login_session):
        """
        测试场景8：验证交易列表分页功能
        验证点：
        1. 使用有数据的 FA，确保分页元数据有意义
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_transactions(fa_api)
        if not fa_id:
            pytest.skip("未找到有交易数据的 Financial Account")

        logger.info(f"使用分页参数 page=0, size=5（FA: {fa_id}）")
        txn_response = fa_api.get_related_transactions(fa_id, page=0, size=5)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)

        assert parsed_txn["size"] == 5, f"size 不正确: {parsed_txn['size']}"
        assert parsed_txn["number"] == 0, f"number 不正确: {parsed_txn['number']}"
        assert len(parsed_txn.get("content", [])) <= 5, "返回数量超过 size=5"
        # 有数据时验证 total_elements > 0
        assert parsed_txn["total_elements"] > 0, \
            f"有数据的 FA 分页 total_elements 应 > 0，实际: {parsed_txn['total_elements']}"

        logger.info(f"✓ 分页测试通过: total={parsed_txn['total_elements']}, "
                    f"size={parsed_txn['size']}, page={parsed_txn['number']}, "
                    f"返回={len(parsed_txn.get('content', []))} 条")

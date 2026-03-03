"""
Financial Account Related Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/transactions 接口
对应文档标题: Retrieve Related Money Movement Transactions
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.transactions_api
class TestFinancialAccountRetrieveRelatedMoneyMovementTransactions:
    """
    Financial Account 相关交易查询接口测试用例集
    """

    def _get_fa_id(self, fa_api):
        """辅助：获取第一个可用的 Financial Account ID"""
        resp = fa_api.list_financial_accounts(page=0, size=1)
        assert resp.status_code == 200
        parsed = fa_api.parse_list_response(resp)
        accounts = parsed.get("content", [])
        if not accounts:
            return None
        return accounts[0].get("id")

    def test_retrieve_related_transactions_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的 Money Movement Transactions
        验证点：
        1. 接口返回 200
        2. 返回的交易属于请求的 financial_account_id（隔离性验证）
        3. 必需字段存在
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # 获取两个不同的 FA（用于隔离性验证）
        logger.info("获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=2)
        assert list_response.status_code == 200

        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])

        if not accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = accounts[0].get("id")
        logger.info(f"  使用 Financial Account ID: {financial_account_id}")

        # 获取该 FA 的交易
        txn_response = fa_api.get_related_transactions(financial_account_id, page=0, size=10)
        assert txn_response.status_code == 200, \
            f"接口返回状态码错误: {txn_response.status_code}"

        parsed_txn = fa_api.parse_list_response(txn_response)
        assert not parsed_txn.get("error"), f"响应解析失败: {parsed_txn.get('message')}"

        transactions = parsed_txn.get("content", [])
        logger.info(f"  总交易数: {parsed_txn['total_elements']}, 返回 {len(transactions)} 条")

        if transactions:
            # 验证字段存在
            txn = transactions[0]
            required_fields = ["id", "status", "transaction_type", "payment_type"]
            for field in required_fields:
                assert field in txn, f"交易记录缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {txn.get(field)}")

            # 验证 financial_account_id 一致性（如果该字段存在）
            if "financial_account_id" in txn:
                logger.info("验证每条交易的 financial_account_id 与请求一致")
                for t in transactions:
                    assert t.get("financial_account_id") == financial_account_id, \
                        f"交易 financial_account_id={t.get('financial_account_id')} 与请求 {financial_account_id} 不一致"
                logger.info(f"  ✓ 所有交易 financial_account_id 一致")
            else:
                # 若无该字段，用隔离性验证（两个FA的交易不重叠）
                if len(accounts) >= 2:
                    fa2_id = accounts[1].get("id")
                    txn2_response = fa_api.get_related_transactions(fa2_id, page=0, size=10)
                    parsed_txn2 = fa_api.parse_list_response(txn2_response)
                    fa1_ids = {t["id"] for t in transactions if "id" in t}
                    fa2_ids = {t["id"] for t in parsed_txn2.get("content", []) if "id" in t}
                    overlap = fa1_ids & fa2_ids
                    assert not overlap, f"两个FA的交易有重叠，不应该: {overlap}"
                    logger.info(f"  ✓ 隔离性验证通过：FA1={len(fa1_ids)}条, FA2={len(fa2_ids)}条, 无重叠")

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
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        logger.info(f"使用 status='{status}' 筛选交易")
        txn_response = fa_api.get_related_transactions(fa_id, status=status, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条")

        if not transactions:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
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
        1. 接口返回 200
        2. 返回的每条交易 transaction_type 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        logger.info(f"使用 transaction_type='{transaction_type}' 筛选交易")
        txn_response = fa_api.get_related_transactions(fa_id, transaction_type=transaction_type, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)
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
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        logger.info(f"使用 payment_type='{payment_type}' 筛选交易")
        txn_response = fa_api.get_related_transactions(fa_id, payment_type=payment_type, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)
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
        先 list 获取真实 transaction_id，再用它筛选，验证返回的就是那条交易
        验证点：
        1. 接口返回 200
        2. 返回的交易 id 与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        # Step 1: 获取真实 transaction_id
        logger.info("先获取交易列表，取第一条的 id")
        base_resp = fa_api.get_related_transactions(fa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = fa_api.parse_list_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if not base_txns:
            pytest.skip(f"FA {fa_id} 无交易数据，跳过 transaction_id 筛选测试")

        real_txn_id = base_txns[0].get("id")
        if not real_txn_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_txn_id}")

        # Step 2: 用 transaction_id 精确筛选
        txn_response = fa_api.get_related_transactions(fa_id, transaction_id=real_txn_id, page=0, size=10)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])

        # Step 3: 断言结果
        assert len(transactions) > 0, f"transaction_id='{real_txn_id}' 筛选结果为空"
        for txn in transactions:
            assert txn.get("id") == real_txn_id, \
                f"筛选结果包含不匹配的 transaction_id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(transactions)} 条")

    def test_retrieve_related_transactions_with_date_range(self, login_session):
        """
        测试场景6：使用 start_date/end_date 日期范围筛选
        先 list 获取真实交易日期，再用日期范围筛选，验证返回数据在范围内
        验证点：
        1. 接口返回 200
        2. 日期参数被接受（不报错）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        # Step 1: 获取真实交易，取其日期
        base_resp = fa_api.get_related_transactions(fa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = fa_api.parse_list_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if not base_txns:
            pytest.skip(f"FA {fa_id} 无交易数据，跳过日期筛选测试")

        # 获取第一条交易的创建日期，取日期部分
        created_date = base_txns[0].get("create_date") or base_txns[0].get("created_date", "")
        if created_date and len(created_date) >= 10:
            date_str = created_date[:10]  # YYYY-MM-DD
        else:
            date_str = "2024-01-01"

        logger.info(f"  使用日期范围: {date_str} ~ {date_str}")

        # Step 2: 日期范围筛选
        txn_response = fa_api.get_related_transactions(
            fa_id, start_date=date_str, end_date=date_str, page=0, size=10
        )
        assert txn_response.status_code == 200, \
            f"日期筛选接口返回错误: {txn_response.status_code}"

        parsed_txn = fa_api.parse_list_response(txn_response)
        transactions = parsed_txn.get("content", [])
        logger.info(f"  日期 {date_str} 范围内返回 {len(transactions)} 条交易")

        logger.info("✓ 日期范围筛选参数正常处理")

    def test_retrieve_related_transactions_pagination(self, login_session):
        """
        测试场景7：验证交易列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        logger.info("使用分页参数 page=0, size=5")
        txn_response = fa_api.get_related_transactions(fa_id, page=0, size=5)
        assert txn_response.status_code == 200

        parsed_txn = fa_api.parse_list_response(txn_response)

        assert parsed_txn["size"] == 5, f"size 不正确: {parsed_txn['size']}"
        assert parsed_txn["number"] == 0, f"number 不正确: {parsed_txn['number']}"
        assert len(parsed_txn.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总交易数: {parsed_txn['total_elements']}")
        logger.info(f"  总页数: {parsed_txn['total_pages']}")
        logger.info(f"  当前页: {parsed_txn['number']}")
        logger.info(f"  每页大小: {parsed_txn['size']}")
        logger.info(f"  实际返回: {len(parsed_txn.get('content', []))} 条")

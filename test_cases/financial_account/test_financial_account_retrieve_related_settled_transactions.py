"""
Financial Account Related Settled Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/settled-transactions 接口
对应文档标题: Retrieve Related Settled Transactions
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.settled_transactions_api
class TestFinancialAccountRetrieveRelatedSettledTransactions:
    """
    Financial Account 相关已结算交易查询接口测试用例集
    """

    def _get_fa_id(self, fa_api):
        resp = fa_api.list_financial_accounts(page=0, size=1)
        assert resp.status_code == 200
        parsed = fa_api.parse_list_response(resp)
        accounts = parsed.get("content", [])
        return accounts[0].get("id") if accounts else None

    def test_retrieve_settled_transactions_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的已结算交易
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用已结算交易接口返回 200
        3. 必需字段存在
        4. 返回的交易属于该 FA（隔离性验证）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        list_response = fa_api.list_financial_accounts(page=0, size=2)
        assert list_response.status_code == 200

        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])

        if not accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = accounts[0].get("id")
        logger.info(f"  使用 Financial Account ID: {financial_account_id}")

        settled_response = fa_api.get_settled_transactions(financial_account_id, page=0, size=10)
        assert settled_response.status_code == 200, \
            f"接口返回状态码错误: {settled_response.status_code}"

        parsed_settled = fa_api.parse_list_response(settled_response)
        assert not parsed_settled.get("error"), f"响应解析失败: {parsed_settled.get('message')}"

        transactions = parsed_settled.get("content", [])
        logger.info(f"  总交易数: {parsed_settled['total_elements']}, 返回 {len(transactions)} 条")

        if transactions:
            txn = transactions[0]
            required_fields = ["id", "transaction_type", "symbol", "settle_date"]
            for field in required_fields:
                assert field in txn, f"已结算交易记录缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {txn.get(field)}")

            # financial_account_id 一致性验证
            if "financial_account_id" in txn:
                for t in transactions:
                    assert t.get("financial_account_id") == financial_account_id, \
                        f"交易 financial_account_id={t.get('financial_account_id')} 与请求 {financial_account_id} 不一致"
                logger.info(f"  ✓ 所有交易 financial_account_id 一致")
            elif len(accounts) >= 2:
                fa2_id = accounts[1].get("id")
                txn2_resp = fa_api.get_settled_transactions(fa2_id, page=0, size=10)
                parsed2 = fa_api.parse_list_response(txn2_resp)
                fa1_ids = {t["id"] for t in transactions if "id" in t}
                fa2_ids = {t["id"] for t in parsed2.get("content", []) if "id" in t}
                overlap = fa1_ids & fa2_ids
                assert not overlap, f"两个FA已结算交易有重叠: {overlap}"
                logger.info(f"  ✓ 隔离性验证通过：FA1={len(fa1_ids)}条, FA2={len(fa2_ids)}条, 无重叠")

        logger.info("✓ 获取已结算交易成功")

    def test_retrieve_settled_transactions_with_date_filter(self, login_session):
        """
        测试场景2：使用日期范围筛选已结算交易
        先获取真实交易日期再用于筛选
        验证点：
        1. 接口返回 200
        2. 日期参数正常处理
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        # 先取真实日期
        base_resp = fa_api.get_settled_transactions(fa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = fa_api.parse_list_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if base_txns:
            date_val = base_txns[0].get("settle_date") or base_txns[0].get("trade_date", "")
            date_str = date_val[:10] if date_val and len(date_val) >= 10 else "2024-01-01"
        else:
            date_str = "2024-01-01"

        logger.info(f"使用日期范围筛选: {date_str}")
        settled_response = fa_api.get_settled_transactions(
            fa_id, begin_date=date_str, end_date=date_str, page=0, size=10
        )

        assert settled_response.status_code == 200

        parsed_settled = fa_api.parse_list_response(settled_response)
        transactions = parsed_settled.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条匹配的交易记录")

        logger.info("✓ 日期筛选测试完成")

    def test_retrieve_settled_transactions_with_security_filter(self, login_session):
        """
        测试场景3：使用 security 筛选已结算交易
        先 list 获取真实 symbol，再用它筛选，验证每条结果的 symbol 包含关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 symbol 包含筛选关键词
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        # 先取真实 symbol
        base_resp = fa_api.get_settled_transactions(fa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = fa_api.parse_list_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if not base_txns:
            pytest.skip(f"FA {fa_id} 无已结算交易数据，跳过 security 筛选测试")

        real_symbol = base_txns[0].get("symbol", "")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        keyword = real_symbol[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 symbol='{real_symbol}'）")

        settled_response = fa_api.get_settled_transactions(fa_id, security=keyword, page=0, size=10)
        assert settled_response.status_code == 200

        parsed_settled = fa_api.parse_list_response(settled_response)
        transactions = parsed_settled.get("content", [])

        if transactions:
            for txn in transactions:
                # security 支持模糊匹配（symbol/name/cusip）
                matched = (
                    keyword.lower() in (txn.get("symbol") or "").lower()
                    or keyword.lower() in (txn.get("security_name") or "").lower()
                    or keyword.lower() in (txn.get("cusip") or "").lower()
                )
                assert matched, f"返回的交易不包含关键词 '{keyword}': symbol={txn.get('symbol')}"
            logger.info(f"✓ security 筛选验证通过，返回 {len(transactions)} 条")
        else:
            logger.info(f"  ⚠️ security='{keyword}' 无数据，跳过筛选值验证")

        logger.info("✓ Security 筛选测试完成")

    def test_retrieve_settled_transactions_pagination(self, login_session):
        """
        测试场景4：验证已结算交易列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        settled_response = fa_api.get_settled_transactions(fa_id, page=0, size=5)
        assert settled_response.status_code == 200

        parsed_settled = fa_api.parse_list_response(settled_response)

        assert parsed_settled["size"] == 5, f"size 不正确: {parsed_settled['size']}"
        assert parsed_settled["number"] == 0, f"number 不正确: {parsed_settled['number']}"
        assert len(parsed_settled.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总交易数: {parsed_settled['total_elements']}")
        logger.info(f"  每页大小: {parsed_settled['size']}, 当前页: {parsed_settled['number']}")

    def test_retrieve_settled_transactions_response_fields(self, login_session):
        """
        测试场景5：验证已结算交易响应字段完整性
        验证点：
        1. 接口返回 200
        2. 交易对象必须包含必需字段（assert 断言）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id = self._get_fa_id(fa_api)
        if not fa_id:
            pytest.skip("没有可用的 Financial Account")

        settled_response = fa_api.get_settled_transactions(fa_id, page=0, size=1)
        assert settled_response.status_code == 200

        parsed_settled = fa_api.parse_list_response(settled_response)
        transactions = parsed_settled.get("content", [])

        if not transactions:
            pytest.skip("无已结算交易数据，跳过字段验证")

        txn = transactions[0]
        required_fields = ["id", "symbol", "transaction_type", "settle_date"]

        logger.info("验证已结算交易必需字段")
        for field in required_fields:
            assert field in txn, f"已结算交易缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {txn.get(field)}")

        logger.info("✓ 字段完整性验证通过")

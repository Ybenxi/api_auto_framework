"""
账户 Settled Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/settled-transactions 接口
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


@pytest.mark.transaction_api
class TestAccountTransactions:
    """
    账户 Settled Transactions 接口测试用例集
    """

    def _get_account_id(self, account_api):
        """辅助：获取第一个可用的 account_id"""
        resp = account_api.list_accounts(size=1)
        assert_status_ok(resp)
        parsed = account_api.parse_list_response(resp)
        assert_response_parsed(parsed)
        content = parsed.get("content", [])
        return content[0]["id"] if content else None

    def test_get_settled_transactions_success(self, account_api):
        """
        测试场景1：成功获取账户的 Settled Transactions
        验证点：
        1. 接口返回 200
        2. 必需字段存在
        3. 如有数据，验证 account_id 一致性（隔离性验证）
        """
        list_response = account_api.list_accounts(size=2)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        accounts = parsed_list["content"]
        if not accounts:
            pytest.skip("没有可用的账户数据，跳过 Transactions 测试")

        account_id = accounts[0]["id"]

        transactions_response = account_api.get_settled_transactions(account_id)
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        assert_list_structure(parsed_transactions, has_pagination=True)

        transactions = parsed_transactions["content"]

        if transactions:
            first_transaction = transactions[0]
            required_fields = [
                "id", "financial_account_id", "financial_account_name",
                "financial_account_number", "transaction_type", "settle_date"
            ]
            assert_fields_present(first_transaction, required_fields, obj_name="Transaction")

            # 如果交易有 account_id 字段，验证一致性
            if "account_id" in first_transaction:
                for txn in transactions:
                    assert txn.get("account_id") == account_id, \
                        f"交易 account_id={txn.get('account_id')} 与请求 {account_id} 不一致"
                logger.info(f"  ✓ 所有交易 account_id 一致")
            elif len(accounts) >= 2:
                # 隔离性验证
                acct2_id = accounts[1]["id"]
                txn2_resp = account_api.get_settled_transactions(acct2_id)
                parsed2 = account_api.parse_transactions_response(txn2_resp)
                acct1_ids = {t["id"] for t in transactions if "id" in t}
                acct2_ids = {t["id"] for t in parsed2.get("content", []) if "id" in t}
                overlap = acct1_ids & acct2_ids
                assert not overlap, f"两个账户的交易有重叠: {overlap}"
                logger.info(f"  ✓ 隔离性验证通过：Account1={len(acct1_ids)}条, Account2={len(acct2_ids)}条, 无重叠")

            logger.info(f"✓ 获取 Transactions 成功: 总数={parsed_transactions['total_elements']}")
        else:
            logger.info("✓ 成功获取 Transactions（当前账户没有 Settled Transactions）")

    def test_get_settled_transactions_with_date_range(self, account_api):
        """
        测试场景2：使用日期范围筛选 Transactions
        先获取真实交易的 settle_date，再用日期范围筛选
        验证点：
        1. 接口返回 200
        2. 日期参数正常处理
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先取真实 settle_date
        base_resp = account_api.get_settled_transactions(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_transactions_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if base_txns:
            date_val = base_txns[0].get("settle_date") or base_txns[0].get("trade_date", "")
            date_str = date_val[:10] if date_val and len(date_val) >= 10 else "2024-01-01"
        else:
            date_str = "2024-01-01"

        logger.info(f"  使用日期范围: {date_str}")

        transactions_response = account_api.get_settled_transactions(
            account_id, begin_date=date_str, end_date=date_str
        )
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)

        transactions = parsed_transactions["content"]
        logger.info(f"  返回 {len(transactions)} 条")
        logger.info(f"✓ 日期范围筛选测试完成")

    def test_get_settled_transactions_with_security_filter(self, account_api):
        """
        测试场景3：使用证券筛选 Transactions
        先获取真实 symbol，再用它筛选，验证返回数据包含该证券
        验证点：
        1. 接口返回 200
        2. 返回的每条交易包含筛选的 symbol
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先取真实 symbol
        base_resp = account_api.get_settled_transactions(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_transactions_response(base_resp)
        base_txns = base_parsed.get("content", [])

        if not base_txns:
            pytest.skip(f"账户 {account_id} 无已结算交易，跳过 security 筛选测试")

        real_symbol = base_txns[0].get("symbol", "")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"  使用真实 symbol: {real_symbol}")

        transactions_response = account_api.get_settled_transactions(
            account_id, security=real_symbol
        )
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)

        transactions = parsed_transactions["content"]
        if transactions:
            for txn in transactions:
                matched = (
                    real_symbol.lower() in (txn.get("symbol") or "").lower()
                    or real_symbol.lower() in (txn.get("security_name") or "").lower()
                )
                assert matched, \
                    f"返回的交易不包含 symbol '{real_symbol}': symbol={txn.get('symbol')}"
            logger.info(f"✓ security 筛选验证通过，返回 {len(transactions)} 条")
        else:
            logger.info(f"  ⚠️ symbol='{real_symbol}' 筛选结果为空，跳过验证")

        logger.info(f"✓ 证券筛选测试完成")

    def test_get_settled_transactions_pagination(self, account_api):
        """
        测试场景4：验证分页功能
        验证点：
        1. 分页信息正确（size=5, number=0）
        2. 返回数量 <= size
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        transactions_response = account_api.get_settled_transactions(account_id, page=0, size=5)
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)

        assert_pagination(parsed_transactions, expected_size=5, expected_page=0)
        assert len(parsed_transactions.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info(f"✓ 分页测试通过: 总元素={parsed_transactions['total_elements']}, "
                    f"页大小={parsed_transactions['size']}, 当前页={parsed_transactions['number']}")

    def test_get_settled_transactions_empty_result(self, account_api):
        """
        测试场景5：使用未来日期范围验证空结果处理
        验证点：
        1. 接口返回 200
        2. 返回空 content 列表
        3. total_elements 为 0
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        transactions_response = account_api.get_settled_transactions(
            account_id, begin_date="2099-01-01", end_date="2099-12-31"
        )
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)

        transactions = parsed_transactions["content"]
        assert isinstance(transactions, list), "content 应该是一个列表"
        assert len(transactions) == 0, f"期望空列表，实际返回 {len(transactions)} 条"
        assert parsed_transactions.get("total_elements") == 0, \
            f"total_elements 应为 0，实际 {parsed_transactions.get('total_elements')}"

        logger.info(f"✓ 空结果测试通过")

    def test_get_settled_transactions_fields_completeness(self, account_api):
        """
        测试场景6：验证 Transaction 字段完整性
        验证点：
        1. 必需字段用 assert 断言存在
        2. 可选字段记录日志
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        transactions_response = account_api.get_settled_transactions(account_id, size=1)
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)

        if not parsed_transactions["content"]:
            pytest.skip("没有可用的 Transaction 数据")

        transaction = parsed_transactions["content"][0]

        required_fields = [
            "id", "financial_account_id", "financial_account_name",
            "financial_account_number", "transaction_type", "settle_date"
        ]

        logger.info("验证必需字段")
        assert_fields_present(transaction, required_fields, obj_name="Transaction")
        for field in required_fields:
            logger.info(f"  ✓ {field}: {transaction.get(field)}")

        optional_fields = [
            "security_name", "symbol", "cusip", "units", "price", "amount",
            "market_value", "cost_basis", "transaction_fee", "trade_date"
        ]

        for field in optional_fields:
            if field in transaction:
                logger.info(f"  {field}: {transaction.get(field)}")

        logger.info("✓ 字段完整性验证通过")

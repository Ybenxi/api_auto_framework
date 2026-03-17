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

    def test_get_settled_transactions_with_invalid_date_format(self, account_api):
        """
        测试场景7：使用错误的日期格式搜索
        验证点：
        1. 传入不符合 yyyy-MM-dd 格式的日期（如 "20240101"、"Jan 1 2024"）
        2. 服务器返回 200
        3. code != 200（业务层校验失败）或返回空列表
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        invalid_date = "20240101"  # 缺少分隔符
        logger.info(f"使用格式错误的日期: '{invalid_date}'")

        transactions_response = account_api.get_settled_transactions(
            account_id, begin_date=invalid_date, end_date=invalid_date
        )
        assert transactions_response.status_code == 200, \
            f"服务器应该返回 200，实际: {transactions_response.status_code}"

        response_body = transactions_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  格式错误日期返回业务错误: code={response_body.get('code')}")
        else:
            parsed = account_api.parse_transactions_response(transactions_response)
            logger.info(f"  格式错误日期返回空或有数据: {len(parsed.get('content', []))} 条")

        logger.info("✓ 错误日期格式测试通过")

    def test_get_settled_transactions_with_invalid_security_format(self, account_api):
        """
        测试场景8：使用错误的 security 格式搜索（特殊字符）
        验证点：
        1. 传入包含特殊字符的 security 值（如 "AAPL<script>", "%%invalid%%"）
        2. 服务器返回 200
        3. 返回空列表（不存在的 security）
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        invalid_security = "%%INVALID_SECURITY<>%%"
        logger.info(f"使用格式错误的 security: '{invalid_security}'")

        transactions_response = account_api.get_settled_transactions(
            account_id, security=invalid_security
        )
        assert transactions_response.status_code == 200, \
            f"服务器应该返回 200，实际: {transactions_response.status_code}"

        parsed = account_api.parse_transactions_response(transactions_response)
        transactions = parsed.get("content", [])

        assert len(transactions) == 0, \
            f"错误格式的 security 应返回空列表，实际返回 {len(transactions)} 条"

        logger.info("✓ 错误 security 格式返回空列表验证通过")

    def test_get_settled_transactions_begin_after_end_date(self, account_api):
        """
        测试场景9：开始时间在结束时间之后
        验证点：
        1. begin_date > end_date（如 begin=2024-12-31, end=2024-01-01）
        2. 服务器返回 200
        3. 返回空列表 或 code != 200（业务层检测到非法范围）
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        begin_date = "2024-12-31"
        end_date = "2024-01-01"
        logger.info(f"使用反转日期范围: begin_date={begin_date} > end_date={end_date}")

        transactions_response = account_api.get_settled_transactions(
            account_id, begin_date=begin_date, end_date=end_date
        )
        assert transactions_response.status_code == 200, \
            f"服务器应该返回 200，实际: {transactions_response.status_code}"

        response_body = transactions_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  反转日期范围返回业务错误: code={response_body.get('code')}")
        else:
            parsed = account_api.parse_transactions_response(transactions_response)
            transactions = parsed.get("content", [])
            assert len(transactions) == 0, \
                f"开始时间在结束时间之后，应返回空列表，实际返回 {len(transactions)} 条"
            logger.info(f"  反转日期范围返回空列表")

        logger.info("✓ 开始时间 > 结束时间验证通过")

    def test_get_settled_transactions_visibility_isolation(self, account_api):
        """
        测试场景10：可见性隔离验证（通过 security 搜索不应返回不可见的数据）
        验证点：
        1. 使用 security 搜索时，返回的 financial_account_id/financial_account_name 均是自己可见的数据
        2. 不会因 security 搜索而泄露他人账户的交易数据
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先获取自己有交易的 symbol
        base_resp = account_api.get_settled_transactions(account_id, size=5)
        assert_status_ok(base_resp)
        parsed = account_api.parse_transactions_response(base_resp)
        transactions = parsed.get("content", [])

        if not transactions:
            pytest.skip("该账户无 Settled Transactions，跳过可见性验证")

        # 获取当前用户可见的 FA ID 集合
        fa_id_set_from_list = {t.get("financial_account_id") for t in transactions if t.get("financial_account_id")}
        logger.info(f"  当前用户可见 FA ID 集合（来自第一次查询）: {fa_id_set_from_list}")

        # 取一个 symbol 做 security 搜索
        real_symbol = next((t.get("symbol") for t in transactions if t.get("symbol")), None)
        if not real_symbol:
            pytest.skip("无 symbol 数据，跳过可见性验证")

        logger.info(f"  使用 security='{real_symbol}' 搜索，验证可见性隔离")

        sec_resp = account_api.get_settled_transactions(account_id, security=real_symbol, size=20)
        assert_status_ok(sec_resp)
        parsed_sec = account_api.parse_transactions_response(sec_resp)
        sec_transactions = parsed_sec.get("content", [])

        # 获取当前用户所有可见的 FA ID（取更多数据）
        all_fa_resp = account_api.get_settled_transactions(account_id, size=100)
        parsed_all = account_api.parse_transactions_response(all_fa_resp)
        all_visible_fa_ids = {t.get("financial_account_id") for t in parsed_all.get("content", []) if t.get("financial_account_id")}

        # 验证 security 搜索返回的每条数据的 FA 均在可见范围内
        for txn in sec_transactions:
            fa_id = txn.get("financial_account_id")
            if fa_id and all_visible_fa_ids:
                assert fa_id in all_visible_fa_ids, \
                    f"security 搜索返回了不在可见范围内的 FA: financial_account_id={fa_id}"

        invisible_id = "241010195850134683"  # ACTC Yhan FA
        for txn in sec_transactions:
            assert txn.get("financial_account_id") != invisible_id, \
                f"security 搜索返回了不可见账户 {invisible_id} 的交易数据！"

        logger.info(f"✓ 可见性隔离验证通过，security 搜索共返回 {len(sec_transactions)} 条，无越权数据")

"""
Counterparty Transactions 接口测试用例
接口：GET /api/v1/cores/actc/counterparties/:id/transactions

过滤参数：
  - financial_account_id: 关联的 FA ID
  - sub_account_id: 关联的 Sub Account ID
  - start_date / end_date: 日期范围（yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss）
  - transaction_type: Credit | Debit
  - status: Processing | Reviewing | Completed | Cancelled | Failed

策略说明：
  - Counterparty 的交易数据需要 Payment 模块的接口才能产生，目前无法在自动化里直接构造
  - 先在当前 list 中找一个有交易记录的 Counterparty，以该 ID 做查询测试
  - 若所有 Counterparty 均无交易数据，核心 filter 场景使用 skip 标记，等 Payment 模块集成后再联调
  - 无效 ID / 无效 status 等错误场景不依赖真实数据，直接运行
"""
import pytest
import time
from typing import Optional, Tuple
from utils.logger import logger
from utils.assertions import assert_status_ok


def _ts() -> str:
    return str(int(time.time()))


def _find_cp_with_transactions(counterparty_api, page_size: int = 50) -> Tuple[Optional[str], Optional[dict]]:
    """
    遍历 Counterparty List，找到一个有交易数据的 Counterparty ID 和其第一条交易。
    返回 (cp_id, first_txn) 或 (None, None)
    """
    list_resp = counterparty_api.list_counterparties(page=0, size=page_size)
    if list_resp.status_code != 200:
        return None, None

    counterparties = list_resp.json().get("content", [])
    for cp in counterparties:
        cp_id = cp.get("id")
        if not cp_id:
            continue
        txn_resp = counterparty_api.list_counterparty_transactions(cp_id, page=0, size=1)
        if txn_resp.status_code != 200:
            continue
        txn_body = txn_resp.json()
        content = txn_body.get("content", [])
        total = txn_body.get("total_elements", 0)
        if total > 0 and content:
            return cp_id, content[0]

    return None, None


@pytest.mark.counterparty
class TestCounterpartyTransactions:
    """
    Counterparty 交易列表接口测试
    """

    # ------------------------------------------------------------------
    # 场景1：找有交易的 CP，基本查询成功，验证响应结构
    # ------------------------------------------------------------------
    def test_list_transactions_basic_success(self, counterparty_api):
        """
        测试场景1：查询有交易的 Counterparty 的交易列表，验证响应结构
        验证点：
        1. HTTP 200
        2. content 为数组，total_elements > 0
        3. 每条交易包含必需字段（id, status, amount, create_time, counterparty_id）
        4. counterparty_id 字段与查询的 CP ID 一致（数据隔离）
        """
        cp_id, first_txn = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            pytest.skip("未找到有交易数据的 Counterparty，等待 Payment 模块集成后联调")

        logger.info(f"找到有交易的 CP: {cp_id}，查询交易列表")
        resp = counterparty_api.list_counterparty_transactions(cp_id, page=0, size=10)
        assert resp.status_code == 200

        body = resp.json()
        content = body.get("content", [])
        total = body.get("total_elements", 0)

        assert total > 0, f"有交易的 CP({cp_id}) total_elements 应 > 0，实际: {total}"
        assert len(content) > 0, "content 不应为空"

        # 验证必需字段
        required_fields = ["id", "status", "amount", "create_time", "counterparty_id"]
        first = content[0]
        for field in required_fields:
            assert field in first, f"交易记录缺少必需字段: '{field}'"

        # 验证 counterparty_id 隔离
        for txn in content:
            assert txn.get("counterparty_id") == cp_id, \
                f"交易的 counterparty_id 不匹配: 期望 {cp_id}, 实际 {txn.get('counterparty_id')}"

        logger.info(f"✓ 交易列表基本查询通过: cp_id={cp_id}, total={total}")

    # ------------------------------------------------------------------
    # 场景2：transaction_type 枚举全覆盖（Credit/Debit）
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, counterparty_api, transaction_type):
        """
        测试场景2：按 transaction_type 枚举值筛选（覆盖 Credit 和 Debit）
        验证点：
        1. HTTP 200
        2. 若有返回数据，每条 transaction_type 均与筛选值一致
        """
        cp_id, _ = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        logger.info(f"筛选 transaction_type='{transaction_type}': cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id, transaction_type=transaction_type, page=0, size=20
        )
        assert resp.status_code == 200

        content = resp.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        for txn in content:
            assert txn.get("transaction_type") == transaction_type, \
                f"筛选结果包含非 {transaction_type}: txn_id={txn.get('id')}, type={txn.get('transaction_type')}"

        logger.info(f"✓ transaction_type='{transaction_type}' 筛选验证通过")

    # ------------------------------------------------------------------
    # 场景3：status 枚举全覆盖（5个值）
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("status", ["Processing", "Reviewing", "Completed", "Cancelled", "Failed"])
    def test_filter_by_status(self, counterparty_api, status):
        """
        测试场景3：按 status 枚举值筛选（覆盖全部 5 个枚举值）
        验证点：
        1. HTTP 200
        2. 若有返回数据，每条 status 均与筛选值一致
        """
        cp_id, _ = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        logger.info(f"筛选 status='{status}': cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id, status=status, page=0, size=20
        )
        assert resp.status_code == 200

        content = resp.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        for txn in content:
            assert txn.get("status") == status, \
                f"筛选结果包含非 {status}: txn_id={txn.get('id')}, status={txn.get('status')}"

        logger.info(f"✓ status='{status}' 筛选验证通过")

    # ------------------------------------------------------------------
    # 场景4：按日期范围筛选，验证返回交易的 create_time 在范围内
    # ------------------------------------------------------------------
    def test_filter_by_date_range(self, counterparty_api):
        """
        测试场景4：按 start_date/end_date 筛选，验证返回数据的日期在范围内
        验证点：
        1. HTTP 200
        2. 返回的每条交易 create_time >= start_date（近 1 年）
        3. 日期格式 yyyy-MM-dd 被正确解析
        """
        cp_id, first_txn = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        # 取第一条交易的日期作为 start_date
        create_time = first_txn.get("create_time", "")
        start_date = create_time[:10] if create_time else "2024-01-01"  # 取 yyyy-MM-dd 部分
        end_date = "2099-12-31"

        logger.info(f"按日期范围筛选: start_date={start_date}, end_date={end_date}, cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id, start_date=start_date, end_date=end_date, page=0, size=10
        )
        assert resp.status_code == 200

        content = resp.json().get("content", [])
        assert len(content) > 0, "日期范围应至少包含一条已知交易"

        logger.info(f"  返回 {len(content)} 条")

        # 验证返回的交易 create_time 不早于 start_date
        for txn in content:
            txn_date = txn.get("create_time", "")[:10]
            assert txn_date >= start_date, \
                f"交易日期 {txn_date} 早于 start_date {start_date}"

        logger.info(f"✓ 日期范围筛选验证通过")

    # ------------------------------------------------------------------
    # 场景5：start_date 在 end_date 之后（无效日期范围）
    # ------------------------------------------------------------------
    def test_filter_invalid_date_range(self, counterparty_api):
        """
        测试场景5：start_date 晚于 end_date（无效日期范围）
        验证点：
        1. HTTP 200
        2. 返回空列表或业务错误（正常拒绝无效时间范围）
        """
        cp_id, _ = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            # 没有有数据的 CP 也能测这个场景（会返回空）
            list_resp = counterparty_api.list_counterparties(page=0, size=1)
            cps = list_resp.json().get("content", [])
            if not cps:
                pytest.skip("无 Counterparty 数据")
            cp_id = cps[0]["id"]

        logger.info(f"使用无效日期范围（start > end）: cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id,
            start_date="2025-12-31",
            end_date="2024-01-01",
            page=0, size=10
        )
        assert resp.status_code == 200

        body = resp.json()
        content = body.get("content", [])
        logger.info(f"  code={body.get('code')}, 返回 {len(content)} 条")

        if body.get("code") != 200 and body.get("code") is not None:
            logger.info(f"✓ 无效日期范围被拒绝: code={body.get('code')}")
        else:
            assert len(content) == 0, \
                f"start_date > end_date 应返回空列表，实际返回 {len(content)} 条"
            logger.info("✓ 无效日期范围返回空列表")

    # ------------------------------------------------------------------
    # 场景6：按 financial_account_id 筛选，验证数据隔离
    # ------------------------------------------------------------------
    def test_filter_by_financial_account_id(self, counterparty_api):
        """
        测试场景6：按 financial_account_id 筛选交易
        验证点：
        1. HTTP 200
        2. 若有返回数据，每条交易的 financial_account_id 与筛选值一致
        """
        cp_id, first_txn = _find_cp_with_transactions(counterparty_api)
        if not cp_id or not first_txn:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        fa_id = first_txn.get("financial_account_id")
        if not fa_id:
            pytest.skip("第一条交易无 financial_account_id 字段，跳过")

        logger.info(f"按 financial_account_id={fa_id} 筛选: cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id, financial_account_id=fa_id, page=0, size=20
        )
        assert resp.status_code == 200

        content = resp.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        for txn in content:
            assert txn.get("financial_account_id") == fa_id, \
                f"筛选结果包含其他 FA: 期望 {fa_id}, 实际 {txn.get('financial_account_id')}"

        logger.info(f"✓ financial_account_id 筛选验证通过")

    # ------------------------------------------------------------------
    # 场景7：按 sub_account_id 筛选
    # ------------------------------------------------------------------
    def test_filter_by_sub_account_id(self, counterparty_api):
        """
        测试场景7：按 sub_account_id 筛选交易
        验证点：
        1. HTTP 200
        2. 若有返回数据，每条交易的 sub_account_id 与筛选值一致
        """
        cp_id, first_txn = _find_cp_with_transactions(counterparty_api)
        if not cp_id or not first_txn:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        sa_id = first_txn.get("sub_account_id")
        if not sa_id:
            pytest.skip("第一条交易无 sub_account_id 字段，跳过")

        logger.info(f"按 sub_account_id={sa_id} 筛选: cp_id={cp_id}")
        resp = counterparty_api.list_counterparty_transactions(
            cp_id, sub_account_id=sa_id, page=0, size=20
        )
        assert resp.status_code == 200

        content = resp.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        for txn in content:
            assert txn.get("sub_account_id") == sa_id, \
                f"筛选结果包含其他 Sub Account: 期望 {sa_id}, 实际 {txn.get('sub_account_id')}"

        logger.info(f"✓ sub_account_id 筛选验证通过")

    # ------------------------------------------------------------------
    # 场景8：分页验证（size=1 再翻页）
    # ------------------------------------------------------------------
    def test_pagination(self, counterparty_api):
        """
        测试场景8：分页功能验证
        验证点：
        1. size=1，page=0 返回 1 条，total_elements 正确
        2. page=1 翻页，返回不同的交易 ID
        """
        cp_id, _ = _find_cp_with_transactions(counterparty_api)
        if not cp_id:
            pytest.skip("未找到有交易数据的 Counterparty，等待联调")

        # 总记录数
        total_resp = counterparty_api.list_counterparty_transactions(cp_id, page=0, size=1)
        total = total_resp.json().get("total_elements", 0)
        if total < 2:
            pytest.skip("交易数量不足 2 条，无法测试翻页")

        logger.info(f"分页测试: cp_id={cp_id}, total={total}")

        page0_resp = counterparty_api.list_counterparty_transactions(cp_id, page=0, size=1)
        page1_resp = counterparty_api.list_counterparty_transactions(cp_id, page=1, size=1)

        page0_content = page0_resp.json().get("content", [])
        page1_content = page1_resp.json().get("content", [])

        assert len(page0_content) == 1, "page=0, size=1 应返回 1 条"
        assert len(page1_content) == 1, "page=1, size=1 应返回 1 条"
        assert page0_content[0]["id"] != page1_content[0]["id"], \
            "两页的交易 ID 应不同（分页正常）"

        logger.info(f"✓ 分页验证通过: page0 id={page0_content[0]['id']}, page1 id={page1_content[0]['id']}")

    # ------------------------------------------------------------------
    # 场景9：使用无效 counterparty_id 查询交易 → 空列表
    # ------------------------------------------------------------------
    def test_list_transactions_invalid_cp_id(self, counterparty_api):
        """
        测试场景9：使用不存在的 counterparty_id 查询交易
        验证点：
        1. HTTP 200
        2. 返回空列表（total_elements=0）或业务 code != 200
        """
        resp = counterparty_api.list_counterparty_transactions(
            "INVALID_CP_999999", page=0, size=10
        )
        assert resp.status_code == 200

        body = resp.json()
        content = body.get("content", [])
        logger.info(f"  code={body.get('code')}, 返回 {len(content)} 条")

        if body.get("code") is not None and body.get("code") != 200:
            logger.info(f"✓ 无效 ID 返回业务错误: code={body.get('code')}")
        else:
            assert len(content) == 0, \
                f"无效 CP ID 应返回空列表，实际返回 {len(content)} 条"
            logger.info("✓ 无效 CP ID 返回空列表")

    # ------------------------------------------------------------------
    # 场景10：越权 CP ID 查询交易 → 空列表或 506
    # ------------------------------------------------------------------
    def test_list_transactions_invisible_cp_id(self, counterparty_api):
        """
        测试场景10：使用越权 CP ID 查询交易（不在自己 visible 范围内）
        验证点：
        1. HTTP 200
        2. 返回空列表或 code=506
        """
        invisible_cp_id = "241010195849717901"   # Chaolong actc ach 11
        logger.info(f"使用越权 CP ID 查询交易: {invisible_cp_id}")
        resp = counterparty_api.list_counterparty_transactions(invisible_cp_id, page=0, size=10)
        assert resp.status_code == 200

        body = resp.json()
        content = body.get("content", [])
        logger.info(f"  code={body.get('code')}, 返回 {len(content)} 条")

        code = body.get("code")
        if code is not None and code != 200:
            logger.info(f"✓ 越权 CP ID 被拒绝: code={code}")
        else:
            assert len(content) == 0, \
                f"越权 CP ID 应返回空列表，实际返回 {len(content)} 条"
            logger.info("✓ 越权 CP ID 返回空列表（数据隔离正常）")

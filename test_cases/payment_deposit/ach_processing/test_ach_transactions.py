"""
ACH Processing - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/ach/transactions 接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus, PaymentTransactionType
from api.financial_account_api import FinancialAccountAPI


@pytest.mark.ach_processing
@pytest.mark.list_api
class TestACHTransactions:
    """ACH交易列表测试"""

    def _get_base_data(self, api):
        """获取基础数据：第一条交易的详情"""
        resp = api.list_transactions(page=0, size=1)
        assert resp.status_code == 200
        return resp.json().get("content", [])

    def test_list_transactions_success(self, ach_processing_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. content 是数组，必需字段存在
        """
        logger.info("测试场景1：成功获取ACH交易列表")

        response = ach_processing_api.list_transactions(page=0, size=10)
        assert response.status_code == 200

        data = response.json()
        content = data.get("content", [])
        assert isinstance(content, list), "content 应为数组"

        if content:
            txn = content[0]
            required_fields = ["id", "status"]
            for field in required_fields:
                assert field in txn, f"交易记录缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {txn.get(field)}")

        logger.info(f"✓ 交易列表获取成功，返回 {len(content)} 条")

    @pytest.mark.parametrize("status", [
        "Reviewing", "Cancelled", "Completed", "Processing", "Failed"
    ])
    def test_filter_by_status(self, ach_processing_api, status):
        """
        测试场景2：按 status 筛选（覆盖全部5个枚举值）
        验证点：每条返回交易的 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = ach_processing_api.list_transactions(status=status, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        if not content:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for txn in content:
                assert txn.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {txn.get('status')}"
            logger.info(f"✓ {len(content)} 条交易均为 {status} 状态")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, ach_processing_api, transaction_type):
        """
        测试场景3：按 transaction_type 筛选（覆盖全部2个枚举值）
        验证点：每条返回交易的 transaction_type 均与筛选值一致
        """
        logger.info(f"测试场景3：按 transaction_type='{transaction_type}' 筛选")

        response = ach_processing_api.list_transactions(transaction_type=transaction_type, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        if not content:
            logger.info(f"  ⚠️ transaction_type='{transaction_type}' 无数据，跳过验证")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type, \
                    f"筛选结果包含非 {transaction_type}: {txn.get('transaction_type')}"
            logger.info(f"✓ {len(content)} 条交易均为 {transaction_type} 类型")

    def test_filter_by_transaction_id(self, ach_processing_api):
        """
        测试场景4：按 transaction_id 精确筛选
        先 list 获取真实 id，再用它筛选，验证返回的就是那条交易
        """
        logger.info("测试场景4：按 transaction_id 精确筛选")

        base_txns = self._get_base_data(ach_processing_api)
        if not base_txns:
            pytest.skip("无ACH交易数据，跳过 transaction_id 筛选测试")

        real_id = base_txns[0].get("id")
        if not real_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_id}")

        response = ach_processing_api.list_transactions(transaction_id=real_id, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        assert len(content) > 0, f"transaction_id='{real_id}' 筛选结果为空"
        for txn in content:
            assert txn.get("id") == real_id, f"筛选结果包含不匹配的 id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(content)} 条")

    def test_filter_by_financial_account_id(self, ach_processing_api, login_session):
        """
        测试场景5：按 financial_account_id 筛选
        先从交易列表或 FA 列表获取真实 ID，再筛选并验证
        """
        logger.info("测试场景5：按 financial_account_id 筛选")

        # 从交易中获取真实 financial_account_id
        base_txns = self._get_base_data(ach_processing_api)
        if base_txns and base_txns[0].get("financial_account_id"):
            real_fa_id = base_txns[0]["financial_account_id"]
        else:
            # 从 FA list 获取
            fa_api = FinancialAccountAPI(session=login_session)
            fa_parsed = fa_api.parse_list_response(fa_api.list_financial_accounts(page=0, size=1))
            if not fa_parsed.get("content"):
                pytest.skip("无可用 Financial Account 数据，跳过")
            real_fa_id = fa_parsed["content"][0]["id"]

        logger.info(f"  使用 financial_account_id: {real_fa_id}")

        response = ach_processing_api.list_transactions(financial_account_id=real_fa_id, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        if content and "financial_account_id" in content[0]:
            for txn in content:
                assert txn.get("financial_account_id") == real_fa_id, \
                    f"返回了不属于该FA的交易: {txn.get('financial_account_id')}"
            logger.info(f"✓ financial_account_id 筛选验证通过")

    def test_pagination(self, ach_processing_api):
        """
        测试场景6：分页查询
        验证点：size=5, number=0, 返回数量 <= size
        """
        logger.info("测试场景6：分页查询")

        response = ach_processing_api.list_transactions(page=0, size=5)
        assert response.status_code == 200

        raw = response.json()
        # 兼容有 data 包装层和无包装层两种格式
        data = raw.get("data", raw)
        assert data.get("size") == 5, f"size 不正确: {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: {data.get('number')}"
        assert len(data.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页验证通过")

    def test_undefined_response_fields(self, ach_processing_api):
        """测试场景7：未定义响应字段验证（文档问题记录）"""
        logger.info("测试场景7：未定义响应字段验证")

        response = ach_processing_api.list_transactions(size=1)
        content = response.json().get("content", [])

        if content:
            transaction = content[0]
            undefined = ["fee", "completed_date", "financial_account_name",
                         "counterparty_name", "schedule_date", "transaction_id",
                         "first_party", "same_day", "reversal_id", "direction",
                         "reference_number"]

            found = [f for f in undefined if f in transaction]
            if found:
                logger.warning(f"⚠️ 检测到未定义字段: {found}")

        logger.info("✓ 未定义字段验证完成")

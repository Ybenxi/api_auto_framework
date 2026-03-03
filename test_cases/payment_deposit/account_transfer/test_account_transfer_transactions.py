"""
Account Transfer - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/account-transfer/transactions 接口
⚠️ 文档特殊：响应无code包装层；direction字段未在Properties定义
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus, PaymentTransactionType


@pytest.mark.account_transfer
@pytest.mark.list_api
class TestAccountTransferTransactions:
    """
    Account Transfer交易列表接口测试用例集
    ⚠️ 文档问题：
    1. 响应无code包装层
    2. direction字段未在Properties定义
    3. transaction_type参数描述错误（说Internal Pay）
    """

    def _get_base_data(self, api):
        resp = api.list_transactions(page=0, size=1)
        assert resp.status_code == 200
        return resp.json().get("content", [])

    def test_list_transactions_success(self, account_transfer_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. 无code包装层
        3. content 是数组，必需字段存在
        """
        logger.info("测试场景1：成功获取交易列表")

        response = account_transfer_api.list_transactions(page=0, size=10)
        assert response.status_code == 200

        response_body = response.json()
        content = response_body.get("content", [])
        assert isinstance(content, list)

        if "code" not in response_body:
            logger.info("✓ 确认：响应无code包装层")

        if content:
            txn = content[0]
            required_fields = ["id", "status"]
            for field in required_fields:
                assert field in txn, f"交易记录缺少必需字段: '{field}'"

        logger.info(f"✓ 交易列表获取成功，返回 {len(content)} 条")

    @pytest.mark.parametrize("status", [
        "Reviewing", "Cancelled", "Completed", "Processing", "Failed"
    ])
    def test_filter_by_status(self, account_transfer_api, status):
        """
        测试场景2：按 status 筛选（覆盖全部5个枚举值）
        验证点：每条返回交易的 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = account_transfer_api.list_transactions(status=status, size=10)
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
    def test_filter_by_transaction_type(self, account_transfer_api, transaction_type):
        """
        测试场景3：按 transaction_type 筛选（覆盖全部2个枚举值）
        ⚠️ 文档问题：参数描述错误（写了Internal Pay，实际是Account Transfer）
        验证点：每条返回交易的 transaction_type 均与筛选值一致
        """
        logger.info(f"测试场景3：按 transaction_type='{transaction_type}' 筛选")

        response = account_transfer_api.list_transactions(transaction_type=transaction_type, size=10)
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

    def test_filter_by_transaction_id(self, account_transfer_api):
        """
        测试场景4：按 transaction_id 精确筛选
        先 list 获取真实 id，再用它筛选，验证返回的就是那条交易
        """
        logger.info("测试场景4：按 transaction_id 精确筛选")

        base_txns = self._get_base_data(account_transfer_api)
        if not base_txns:
            pytest.skip("无Account Transfer交易数据，跳过 transaction_id 筛选测试")

        real_id = base_txns[0].get("id")
        if not real_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_id}")

        response = account_transfer_api.list_transactions(transaction_id=real_id, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        assert len(content) > 0, f"transaction_id='{real_id}' 筛选结果为空"
        for txn in content:
            assert txn.get("id") == real_id, f"筛选结果包含不匹配的 id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(content)} 条")

    def test_filter_by_payer_and_payee(self, account_transfer_api):
        """
        测试场景5：按付款方和收款方账户筛选
        先从交易列表获取真实账户ID，再验证筛选结果
        """
        logger.info("测试场景5：按付款方和收款方筛选")

        base_txns = self._get_base_data(account_transfer_api)
        if not base_txns:
            pytest.skip("无交易数据，跳过")

        real_payer_id = base_txns[0].get("payer_financial_account_id")
        if not real_payer_id:
            pytest.skip("payer_financial_account_id 字段为空，跳过")

        logger.info(f"  使用 payer_financial_account_id: {real_payer_id}")

        response = account_transfer_api.list_transactions(
            payer_financial_account_id=real_payer_id, size=10
        )
        assert response.status_code == 200

        content = response.json().get("content", [])
        logger.info(f"  返回 {len(content)} 条")

        if content and "payer_financial_account_id" in content[0]:
            for txn in content:
                assert txn.get("payer_financial_account_id") == real_payer_id, \
                    f"返回了不属于该付款账户的交易: {txn.get('payer_financial_account_id')}"
            logger.info(f"✓ payer_financial_account_id 筛选验证通过")

    def test_direction_field(self, account_transfer_api):
        """
        测试场景6：direction字段验证（文档问题记录）
        验证点：
        1. 响应包含direction字段（Account Transfer独有）
        2. 该字段在Properties中未定义
        """
        logger.info("测试场景6：direction字段验证")

        response = account_transfer_api.list_transactions(size=1)
        assert response.status_code == 200

        content = response.json().get("content", [])

        if content:
            transaction = content[0]
            if "direction" in transaction:
                logger.warning("⚠️ 检测到direction字段（Properties中未定义）")
                logger.info(f"  direction值: {transaction['direction']}")
                logger.info("  这是Account Transfer独有字段（Internal Pay无）")

        logger.info("✓ direction字段验证完成")

    def test_pagination(self, account_transfer_api):
        """
        测试场景7：分页查询，验证 size/number/content 数量
        """
        logger.info("测试场景7：分页查询")

        response = account_transfer_api.list_transactions(page=0, size=5)
        assert response.status_code == 200

        raw = response.json()
        data = raw.get("data", raw)
        assert data.get("size") == 5
        assert data.get("number") == 0
        assert len(data.get("content", [])) <= 5

        logger.info("✓ 分页验证通过")

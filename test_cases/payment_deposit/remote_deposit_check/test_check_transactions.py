"""
Remote Deposit Check - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/checks/transactions 接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus


@pytest.mark.remote_deposit_check
@pytest.mark.list_api
class TestCheckTransactions:
    """Check交易列表测试"""

    def _get_base_data(self, api):
        resp = api.list_transactions(page=0, size=1)
        assert resp.status_code == 200
        return resp.json().get("content", [])

    def test_list_transactions_success(self, remote_deposit_check_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. content 是数组，必需字段存在
        """
        logger.info("测试场景1：成功获取Check交易列表")

        response = remote_deposit_check_api.list_transactions(page=0, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        assert isinstance(content, list)

        if content:
            txn = content[0]
            required_fields = ["id", "status"]
            for field in required_fields:
                assert field in txn, f"交易记录缺少必需字段: '{field}'"

        logger.info(f"✓ 交易列表获取成功，返回 {len(content)} 条")

    @pytest.mark.parametrize("status", [
        "Reviewing", "Cancelled", "Completed", "Processing", "Failed"
    ])
    def test_filter_by_status(self, remote_deposit_check_api, status):
        """
        测试场景2：按 status 筛选（覆盖全部5个枚举值）
        验证点：每条返回交易的 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = remote_deposit_check_api.list_transactions(status=status, size=10)
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

    def test_filter_by_transaction_id(self, remote_deposit_check_api):
        """
        测试场景3：按 transaction_id 精确筛选
        先 list 获取真实 id，再用它筛选，验证返回的就是那条交易
        """
        logger.info("测试场景3：按 transaction_id 精确筛选")

        base_txns = self._get_base_data(remote_deposit_check_api)
        if not base_txns:
            pytest.skip("无Check交易数据，跳过 transaction_id 筛选测试")

        real_id = base_txns[0].get("id")
        if not real_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_id}")

        response = remote_deposit_check_api.list_transactions(transaction_id=real_id, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        assert len(content) > 0, f"transaction_id='{real_id}' 筛选结果为空"
        for txn in content:
            assert txn.get("id") == real_id, f"筛选结果包含不匹配的 id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(content)} 条")

    def test_pagination(self, remote_deposit_check_api):
        """
        测试场景4：分页查询，验证 size/number/content 数量
        """
        logger.info("测试场景4：分页查询")

        response = remote_deposit_check_api.list_transactions(page=0, size=5)
        assert response.status_code == 200

        raw = response.json()
        data = raw.get("data", raw)
        assert data.get("size") == 5
        assert data.get("number") == 0
        assert len(data.get("content", [])) <= 5

        logger.info("✓ 分页验证通过")

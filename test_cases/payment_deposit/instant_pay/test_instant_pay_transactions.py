"""
Instant Pay - Transactions 接口测试用例
测试交易列表和Request Payment列表接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus, RequestPaymentStatus, WireDirection


@pytest.mark.instant_pay
@pytest.mark.list_api
class TestInstantPayTransactions:
    """Instant Pay交易列表测试"""

    def _get_base_data(self, api):
        resp = api.list_transactions(page=0, size=1)
        assert resp.status_code == 200
        return resp.json().get("content", [])

    def test_list_transactions_success(self, instant_pay_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. 无code包装层
        3. content 是数组，必需字段存在
        """
        logger.info("测试场景1：成功获取Instant Pay交易列表")

        response = instant_pay_api.list_transactions(page=0, size=10)
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
    def test_filter_by_status(self, instant_pay_api, status):
        """
        测试场景2：按 status 筛选（覆盖全部5个枚举值）
        验证点：每条返回交易的 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = instant_pay_api.list_transactions(status=status, size=10)
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

    def test_filter_by_transaction_id(self, instant_pay_api):
        """
        测试场景3：按 transaction_id 精确筛选
        先 list 获取真实 id，再用它筛选，验证返回的就是那条交易
        """
        logger.info("测试场景3：按 transaction_id 精确筛选")

        base_txns = self._get_base_data(instant_pay_api)
        if not base_txns:
            pytest.skip("无Instant Pay交易数据，跳过 transaction_id 筛选测试")

        real_id = base_txns[0].get("id")
        if not real_id:
            pytest.skip("transaction id 字段为空，跳过")

        logger.info(f"  使用真实 transaction_id: {real_id}")

        response = instant_pay_api.list_transactions(transaction_id=real_id, size=10)
        assert response.status_code == 200

        content = response.json().get("content", [])
        assert len(content) > 0, f"transaction_id='{real_id}' 筛选结果为空"
        for txn in content:
            assert txn.get("id") == real_id, f"筛选结果包含不匹配的 id: {txn.get('id')}"

        logger.info(f"✓ transaction_id 精确筛选验证通过，返回 {len(content)} 条")

    def test_pagination(self, instant_pay_api):
        """
        测试场景4：分页查询，验证 size/number/content 数量
        """
        logger.info("测试场景4：分页查询")

        response = instant_pay_api.list_transactions(page=0, size=5)
        assert response.status_code == 200

        raw = response.json()
        data = raw.get("data", raw)
        assert data.get("size") == 5
        assert data.get("number") == 0
        assert len(data.get("content", [])) <= 5

        logger.info("✓ 分页验证通过")


@pytest.mark.instant_pay
@pytest.mark.list_api
class TestInstantPayRequestPaymentTransactions:
    """Request Payment交易列表测试"""

    def test_list_request_payment_success(self, instant_pay_api):
        """
        测试场景5：成功获取Request Payment列表
        验证点：
        1. 接口返回 200
        2. 此接口有code包装层（与List Transactions不同）
        """
        logger.info("测试场景5：成功获取Request Payment列表")

        response = instant_pay_api.list_request_payment_transactions(page=0, size=10)
        assert response.status_code == 200

        response_body = response.json()
        if "code" in response_body:
            logger.info("✓ 此接口有code包装层（与List Transactions不同）")
            assert response_body.get("code") == 200

        content_data = response_body.get("data", response_body)
        content = content_data.get("content", []) if isinstance(content_data, dict) else []
        logger.info(f"✓ Request Payment列表获取成功，返回 {len(content)} 条")

    @pytest.mark.parametrize("status", [
        "Cancelled", "Pending", "Rejected", "Paid_In_Full", "Paid_In_Partial"
    ])
    def test_filter_by_rfp_status(self, instant_pay_api, status):
        """
        测试场景6：按 Request Payment 专有 status 筛选（覆盖全部5个枚举值）
        ⚠️ 注意：RFP status 与普通 Payment status 完全不同
        验证点：每条返回数据的 status 均与筛选值一致
        """
        logger.info(f"测试场景6：按 RFP status='{status}' 筛选")

        response = instant_pay_api.list_request_payment_transactions(status=status, size=10)
        assert response.status_code == 200

        response_body = response.json()
        content_data = response_body.get("data", response_body)
        content = content_data.get("content", []) if isinstance(content_data, dict) else []
        logger.info(f"  返回 {len(content)} 条")

        if not content:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for txn in content:
                assert txn.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {txn.get('status')}"
            logger.info(f"✓ {len(content)} 条数据均为 {status} 状态")

    @pytest.mark.parametrize("direction", ["Incoming", "Outgoing"])
    def test_filter_by_direction(self, instant_pay_api, direction):
        """
        测试场景7：按 direction 筛选（覆盖全部2个枚举值）
        验证点：每条返回数据的 direction 均与筛选值一致
        """
        logger.info(f"测试场景7：按 direction='{direction}' 筛选")

        response = instant_pay_api.list_request_payment_transactions(direction=direction, size=10)
        assert response.status_code == 200

        response_body = response.json()
        content_data = response_body.get("data", response_body)
        content = content_data.get("content", []) if isinstance(content_data, dict) else []
        logger.info(f"  返回 {len(content)} 条")

        if not content:
            logger.info(f"  ⚠️ direction='{direction}' 无数据，跳过筛选值验证")
        else:
            for txn in content:
                assert txn.get("direction") == direction, \
                    f"筛选结果包含非 {direction}: {txn.get('direction')}"
            logger.info(f"✓ {len(content)} 条数据均为 {direction}")

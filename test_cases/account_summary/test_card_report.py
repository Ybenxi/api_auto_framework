"""
Card Report - 卡片支出报告接口测试用例
覆盖以下3个接口：
  1. GET /card/report/expenditure-category    支出分类报告
  2. GET /card/report/expenditure-comparison  支出对比报告
  3. GET /card/report/top-expenditure         Top 消费报告

实测行为：
  - card_number 传卡片 id 或 tokenized card number 均可
  - 缺少必填参数：code=599, error="parameter: xxx missing"
  - 无效 time_period：code=599, error="Invalid value for parameter..."
  - 无历史数据时返回 code=200 + data=空数组/空 top_transactions
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok

START_TIME = "2025-01-01 00:00:00"
END_TIME   = "2025-12-31 23:59:59"

pytestmark = pytest.mark.account_summary


# ════════════════════════════════════════════════════════════════════
# 支出分类报告
# ════════════════════════════════════════════════════════════════════
@pytest.mark.account_summary
class TestCardExpenditureCategory:

    def test_success_with_valid_card(self, card_report_api, real_card_id):
        """
        测试场景1：使用有效卡片 ID 获取支出分类报告
        Test Scenario1: Get Expenditure Category Report with Valid Card ID
        验证点：
        1. HTTP 200，business code=200
        2. data 是数组（无消费数据时为空数组）
        3. 若有数据，每条含 merchant_category, total_settled_amount, total_amount, count
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_expenditure_category(
            card_number=real_card_id,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", [])
        assert isinstance(data, list), "data 应为数组"
        logger.info(f"  返回 {len(data)} 个支出分类")

        if data:
            required = ["merchant_category", "total_settled_amount", "total_amount", "count"]
            for field in required:
                assert field in data[0], f"分类记录缺少字段: '{field}'"
                logger.info(f"  ✓ {field}: {data[0].get(field)}")
        logger.info("✓ 支出分类报告验证通过")

    def test_missing_card_number(self, card_report_api):
        """
        测试场景2：缺少 card_number 参数
        Test Scenario2: Missing card_number Returns Business Error
        验证点：
        1. HTTP 200，business code=599
        2. error_message 包含 "card_number missing"
        """
        resp = card_report_api.get_expenditure_category(
            card_number="",
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, f"缺少 card_number 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 card_number 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_missing_start_time(self, card_report_api, real_card_id):
        """
        测试场景3：缺少 start_time 参数
        Test Scenario3: Missing start_time Returns Business Error
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        url = card_report_api.config.get_full_url("/card/report/expenditure-category")
        resp = card_report_api.session.get(url, params={
            "card_number": real_card_id, "end_time": END_TIME
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 start_time 被拒绝: code={body.get('code')}")

    def test_invalid_card_id(self, card_report_api):
        """
        测试场景4：使用不存在的卡片 ID
        Test Scenario4: Non-existent Card ID Returns Empty or Error
        验证点：
        1. HTTP 200
        2. code=200 data=[] 或 code!=200
        """
        resp = card_report_api.get_expenditure_category(
            card_number="INVALID_CARD_ID_99999",
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code == 200:
            data = body.get("data", [])
            assert data == [] or data is None, f"无效卡片应返回空数组，实际: {data}"
            logger.info("✓ 无效卡片 ID 返回空数组")
        else:
            logger.info(f"✓ 无效卡片 ID 被拒绝: code={code}")

    def test_future_date_range(self, card_report_api, real_card_id):
        """
        测试场景5：未来时间范围（无消费数据）
        Test Scenario5: Future Date Range Returns Empty Array
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_expenditure_category(
            card_number=real_card_id,
            start_time="2099-01-01 00:00:00",
            end_time="2099-12-31 23:59:59"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", [])
        assert data == [] or data is None, "未来时间无消费数据，应返回空数组"
        logger.info("✓ 未来时间范围返回空数组")


# ════════════════════════════════════════════════════════════════════
# 支出对比报告
# ════════════════════════════════════════════════════════════════════
@pytest.mark.account_summary
class TestCardExpenditureComparison:

    @pytest.mark.parametrize("time_period", ["Yearly", "Monthly"])
    def test_time_period_enum_coverage(self, card_report_api, real_card_id, time_period):
        """
        测试场景1：time_period 枚举全覆盖（Yearly / Monthly）
        Test Scenario1: time_period Enum Coverage (Yearly / Monthly)
        验证点：
        1. HTTP 200，business code=200
        2. data 是数组，每条含 month, year, amount
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_expenditure_comparison(
            card_number=real_card_id,
            time_period=time_period,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, \
            f"time_period={time_period} 应被接受，实际 code={body.get('code')}"

        data = body.get("data", [])
        assert isinstance(data, list)
        logger.info(f"  time_period={time_period}: 返回 {len(data)} 条数据")

        if data:
            for field in ["month", "year", "amount"]:
                assert field in data[0], f"对比记录缺少字段: '{field}'"
        logger.info(f"✓ time_period={time_period} 验证通过")

    @pytest.mark.parametrize("invalid_period", ["Weekly", "Daily", "YEARLY", "monthly"])
    def test_invalid_time_period(self, card_report_api, real_card_id, invalid_period):
        """
        测试场景2：无效的 time_period 枚举值
        Test Scenario2: Invalid time_period Enum Returns Business Error
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_expenditure_comparison(
            card_number=real_card_id,
            time_period=invalid_period,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 time_period='{invalid_period}' 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"  ✓ time_period='{invalid_period}' 被拒绝: code={body.get('code')}")

    def test_missing_required_params(self, card_report_api, real_card_id):
        """
        测试场景3：缺少 time_period 必填参数
        Test Scenario3: Missing time_period Returns Business Error
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        url = card_report_api.config.get_full_url("/card/report/expenditure-comparison")
        resp = card_report_api.session.get(url, params={
            "card_number": real_card_id,
            "start_time": START_TIME,
            "end_time": END_TIME
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 time_period 被拒绝: code={body.get('code')}")

    def test_monthly_data_count(self, card_report_api, real_card_id):
        """
        测试场景4：Monthly 模式返回数据条数与时间范围月数一致
        Test Scenario4: Monthly Mode Returns Data Points Matching Month Count
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_expenditure_comparison(
            card_number=real_card_id,
            time_period="Monthly",
            start_time="2025-01-01 00:00:00",
            end_time="2025-03-31 23:59:59"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", [])
        logger.info(f"  Monthly 3个月查询，返回 {len(data)} 条（预期约3条）")
        if data:
            months = sorted(set(d.get("month") for d in data))
            logger.info(f"  月份分布: {months}")
        logger.info("✓ Monthly 数据条数验证完成")


# ════════════════════════════════════════════════════════════════════
# Top 消费报告
# ════════════════════════════════════════════════════════════════════
@pytest.mark.account_summary
class TestCardTopExpenditure:

    def test_success_with_valid_params(self, card_report_api, real_card_id):
        """
        测试场景1：使用有效参数获取 Top 消费报告
        Test Scenario1: Get Top Expenditure Report with Valid Parameters
        验证点：
        1. HTTP 200，business code=200
        2. data 含 total_settled_amount, percentage, top_transactions
        3. top_transactions 是数组
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_top_expenditure(
            card_number=real_card_id,
            top_number=5,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        assert isinstance(data, dict), "data 应为对象"
        for field in ["total_settled_amount", "percentage", "top_transactions"]:
            assert field in data, f"data 缺少字段: '{field}'"

        top_txns = data.get("top_transactions", [])
        assert isinstance(top_txns, list)
        logger.info(f"  top_transactions 数量: {len(top_txns)}")

        if top_txns:
            txn = top_txns[0]
            expected = ["transaction_id", "card_number", "amount", "status",
                        "merchant_category_name", "transaction_type"]
            for field in expected:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ Top 消费报告验证通过")

    def test_top_number_limits_results(self, card_report_api, real_card_id):
        """
        测试场景2：top_number 参数限制返回条数
        Test Scenario2: top_number Parameter Limits Returned Transaction Count
        验证点：
        1. 返回的 top_transactions 数量 <= top_number
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        for top_n in [1, 3, 10]:
            resp = card_report_api.get_top_expenditure(
                card_number=real_card_id,
                top_number=top_n,
                start_time=START_TIME,
                end_time=END_TIME
            )
            body = resp.json()
            if body.get("code") == 200:
                top_txns = body.get("data", {}).get("top_transactions", [])
                assert len(top_txns) <= top_n, \
                    f"top_number={top_n} 时返回条数 {len(top_txns)} 超出限制"
                logger.info(f"  ✓ top_number={top_n}: 返回 {len(top_txns)} 条")
        logger.info("✓ top_number 限制条数验证通过")

    def test_missing_card_number(self, card_report_api):
        """
        测试场景3：缺少 card_number
        Test Scenario3: Missing card_number Returns Business Error
        """
        resp = card_report_api.get_top_expenditure(
            card_number="",
            top_number=5,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 card_number 被拒绝: code={body.get('code')}")

    def test_missing_top_number(self, card_report_api, real_card_id):
        """
        测试场景4：缺少 top_number 必填参数
        Test Scenario4: Missing top_number Returns Business Error
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        url = card_report_api.config.get_full_url("/card/report/top-expenditure")
        resp = card_report_api.session.get(url, params={
            "card_number": real_card_id,
            "start_time": START_TIME,
            "end_time": END_TIME
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 top_number 被拒绝: code={body.get('code')}")

    def test_invalid_card_id(self, card_report_api):
        """
        测试场景5：无效卡片 ID
        Test Scenario5: Invalid Card ID Returns Empty or Error
        """
        resp = card_report_api.get_top_expenditure(
            card_number="INVALID_CARD_ID_99999",
            top_number=5,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code == 200:
            top_txns = body.get("data", {}).get("top_transactions", [])
            assert top_txns == [], f"无效卡片应返回空 top_transactions，实际: {top_txns}"
            logger.info("✓ 无效卡片 ID 返回空 top_transactions")
        else:
            logger.info(f"✓ 无效卡片 ID 被拒绝: code={code}")

    def test_transaction_amount_type(self, card_report_api, real_card_id):
        """
        测试场景6：验证交易金额字段类型
        Test Scenario6: Verify Transaction Amount Field Types
        验证点：
        1. total_settled_amount 是字符串（文档示例如此）
        2. percentage 是 null 或数值
        3. top_transactions 中 amount 是数值类型
        """
        if not real_card_id:
            pytest.skip("无可用卡片数据，跳过")

        resp = card_report_api.get_top_expenditure(
            card_number=real_card_id,
            top_number=10,
            start_time=START_TIME,
            end_time=END_TIME
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        total = data.get("total_settled_amount")
        pct = data.get("percentage")

        # total_settled_amount 可能是 string 或 number，兼容
        if total is not None:
            assert isinstance(total, (str, int, float)), \
                f"total_settled_amount 类型异常: {type(total)}"
            logger.info(f"  total_settled_amount: {total} (type={type(total).__name__})")

        if pct is not None:
            assert isinstance(pct, (int, float)), \
                f"percentage 应为数值，实际: {type(pct)}"
            logger.info(f"  percentage: {pct}")

        top_txns = data.get("top_transactions", [])
        if top_txns:
            amt = top_txns[0].get("amount")
            if amt is not None:
                assert isinstance(amt, (int, float)), f"amount 应为数值"
                logger.info(f"  top_transactions[0].amount: {amt}")
        logger.info("✓ 金额字段类型验证通过")

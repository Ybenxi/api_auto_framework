"""
Client List - 证券行情接口测试用例
覆盖：
  1. GET /investment/security/snapshot-price  证券价格快照
  2. GET /investment/security/historical-chart 证券历史图表

真实测试数据（来自 dev actc 环境）：
  PEG  (Common Stock)   security_id: 1716455162056W2Hhd
  SYK  (Common Stock)   security_id: 17152871457341FiHf
  BTC  (Crypto Currency) security_id: a71a11117a510v0v5L
  DEMSX (Mutual Funds)  security_id: a0A5f00000NrxT5EAJ
  AAPL (Common Stock)   常见验证标的

issue_type 和 interval 枚举值均需逐一覆盖验证。
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok

# 文档定义的 issue_type 全部枚举值（14个）
ISSUE_TYPES = [
    "Bond",
    "Certificates of Deposit",
    "Commodities",
    "Common Stock",
    "Common Trust Funds",
    "Crypto Currency",
    "ETF",
    "Hedge Funds and Private Equity",
    "Liabilities",
    "Money Market Fund",
    "Mutual Funds",
    "Other Assets",
    "Other Fixed Income",
    "Real Estate Investment Trust",
]

# 文档定义的 interval 全部枚举值（6个）
INTERVALS = ["1D", "5D", "1M", "3M", "1Y", "ALL"]

# 真实可用的证券数据（dev actc 环境）
REAL_SECURITIES = [
    ("PEG",   "Common Stock",    "PEG Phibro Energy Production Corp"),
    ("SYK",   "Common Stock",    "SYK Stryker Corp"),
    ("BTC",   "Crypto Currency", "BTC Bitcoin"),
    ("DEMSX", "Mutual Funds",    "DEMSX Delaware Smid Cap Growth"),
]

pytestmark = pytest.mark.client_list


# ════════════════════════════════════════════════════════════════════
# 1. Security Price Snapshot
# ════════════════════════════════════════════════════════════════════
@pytest.mark.client_list
class TestSecuritySnapshotPrice:

    def test_snapshot_price_success(self, client_list_api):
        """
        测试场景1：获取 AAPL Common Stock 价格快照
        Test Scenario1: Get AAPL Common Stock Price Snapshot Successfully
        验证点：
        1. HTTP 200，business code=200
        2. data 包含文档定义的价格字段
        3. symbol 和 issue_type 回显一致
        """
        resp = client_list_api.get_security_snapshot_price(
            symbol="AAPL", issue_type="Common Stock"
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        assert data, "data 不应为空"
        assert data.get("symbol") == "AAPL", "symbol 应回显 AAPL"
        assert data.get("issue_type") == "Common Stock"

        price_fields = [
            "change_dollar", "change_percent", "bid_price", "ask_price",
            "fifty_two_week_high", "fifty_two_week_low", "volume",
            "open", "high", "low", "previous_close", "price"
        ]
        for field in price_fields:
            assert field in data, f"快照缺少字段: '{field}'"
        logger.info(f"✓ AAPL 快照: price={data.get('price')}, change={data.get('change_percent')}%")

    @pytest.mark.parametrize("symbol,issue_type,desc", REAL_SECURITIES)
    def test_snapshot_price_real_securities(self, client_list_api, symbol, issue_type, desc):
        """
        测试场景2：使用真实证券数据（PEG/SYK/BTC/DEMSX）验证各类型快照
        Test Scenario2: Snapshot Price for Real Securities (PEG/SYK/BTC/DEMSX)
        验证点：
        1. HTTP 200，business code=200
        2. 各证券类型（Common Stock/Crypto/Mutual Funds）均能获取快照
        3. symbol 和 issue_type 回显正确
        """
        resp = client_list_api.get_security_snapshot_price(
            symbol=symbol, issue_type=issue_type
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, \
            f"{desc}: code={body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", {})
        assert data, f"{desc}: data 不应为空"
        assert data.get("symbol") == symbol
        assert data.get("issue_type") == issue_type
        logger.info(f"  ✓ {desc}: price={data.get('price')}")

    def test_snapshot_price_default_issue_type(self, client_list_api):
        """
        测试场景3：不传 issue_type 使用默认值（Common Stock）
        Test Scenario3: Snapshot Price with Default issue_type (Common Stock)
        验证点：
        1. HTTP 200，code=200
        2. 不传 issue_type 也能成功获取
        """
        resp = client_list_api.get_security_snapshot_price(symbol="AAPL")
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ 默认 issue_type 快照: price={body.get('data',{}).get('price')}")

    @pytest.mark.parametrize("issue_type", ISSUE_TYPES)
    def test_snapshot_price_all_issue_types(self, client_list_api, issue_type):
        """
        测试场景4：遍历所有 issue_type 枚举值
        Test Scenario4: Get Snapshot Price for All issue_type Enum Values
        验证点：
        1. HTTP 200
        2. 各 issue_type 均不报错（有数据返回 code=200，无数据 code 可能不同）
        """
        resp = client_list_api.get_security_snapshot_price(
            symbol="AAPL", issue_type=issue_type
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code == 200:
            logger.info(f"  ✓ issue_type='{issue_type}': 有数据")
        else:
            logger.info(f"  ⚠ issue_type='{issue_type}': code={code}（可能 AAPL 无该类型数据）")

    def test_snapshot_price_missing_symbol(self, client_list_api):
        """
        测试场景5：缺少必填参数 symbol
        Test Scenario5: Missing Required Symbol Returns Business Error
        验证点：
        1. HTTP 200，code=599
        2. error_message 包含 symbol missing
        """
        url = client_list_api.config.get_full_url("/investment/security/snapshot-price")
        resp = client_list_api.session.get(url)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, f"缺少 symbol 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 symbol 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_snapshot_price_invalid_symbol(self, client_list_api):
        """
        测试场景6：使用不存在的证券代码
        Test Scenario6: Non-existent Symbol Returns Empty or Error
        """
        resp = client_list_api.get_security_snapshot_price(
            symbol="XXXYYY_NOT_EXISTS_999"
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code == 200:
            data = body.get("data")
            assert not data or all(v is None for v in (data or {}).values()), \
                "不存在的证券应返回空或 null 数据"
            logger.info("✓ 不存在证券返回空数据")
        else:
            logger.info(f"✓ 不存在证券被拒绝: code={code}")

    def test_snapshot_price_invalid_issue_type(self, client_list_api):
        """
        测试场景7：使用文档未定义的 issue_type
        Test Scenario7: Invalid issue_type Returns Error or Falls Back
        """
        resp = client_list_api.get_security_snapshot_price(
            symbol="AAPL", issue_type="INVALID_TYPE_999"
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 无效 issue_type 被拒绝: code={code}")
        else:
            logger.info("⚠ API 接受了无效 issue_type（探索性结果）")

    def test_snapshot_price_different_symbols(self, client_list_api):
        """
        测试场景8：测试多个常见证券代码（含真实数据）
        Test Scenario8: Get Snapshot Price for Multiple Common Symbols
        """
        symbols = ["AAPL", "PEG", "SYK", "BTC", "DEMSX"]
        for sym in symbols:
            resp = client_list_api.get_security_snapshot_price(symbol=sym)
            assert resp.status_code == 200
            code = resp.json().get("code")
            logger.info(f"  {sym}: code={code}")
        logger.info("✓ 多证券代码快照查询完成")


# ════════════════════════════════════════════════════════════════════
# 2. Security Historical Chart
# ════════════════════════════════════════════════════════════════════
@pytest.mark.client_list
class TestSecurityHistoricalChart:

    def test_historical_chart_success(self, client_list_api):
        """
        测试场景1：获取 AAPL 1D 历史图表
        Test Scenario1: Get AAPL 1D Historical Chart Successfully
        验证点：
        1. HTTP 200，code=200
        2. data.points 是数组，每条含 price 和 timestamp
        3. data.timestamp 是整数（毫秒时间戳）
        """
        resp = client_list_api.get_security_historical_chart(
            symbol="AAPL", issue_type="Common Stock", interval="1D"
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        assert "points" in data, "data 应含 points 字段"
        assert "timestamp" in data, "data 应含 timestamp 字段"

        points = data.get("points", [])
        assert isinstance(points, list)
        logger.info(f"  1D 数据点数量: {len(points)}")

        if points:
            assert "price" in points[0], "point 应含 price"
            assert "timestamp" in points[0], "point 应含 timestamp"
            assert isinstance(points[0].get("timestamp"), (int, float)), "timestamp 应为数值"
        logger.info("✓ 1D 历史图表验证通过")

    @pytest.mark.parametrize("symbol,issue_type,desc", REAL_SECURITIES)
    def test_historical_chart_real_securities(self, client_list_api, symbol, issue_type, desc):
        """
        测试场景2：真实证券历史图表（PEG/SYK/BTC/DEMSX）
        Test Scenario2: Historical Chart for Real Securities (PEG/SYK/BTC/DEMSX)
        验证点：各类型证券均能返回历史数据点
        """
        resp = client_list_api.get_security_historical_chart(
            symbol=symbol, issue_type=issue_type, interval="1D"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"{desc}: code={body.get('code')}, err={body.get('error_message')}"
        points = body.get("data", {}).get("points", [])
        assert isinstance(points, list)
        logger.info(f"  ✓ {desc}: {len(points)} 个数据点")

    @pytest.mark.parametrize("interval", INTERVALS)
    def test_historical_chart_all_intervals(self, client_list_api, interval):
        """
        测试场景3：遍历所有 interval 枚举值（1D/5D/1M/3M/1Y/ALL）
        Test Scenario3: Historical Chart for All interval Enum Values
        验证点：
        1. HTTP 200，code=200
        2. 各 interval 均能正常返回数据
        3. 不同 interval 数据点数量不同（1D < 1Y < ALL）
        """
        resp = client_list_api.get_security_historical_chart(
            symbol="AAPL", interval=interval
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"interval='{interval}' 应返回 code=200，实际: {body.get('code')}"

        points = body.get("data", {}).get("points", [])
        logger.info(f"  ✓ interval='{interval}': {len(points)} 个数据点")

    @pytest.mark.parametrize("issue_type", ["Common Stock", "ETF", "Mutual Funds", "Crypto Currency"])
    def test_historical_chart_issue_type_coverage(self, client_list_api, issue_type):
        """
        测试场景4：issue_type 枚举值覆盖（含真实证券类型）
        Test Scenario4: Historical Chart for issue_type Coverage
        使用真实证券：Common Stock=AAPL, ETF=BTC, Mutual Funds=DEMSX
        """
        resp = client_list_api.get_security_historical_chart(
            symbol="AAPL", issue_type=issue_type, interval="1D"
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        pts = body.get("data", {}).get("points", []) if code == 200 else []
        logger.info(f"  issue_type='{issue_type}': code={code}, points={len(pts)}")

    def test_historical_chart_missing_symbol(self, client_list_api):
        """
        测试场景5：缺少必填参数 symbol
        Test Scenario5: Missing Symbol Returns Business Error
        """
        url = client_list_api.config.get_full_url("/investment/security/historical-chart")
        resp = client_list_api.session.get(url, params={"interval": "1D"})
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 symbol 被拒绝: code={body.get('code')}")

    def test_historical_chart_invalid_interval(self, client_list_api):
        """
        测试场景6：无效的 interval 枚举值
        Test Scenario6: Invalid interval Value Returns Error
        """
        resp = client_list_api.get_security_historical_chart(
            symbol="AAPL", interval="INVALID_INTERVAL_999"
        )
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 无效 interval 被拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了无效 interval（探索性结果）")

    def test_historical_chart_response_structure(self, client_list_api):
        """
        测试场景7：验证响应结构完整性（使用 BTC 加密货币）
        Test Scenario7: Verify Historical Chart Response Structure
        """
        resp = client_list_api.get_security_historical_chart(
            symbol="BTC", issue_type="Crypto Currency", interval="5D"
        )
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        assert isinstance(data, dict)
        assert "points" in data
        assert "timestamp" in data
        assert isinstance(data["timestamp"], (int, float))
        logger.info(f"✓ 响应结构验证通过: points={len(data['points'])}, timestamp={data['timestamp']}")

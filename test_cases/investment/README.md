# Investment 模块测试

## 模块概述
Investment（投资报表）模块提供全面的商业智能数据和分析洞察，包括活动摘要、趋势分析、绩效评估和资产配置等功能。

## API 接口列表（6个）

### 活动报表接口（2个）
1. **GET** `/api/v1/cores/{core}/reports/investments/activity-summaries` - 获取活动摘要
2. **GET** `/api/v1/cores/{core}/reports/investments/activity-trends` - 获取投资趋势

### 绩效报表接口（2个）
3. **GET** `/api/v1/cores/{core}/reports/investments/performances/returns` - 获取绩效回报率
4. **GET** `/api/v1/cores/{core}/reports/investments/performances/risks` - 获取绩效风险指标

### 资产配置接口（2个）
5. **GET** `/api/v1/cores/{core}/reports/investments/asset-allocations` - 获取资产配置
6. **GET** `/api/v1/cores/{core}/reports/investments/asset-allocations/comparison` - 获取配置对比

## 测试文件列表（6个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_investment_activity_summaries.py` | 6 | 活动摘要查询 |
| `test_investment_activity_trends.py` | 6 | 活动趋势查询（数组） |
| `test_investment_performance_returns.py` | 7 | 绩效回报率（含fee/interval参数） |
| `test_investment_performance_risks.py` | 6 | 风险指标（Alpha/Beta/R-Squared） |
| `test_investment_asset_allocations.py` | 6 | 资产配置（嵌套结构） |
| `test_investment_asset_allocations_comparison.py` | 6 | 配置对比（实际vs目标） |

**总计：37个测试场景**

## 关键枚举类型

```python
class FeeType(str, Enum):
    """费用计算类型"""
    NET_OF_FEE = "NET_OF_FEE"      # 扣除费用后
    GROSS_OF_FEE = "GROSS_OF_FEE"  # 扣除费用前

class IntervalType(str, Enum):
    """数据时间间隔"""
    DAILY = "DAILY"
    QUARTERLY = "QUARTERLY"
```

## 共同参数

所有接口都需要以下参数：
- `begin_date`: 开始日期（YYYY-MM-DD，必需）
- `end_date`: 结束日期（YYYY-MM-DD，必需）
- `account_id` 或 `financial_account_id`: 账户ID（二选一必需）

## 文档已知问题（15个）

### 🔴 严重问题（5个）
1. **URL路径错误**（Activity Summary）：URL中重复了"investments"
2. **JSON格式错误**（多处）：trailing comma（5处）
3. **字符串引号重复**（Performance Risks）：`"name": ""S&P 500 INDEX"`
4. **分号替代逗号**（Asset Allocations Comparison）：`"market_value": 149.00;`

### 🟡 中等问题（5个）
5. **专业术语拼写错误**：`sharp_ratio` 应为 `sharpe_ratio`
6. **响应字段未定义**：benchmark/account对象内部结构未说明
7. **字段命名不一致**：actual_percent vs percent
8. **条件必需字段规则不清晰**：account_id vs financial_account_id
9. **嵌套结构说明不足**：Asset Allocations的children层级

### 🟢 轻微问题（5个）
10. **日期格式未定义**：推测为YYYY-MM-DD
11. **currency类型未定义**：实际是number
12. **interval参数枚举不完整**：只有DAILY和QUARTERLY
13. **fee参数默认值说明不一致**
14. **嵌套结构未完全展开**

## 响应格式注意事项

### Activity Summaries 响应
```json
{
    "beginning_market_value": 19564827.26,
    "net_additions": -620359.33,
    "ending_market_value": 19870117.14
}
```

### Activity Trends 响应（数组）
```json
[
    {
        "date": "2023-01-03",
        "market_value": 507883.36,
        "net_addition": 7.25
    }
]
```

### Performance Risks 响应
```json
{
    "benchmark": {
        "name": "S&P 500 INDEX",
        "return_rate": -0.0304,
        "sharp_ratio": -0.2058  // ⚠️ 拼写错误
    },
    "alpha": -0.0556,
    "beta": 0.3192,
    "r_squared": 0.9847
}
```

## Skip的测试

大部分测试标记为skip，原因：
- **需要真实投资数据**：Activity Summaries、Trends、Returns等
- **需要已配置策略**：Asset Allocations Comparison
- **需要复杂前置条件**：真实的financial_account_id

**可直接运行的测试**：
- 日期格式验证测试
- 无效参数测试
- 枚举值验证测试
- 空数据时间段测试

## 测试策略

### 1. 错误处理测试（可运行）
```python
# 无效日期格式
test_invalid_date_format()

# 日期范围倒置
test_date_range_reversed()

# 缺少必需参数
test_missing_account_ids()

# 无效枚举值
test_invalid_fee_enum()
```

### 2. 真实数据测试（skip）
```python
@pytest.mark.skip(reason="需要真实的financial_account_id")
def test_with_real_data():
    # 使用真实账户ID
    pass
```

### 3. 容错处理

#### sharp_ratio拼写兼容
```python
# 兼容两种拼写
if "sharp_ratio" in benchmark:
    logger.warning("⚠️ 检测到拼写错误")
elif "sharpe_ratio" in benchmark:
    logger.info("✓ 使用正确拼写")
```

#### JSON格式错误容错
API封装层已处理JSON解析，测试时注意响应验证。

## 运行测试

```bash
# 运行所有Investment测试
pytest test_cases/investment/ -v

# 运行特定文件
pytest test_cases/investment/test_investment_activity_summaries.py -v

# 按标记运行
pytest -m investment -v

# 运行不包含skip的测试
pytest test_cases/investment/ -v -m "not skip"
```

## 数据准备建议

### 获取真实financial_account_id
```python
# 从Financial Account列表获取
from api.financial_account_api import FinancialAccountAPI

fa_api = FinancialAccountAPI(session=login_session)
accounts = fa_api.list_financial_accounts(size=1)
fa_id = accounts.json()["content"][0]["id"]
```

### 日期范围建议
- **快速测试**：使用3天范围（2024-01-01 to 2024-01-03）
- **完整测试**：使用1个月（2024-01-01 to 2024-01-31）
- **季度测试**：使用3个月（QUARTERLY interval）

## 特殊说明

### Performance Risks指标含义
- **Alpha**：超额收益，相对于基准的主动收益
- **Beta**：系统风险，相对于市场的波动性
- **R-Squared**：相关性，收益中可由市场解释的比例（0-1）
- **Sharpe Ratio**：风险调整后收益（⚠️文档拼写为sharp_ratio）

### Asset Allocations嵌套层级
```
Level 1: class (如 Equities)
  └─ Level 2: segment (如 US Equity-Other)
      └─ Level 3: name (如 ALPHABET INC A)
          └─ symbol: GOOGL
```

- `percent_of_level`：在当前层级的占比
- `percent_of_total`：在总资产的占比

## 问题反馈

所有文档问题已提交给开发团队，包括：
- JSON格式错误
- 拼写错误
- 字段定义缺失
- URL路径错误

测试代码已做兼容处理。

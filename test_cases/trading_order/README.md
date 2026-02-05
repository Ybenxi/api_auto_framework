# Trading Order 模块测试

## 模块概述
Trading Order（交易订单）模块提供证券交易订单的完整生命周期管理，包括订单创建、查询、提交、更新和取消等功能。

## API 接口列表（9个）

### 辅助查询接口（2个）
1. **GET** `/api/v1/cores/{core}/trading-orders/financial-accounts` - 获取投资类型的Financial Accounts列表
2. **GET** `/api/v1/cores/{core}/trading-orders/securities` - 获取可交易证券列表

### 订单查询接口（2个）
3. **GET** `/api/v1/cores/{core}/trading-orders` - 获取交易订单列表
4. **GET** `/api/v1/cores/{core}/trading-orders/{order_id}` - 获取订单详情

### 订单创建接口（2个）
5. **POST** `/api/v1/cores/{core}/trading-orders/draft` - 创建草稿订单（需要后续Submit）
6. **POST** `/api/v1/cores/{core}/trading-orders` - 直接发起交易订单（立即提交到市场）

### 订单操作接口（3个）
7. **POST** `/api/v1/cores/{core}/trading-orders/{order_id}/submit` - 提交草稿订单到市场
8. **PATCH** `/api/v1/cores/{core}/trading-orders/{order_id}` - 更新订单信息
9. **POST** `/api/v1/cores/{core}/trading-orders/{order_id}/cancel` - 取消订单

## 测试文件列表（9个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_trading_order_list_financial_accounts.py` | 9 | 投资账户列表查询 |
| `test_trading_order_list_securities.py` | 9 | 可交易证券列表查询 |
| `test_trading_order_list.py` | 10 | 订单列表查询（含多种筛选） |
| `test_trading_order_detail.py` | 4 | 订单详情查询 |
| `test_trading_order_draft.py` | 1 | 创建草稿订单（skip） |
| `test_trading_order_initiate.py` | 6 | 直接发起订单 |
| `test_trading_order_submit.py` | 4 | 提交草稿订单 |
| `test_trading_order_update.py` | 6 | 更新订单 |
| `test_trading_order_cancel.py` | 6 | 取消订单（破坏性操作） |

**总计：55个测试场景**

## 关键枚举类型

```python
class IssueType(str, Enum):
    """证券类型"""
    COMMON_STOCK = "Common Stock"
    ETF = "ETF"
    MUTUAL_FUNDS = "Mutual Funds"
    CRYPTO_CURRENCY = "Crypto Currency"
    # ...等14种类型

class OrderAction(str, Enum):
    """订单动作"""
    BUY = "Buy"
    SELL = "Sell"
    SELL_ALL = "Sell_All"

class OrderType(str, Enum):
    """订单类型"""
    MARKET_ORDER = "Market_Order"
    LIMIT_ORDER = "Limit_Order"
    STOP_ORDER = "Stop_Order"
    STOP_LIMIT = "Stop_Limit"

class OrderStatus(str, Enum):
    """订单状态"""
    NEW = "New"
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    FILLED = "Filled"
    POSTED = "Posted"
    CANCELLED = "Cancelled"
    # ...等9种状态
```

## 订单状态流转

```
New (草稿) → Submit → Pending/In_Progress → Partially_Filled → Filled → Posted
                      ↓
                   Cancelled/Rejected
```

## Draft vs Initiate 差异

- **Draft**：创建草稿订单，status=New，需要手动Submit
- **Initiate**：直接发起订单，status=In_Progress，立即提交到市场

## 重要限制

1. **Update限制**：只能更新status=New的草稿订单，已提交的订单无法更新
2. **Cancel限制**：可以取消New, Pending, Overnight状态的订单，已成交订单不可取消
3. **条件必需字段**：
   - Limit_Order需要limit_price
   - Stop_Order需要stop_price
   - Stop_Limit需要stop_price和limit_price

## 文档已知问题

1. order_type类型错误（文档说int，实际是string）
2. quantity类型不一致
3. Draft vs Initiate差异未明确说明
4. 部分响应字段未定义

## Skip的测试

大部分创建、更新、取消测试都标记为skip，原因：
- 需要真实的financial_account_id
- 需要真实的security_id
- 破坏性操作（Cancel）
- 待完善数据准备逻辑

## 运行测试

```bash
# 运行所有Trading Order测试
pytest test_cases/trading_order/ -v

# 运行特定文件
pytest test_cases/trading_order/test_trading_order_list.py -v

# 按标记运行
pytest -m trading_order -v
```

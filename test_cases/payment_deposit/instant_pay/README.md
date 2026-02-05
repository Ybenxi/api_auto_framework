# Instant Pay 模块测试

## 模块概述
Instant Pay是Federal Reserve提供的实时支付和结算服务（FedNow），支持24/7全天候运行，秒级结算。

## API 接口列表（15个）

### 查询接口（2个）
1. **GET** `/money-movements/instant-pay/transactions` - 获取交易列表
2. **GET** `/money-movements/instant-pay/request-payment/transactions` - 获取收款请求列表

### 账户和对手方（3个）
3. **GET** `/money-movements/instant-pay/financial-accounts` - 获取可用账户列表
4. **GET** `/money-movements/instant-pay/counterparties` - 获取对手方列表
5. **POST** `/money-movements/instant-pay/counterparties` - 创建对手方

### 支付接口（2个）
6. **POST** `/money-movements/instant-pay/payment` - 发起支付
7. **POST** `/money-movements/instant-pay/request-payment` - 发起收款请求

### Request Payment操作（3个）
8. **POST** `/money-movements/instant-pay/request-payment/cancel/:id` - 取消收款请求
9. **POST** `/money-movements/instant-pay/payment-request/approve/:id` - 批准付款请求
10. **POST** `/money-movements/instant-pay/payment-request/reject/:id` - 拒绝付款请求

### Return相关（4个）
11. **POST** `/money-movements/instant-pay/return-payment/:transaction_id` - 退款支付
12. **POST** `/money-movements/instant-pay/return-request/:transaction_id` - 退款请求
13. **POST** `/money-movements/instant-pay/return-request/approve/:id` - 批准退款请求
14. **POST** `/money-movements/instant-pay/return-request/reject/:id` - 拒绝退款请求

### 费用接口（1个）
15. **POST** `/money-movements/instant-pay/fee` - 计算交易费用

## 测试文件列表（6个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_instant_pay_transactions.py` | 7 | 交易和RFP列表 |
| `test_instant_pay_payment.py` | 8 | 发起支付和收款请求 |
| `test_instant_pay_cancel_approve_reject.py` | 6 | Cancel/Approve/Reject RFP |
| `test_instant_pay_return.py` | 8 | Return相关操作 |
| `test_instant_pay_counterparties.py` | 2 | 对手方管理 |
| `test_instant_pay_fee.py` | 2 | 费用计算 |

**总计：33个测试场景**

## 关键枚举类型

```python
class RequestPaymentStatus(str, Enum):
    """Request Payment专有状态（与普通Payment不同）"""
    CANCELLED = "Cancelled"
    PENDING = "Pending"
    REJECTED = "Rejected"
    PAID_IN_FULL = "Paid_In_Full"       # 全额支付
    PAID_IN_PARTIAL = "Paid_In_Partial" # 部分支付
```

## Payment Timeout Clock

### ⚠️ 20秒超时限制
- Federal Reserve规定：所有Instant Pay必须在20秒内完成或失败
- 大部分交易在几秒内完成
- 超时交易自动失败
- 这是FedNow系统的硬性约束

## 术语说明

### Cancel vs Reject vs Return

| 操作 | 场景 | 发起方 |
|------|------|--------|
| **Cancel** Request Payment | 取消自己发起的收款请求 | 收款方 |
| **Reject** Payment Request | 拒绝收到的付款请求 | 付款方 |
| **Return** Payment | 退款已完成的支付 | 收款方 |
| **Return** Request | 请求退款 | 收款方？ |
| **Approve** Return Request | 批准退款请求 | 付款方 |
| **Reject** Return Request | 拒绝退款请求 | 付款方 |

⚠️ **文档问题**：这些概念在文档中说明混乱，缺少流程图。

## URL命名不一致问题

```
/request-payment/cancel      ✅ request-payment
/payment-request/approve     ❌ payment-request
/payment-request/reject      ❌ payment-request
/return-request/approve      ✅ return-request
/return-request/reject       ✅ return-request
```

**问题**：request-payment vs payment-request混用，容易出错。

## 文档已知问题（45个）

### 🔴 严重问题（15个）
- URL路径示例错误
- Cancel/Reject/Return概念混淆
- cancel_code/return_code/reject_code值未知（外部链接缺失）
- Request Payment专有字段完全未定义
- URL命名不一致
- Reject Return Request URL示例完全错误

### 🟡 中等问题（20个）
- 响应格式不一致（7个接口无code包装层）
- 大量响应字段未定义
- structured_content说明不清
- amount_modification_allowed逻辑未详细说明

### 🟢 轻微问题（10个）
- HTTP方法示例错误
- sub_type拼写错误
- 示例内容不符合场景

## Request Payment专有字段

以下字段完全未在Properties定义：
- `execution_date` - 执行日期
- `expiration_date` - 过期日期（默认1年）
- `amount_modification_allowed` - 是否允许修改金额
- `early_payment_allowed` - 是否允许提前支付

## Skip的测试

### 可运行（约10个）
- List接口
- 费用计算
- 错误处理
- 概念验证

### Skip（约23个）
- 所有payment操作（真实扣款）
- 所有approve操作（会触发实际操作）
- 需要真实RFP ID的操作

## 安全提醒

### ⚠️⚠️⚠️ Instant Pay极度危险
- 会实际扣款/收款
- 20秒超时限制
- 不可撤销
- 24/7运行（包括周末和节假日）

## 运行测试

```bash
pytest test_cases/payment_deposit/instant_pay/ -v
pytest -m instant_pay -v
```

# ACH Processing 模块测试

## 模块概述
ACH（Automated Clearing House）是美国电子支付系统，由Federal Reserve Bank运营。支持工资直接存款、账单支付、B2B交易等场景。

## API 接口列表（11个）

### 查询接口（4个）
1. **GET** `/money-movements/ach/transactions` - 获取交易列表
2. **GET** `/money-movements/ach/financial-accounts` - 获取可用账户列表
3. **GET** `/money-movements/ach/counterparties` - 获取对手方列表（第三方）
4. **GET** `/money-movements/ach/bank-accounts` - 获取银行账户列表（第一方）

### 对手方管理（1个）
5. **POST** `/money-movements/ach/counterparties` - 创建对手方（第三方）

### 转账接口（2个）
6. **POST** `/money-movements/ach/credit` - 发起Credit转账（付款）
7. **POST** `/money-movements/ach/debit` - 发起Debit转账（收款）

### 交易操作（3个）
8. **POST** `/money-movements/ach/:transaction_id/cancel` - 取消交易
9. **POST** `/money-movements/ach/reversal` - 发起冲正
10. **GET** `/money-movements/ach/reversal/:transaction_reversal_id/detail` - 获取冲正详情

### 批量处理（1个）
11. **POST** `/money-movements/ach/batch-file` - 上传批量文件

### 费用接口（1个）
12. **POST** `/money-movements/ach/fee` - 计算交易费用

## 测试文件列表（6个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_ach_transactions.py` | 3 | 交易列表查询 |
| `test_ach_first_party_logic.py` | 6 | First Party业务逻辑（核心） |
| `test_ach_credit_debit.py` | 6 | Credit/Debit转账 |
| `test_ach_cancel_reversal.py` | 7 | Cancel和Reversal操作 |
| `test_ach_batch_file.py` | 5 | 批量文件上传 |
| `test_ach_counterparties.py` | 2 | 对手方管理 |
| `test_ach_fee.py` | 4 | 费用计算 |

**总计：33个测试场景**

## ⚠️⚠️⚠️ 核心业务逻辑：First Party

### 关键概念

**first_party字段决定counterparty_id的来源**：

#### First Party = true（第一方转账）
```python
# 场景：自己的不同银行账户间转账
# Step 1: 获取Bank Account ID
bank_accounts = ach_api.list_bank_accounts()
bank_id = bank_accounts[0]["id"]

# Step 2: 使用Bank Account ID转账
ach_api.initiate_credit(
    amount="100.00",
    financial_account_id="my_fa_id",
    counterparty_id=bank_id,  # ⚠️ 使用Bank Account ID
    first_party=True           # ⚠️ 标记为第一方
)
```

#### First Party = false（第三方转账）
```python
# 场景：给其他人/公司转账
# Step 1: 获取ACH Counterparty ID
counterparties = ach_api.list_counterparties()
cp_id = counterparties[0]["id"]

# Step 2: 使用Counterparty ID转账
ach_api.initiate_credit(
    amount="100.00",
    financial_account_id="my_fa_id",
    counterparty_id=cp_id,    # ⚠️ 使用Counterparty ID
    first_party=False          # ⚠️ 标记为第三方
)
```

### 业务差异

| 特性 | First Party（第一方） | Third Party（第三方） |
|------|---------------------|---------------------|
| **counterparty_id来源** | Bank Account ID | ACH Counterparty ID |
| **获取接口** | list_bank_accounts() | list_counterparties() |
| **使用场景** | 自己账户间转账 | 给他人转账 |
| **验证** | 验证银行所有人信息 | 使用已批准的counterparty |
| **费用** | 可能更低？ | 标准费用 |

### 错误场景

```python
# ❌ 错误：first_party=true但用Counterparty ID
ach_api.initiate_credit(
    counterparty_id="counterparty_id",  # 错误的ID类型
    first_party=True
)
# 结果：验证失败

# ❌ 错误：first_party=false但用Bank Account ID
ach_api.initiate_credit(
    counterparty_id="bank_account_id",  # 错误的ID类型
    first_party=False
)
# 结果：可能找不到counterparty
```

## Same Day ACH截止时间

### UniFi Deadline（4个时间窗口）

| UniFi Deadline | Payment Gateway | Same Day |
|---------------|-----------------|----------|
| 9:45 AM ET | 10:00 AM ET | ✅ Yes |
| 3:45 PM ET | 4:00 PM ET | ✅ Yes |
| 6:45 PM ET | 7:00 PM ET | ❌ No |
| 9:45 PM ET | 10:00 PM ET | ❌ No |

⚠️ **文档问题**：Properties说3:00 PM CT，与表格不一致。

## 文档已知问题（45个）

### 🔴 严重问题（15个）
- same_day截止时间不一致（3:00PM CT vs 3:45PM ET）
- first_party概念说明不清
- Batch File格式未说明
- Batch File响应50+字段全部未定义
- request_reason外部链接缺失
- Reversal限制说明不清

### 🟡 中等问题（20个）
- 响应格式不一致（7个接口无code包装层）
- List Bank Accounts所有字段未定义
- JSON格式错误（缺少逗号）
- Reversal Detail包含原交易信息但未说明

### 🟢 轻微问题（10个）
- sub_type拼写错误
- file_controler拼写错误
- Content-Type不一致
- 500笔限制说明不当

## Skip的测试

### 可运行（约8个）
- List接口查询
- 费用计算
- 业务逻辑说明
- 错误验证

### Skip（约25个）
- 所有Credit/Debit操作（真实扣款）
- Cancel/Reversal操作
- Batch File上传（格式复杂）
- First Party转账（需要理解逻辑）

## 安全提醒

### ⚠️⚠️⚠️ ACH操作极度危险
- Credit/Debit会真实扣款
- 不可撤销
- 涉及Federal Reserve系统
- 必须在截止时间前提交

### ⚠️ 操作时间窗口
- Same Day ACH有严格截止时间
- Cancel只能在发送到FRB前
- Reversal只能对已结算交易

## 运行测试

```bash
pytest test_cases/payment_deposit/ach_processing/ -v
pytest -m ach_processing -v
```

## 关键提醒

1. **理解First Party逻辑**是使用ACH的前提
2. **Same Day截止时间**影响交易处理
3. **Batch File格式**需要NACHA标准（复杂）
4. **所有转账操作**会真实影响账户

---

**重要性**：ACH是美国最主要的支付轨道，理解First Party vs Third Party的区别至关重要！

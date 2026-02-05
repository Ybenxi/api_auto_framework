# Internal Pay 模块测试

## 模块概述
Internal Pay提供同一UniFi实例内的P2P（点对点）支付功能，用户可通过邮箱查找收款人并实时转账。

## API 接口列表（5个）

1. **GET** `/api/v1/cores/{core}/money-movements/internal-pay/transactions` - 获取交易列表
2. **GET** `/api/v1/cores/{core}/money-movements/internal-pay/financial-accounts` - 获取付款方账户列表
3. **GET** `/api/v1/cores/{core}/money-movements/internal-pay/payees` - 根据邮箱查询收款人
4. **POST** `/api/v1/cores/{core}/money-movements/internal-pay/transfer` - 发起转账
5. **POST** `/api/v1/cores/{core}/money-movements/internal-pay/fee` - 计算交易费用

## 测试文件列表（5个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_internal_pay_transactions.py` | 8 | 交易列表查询 |
| `test_internal_pay_payers.py` | 6 | 付款方账户查询 |
| `test_internal_pay_payees.py` | 5 | 收款人查询（基于邮箱） |
| `test_internal_pay_transfer.py` | 7 | 发起转账（破坏性操作） |
| `test_internal_pay_fee.py` | 5 | 费用计算 |

**总计：31个测试场景**

## 核心特性

### 📧 基于邮箱的收款人查找
- 使用邮箱作为唯一查找键
- 系统自动匹配同一UniFi实例内的用户
- 隐私保护：account_number脱敏显示

### ⚡ 实时账本结算
- 资金立即入账
- 双方余额实时更新
- 无需外部清算网络

### 💸 仅支持发送
- 只能主动发送资金
- 不支持请求付款
- 不支持拉取交易

## 文档已知问题（25个）

### 🔴 严重问题（7个）
1. HTTP方法示例错误（List Payers: GET写成POST）
2. HTTP方法示例错误（Quote Fee: POST写成GET）
12. amount字段类型不一致（string vs number）
13. 条件必需字段逻辑不清（sub_account_id）
14. List Payees的email参数标记为required（与List语义矛盾）
21. Properties与Transfer条件说明不一致
24. List Payees接口名称与功能不符

### 🟡 中等问题（13个）
3-6. 响应格式不一致（4个接口无code包装层）
7-11. 响应字段未在Properties定义（fee, completed_date等）
16. same_day字段未说明
17. List接口缺少分页参数说明
20. account_ids参数格式说明不清

### 🟢 轻微问题（5个）
15. account_number脱敏规则不一致
18. status枚举值顺序不一致
19. sub_type拼写错误（Saving vs Savings）
22. 接口描述用词不当
23, 25. 描述细节问题

## 响应格式特殊说明

### ⚠️ 重要：响应格式不一致

**无code包装层**（4个接口）：
- GET /transactions
- GET /financial-accounts
- GET /payees
- POST /transfer

```json
// 直接返回数据
{
    "content": [...],
    "pageable": {...}
}

// 或直接返回对象
{
    "id": "...",
    "status": "...",
    ...
}
```

**有code包装层**（1个接口）：
- POST /fee

```json
{
    "code": 200,
    "data": {...}
}
```

## 字段类型兼容

### amount字段
- **请求参数**：string（"1.00"）
- **响应**：number（1）
- **处理**：使用to_float()转换

### balance字段
- **类型**：number
- **包含**：available_balance, balance, pending_deposits等

## Skip的测试

### 可运行（约15个场景）
- 所有List接口查询
- 费用计算（只读）
- 错误处理测试
- 参数验证

### Skip（约16个场景）
- 发起转账（真实扣款，破坏性）
- 需要真实收款人邮箱
- 需要测试账户准备

## 隐私保护

### account_number脱敏规则
- **Payers（付款方）**：完整显示（1-01-1-0007876）
- **Payees（收款人）**：脱敏显示（*******7876）

### 余额信息显示
- **Payers列表**：显示余额（需要知道是否有足够资金）
- **Payees列表**：不显示余额（隐私保护）

## 运行测试

```bash
# 运行所有Internal Pay测试
pytest test_cases/internal_pay/ -v

# 按标记运行
pytest -m internal_pay -v

# 只运行不skip的测试
pytest test_cases/internal_pay/ -v -m "not skip"
```

## 重要提醒

### ⚠️ 转账操作非常危险
- 会实际扣款
- 不可撤销
- 所有transfer测试添加`@pytest.mark.no_rerun`
- 建议使用专门的测试账户

### ⚠️ 条件必需字段注意
sub_account_id的"Required if exists"逻辑不清晰：
- 如何判断"exists"？
- 有多个sub account时如何选择？
- 建议实际测试验证行为

## 使用场景

### P2P转账
用户之间通过邮箱互相转账，无需知道账号。

### 商户支付
消费者向商户支付，基于邮箱查找。

### 简单数字支付
替代现金或支票，在UniFi生态内快速支付。

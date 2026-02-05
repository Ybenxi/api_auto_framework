# Account Transfer 模块测试

## 模块概述
Account Transfer提供UniFi平台内管理账户之间的资金转移功能。这些账户可以属于同一profile或不同profile，支持跨组织、跨业务单元的灵活资金调配。

## API 接口列表（4个）

1. **GET** `/api/v1/cores/{core}/money-movements/account-transfer/transactions` - 获取交易列表
2. **GET** `/api/v1/cores/{core}/money-movements/account-transfer/financial-accounts` - 获取可用账户列表
3. **POST** `/api/v1/cores/{core}/money-movements/account-transfer` - 发起转账
4. **POST** `/api/v1/cores/{core}/money-movements/account-transfer/fee` - 计算交易费用

## 测试文件列表（4个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_account_transfer_transactions.py` | 6 | 交易列表查询 |
| `test_account_transfer_financial_accounts.py` | 6 | 可用账户查询 |
| `test_account_transfer_transfer.py` | 6 | 发起转账（破坏性操作） |
| `test_account_transfer_fee.py` | 4 | 费用计算 |

**总计：22个测试场景**

## 核心特性

### ⚡ 实时结算
- 转账立即处理
- 资金即时可用
- 无需外部清算

### 🔄 跨Profile灵活性
- **重要差异**：与Internal Pay的主要区别
- 可在不同profile间转账
- 支持跨业务单元、跨客户的资金调配

### 💰 成本效率
- 内部处理，无外部费用
- 不依赖第三方清算所
- 降低处理成本

### 📑 可审计性强
- 每笔交易有唯一ID
- 支持memo和外部参考号
- 完整的交易历史

## 与Internal Pay的差异

| 特性 | Internal Pay | Account Transfer |
|------|-------------|-----------------|
| **使用场景** | P2P支付（个人间） | 账户间转移（管理性质） |
| **跨Profile** | 不明确 | ✅ 明确支持 |
| **收款人查找** | 基于邮箱 | 直接使用账户ID |
| **direction字段** | ❌ 无 | ✅ 有 |
| **响应格式** | 无code包装层 | 无code包装层 |
| **其他** | 完全相同 | 完全相同 |

⚠️ **文档问题**：两个模块差异未明确说明，建议补充使用场景指南。

## 文档已知问题（25个）

### 🔴 严重问题（7个）
1. HTTP方法示例错误（List Accounts: GET写成POST）
2. HTTP方法示例错误（Quote Fee: POST写成GET）
12. amount字段类型不一致
13. 条件必需字段逻辑不清
16. 接口描述错误（说ACH应为Account Transfer）
18. 模块差异未说明
19. transaction_type参数描述错误

### 🟡 中等问题（13个）
3-5. 响应格式不一致（3个接口无code包装层）
6-11. 响应字段未定义（fee, completed_date, direction等）
14. same_day字段未说明
15. List接口缺少分页参数说明
21. Properties条件说明不一致
22. direction字段枚举值未说明

### 🟢 轻微问题（5个）
17. 接口描述语法错误
20. sub_type拼写错误
23, 24. 接口标题描述问题
25. 转义字符错误

## 响应格式说明

### 无code包装层（3个接口）
```json
// List接口
{
    "content": [...],
    "pageable": {...},
    "total_elements": 15
}

// Transfer接口
{
    "id": "...",
    "status": "Completed",
    "amount": 10,
    "fee": 0.21,
    ...
}
```

### 有code包装层（1个接口）
```json
// Quote Fee接口
{
    "code": 200,
    "data": {
        "fee": 1.01,
        "amount": 10
    }
}
```

## 未定义的响应字段

以下字段在响应示例中出现，但Properties中未定义：
1. `fee` - 交易费用
2. `completed_date` - 完成日期
3. `transaction_id` - 交易ID（与id的关系？）
4. `payer_financial_account_name` - 付款方账户名称
5. `payer_sub_account_name` - 付款方子账户名称
6. `payee_financial_account_name` - 收款方账户名称
7. `payee_sub_account_name` - 收款方子账户名称
8. `transaction_type` - 交易类型（Credit/Debit）
9. `direction` - 交易方向（Origination等）
10. `same_day` - 当天处理标识（在fee响应中）

## Skip的测试

### 可运行（约12个场景）
- 交易列表查询
- 账户列表查询
- 费用计算（只读）
- 错误处理

### Skip（约10个场景）
- 发起转账（真实扣款）
- 需要真实收款人
- 需要测试账户

## 运行测试

```bash
# 运行所有Account Transfer测试
pytest test_cases/account_transfer/ -v

# 按标记运行
pytest -m account_transfer -v
```

## 重要提醒

### ⚠️ 转账操作极度危险
- **会实际扣款**
- **不可撤销**
- **影响真实账户余额**
- 所有transfer测试必须skip或使用专门测试账户

### ⚠️ 跨Profile转账
这是Account Transfer的核心优势，可以：
- 跨不同用户profile转账
- 跨业务单元调配资金
- 在管理伞下灵活移动资产

## 条件必需字段规则

### sub_account_id
```
payer_sub_account_id: Required if a sub account exists under the payer financial account.
payee_sub_account_id: Required if a sub account exists under the payee financial account.
```

**问题**：
- "if exists"逻辑不清
- 有多个sub account时如何处理？
- 建议实际测试验证

## 项目统计（完成后）

- 模块数：19 → 21（+2）
- 测试场景：549 → 602（+53）
- API接口：114 → 123（+9）

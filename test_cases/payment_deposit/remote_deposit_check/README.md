# Remote Deposit Check 模块测试

## 模块概述
Remote Deposit Check（远程支票存款）提供通过拍照方式远程存入支票的功能，使用ICL（Image Cash Letter）标准处理支票图像。

## API 接口列表（9个）

### 查询接口（3个）
1. **GET** `/money-movements/checks/transactions` - 获取交易列表
2. **GET** `/money-movements/checks/financial-accounts` - 获取可用账户列表
3. **GET** `/money-movements/checks/counterparties` - 获取对手方列表

### 对手方管理（1个）
4. **POST** `/money-movements/checks/counterparties` - 创建对手方

### 支票处理流程（4个）
5. **POST** `/money-movements/checks/scan` - 扫描支票（文件上传）
6. **POST** `/money-movements/checks/deposit` - 提交存款
7. **PATCH** `/money-movements/checks/deposit/:transaction_id` - 更新号码
8. **POST** `/money-movements/checks/download/:transaction_id` - 下载图片

### 费用接口（1个）
9. **POST** `/money-movements/checks/fee` - 计算交易费用

## 测试文件列表（6个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_check_transactions.py` | 3 | 交易列表查询 |
| `test_check_financial_accounts.py` | 7 | 可用账户列表 |
| `test_check_counterparties.py` | 3 | 对手方管理 |
| `test_check_scan_deposit.py` | 7 | 扫描和存款（核心流程） |
| `test_check_update_download.py` | 6 | 更新和下载 |
| `test_check_fee.py` | 2 | 费用计算 |

**总计：28个测试场景**

## 支票存款流程

### 完整流程（4步）
```
Step 1: Scan Check
  POST /checks/scan
  上传正反面图片 → 获取item_identifier, routing_number, account_number
  响应格式特殊：{"success": true, ...}（不是code）
  
Step 2: Submit Deposit
  POST /checks/deposit
  使用scan结果创建存款 → 交易开始处理
  ⚠️ 真实入账操作
  
Step 3: Update (可选)
  PATCH /checks/deposit/:transaction_id
  修正OCR识别错误的routing/account number
  只能在特定状态下修改
  
Step 4: Download (可选)
  POST /checks/download/:transaction_id
  获取支票图片URL
```

## 文档已知问题（45个）

### 🔴 严重问题（15个）
- 接口描述错误（说ACH应为Check）
- Scan→Deposit流程说明缺失
- Download应该用GET不是POST
- transaction_type说明与实际矛盾
- 大量响应字段未定义

### 🟡 中等问题（20个）
- 响应格式不一致（7个接口无code包装层）
- Scan响应使用success字段（独特）
- item_identifier依赖关系未说明
- Update状态限制不清

### 🟢 轻微问题（10个）
- HTTP方法示例错误
- 文件格式说明错误
- sub_type拼写错误

## 响应格式特殊说明

### Scan Check响应（独特格式）
```json
{
    "success": true,  // 不是code!
    "item_identifier": "uuid",
    "routing_number": "...",
    "account_number": "..."
}
```

其他所有Check接口都无code包装层。

## 文件上传要求

### Scan Check需要
- **格式**：jpeg, png, pdf, tiff
- **文件**：front_check_image + back_check_image
- **大小**：未说明
- **分辨率**：未说明

## Skip的测试

### 可运行（约8个）
- List接口
- 费用计算
- 错误处理
- 格式验证

### Skip（约13个）
- 扫描支票（需要图片文件）
- 提交存款（真实入账）
- 完整流程测试

## 安全提醒

### ⚠️ 存款操作危险
- Submit Deposit会真实入账
- 不可撤销
- 所有deposit测试skip

## 运行测试

```bash
pytest test_cases/payment_deposit/remote_deposit_check/ -v
pytest -m remote_deposit_check -v
```

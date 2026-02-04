# Open Banking 模块自动化测试

## 📁 文件结构

```
test_cases/open_banking/
├── conftest.py                                                      # Pytest 配置文件
├── test_open_banking_list_authorized_accounts.py                   # 授权账户列表接口测试
├── test_open_banking_create_open_banking_connect_link.py          # 创建 Open Banking 连接链接接口测试
├── test_open_banking_create_bank_account_connect_link.py          # 创建银行账户连接链接接口测试
├── test_open_banking_list_connected_external_accounts.py          # 已连接外部账户列表接口测试
├── test_open_banking_list_account_transactions.py                 # 账户交易列表接口测试
└── README.md                                                        # 本说明文档
```

## 🔍 测试用例说明

### 1. `test_open_banking_list_authorized_accounts.py`

测试 `GET /api/v1/cores/{core}/open-banking/accounts/authorized-accounts` 接口

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_list_authorized_accounts_success` | 成功获取授权账户列表 | 验证返回 200，data 是数组，包含必需字段 |
| `test_list_authorized_accounts_with_name_filter` | 使用 name 参数筛选 | 验证筛选功能正常工作 |
| `test_list_authorized_accounts_response_structure` | 验证响应数据结构 | 验证响应包含 code, error_message, error, data 字段 |
| `test_list_authorized_accounts_all_fields` | 验证所有字段存在 | 验证账户数据包含所有文档定义的字段 |
| `test_list_authorized_accounts_account_status_values` | 验证 account_status 字段值 | 验证状态值为常见值（Active, Inactive 等） |
| `test_list_authorized_accounts_using_helper_method` | 使用辅助方法解析响应 | 验证 parse_list_response 方法 |

---

### 2. `test_open_banking_create_open_banking_connect_link.py`

测试 `POST /api/v1/cores/{core}/open-banking/connections/manage/open-banking` 接口

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_create_open_banking_connect_link_success` | 成功创建 Open Banking 连接链接 | 验证返回 200，data 是有效的 URL |
| `test_create_open_banking_connect_link_response_structure` | 验证响应数据结构 | 验证响应结构正确 |
| `test_create_open_banking_connect_link_missing_redirect_url` | 缺少 redirect_url 参数 | 验证必需参数校验 |
| `test_create_open_banking_connect_link_missing_account_id` | 缺少 account_id 参数 | 验证必需参数校验 |
| `test_create_open_banking_connect_link_invalid_account_id` | 使用无效的 account_id | 验证错误处理 |

---

### 3. `test_open_banking_create_bank_account_connect_link.py`

测试 `POST /api/v1/cores/{core}/open-banking/connections/manage/banks` 接口

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_create_bank_account_connect_link_success` | 成功创建银行账户连接链接 | 验证返回 200，data 是有效的 URL |
| `test_create_bank_account_connect_link_response_structure` | 验证响应数据结构 | 验证响应结构正确 |
| `test_create_bank_account_connect_link_missing_redirect_url` | 缺少 redirect_url 参数 | 验证必需参数校验 |
| `test_create_bank_account_connect_link_missing_account_id` | 缺少 account_id 参数 | 验证必需参数校验 |
| `test_create_bank_account_connect_link_invalid_account_id` | 使用无效的 account_id | 验证错误处理 |
| `test_create_bank_account_connect_link_different_redirect_urls` | 测试不同的 redirect_url | 验证支持不同的重定向 URL |

---

### 4. `test_open_banking_list_connected_external_accounts.py`

测试 `GET /api/v1/cores/{core}/open-banking/accounts` 接口

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_list_connected_external_accounts_success` | 成功获取已连接外部账户列表 | 验证返回 200，data 是数组，包含必需字段 |
| `test_list_connected_external_accounts_response_structure` | 验证响应数据结构 | 验证响应结构正确 |
| `test_list_connected_external_accounts_all_fields` | 验证所有字段存在 | 验证外部账户数据包含所有字段 |
| `test_list_connected_external_accounts_status_values` | 验证 status 字段值 | 验证状态值为常见值（Open, Closed 等） |
| `test_list_connected_external_accounts_record_type_values` | 验证 record_type 字段值 | 验证账户类型为常见值（Saving, Checking 等） |
| `test_list_connected_external_accounts_using_helper_method` | 使用辅助方法解析响应 | 验证 parse_list_response 方法 |

---

### 5. `test_open_banking_list_account_transactions.py`

测试 `GET /api/v1/cores/{core}/open-banking/accounts/:account_id/transactions` 接口

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_list_account_transactions_success` | 成功获取账户交易列表 | 验证返回 200，data 包含 content 数组 |
| `test_list_account_transactions_response_structure` | 验证响应数据结构 | 验证响应结构正确 |
| `test_list_account_transactions_key_fields` | 验证交易记录的关键字段 | 验证 transaction_id, transaction_type 等字段 |
| `test_list_account_transactions_amount_fields` | 验证金额相关字段 | 验证金额字段为数字类型 |
| `test_list_account_transactions_categorization_fields` | 验证分类相关字段 | 验证 categorization_* 系列字段 |
| `test_list_account_transactions_invalid_financial_account_id` | 使用无效的 financial_account_id | 验证错误处理 |

---

## 🚀 运行测试

### 激活虚拟环境并运行

```bash
# 进入项目目录
cd "/Users/mac/api auto/api_auto_framework"

# 激活虚拟环境
source .venv/bin/activate

# 运行所有 Open Banking 测试用例
pytest test_cases/open_banking/ -v

# 运行指定测试文件
pytest test_cases/open_banking/test_open_banking_list_authorized_accounts.py -v

# 运行指定的测试方法
pytest test_cases/open_banking/test_open_banking_list_authorized_accounts.py::TestOpenBankingListAuthorizedAccounts::test_list_authorized_accounts_success -v
```

### 使用 Marker 运行

```bash
# 运行所有 open_banking 相关测试
pytest -m open_banking -v

# 运行所有 list_api 相关测试
pytest -m list_api -v

# 运行所有 create_api 相关测试
pytest -m create_api -v

# 运行所有 transactions_api 相关测试
pytest -m transactions_api -v
```

## 📦 API 封装

API 封装位于 `api/open_banking_api.py`，提供以下方法：

### `OpenBankingAPI` 类

```python
from api.open_banking_api import OpenBankingAPI

# 初始化（使用登录会话）
open_banking_api = OpenBankingAPI(session=login_session)

# 1. 获取授权账户列表
response = open_banking_api.list_authorized_accounts(name="haif")

# 2. 创建 Open Banking 连接链接
response = open_banking_api.create_open_banking_connect_link(
    redirect_url="https://www.fintech.com",
    account_id="xxx"
)

# 3. 创建银行账户连接链接
response = open_banking_api.create_bank_account_connect_link(
    redirect_url="https://www.fintech.com",
    account_id="xxx"
)

# 4. 获取已连接外部账户列表
response = open_banking_api.list_connected_external_accounts(
    account_id="xxx"
)

# 5. 获取账户交易列表
response = open_banking_api.list_account_transactions(
    financial_account_id="xxx"
)

# 解析响应
parsed = open_banking_api.parse_list_response(response)
data = parsed['data']
```

## 📝 响应示例

### 1. 授权账户列表响应

```json
{
  "code": 200,
  "error_message": null,
  "error": null,
  "data": [
    {
      "id": "1714399032257vT2VC",
      "account_name": "0429001-haif",
      "account_number": "1-0001154",
      "account_status": "Active",
      "record_type": "Saving",
      ...
    }
  ]
}
```

### 2. 创建连接链接响应

```json
{
  "code": 200,
  "error_message": null,
  "error": null,
  "data": "https://connect2.finicity.com?customerId=xxxx&..."
}
```

### 3. 已连接外部账户列表响应

```json
{
  "code": 200,
  "error_message": null,
  "error": null,
  "data": [
    {
      "id": "1710524697411UNzmF",
      "name": "FinBank - Home Mortgage",
      "account_number": "1-02-1-0000146",
      "status": "Open",
      "record_type": "Saving",
      ...
    }
  ]
}
```

### 4. 账户交易列表响应

```json
{
  "code": 200,
  "error_message": null,
  "error": null,
  "data": {
    "content": [
      {
        "transaction_id": "xxx",
        "transaction_type": "debit",
        "description": "Transaction description",
        ...
      }
    ]
  }
}
```

## 🔗 相关文档

- 接口文档：Open Banking API Documentation
- 配置文件：`config/config.py`
- 全局 Fixture：`test_cases/conftest.py`

## 📋 测试统计

| 模块 | 测试文件数 | 测试场景数 |
|------|-----------|-----------|
| 授权账户列表 | 1 | 6 |
| 创建 Open Banking 连接链接 | 1 | 5 |
| 创建银行账户连接链接 | 1 | 6 |
| 已连接外部账户列表 | 1 | 6 |
| 账户交易列表 | 1 | 6 |
| **总计** | **5** | **29** |

## 💡 注意事项

1. **依赖关系**：部分测试需要先获取有效的 `account_id` 或 `financial_account_id`，因此会先调用相关的 List 接口
2. **数据可用性**：如果环境中没有相应的数据，测试会自动跳过（使用 `pytest.skip`）
3. **连接链接**：创建连接链接的接口返回的是第三方服务（如 Finicity）的 URL
4. **交易字段**：交易接口返回的字段非常多（50+ 字段），测试主要关注关键字段
5. **路径参数**：交易接口使用路径参数 `:account_id`，需要在 URL 中直接传入

## 🎯 测试覆盖范围

✅ 成功场景测试  
✅ 响应数据结构验证  
✅ 字段完整性验证  
✅ 字段类型验证  
✅ 枚举值验证  
✅ 参数筛选功能  
✅ 缺少必需参数  
✅ 无效参数处理  
✅ 辅助方法验证

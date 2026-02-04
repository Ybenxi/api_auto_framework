# Counterparty Management 模块自动化测试

## 📁 模块说明

Counterparty（交易对手方）是指与银行进行金融交易或合同安排的任何实体——个人、金融机构、公司、政府机构或法律组织。该模块提供了完整的 Counterparty 管理功能，包括创建、更新、查询、分组管理等，以及 MFA（多因素认证）相关功能。

---

## 📊 接口统计

本模块包含 **17 个接口**，分为以下几类：

| 分类 | 接口数量 | 说明 |
|------|---------|------|
| **Counterparty CRUD** | 3 | 列表、创建、更新 |
| **Counterparty MFA** | 5 | MFA 获取、发送、验证、带 MFA 创建/更新 |
| **Counterparty 关联** | 2 | 交易列表、终止操作 |
| **Counterparty Group** | 7 | 分组的 CRUD、分组内 Counterparty 管理 |
| **总计** | **17** | - |

---

## 🔍 接口详情

### 一、Counterparty CRUD 接口（3个）

#### 1. GET `/api/v1/cores/{core}/counterparties` - List Counterparties
**功能**：获取 Counterparties 列表（分页）  
**测试文件**：`test_counterparty_list_counterparties.py` ✅ **已创建**  
**测试场景**（6个）：
- ✅ 成功获取列表
- ✅ 使用 name 参数筛选
- ✅ 使用 status 参数筛选（Approved, Pending, Rejected, Terminated）
- ✅ 使用 payment_type 参数筛选（ACH, Check, Wire, International_Wire）
- ✅ 分页功能测试
- ✅ 使用辅助方法解析响应

#### 2. POST `/api/v1/cores/{core}/counterparties` - Create A New Counterparty
**功能**：创建新的 Counterparty（支持草稿模式）  
**测试文件**：`test_counterparty_create_counterparty.py` ✅ **已创建**  
**测试场景**（5个）：
- ✅ 成功创建 ACH 类型 Counterparty
- ✅ 成功创建 Wire 类型 Counterparty（自动填充字段）
- ✅ 缺少必需字段（验证错误处理）
- ✅ 使用无效的 type 值
- ✅ 创建草稿模式 Counterparty（payment_enable=false）

#### 3. PATCH `/api/v1/cores/{core}/counterparties/:id` - Update Counterparty Detail
**功能**：更新 Counterparty 信息  
**测试文件**：`test_counterparty_update_counterparty.py` 📝 **待创建**  
**推荐测试场景**（6个）：
- 成功更新 Counterparty 基本信息
- 更新银行账户信息
- 更新地址信息
- 更新 assign_account_ids
- 使用无效的 counterparty_id
- 缺少必需字段

---

### 二、Counterparty MFA 接口（5个）

#### 4. GET `/api/v2/cores/{core}/counterparties/:id/mfa` - Get MFA Message
**功能**：获取 Counterparty Record Owner 的 MFA 信息  
**测试文件**：`test_counterparty_get_mfa.py` 📝 **待创建**  
**推荐测试场景**（4个）：
- 成功获取 MFA 信息（email 和 phone_number）
- 使用无效的 counterparty_id
- 验证响应结构
- 验证字段类型

#### 5. POST `/api/v2/cores/{core}/counterparties/:id/mfa/send` - Send MFA Message
**功能**：发送 MFA 验证码  
**测试文件**：`test_counterparty_send_mfa.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功发送 Email 验证码
- 成功发送 Phone 验证码
- 使用无效的 verification_method
- 缺少 verification_method 参数
- 使用无效的 counterparty_id

#### 6. POST `/api/v2/cores/{core}/counterparties/:id/mfa/verify` - Verify MFA Message
**功能**：验证 MFA 验证码  
**测试文件**：`test_counterparty_verify_mfa.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功验证（返回 access_token）
- 使用错误的 verification_code
- 使用过期的 verification_code
- 缺少必需参数
- 验证 access_token 有效性

#### 7. POST `/api/v2/cores/{core}/counterparties` - Create with MFA
**功能**：使用 MFA 创建 Counterparty（V2 接口）  
**测试文件**：`test_counterparty_create_with_mfa.py` 📝 **待创建**  
**推荐测试场景**（6个）：
- 成功使用 access_token 创建
- access_token 15分钟有效期测试
- 使用无效的 access_token
- 缺少 access_token 参数
- M2M 认证直接创建（无需 MFA）
- 验证 low risk 账户自动 Approved

#### 8. PATCH `/api/v2/cores/{core}/counterparties/:id` - Update with MFA
**功能**：使用 MFA 更新 Counterparty（V2 接口）  
**测试文件**：`test_counterparty_update_with_mfa.py` 📝 **待创建**  
**推荐测试场景**（6个）：
- 成功使用 access_token 更新
- access_token 重复使用（15分钟内有效）
- 使用无效的 access_token
- 缺少 access_token 参数
- M2M 认证直接更新
- Record Owner 权限验证

---

### 三、Counterparty 关联接口（2个）

#### 9. GET `/api/v1/cores/{core}/counterparties/:id/transactions` - List Related Transactions
**功能**：获取 Counterparty 相关交易列表  
**测试文件**：`test_counterparty_list_transactions.py` 📝 **待创建**  
**推荐测试场景**（6个）：
- 成功获取交易列表
- 使用 financial_account_id 筛选
- 使用 sub_account_id 筛选
- 使用 start_date 和 end_date 筛选
- 使用 transaction_type 筛选（Credit, Debit）
- 使用 status 筛选（Processing, Reviewing, Completed, Cancelled, Failed）

#### 10. PATCH `/api/v1/cores/{core}/counterparties/:id/terminate` - Terminate Counterparty
**功能**：终止 Counterparty  
**测试文件**：`test_counterparty_terminate.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功终止 Counterparty
- 终止后状态变为 Terminated
- 使用无效的 counterparty_id
- 缺少 account_ids 参数
- 终止后无法用于 money movement

---

### 四、Counterparty Group 接口（7个）

#### 11. GET `/api/v1/cores/{core}/counterparty-groups` - List Groups
**功能**：获取 Counterparty Groups 列表  
**测试文件**：`test_counterparty_list_groups.py` ✅ **已创建**  
**测试场景**（6个）：
- ✅ 成功获取 Groups 列表
- ✅ 使用 name 参数筛选
- ✅ 分页功能测试
- ✅ 验证响应数据结构
- ✅ 使用辅助方法解析响应
- ✅ 测试空结果场景

#### 12. POST `/api/v1/cores/{core}/counterparty-groups` - Create Group
**功能**：创建 Counterparty Group  
**测试文件**：`test_counterparty_create_group.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功创建 Group
- 返回 id 和 name 字段
- 缺少 name 参数
- 使用重复的 name
- 验证响应结构

#### 13. PATCH `/api/v1/cores/{core}/counterparty-groups/:id` - Update Group
**功能**：更新 Counterparty Group 名称  
**测试文件**：`test_counterparty_update_group.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功更新 Group 名称
- 使用无效的 group_id
- 缺少 name 参数
- 更新为重复的 name
- 验证更新后的数据

#### 14. GET `/api/v1/cores/{core}/counterparty-groups/:id/counterparties` - List Group Counterparties
**功能**：获取 Group 下的 Counterparties 列表  
**测试文件**：`test_counterparty_list_group_counterparties.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功获取 Group 内的 Counterparties
- 分页功能测试
- 使用无效的 group_id
- 空 Group 测试
- 验证响应结构

#### 15. POST `/api/v1/cores/{core}/counterparty-groups/:id/counterparty` - Add to Group
**功能**：添加 Counterparties 到 Group  
**测试文件**：`test_counterparty_add_to_group.py` 📝 **待创建**  
**推荐测试场景**（6个）：
- 成功添加单个 Counterparty
- 成功添加多个 Counterparties
- 使用无效的 group_id
- 使用无效的 counterparty_id
- 缺少 counterparty_ids 参数
- 重复添加测试

#### 16. DELETE `/api/v1/cores/{core}/counterparty-groups/:id/counterparty` - Remove from Group
**功能**：从 Group 中移除 Counterparty  
**测试文件**：`test_counterparty_remove_from_group.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功移除 Counterparty
- 使用无效的 group_id
- 使用无效的 counterparty_id
- 缺少 counterparty_id 参数
- 移除不存在的 Counterparty

#### 17. DELETE `/api/v1/cores/{core}/counterparty-groups/:id` - Delete Group
**功能**：删除 Counterparty Group  
**测试文件**：`test_counterparty_delete_group.py` 📝 **待创建**  
**推荐测试场景**（5个）：
- 成功删除 Group
- 删除后 Group 不存在
- 使用无效的 group_id
- 删除包含 Counterparties 的 Group
- 重复删除测试

---

## 🚀 快速开始

### 运行所有测试

```bash
cd "/Users/mac/api auto/api_auto_framework"
source .venv/bin/activate

# 运行所有 Counterparty 测试
pytest test_cases/counterparty/ -v

# 或使用 marker
pytest -m counterparty -v
```

### 运行指定测试文件

```bash
# 已创建的测试文件
pytest test_cases/counterparty/test_counterparty_list_counterparties.py -v
pytest test_cases/counterparty/test_counterparty_create_counterparty.py -v
pytest test_cases/counterparty/test_counterparty_list_groups.py -v
```

### 使用 Marker 筛选

```bash
# 列表接口
pytest -m list_api -v

# 创建接口
pytest -m create_api -v

# 删除接口
pytest -m delete_api -v

# MFA 接口
pytest -m mfa_api -v
```

---

## 📦 API 使用示例

```python
from api.counterparty_api import CounterpartyAPI

# 初始化
counterparty_api = CounterpartyAPI(session=login_session)

# 1. 列表接口
response = counterparty_api.list_counterparties(
    name="Test",
    status="Approved",
    payment_type="ACH",
    page=0,
    size=10
)

# 2. 创建 Counterparty
counterparty_data = {
    "name": "Test Counterparty",
    "type": "Person",
    "payment_type": "ACH",
    "bank_account_type": "Checking",
    "bank_routing_number": "091918457",
    "bank_account_owner_name": "Test Owner",
    "bank_account_number": "111111111",
    "assign_account_ids": ["account_id_123"]
}
response = counterparty_api.create_counterparty(counterparty_data)

# 3. 更新 Counterparty
update_data = {
    "name": "Updated Name",
    "bank_account_owner_name": "New Owner"
}
response = counterparty_api.update_counterparty("counterparty_id", update_data)

# 4. MFA 流程
# 4.1 获取 MFA 信息
response = counterparty_api.get_counterparty_mfa("counterparty_id")

# 4.2 发送 MFA 验证码
response = counterparty_api.send_counterparty_mfa("counterparty_id", "Email")

# 4.3 验证 MFA
response = counterparty_api.verify_counterparty_mfa(
    "counterparty_id",
    "123456",
    "Email"
)
access_token = response.json()["data"]["access_token"]

# 4.4 使用 access_token 创建/更新
counterparty_data["access_token"] = access_token
response = counterparty_api.create_counterparty_with_mfa(counterparty_data)

# 5. 交易列表
response = counterparty_api.list_counterparty_transactions(
    "counterparty_id",
    financial_account_id="fa_id",
    start_date="2025-01-01",
    end_date="2025-01-31"
)

# 6. Group 管理
# 6.1 创建 Group
response = counterparty_api.create_counterparty_group("My Group")

# 6.2 添加到 Group
response = counterparty_api.add_counterparties_to_group(
    "group_id",
    ["counterparty_id1", "counterparty_id2"]
)

# 6.3 从 Group 移除
response = counterparty_api.remove_counterparty_from_group(
    "group_id",
    "counterparty_id"
)

# 6.4 删除 Group
response = counterparty_api.delete_counterparty_group("group_id")

# 7. 终止 Counterparty
response = counterparty_api.terminate_counterparty(
    "counterparty_id",
    ["account_id1", "account_id2"]
)

# 8. 解析响应（列表接口）
parsed = counterparty_api.parse_list_response(response)
if not parsed.get("error"):
    content = parsed["content"]
    total = parsed["total_elements"]
```

---

## 📝 测试进度

| 状态 | 文件数 | 说明 |
|------|-------|------|
| ✅ **已创建** | 3 | List Counterparties, Create Counterparty, List Groups |
| 📝 **待创建** | 14 | 其他接口测试文件 |
| **总计** | **17** | - |

### 已创建的测试文件（3个）

1. ✅ `test_counterparty_list_counterparties.py` - 6 个测试场景
2. ✅ `test_counterparty_create_counterparty.py` - 5 个测试场景
3. ✅ `test_counterparty_list_groups.py` - 6 个测试场景

### 测试文件创建模板

其余 14 个测试文件可以参考已创建的文件结构，遵循以下模式：

```python
"""
接口描述
测试 HTTP_METHOD /api/path 接口
"""
import pytest
from api.counterparty_api import CounterpartyAPI


@pytest.mark.counterparty
@pytest.mark.{类型}_api  # list_api, create_api, update_api, delete_api, mfa_api
class Test{ClassName}:
    """
    接口测试用例集
    """

    def test_{scenario_name}(self, login_session):
        """
        测试场景描述
        验证点：
        1. ...
        2. ...
        """
        # 测试逻辑
        pass
```

---

## 💡 重要概念

### 1. Counterparty Status

| Status | 描述 |
|--------|------|
| **Approved** | 激活状态，可以正常使用 |
| **Rejected** | 被拒绝，无法正常操作 |
| **Pending** | 待审批状态 |
| **Terminated** | 已终止，无法继续使用 |

### 2. Counterparty Type

- **Person**: 个人
- **Company**: 公司
- **Vendor**: 供应商
- **Employee**: 员工

### 3. Payment Type

- **ACH**: 自动清算所转账
- **Check**: 支票
- **Wire**: 电汇
- **International_Wire**: 国际电汇
- **Stablecoin**: 稳定币

### 4. MFA 认证流程

1. **获取 MFA 信息**：`GET /counterparties/:id/mfa`
2. **发送验证码**：`POST /counterparties/:id/mfa/send`
3. **验证**：`POST /counterparties/:id/mfa/verify` → 获得 access_token
4. **使用 access_token**：创建/更新操作（15分钟有效期）

### 5. payment_enable 字段

- `true`: 所有必需字段完整，可用于 money movement
- `false`: 字段不完整，为草稿状态，不可用于转账

### 6. assign_account_ids 状态

- **Low risk 账户**: 自动标记为 "Approved"
- **High risk 账户**: 标记为 "Pending"，需要审批

---

## 🔗 相关文档

- 详细 API 文档：Counterparty Management API Documentation
- API 封装：`api/counterparty_api.py`
- 配置文件：`config/config.py`
- 全局 Fixture：`test_cases/conftest.py`

---

## 📊 字段清单

### Counterparty 主要字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | string | - | 唯一标识符 |
| `name` | string | ✅ | 名称 |
| `type` | string | ✅ | 类型 |
| `payment_type` | string | ✅ | 支付类型 |
| `bank_account_number` | string | - | 银行账号 |
| `bank_account_type` | string | - | 账户类型 |
| `bank_routing_number` | string | - | 路由号码 |
| `bank_account_owner_name` | string | - | 账户所有者 |
| `assign_account_ids` | array | - | 关联账户 |
| `payment_enable` | boolean | - | 是否可用于支付 |
| `country` | string | - | 国家 |
| `address1` | string | - | 地址1 |
| `city` | string | - | 城市 |
| `state` | string | - | 州/省 |
| `zip_code` | string | - | 邮编 |
| `swift_code` | string | - | SWIFT 代码 |

---

**创建时间**：2026-02-04  
**版本**：v1.0  
**状态**：核心功能已完成，待扩展其他测试文件

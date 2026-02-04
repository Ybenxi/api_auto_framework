# Counterparty Management 模块自动化测试 - 设置完成

## ✅ 任务完成摘要

已成功为 **Counterparty Management** 模块生成自动化测试脚本的基础架构和核心测试文件。

---

## 📁 已创建的文件

### 1. API 封装层
- ✅ `api/counterparty_api.py` - Counterparty API 封装类（完整实现 17 个接口）

### 2. 测试用例层
```
test_cases/counterparty/
├── conftest.py                                              # Pytest 配置 ✅
├── test_counterparty_list_counterparties.py                 # 列表接口（6 个场景）✅
├── test_counterparty_create_counterparty.py                 # 创建接口（5 个场景）✅
├── test_counterparty_list_groups.py                         # 分组列表（6 个场景）✅
└── README.md                                                # 详细说明文档 ✅
```

### 3. 配置更新
- ✅ 更新 `test_cases/conftest.py` - 添加 Counterparty 模块映射
- ✅ 更新 `pytest.ini` - 添加 counterparty, delete_api, mfa_api markers

---

## 📊 接口统计

| 分类 | 接口数量 | 已创建测试 | 待创建测试 | 状态 |
|------|---------|-----------|-----------|------|
| **Counterparty CRUD** | 3 | 2 | 1 | 🟡 部分完成 |
| **Counterparty MFA** | 5 | 0 | 5 | 🔴 待创建 |
| **Counterparty 关联** | 2 | 0 | 2 | 🔴 待创建 |
| **Counterparty Group** | 7 | 1 | 6 | 🔴 待创建 |
| **总计** | **17** | **3** | **14** | - |

---

## 🔍 完整接口清单

### ✅ 已创建测试的接口（3个）

| # | 接口 | HTTP | 测试文件 | 场景数 |
|---|------|------|---------|--------|
| 1 | List Counterparties | GET | test_counterparty_list_counterparties.py | 6 |
| 2 | Create Counterparty | POST | test_counterparty_create_counterparty.py | 5 |
| 11 | List Groups | GET | test_counterparty_list_groups.py | 6 |

### 📝 待创建测试的接口（14个）

#### Counterparty CRUD（1个）
| # | 接口 | HTTP | 推荐场景数 |
|---|------|------|-----------|
| 3 | Update Counterparty | PATCH | 6 |

#### Counterparty MFA（5个）
| # | 接口 | HTTP | 推荐场景数 |
|---|------|------|-----------|
| 4 | Get MFA Message | GET | 4 |
| 5 | Send MFA Message | POST | 5 |
| 6 | Verify MFA Message | POST | 5 |
| 7 | Create with MFA (V2) | POST | 6 |
| 8 | Update with MFA (V2) | PATCH | 6 |

#### Counterparty 关联（2个）
| # | 接口 | HTTP | 推荐场景数 |
|---|------|------|-----------|
| 9 | List Related Transactions | GET | 6 |
| 10 | Terminate Counterparty | PATCH | 5 |

#### Counterparty Group（6个）
| # | 接口 | HTTP | 推荐场景数 |
|---|------|------|-----------|
| 12 | Create Group | POST | 5 |
| 13 | Update Group | PATCH | 5 |
| 14 | List Group Counterparties | GET | 5 |
| 15 | Add to Group | POST | 6 |
| 16 | Remove from Group | DELETE | 5 |
| 17 | Delete Group | DELETE | 5 |

---

## 🚀 快速开始

### 运行已创建的测试

```bash
# 进入项目目录并激活虚拟环境
cd "/Users/mac/api auto/api_auto_framework"
source .venv/bin/activate

# 运行所有 Counterparty 测试
pytest test_cases/counterparty/ -v

# 运行指定文件
pytest test_cases/counterparty/test_counterparty_list_counterparties.py -v
pytest test_cases/counterparty/test_counterparty_create_counterparty.py -v
pytest test_cases/counterparty/test_counterparty_list_groups.py -v

# 使用 marker
pytest -m counterparty -v
pytest -m list_api -v
pytest -m create_api -v
```

---

## 📦 API 使用示例

### 基础操作

```python
from api.counterparty_api import CounterpartyAPI

# 初始化
counterparty_api = CounterpartyAPI(session=login_session)

# 1. 列表查询
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
update_data = {"name": "Updated Name"}
response = counterparty_api.update_counterparty("counterparty_id", update_data)
```

### MFA 认证流程

```python
# 1. 获取 MFA 信息
mfa_info = counterparty_api.get_counterparty_mfa("counterparty_id")
# 返回: {"email": "user@example.com", "phone_number": "+1234567890"}

# 2. 发送验证码
counterparty_api.send_counterparty_mfa("counterparty_id", "Email")

# 3. 验证验证码
verify_response = counterparty_api.verify_counterparty_mfa(
    "counterparty_id",
    "123456",  # 用户输入的验证码
    "Email"
)
access_token = verify_response.json()["data"]["access_token"]

# 4. 使用 access_token 创建/更新
counterparty_data["access_token"] = access_token
response = counterparty_api.create_counterparty_with_mfa(counterparty_data)
```

### Group 管理

```python
# 1. 创建 Group
response = counterparty_api.create_counterparty_group("My Group")
group_id = response.json()["id"]

# 2. 列出 Groups
response = counterparty_api.list_counterparty_groups(name="My Group")

# 3. 添加 Counterparties 到 Group
counterparty_api.add_counterparties_to_group(
    group_id,
    ["counterparty_id1", "counterparty_id2"]
)

# 4. 列出 Group 内的 Counterparties
response = counterparty_api.list_group_counterparties(group_id)

# 5. 从 Group 移除 Counterparty
counterparty_api.remove_counterparty_from_group(group_id, "counterparty_id1")

# 6. 删除 Group
counterparty_api.delete_counterparty_group(group_id)
```

---

## 📝 测试文件创建指南

### 文件命名规范

```
test_counterparty_{operation}_{object}.py
```

**示例**：
- `test_counterparty_update_counterparty.py`
- `test_counterparty_get_mfa.py`
- `test_counterparty_create_group.py`
- `test_counterparty_delete_group.py`

### 测试类命名

```python
class TestCounterparty{Operation}{Object}:
    """测试用例集描述"""
```

**示例**：
- `TestCounterpartyUpdateCounterparty`
- `TestCounterpartyGetMfa`
- `TestCounterpartyCreateGroup`

### 测试方法命名

```python
def test_{scenario_description}(self, login_session):
    """
    测试场景N：场景描述
    验证点：
    1. ...
    2. ...
    """
```

### Markers 使用

```python
@pytest.mark.counterparty           # 所有测试必须添加
@pytest.mark.{type}_api              # list_api, create_api, update_api, delete_api, mfa_api
class TestClassName:
    pass
```

---

## 💡 重要概念

### 1. Status 枚举

| Status | 描述 | 可用性 |
|--------|------|-------|
| **Approved** | 已批准 | ✅ 可用于 money movement |
| **Pending** | 待审批 | ❌ 不可用于 money movement |
| **Rejected** | 已拒绝 | ❌ 不可用 |
| **Terminated** | 已终止 | ❌ 不可用 |

### 2. Type 枚举

- **Person**: 个人
- **Company**: 公司
- **Vendor**: 供应商
- **Employee**: 员工

### 3. Payment Type 枚举

- **ACH**: 自动清算所转账
- **Check**: 支票
- **Wire**: 电汇（自动填充银行信息）
- **International_Wire**: 国际电汇
- **Stablecoin**: 稳定币

### 4. payment_enable 字段

- `true`: 所有必需字段完整，可用于 money movement
- `false`: 字段不完整，为草稿状态

### 5. 账户风险级别

- **Low risk 账户**: 创建时自动标记为 "Approved"
- **High risk 账户**: 创建时标记为 "Pending"，需要审批

### 6. MFA 认证规则

- **M2M 认证**：直接修改，无需 MFA
- **非 M2M 认证**：需要 MFA 验证
- **access_token 有效期**：单次使用后 15 分钟内有效

---

## 📊 数据依赖关系

```
Profile Account
    ↓
Counterparty ←→ Counterparty Group
    ↓
Transactions
```

---

## 🎯 测试优先级建议

### 高优先级（核心功能）
1. ✅ List Counterparties
2. ✅ Create Counterparty
3. 📝 Update Counterparty
4. ✅ List Groups
5. 📝 Create Group

### 中优先级（MFA 流程）
6. 📝 Get MFA Message
7. 📝 Send MFA Message
8. 📝 Verify MFA Message
9. 📝 Create with MFA
10. 📝 Update with MFA

### 普通优先级（关联功能）
11. 📝 List Related Transactions
12. 📝 Terminate Counterparty
13. 📝 Update Group
14. 📝 List Group Counterparties
15. 📝 Add to Group
16. 📝 Remove from Group
17. 📝 Delete Group

---

## 🔗 相关文档

- **详细说明**：`test_cases/counterparty/README.md`
- **API 封装**：`api/counterparty_api.py`
- **配置文件**：`config/config.py`
- **全局 Fixture**：`test_cases/conftest.py`

---

## 📈 扩展建议

### 需要创建的测试文件（14个）

1. `test_counterparty_update_counterparty.py`
2. `test_counterparty_get_mfa.py`
3. `test_counterparty_send_mfa.py`
4. `test_counterparty_verify_mfa.py`
5. `test_counterparty_create_with_mfa.py`
6. `test_counterparty_update_with_mfa.py`
7. `test_counterparty_list_transactions.py`
8. `test_counterparty_terminate.py`
9. `test_counterparty_create_group.py`
10. `test_counterparty_update_group.py`
11. `test_counterparty_list_group_counterparties.py`
12. `test_counterparty_add_to_group.py`
13. `test_counterparty_remove_from_group.py`
14. `test_counterparty_delete_group.py`

### 每个文件推荐 4-6 个测试场景

**参考已创建文件的结构**：
- 成功场景（Happy Path）
- 参数筛选/验证
- 错误处理（无效 ID、缺少参数）
- 边界条件
- 响应结构验证
- 辅助方法验证

---

## ✨ 特色功能

### 1. 完整的 API 封装
- ✅ 17 个接口全部封装
- ✅ 类型提示（Type Hints）
- ✅ 详细的文档字符串
- ✅ 辅助方法（parse_list_response）

### 2. 统一的测试风格
- ✅ 清晰的测试步骤（Step by Step）
- ✅ 详细的日志输出
- ✅ 完善的断言和错误信息
- ✅ Markers 标记分类

### 3. 灵活的参数处理
- ✅ 可选参数支持
- ✅ 列表参数处理
- ✅ 分页参数统一
- ✅ kwargs 扩展支持

### 4. 数据依赖管理
- ✅ 自动获取依赖数据（Account ID）
- ✅ 数据不可用自动跳过（pytest.skip）
- ✅ 使用 login_session fixture

---

## 🎨 代码质量

### ✅ 代码特点
- 遵循项目现有代码风格
- 完整的中文注释
- 详细的日志输出
- 清晰的错误信息
- 完善的文档

### ✅ 测试设计
- 每个接口独立测试文件
- 每个场景独立测试方法
- 清晰的测试步骤
- 完善的断言逻辑

---

**创建时间**：2026-02-04  
**版本**：v1.0  
**状态**：基础架构完成，核心测试已创建（3/17），其余测试待扩展  
**估算测试场景总数**：~85 个（已创建 17 个，待创建 ~68 个）

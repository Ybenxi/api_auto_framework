# Wire Processing 模块测试

## 模块概述
Wire Processing提供国内和国际电汇转账功能，是实时全额结算（RTGS）系统，支持安全可靠的电子资金转移。

## API 接口列表（8个）

### 查询接口（3个）
1. **GET** `/money-movements/wire/transactions` - 获取交易列表
2. **GET** `/money-movements/wire/financial-accounts` - 获取可用账户列表
3. **GET** `/money-movements/wire/counterparties` - 获取对手方列表

### 对手方管理（1个）
4. **POST** `/money-movements/wire/counterparties` - 创建对手方（极其复杂）

### 转账接口（3个）
5. **POST** `/money-movements/wire/payment` - 发起国内电汇
6. **POST** `/money-movements/international-wire/payment` - 发起国际电汇
7. **POST** `/money-movements/wire/request-payment` - 请求收款

### 费用接口（1个）
8. **POST** `/money-movements/wire/fee` - 计算交易费用

## 测试文件列表（4个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_wire_transactions.py` | 5 | 交易列表查询 |
| `test_wire_counterparties.py` | 7 | 对手方列表和创建 |
| `test_wire_payment.py` | 5 | 电汇转账（破坏性） |
| `test_wire_fee.py` | 4 | 费用计算 |

**总计：21个测试场景**

## 关键枚举类型

```python
class WirePaymentType(str, Enum):
    WIRE = "Wire"                           # 国内电汇
    INTERNATIONAL_WIRE = "International_Wire"  # 国际电汇

class CounterpartyType(str, Enum):
    EMPLOYEE = "Employee"
    COMPANY = "Company"
    PERSON = "Person"
    VENDOR = "Vendor"

class BankAccountType(str, Enum):
    SAVINGS = "Savings"
    CHECKING = "Checking"
```

## Create Counterparty 条件必需字段规则

### ⚠️ 极其复杂的条件逻辑

#### 基础必需字段（所有类型）
- name, type, bank_account_type
- bank_account_owner_name, bank_account_number

#### Wire类型条件必需
```python
if payment_type == "Wire":
    必需: bank_routing_number
```

#### International_Wire类型条件必需
```python
if payment_type == "International_Wire":
    必需: 
    - country, address1, city, state, zip_code
    - bank_country, swift_code, bank_name
    - bank_address, bank_city, bank_state, bank_zip_code
```

#### Intermediary Bank 条件必需（第一组）
```python
if 提供了任何intermediary bank字段:
    必需:
    - intermediary_financial_institution
    - intermediary_bank_routing_number
    - intermediary_bank_city
    - intermediary_bank_state
    - intermediary_bank_country
```

#### Intermediary Bank2 条件必需（第二组）
```python
if 提供了任何intermediary bank2字段:
    必需:
    - intermediary_bank2_institution
    - intermediary_bank2_routing_number OR intermediary_bank2_swift_code（至少一个）
    - intermediary_bank2_city
    - intermediary_bank2_state
    - intermediary_bank2_country
```

## 文档已知问题（45个）

### 🔴 严重问题（15个）
- URL路径不一致（2处）
- Create Counterparty条件必需字段规则极其复杂
- Wire vs International Wire接口完全重复
- 大量响应字段未定义（40+个）
- intermediary_bank2_swift_code条件说明错误

### 🟡 中等问题（20个）
- 响应格式不一致（7个接口无code包装层）
- HTTP方法示例错误
- 字段命名不一致
- 条件逻辑说明混乱

### 🟢 轻微问题（10个）
- 拼写错误、描述错误等

## 响应格式说明

### 无code包装层（7个接口）
所有List接口、Create Counterparty、所有Payment接口

### 有code包装层（1个接口）
Quote Fee接口

## Skip的测试

### 可运行（约8个）
- List接口查询
- 费用计算
- 错误处理

### Skip（约13个）
- 创建对手方（参数复杂）
- 所有转账操作（真实扣款）

## 安全提醒

### ⚠️⚠️⚠️ 电汇操作极度危险
- 会实际扣款
- 不可撤销
- 涉及外部银行
- 所有payment测试必须skip

## 运行测试

```bash
pytest test_cases/payment_deposit/wire_processing/ -v
pytest -m wire_processing -v
```

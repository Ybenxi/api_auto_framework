# Account Summary 模块测试

## 模块概述
Account Summary（账户摘要）模块提供可见账户的汇总信息，包括Financial Accounts、Sub Accounts和Debit Cards的详细数据。支持分类和扁平两种展示模式。

## API 接口列表（1个）

1. **GET** `/api/v1/cores/{core}/account/summary` - 获取账户摘要

## 测试文件列表（2个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_account_summary_categorized.py` | 8 | Categorized模式测试 |
| `test_account_summary_flat.py` | 6 | Flat模式测试（探索性） |

**总计：14个测试场景**

## 关键枚举类型

```python
class ClassificationMode(str, Enum):
    """账户摘要分类模式"""
    FLAT = "Flat"              # 扁平结构（无分组）
    CATEGORIZED = "Categorized" # 分类结构（按Asset/Liability分组）
```

## 两种模式对比

### Categorized模式（已知结构）
```json
{
    "code": 200,
    "data": {
        "total_balance": "2990",
        "asset_financial_accounts": {
            "total_balance": "2453394.11",
            "record_type": [
                {
                    "name": "Bank Account",
                    "total_balance": "1000",
                    "financial_accounts": [
                        {
                            "name": "Example",
                            "sub_accounts": [...]
                        }
                    ]
                }
            ]
        },
        "liability_financial_accounts": {...},
        "debit_cards": [...]
    }
}
```

**特点**：
- 按Asset/Liability分组
- 再按record_type分组
- 4层嵌套结构
- 每层都有total_balance

### Flat模式（结构待验证）⚠️
```
⚠️ 文档缺少Flat模式响应示例
测试采用探索性策略：
1. 记录实际响应结构
2. 对比与Categorized的差异
3. 验证数据一致性
```

## 文档已知问题（15个）

### 🔴 严重问题（3个）
1. **字段类型不一致**：balance在响应中是string，应为number
2. **字段命名不一致**：
   - Financial Account层级：`total_balance`
   - Sub Account层级：`balance`
3. **Response Properties完全缺失**：没有任何字段定义

### 🟡 中等问题（6个）
4. **Flat模式缺少示例**：响应结构完全未知
5. **classification_mode行为说明不完整**
6. **枚举值大小写不一致**：Flat vs Categorized（首字母大写）
7. **created_date字段类型不一致**：Sub Account中为null
8. **status枚举值未定义**：Open, Closed等
9. **record_type命名混乱**：既是数组名又是对象属性

### 🟢 轻微问题（6个）
10. **account_type字段说明缺失**：Asset, Liability
11. **字段顺序不一致**
12. **source字段枚举未说明**：Managed等
13. **嵌套层级较深**：缺少结构图
14. **空数组示例意义不明**：liability_financial_accounts为空
15. **卡片字段冗余**：card_holder_id vs created_by

## 响应结构分析

### 嵌套层级（Categorized模式）
```
data (Level 1)
├─ total_balance
├─ asset_financial_accounts (Level 2)
│   ├─ total_balance
│   └─ record_type[] (Level 3)
│       ├─ name: "Bank Account"
│       ├─ total_balance
│       └─ financial_accounts[] (Level 4)
│           ├─ name, total_balance, ...
│           └─ sub_accounts[] (Level 5)
│               └─ name, balance, ...
└─ debit_cards[]
```

**关键字段**：
- Level 1: `total_balance` (string/number)
- Level 2: `total_balance` (string/number)
- Level 3: `total_balance` (string/number)
- Level 4: `total_balance` (string/number)
- Level 5: `balance` (string/number) ⚠️ 命名不一致

## balance字段类型兼容

### 问题
响应示例中balance字段是string：
```json
"total_balance": "2990",      // string
"available_balance": "37068.07"
```

但实际应该是number。

### 解决方案
API封装类提供`_to_float()`方法兼容两种格式：
```python
def _to_float(self, value) -> float:
    """统一转换为float，兼容string和number"""
    if value is None:
        return 0.0
    try:
        return float(value)
    except:
        return 0.0
```

## 测试策略

### 1. Categorized模式（完整测试）
```python
# 可直接运行
test_get_categorized_summary_success()
test_verify_asset_financial_accounts_structure()
test_verify_record_type_grouping()
test_balance_field_type_handling()
```

### 2. Flat模式（探索性测试）
```python
# 探索实际结构
test_verify_flat_response_structure()  # 记录字段

# 对比一致性
test_compare_categorized_vs_flat_data()

# 验证无分组
test_verify_no_grouping_in_flat_mode()
```

### 3. 数据验证
```python
# 余额计算验证
test_total_balance_calculation()

# 嵌套验证
test_verify_sub_accounts_nesting()

# 卡片验证
test_verify_debit_cards_array()
```

## parse方法使用

### parse_categorized_response
```python
parsed = account_summary_api.parse_categorized_response(response)

# 返回：
{
    "error": False,
    "total_balance": 2990.0,  # 已转为float
    "asset_balance": 2453394.11,
    "liability_balance": 0.0,
    "financial_accounts_count": 2,
    "sub_accounts_count": 3,
    "debit_cards_count": 1
}
```

### parse_flat_response
```python
parsed = account_summary_api.parse_flat_response(response)

# 返回：
{
    "error": False,
    "data": {...},  # 原始数据
    "structure": "flat"
}
```

## 运行测试

```bash
# 运行所有Account Summary测试
pytest test_cases/account_summary/ -v

# 运行Categorized模式测试
pytest test_cases/account_summary/test_account_summary_categorized.py -v

# 运行Flat模式测试（探索性）
pytest test_cases/account_summary/test_account_summary_flat.py -v

# 按标记运行
pytest -m account_summary -v
```

## 预期行为

### Categorized模式
✅ 结构已知，测试完整
- 按Asset/Liability分组
- 按record_type二级分组
- 嵌套sub_accounts
- 包含debit_cards数组

### Flat模式
⚠️ 结构未知，采用探索性测试
- 可能直接平铺financial_accounts
- 可能仍保留分组（需验证）
- 数据内容应与Categorized一致

## 数据一致性验证

### 余额计算
```python
# 理论上
total_balance = asset_balance - liability_balance

# 实际验证
calculated = account_summary_api.calculate_total_balance(parsed)
assert abs(calculated - total_balance) < 0.01
```

### 字段命名
- Financial Account: `total_balance`
- Sub Account: `balance` ⚠️ 不一致

建议在parse方法中统一处理。

## 特殊说明

### record_type分类
常见类型：
- Bank Account
- Investment Account
- Credit Card Account
- Loan Account

### sub_type vs record_type
- `record_type`：记录类型（顶层分类）
- `sub_type`：子类型（如Checking, Savings, Investment）

### account_type vs classification
- `account_type`：Asset或Liability
- 决定在哪个分组中显示

### debit_cards独立数组
卡片不在financial_accounts中，而是独立的顶层数组。

## 容错建议

### balance类型处理
```python
# 始终使用_to_float转换
balance = account_summary_api._to_float(raw_balance)
```

### 字段命名兼容
```python
# Sub Account的balance字段
balance = sub_acc.get("balance") or sub_acc.get("total_balance")
```

### Flat模式未知结构
```python
# 先探索，再断言
logger.info(f"实际字段: {list(data.keys())}")
if "financial_accounts" in data:
    # 扁平结构
    pass
elif "asset_financial_accounts" in data:
    # 仍为分组结构
    pass
```

## 问题反馈

所有文档问题已提交给开发团队，最严重的是：
1. Response Properties完全缺失
2. Flat模式无示例
3. balance字段类型不一致

测试代码已做兼容处理，使用探索性测试策略验证未知结构。

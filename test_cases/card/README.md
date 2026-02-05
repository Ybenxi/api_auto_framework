# Card 模块测试

## 模块概述
Card模块是最大的功能模块，包含卡片管理的完整生命周期，从申请、发行、使用到争议处理和风险控制。

## 子模块划分（4个）

### 1. Card Opening（卡片申请）- 4个接口
卡片申请的创建和查询功能

### 2. Card Management（卡片管理）- 14个接口
卡片的查询、激活、锁定、更新、交易查询等完整管理功能

### 3. Sub Program（子项目）- 5个接口
子项目和嵌套项目的管理和查询

### 4. Dispute & Risk Control（争议与风险控制）- 6个接口
争议处理、消费限制和MCC码管理

## API 接口总览（29个）

| 子模块 | 接口数 | 测试文件数 | 测试场景数 |
|--------|--------|-----------|-----------|
| Card Opening | 4 | 4 | ~25 |
| Card Management | 14 | 6 | ~50 |
| Sub Program | 5 | 5 | ~27 |
| Dispute & Risk | 6 | 5 | ~30 |
| **总计** | **29** | **20** | **~132** |

## 测试文件列表

### Card Opening
1. `test_card_opening_debit_card.py` - 借记卡申请（8场景）
2. `test_card_opening_reward_card.py` - 奖励卡申请（7场景，全skip）
3. `test_card_opening_list_applications.py` - 申请列表（6场景）
4. `test_card_opening_application_detail.py` - 申请详情（4场景）

### Card Management
1. `test_card_list_card_holders.py` - 持卡人列表（6场景）
2. `test_card_list_cards.py` - 卡片列表（8场景）
3. `test_card_detail.py` - 卡片详情（4场景）
4. `test_card_remaining_usage.py` - 剩余额度（5场景）
5. `test_card_transactions.py` - 交易查询（7场景）
6. `test_card_operations.py` - 卡片操作（12场景）

### Sub Program
1. `test_sub_program_list.py` - 子项目列表（7场景）
2. `test_sub_program_detail.py` - 子项目详情（4场景）
3. `test_sub_program_nested_programs.py` - 嵌套项目列表（6场景）
4. `test_nested_program_detail.py` - 嵌套项目详情（4场景）
5. `test_nested_program_using_log.py` - 使用日志（6场景）

### Dispute & Risk Control
1. `test_card_dispute_list.py` - 争议列表（6场景）
2. `test_card_dispute_create.py` - 创建争议（5场景，skip）
3. `test_card_dispute_detail.py` - 争议详情（4场景）
4. `test_risk_spending_limit.py` - 消费限制（7场景）
5. `test_risk_mcc_code.py` - MCC码（5场景）

## 关键枚举类型（10个）

```python
# 卡片相关
CardNetwork        # Visa, Mastercard
CardType           # Debit_Card
CardStatus         # Pending, Active, Locked, Expired等
LimitType          # Calendar_Date, Active_Date

# 消费限制
SpendingLimitInterval  # Daily, Weekly, Monthly等

# Sub Program
SubProgramStatus       # Active, Inactive, Under_Review
ClassificationType     # Business, Consumer

# Dispute
DisputeStatus          # New, Submitted, Result

# Transaction
TransactionStatus      # Pending, Settled等
ReplaceReason         # Reissued, Lost

# Nested Program
NestedProgramLogStatus # Completed, Cancel, Pending
```

## 文档已知问题（43个）

### 🔴 严重问题（14个）
1-7. JSON格式错误（缺少逗号，至少8处）
8. 字段名拼写错误（country:）
9. "frist name"拼写错误
10. 日期格式不一致（expiration_date）
11. birth_date vs birthdate命名不一致
12. disputed_reason类型定义错误（int→string）
13. disputed_amount类型不一致
14. 接口描述错误（多处）

### 🟡 中等问题（19个）
15-33. 包括：
- 响应格式不一致
- 字段类型不一致（is_virtual, amount）
- 枚举值未定义
- 字段未在Properties定义
- 条件必需字段不清晰
- 字段命名不统一

### 🟢 轻微问题（10个）
34-43. 包括：
- 结构说明不足
- 加密说明不够详细
- 使用场景说明不清
- 命名规范不统一

## 特殊处理

### 1. PIN加密（不实现）
所有需要PIN的测试全部skip：
- Activate Card
- Change PIN  
- Reward Card申请（SSN加密）

**原因**：RSA + PKCS1Padding加密实现复杂，测试框架不实现加密逻辑。

### 2. 文件上传（部分skip）
Create Dispute需要multipart/form-data上传，已实现封装但测试skip。

### 3. 响应格式兼容
- Sub Program List：直接返回数组（无code）
- Card Opening Detail：无code包装层
- 其他接口：有code包装层

parse方法已做兼容处理。

### 4. 类型转换
- is_virtual: boolean vs string → 使用to_bool()
- amount: string vs number → 使用to_float()
- disputed_amount: string vs number → 容错处理

## Skip的测试

### P0（可运行，约50个场景）
- 所有List接口
- 所有错误处理测试
- 格式验证测试
- 枚举值验证

### P1（需要真实数据，约50个场景）
- Create接口
- Detail接口（部分）
- 带真实ID的查询

### P2（破坏性/加密，约30个场景）
- 所有PIN相关操作
- Block/Unblock/Replace
- Create Dispute（文件上传）
- Update操作

## 运行测试

```bash
# 运行整个Card模块
pytest test_cases/card/ -v

# 按子模块运行
pytest test_cases/card/card_opening/ -v
pytest test_cases/card/card_management/ -v
pytest test_cases/card/sub_program/ -v
pytest test_cases/card/dispute_and_risk/ -v

# 按标记运行
pytest -m card -v
pytest -m card_opening -v
pytest -m card_management -v
```

## 关键字段说明

### spending_limit结构
```json
{
    "amount": 100,
    "count": 10,      // 可选，部分interval需要
    "interval": "Daily",
    "category": "..." // MCC类型需要
}
```

**interval类型**：
- Daily/Weekly/Monthly/Yearly：需要amount和count
- Total/Per_Authorization：只需要amount
- MCC：需要amount和category

### associated_nested_program结构
```json
{
    "nested_program_id": "...",  // 或 "id"
    "amount": 1000,
    "interval": "Total"
}
```

## 日期格式注意事项

### expiration_date（卡片过期日期）
- **大部分接口**：MM/YYYY（如 "12/2026"）
- **Replace Card**：yyyy-MM-dd（如 "2028-04-24"）⚠️ 不一致

### birth_date（出生日期）
- **格式**：yyyy-MM-dd（如 "1990-01-01"）
- **字段名**：
  - 请求参数：birth_date（下划线）
  - 响应字段：birthdate（无下划线）⚠️ 不一致

### transaction_time
- **格式**：yyyy-MM-ddTHH:mm:ss（ISO 8601）
- **时区**：UTC

### 时间范围查询
- **格式**：yyyy-MM-dd HH:mm:ss
- **参数名**：
  - Card Transactions：start_time, end_time（下划线）
  - Dispute List：startTime, endTime（驼峰）⚠️ 不一致

## 安全相关

### PIN加密要求
1. 必须是4位数字
2. 使用Portal Dashboard的公钥
3. RSA + PKCS1Padding加密
4. Base64编码

### SSN脱敏规则
- List Card Holders：显示脱敏SSN（*****1112）
- Detail接口：返回null
- 创建时：需要加密的完整SSN

## 项目统计

完成Card模块后：
- **模块总数**：14 → 18（+4子模块）
- **测试场景**：397 → 518（+121）
- **API接口**：80 → 109（+29）
- **测试文件**：72 → 92（+20）

Card模块是项目中最大的模块，占整体接口数的~27%。

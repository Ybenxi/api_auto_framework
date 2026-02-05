# Client List 模块测试

## 模块概述
Client List（客户列表）模块提供客户信息的管理、查询、导出和统计功能，支持按OMS分类、账户信息等多维度筛选。

## API 接口列表（9个）

### 客户查询接口（2个）
1. **GET** `/api/v1/cores/{core}/client-lists` - 获取客户列表
2. **GET** `/api/v1/cores/{core}/client-lists/{client_id}` - 获取客户详情

### 客户管理接口（3个）
3. **POST** `/api/v1/cores/{core}/client-lists` - 创建客户
4. **PATCH** `/api/v1/cores/{core}/client-lists/{client_id}` - 更新客户信息
5. **DELETE** `/api/v1/cores/{core}/client-lists/{client_id}` - 删除客户

### 导出和统计接口（3个）
6. **GET** `/api/v1/cores/{core}/client-lists/export` - 导出客户列表
7. **GET** `/api/v1/cores/{core}/client-lists/historical-chart` - 获取历史图表数据
8. **GET** `/api/v1/cores/{core}/client-lists/statistics` - 获取客户统计信息

### 占位接口（1个）
9. （预留给可能存在的第9个接口）

## 测试文件列表（8个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_client_list_list.py` | 9 | 客户列表查询（含多种筛选） |
| `test_client_list_detail.py` | 4 | 客户详情查询 |
| `test_client_list_create.py` | 6 | 创建客户（skip） |
| `test_client_list_update.py` | 5 | 更新客户（skip） |
| `test_client_list_delete.py` | 4 | 删除客户（破坏性操作） |
| `test_client_list_export.py` | 6 | 导出客户列表 |
| `test_client_list_historical_chart.py` | 7 | 历史图表数据 |
| `test_client_list_statistics.py` | 5 | 客户统计信息 |

**总计：46个测试场景**

## 关键枚举类型

```python
class OMSCategory(str, Enum):
    """OMS交易分类"""
    EQUITY = "Equity"
    MUTUAL_FUND = "Mutual Fund"
    CRYPTO_CURRENCY = "Crypto Currency"
    CERTIFICATES_OF_DEPOSIT = "Certificates of Deposit"
    OTHERS = "Others"
    BOND = "Bond"
```

## 筛选参数

### List接口支持的筛选
- `oms_category`: OMS分类
- `account_name`: Account名称
- `account_id`: Account ID
- `sub_account_name`: Sub Account名称
- `financial_account_name`: Financial Account名称
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）
- `page`: 页码
- `size`: 每页大小

### Export接口支持的筛选
- `oms_category`: OMS分类
- `start_date`: 开始日期
- `end_date`: 结束日期

## 文档已知问题（25个）

### 严重问题
1. **响应结构定义混乱**：60+字段平铺，嵌套层级关系不清晰
2. **类型定义混乱**：string vs int不一致
3. **分页字段命名不一致**：驼峰vs下划线混用

### 中等问题
4. Export接口URL示例错误
5. Historical Chart响应结构缺失
6. 字段类型定义与示例不符

### 轻微问题
7-25. 命名风格、示例不全等（详见Rule 4）

## 响应格式注意事项

由于文档问题，响应结构可能包含两种格式：
- 分页字段可能是`total_elements`或`totalElements`
- ID字段可能是`id`或`client_id`
- 可能有或没有`code`包装层

API封装的`parse_list_response`方法已做兼容处理。

## Skip的测试

以下测试标记为skip：
- Create相关（需要真实account_id）
- Update相关（需要真实client_id）
- Delete相关（破坏性操作）
- Detail部分测试（需要真实数据）

## 可运行的测试

以下测试可以直接运行（不需要前置数据）：
- List接口的所有筛选测试
- Export接口测试
- Historical Chart接口测试
- Statistics接口测试
- Detail/Create/Update的错误处理测试

## 运行测试

```bash
# 运行所有Client List测试
pytest test_cases/client_list/ -v

# 运行特定类型
pytest test_cases/client_list/ -m list_api -v
pytest test_cases/client_list/ -m export_api -v
pytest test_cases/client_list/ -m statistics_api -v

# 运行不包含skip的测试
pytest test_cases/client_list/ -v --ignore-skip
```

## 导出功能说明

Export接口可能返回：
- JSON格式（Content-Type: application/json）
- CSV格式（Content-Type: text/csv）
- Excel格式（Content-Type: application/vnd.*)

测试代码会自动检测响应格式并验证。

## 统计功能说明

Statistics接口返回客户统计信息，支持：
- 全局统计（不传oms_category）
- 分类统计（传入特定oms_category）
- 对比不同分类的统计数据

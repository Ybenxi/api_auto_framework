# 变更日志

## 2026-02-05 - Instant Pay 模块完成

### 新增功能

#### Instant Pay模块（实时支付）
- ✅ 创建 `api/instant_pay_api.py` - 15个接口封装
- ✅ 创建 6个测试文件，33个测试场景
  - test_instant_pay_transactions.py (7场景)
  - test_instant_pay_payment.py (8场景)
  - test_instant_pay_cancel_approve_reject.py (6场景)
  - test_instant_pay_return.py (8场景)
  - test_instant_pay_counterparties.py (2场景)
  - test_instant_pay_fee.py (2场景)
- ✅ 创建 README.md 文档
- 包含FedNow实时支付、Request Payment、Return处理

#### 核心功能
- 实时支付（20秒超时）
- 收款请求（RFP）
- Cancel/Approve/Reject流程
- Return Payment/Request处理
- 支持link和structured_content

#### 枚举类型
- ✅ 新增1个枚举类：RequestPaymentStatus（5个专有状态）

### 配置更新
- ✅ 更新 `data/enums.py` - 新增1个枚举类
- ✅ 更新 `pytest.ini` - 新增1个marker
  - instant_pay
- ✅ 更新 `test_cases/conftest.py` - 新增1个模块映射
- ✅ 更新 payment_deposit/README.md
- ✅ 更新 CHANGELOG

### 统计数据

#### 本次新增
- 新增测试文件：6个
- 新增测试场景：33个
- 新增API接口：15个
- 新增API封装类：1个
- 新增枚举类型：1个
- 代码行数：约1,500行

#### Payment & Deposit模块总计
- 子模块完成：5/6（83%）
- 测试文件：26个
- 测试场景：142个
- API接口：41个

#### 项目总计
- 总测试文件：122个
- 总测试方法：691个
- 总API封装类：26个
- 完成模块：24个
- 接口总数：155个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 完整的docstring和注释
- ✅ 标注文档问题（45个）
- ✅ 所有破坏性操作triple标记
- ✅ 20秒超时限制明确提醒

### 已知问题

#### Instant Pay文档问题（45个）
- Cancel/Reject/Return概念混淆
- payment-request vs request-payment URL不一致
- cancel_code/return_code/reject_code外部链接缺失
- Request Payment专有字段未在Properties定义
- Reject Return Request URL示例完全错误
- 响应格式不一致（7个接口无code包装层）
- structured_content说明不清
- 大量响应字段未定义

### 特殊处理

#### 1. 20秒超时限制
所有payment接口都提醒Payment Timeout Clock：
```python
logger.warning("⚠️⚠️⚠️ 20秒超时限制！")
```

#### 2. Request Payment专有枚举
新增RequestPaymentStatus处理RFP特殊状态。

#### 3. 响应格式双重兼容
parse_list_response支持has_code_wrapper参数：
- List Transactions：无code包装层
- List Request Payment：有code包装层

#### 4. URL命名混乱标注
详细标注payment-request vs request-payment不一致问题。

#### 5. Code值未知处理
标注cancel_code/return_code/reject_code外部链接缺失。

### 待完善工作
1. 获取完整的cancel/return/reject code列表
2. 补充真实支付测试（专门测试账户）
3. 验证20秒超时实际行为
4. 理清Cancel/Reject/Return概念

---

## 2026-02-05 - Wire Processing & Remote Deposit Check 模块完成

### 新增功能

#### Wire Processing模块（电汇）
- ✅ 创建 `api/wire_processing_api.py` - 8个接口封装
- ✅ 创建 4个测试文件，21个测试场景
  - test_wire_transactions.py (5场景)
  - test_wire_counterparties.py (7场景)
  - test_wire_payment.py (5场景，破坏性)
  - test_wire_fee.py (4场景)
- ✅ 创建 README.md 文档
- 包含国内电汇、国际电汇、对手方管理
- Create Counterparty有40+参数，条件逻辑极其复杂

#### Remote Deposit Check模块（远程支票存款）
- ✅ 创建 `api/remote_deposit_check_api.py` - 9个接口封装
- ✅ 创建 5个测试文件，21个测试场景
  - test_check_transactions.py (3场景)
  - test_check_counterparties.py (3场景)
  - test_check_scan_deposit.py (7场景，破坏性)
  - test_check_update_download.py (6场景)
  - test_check_fee.py (2场景)
- ✅ 创建 README.md 文档
- 包含支票扫描（OCR）、存款、更新、下载
- 提供complete_deposit_flow流程管理

#### 枚举类型
- ✅ 新增4个枚举类：
  - WirePaymentType（Wire/International_Wire）
  - CounterpartyType（4个类型）
  - BankAccountType（Checking/Savings）
  - WireDirection（Incoming/Outgoing/Origination）

### 配置更新
- ✅ 更新 `data/enums.py` - 新增4个枚举类
- ✅ 更新 `pytest.ini` - 新增2个marker
  - wire_processing, remote_deposit_check
- ✅ 更新 `test_cases/conftest.py` - 新增2个模块映射
- ✅ 新增2个模块README文档
- ✅ 更新 CHANGELOG

### 统计数据

#### 本次新增
- 新增测试文件：9个
- 新增测试场景：42个
- 新增API接口：17个
- 新增API封装类：2个
- 新增枚举类型：4个
- 代码行数：约2,500行

#### 项目总计
- 总测试文件：114个
- 总测试方法：644个
- 总API封装类：25个
- 完成模块：23个（19主模块+4子模块）
- 接口总数：140个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 完整的docstring和注释
- ✅ 标注文档问题（90个）
- ✅ 所有破坏性操作添加no_rerun
- ✅ 所有转账/存款操作明确警告

### 已知问题

#### Wire Processing文档问题（45个）
- URL路径不一致
- Create Counterparty条件逻辑极其复杂且混乱
- Wire vs International Wire接口完全重复
- 40+个响应字段未在Properties定义
- intermediary bank字段定义混乱
- HTTP方法示例错误

#### Remote Deposit Check文档问题（45个）
- Scan→Deposit流程说明缺失
- Scan响应使用success字段（独特格式）
- Download应该用GET不是POST
- item_identifier依赖关系未说明
- 15+个响应字段未定义
- transaction_type说明与实际矛盾

### 特殊处理

#### 1. Wire Counterparty创建（极其复杂）
- 40+个参数
- 多层条件必需逻辑
- 大部分测试skip
- 详细的条件逻辑注释

#### 2. Check Scan文件上传
- multipart/form-data处理
- 前后两张图片上传
- parse_scan_response处理特殊格式

#### 3. Complete Deposit Flow
提供完整流程辅助方法：
- 自动Scan→Deposit
- 管理item_identifier传递
- 返回每步结果

#### 4. 三重安全标记
所有破坏性操作：
- @pytest.mark.no_rerun
- @pytest.mark.skip
- logger.warning()明确警告

### 待完善工作
1. 补充真实转账/存款测试（使用专门测试账户）
2. 准备测试支票图片文件
3. 验证OCR识别准确性
4. 测试Intermediary Bank条件逻辑

---

## 2026-02-05 - Internal Pay & Account Transfer 模块完成

### 新增功能

#### Internal Pay模块
- ✅ 创建 `api/internal_pay_api.py` - 5个接口封装
- ✅ 创建 5个测试文件，31个测试场景
  - test_internal_pay_transactions.py (8场景)
  - test_internal_pay_payers.py (6场景)
  - test_internal_pay_payees.py (5场景)
  - test_internal_pay_transfer.py (7场景，破坏性)
  - test_internal_pay_fee.py (5场景)
- ✅ 创建 README.md 文档
- 包含P2P支付、邮箱查找收款人、实时结算

#### Account Transfer模块
- ✅ 创建 `api/account_transfer_api.py` - 4个接口封装
- ✅ 创建 4个测试文件，22个测试场景
  - test_account_transfer_transactions.py (6场景)
  - test_account_transfer_financial_accounts.py (6场景)
  - test_account_transfer_transfer.py (6场景，破坏性)
  - test_account_transfer_fee.py (4场景)
- ✅ 创建 README.md 文档
- 包含跨Profile转账、实时结算、成本效率

#### 枚举类型
- ✅ 新增3个枚举类：
  - PaymentTransactionStatus（5个状态）
  - PaymentTransactionType（Credit/Debit）
  - AccountSubType（Checking/Savings等）

### 配置更新
- ✅ 更新 `data/enums.py` - 新增3个枚举类
- ✅ 更新 `pytest.ini` - 新增2个marker
  - internal_pay, account_transfer
- ✅ 更新 `test_cases/conftest.py` - 新增2个模块映射
- ✅ 新增2个模块README文档
- ✅ 更新 CHANGELOG

### 统计数据

#### 本次新增
- 新增测试文件：9个
- 新增测试场景：53个
- 新增API接口：9个
- 新增API封装类：2个
- 新增枚举类型：3个
- 代码行数：约2,000行

#### 项目总计
- 总测试文件：105个
- 总测试方法：602个
- 总API封装类：23个
- 完成模块：21个
- 接口总数：123个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 完整的docstring和注释
- ✅ 标注文档问题（50个）
- ✅ 转账操作添加no_rerun标记
- ✅ 危险操作明确标注

### 已知问题

#### Internal Pay文档问题（25个）
- HTTP方法示例错误（2处）
- 响应格式不一致（4个接口无code包装层）
- amount字段类型不一致
- 多个响应字段未定义（10个）
- 条件必需字段逻辑不清
- List Payees的email参数required（与List语义矛盾）

#### Account Transfer文档问题（25个）
- HTTP方法示例错误（2处）
- 响应格式不一致（3个接口无code包装层）
- 接口描述错误（说ACH应为Account Transfer）
- 与Internal Pay差异未说明
- 多个响应字段未定义
- 英文语法错误

### 特殊处理

#### 1. 响应格式自适应
两个模块都有响应格式不一致问题：
- parse_list_response()：兼容有无code包装层
- parse_transfer_response()：兼容有无code包装层

#### 2. 转账操作安全标记
```python
@pytest.mark.no_rerun  # 禁止重试
@pytest.mark.skip(reason="真实转账，会实际扣款")
def test_transfer():
    logger.warning("⚠️ 发起转账...")
```

#### 3. 类型转换
- amount: string → number（使用to_float）
- balance字段统一处理

### 待完善工作
1. 补充真实账户测试（当前转账操作skip）
2. 验证条件必需字段逻辑
3. 测试跨Profile转账场景
4. 验证实际响应格式

---

## 2026-02-05 - User Sign Up 模块完成

### 新增功能

#### User Sign Up模块
- ✅ 创建 `api/user_signup_api.py` - 5个接口封装
- ✅ 创建 2个枚举类型（ClientType, RecoveryQuestion）
- ✅ 创建 4个测试文件，31个测试场景
  - test_user_signup_email_verification.py (7场景)
  - test_user_signup_sms_verification.py (6场景)
  - test_user_signup_create_user.py (9场景)
  - test_user_signup_complete_flow.py (5场景，全skip)
- ✅ 创建 README.md 文档
- 包含完整的用户注册流程（邮箱→短信→创建）

### 配置更新
- ✅ 更新 `data/enums.py` - 新增2个枚举类（含19个安全问题）
- ✅ 更新 `pytest.ini` - 新增1个marker
  - user_signup
- ✅ 更新 `test_cases/conftest.py` - 新增1个模块映射
- ✅ 更新 CHANGELOG

### 统计数据

#### 本次新增
- 新增测试文件：4个
- 新增测试场景：31个
- 新增API接口：5个
- 新增API封装类：1个
- 新增枚举类型：2个（含19个安全问题选项）
- 代码行数：约900行

#### 项目总计
- 总测试文件：96个
- 总测试方法：549个
- 总API封装类：21个
- 完成模块：19个
- 接口总数：114个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 完整的docstring和注释
- ✅ 标注文档问题（25个）
- ✅ 提供complete_signup_flow辅助方法
- ✅ 智能条件参数处理

### 已知问题

#### User Sign Up文档问题（25个）
1. token流转链说明不清晰（5步流程）
2. has_idp_user描述不完整（条件逻辑不清）
3. 条件必需字段规则不清（"must be left empty"含义不明）
4. client_type枚举值有空格（Individual Client）
5. phone格式说明不一致
6. 验证码格式未说明（位数、有效期、重试限制）
7. token有效期未说明
8. email/phone重复处理未说明
9. password加密说明不够详细
10. recovery_question有循环定义问题
11-25. 其他格式和命名问题

### 特殊处理

#### 1. 多步骤流程管理
- 提供complete_signup_flow()方法
- 自动传递token
- 根据has_idp_user调整参数

#### 2. 条件必需字段智能处理
```python
if not has_idp_user:
    payload["encoded_password"] = encoded_password
# has_idp_user=true时自动不传
```

#### 3. Client-Id header自动添加
```python
self.session.headers.update({
    "Client-Id": self.client_id
})
```

### 待完善工作
1. 补充真实验证码测试（需要邮箱和短信接收）
2. 实现密码加密工具（可选）
3. 获取真实Client-Id
4. 验证token有效期
5. 测试重复注册策略

---

## 2026-02-05 - Card 模块完成

### 新增功能

#### Card模块（最大模块，4个子模块）

**Card Opening子模块**
- ✅ 创建 `api/card_opening_api.py` - 4个接口封装
- ✅ 创建 4个测试文件，约25个测试场景
- 包含借记卡申请、奖励卡申请、申请列表和详情

**Card Management子模块**
- ✅ 创建 `api/card_management_api.py` - 14个接口封装
- ✅ 创建 6个测试文件，约50个测试场景
- 包含卡片查询、激活、锁定、更新、交易查询等完整功能

**Sub Program子模块**
- ✅ 创建 `api/sub_program_api.py` - 5个接口封装
- ✅ 创建 5个测试文件，约27个测试场景
- 包含子项目、嵌套项目查询和使用日志

**Dispute & Risk Control子模块**
- ✅ 创建 `api/card_dispute_api.py` - 6个接口封装
- ✅ 创建 5个测试文件，约30个测试场景
- 包含争议管理、消费限制和MCC码查询

#### 枚举类型
- ✅ 新增10个枚举类：CardNetwork, CardStatus, LimitType, SpendingLimitInterval等

#### 工具类
- ✅ 创建 `utils/type_converters.py` - 类型转换工具
  - to_bool()：兼容boolean和string
  - to_float()：兼容string和number
  - safe_get_field()：兼容字段命名不一致

### 配置更新
- ✅ 更新 `data/enums.py` - 新增10个枚举类
- ✅ 更新 `pytest.ini` - 新增5个marker
  - card, card_opening, card_management, sub_program, card_dispute_risk
- ✅ 更新 `test_cases/conftest.py` - 新增5个模块映射
- ✅ 创建主README和各子模块文档

### 统计数据

#### 本次新增
- 新增测试文件：20个
- 新增测试场景：121个
- 新增API接口：29个
- 新增API封装类：4个
- 新增枚举类型：10个
- 新增工具类：1个
- 代码行数：约4,500行

#### 项目总计
- 总测试文件：92个
- 总测试方法：518个
- 总API封装类：20个
- 完成模块：18个（14个主模块 + 4个Card子模块）
- 接口总数：109个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 完整的docstring和注释
- ✅ 标注文档问题（43个）
- ✅ 容错处理完善
- ✅ skip和no_rerun标记正确

### 已知问题

#### Card模块文档问题（43个）
- JSON格式错误：至少8处
- 字段类型不一致：is_virtual, amount, disputed_amount等
- 字段命名不一致：birth_date/birthdate, fileId/file_id等
- 日期格式冲突：expiration_date在不同接口使用不同格式
- 响应格式不一致：Sub Program List无code包装层
- 枚举值未定义：disputed_reason, direction等
- 接口描述错误：多处描述为"card holders"
- 条件必需字段不清：classification_type逻辑
- PIN加密说明不够详细

### 特殊处理

#### 1. PIN加密策略
- ❌ 不实现加密逻辑
- ✅ 所有PIN相关测试skip
- ✅ 在README中说明加密要求

#### 2. 响应格式自适应
```python
# 兼容3种格式：
1. 有code包装层：{"code": 200, "data": {...}}
2. 无code包装层：{...}
3. 直接数组：[...]
```

#### 3. 类型兼容处理
- to_bool()：兼容boolean和string
- to_float()：兼容string和number
- safe_get_field()：兼容字段命名不一致

### 待完善工作
1. 补充真实数据测试（当前约70个skip）
2. 实现PIN加密工具（可选）
3. 补充文件上传测试
4. 验证实际响应格式

---

## 2026-02-05 - Investment & Account Summary 模块完成

### 新增功能

#### Investment模块
- ✅ 创建 `api/investment_api.py` - 6个接口封装
- ✅ 创建 2个枚举类型（FeeType, IntervalType）
- ✅ 创建 6个测试文件，37个测试场景
  - test_investment_activity_summaries.py (6场景)
  - test_investment_activity_trends.py (6场景)
  - test_investment_performance_returns.py (7场景)
  - test_investment_performance_risks.py (6场景)
  - test_investment_asset_allocations.py (6场景)
  - test_investment_asset_allocations_comparison.py (6场景)
- ✅ 创建 README.md 文档

#### Account Summary模块
- ✅ 创建 `api/account_summary_api.py` - 1个接口封装
- ✅ 创建 1个枚举类型（ClassificationMode）
- ✅ 创建 2个测试文件，14个测试场景
  - test_account_summary_categorized.py (8场景)
  - test_account_summary_flat.py (6场景，探索性)
- ✅ 创建 README.md 文档

### 配置更新
- ✅ 更新 `data/enums.py` - 新增3个枚举类
- ✅ 更新 `pytest.ini` - 新增2个marker
  - investment
  - account_summary
- ✅ 更新 `test_cases/conftest.py` - 新增2个模块映射
  - investment
  - account_summary

### 统计数据

#### 本次新增
- 新增测试文件：8个
- 新增测试场景：51个（37 + 14）
- 新增API接口：7个（6 + 1）
- 新增API封装类：2个
- 新增枚举类型：3个
- 新增文档：2个README

#### 项目总计
- 总测试文件：72个
- 总测试方法：397个
- 总API封装类：16个
- 完成模块：14个（12个完成 + 2个新增）
- 接口总数：80+个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 使用logger替代print
- ✅ 完整的docstring和注释
- ✅ 标记需要skip的测试
- ✅ 文档问题在代码中标注

### 已知问题

#### Investment文档问题（15个）
1. URL路径错误（重复investments）
2. JSON格式错误（trailing comma等5处）
3. sharp_ratio拼写错误（应为sharpe_ratio）
4. 响应字段未定义（benchmark/account对象）
5. 字段命名不一致
6-15. 其他格式和定义问题

#### Account Summary文档问题（15个）
1. Response Properties完全缺失
2. balance字段类型不一致（string vs number）
3. Flat模式缺少响应示例（结构未知）
4. 字段命名不一致（total_balance vs balance）
5. 枚举值未定义
6-15. 其他结构和命名问题

### 特殊处理

#### Investment模块
- JSON格式错误容错处理
- sharp_ratio拼写兼容（sharp vs sharpe）
- 嵌套结构验证（Asset Allocations 3-4层）
- 大部分测试skip（需要真实投资数据）

#### Account Summary模块
- balance类型兼容（string→float转换）
- Flat模式探索性测试（结构未知）
- 4层嵌套结构验证
- parse方法统一处理

### 待完善工作
1. 补充真实数据的测试场景（当前大部分skip）
2. 验证Account Summary Flat模式实际结构
3. 验证Investment API实际响应格式
4. 补充数据准备逻辑

---

## 2026-02-05 - Trading Order & Client List 模块完成

### 新增功能

#### Trading Order 模块
- ✅ 创建 `api/trading_order_api.py` - 9个接口封装
- ✅ 创建 6个枚举类型（IssueType, OrderAction, QuantityType, OrderType, OrderStatus, OMSCategory）
- ✅ 创建 9个测试文件，55个测试场景
  - test_trading_order_list_financial_accounts.py (9场景)
  - test_trading_order_list_securities.py (9场景)
  - test_trading_order_list.py (10场景)
  - test_trading_order_detail.py (4场景)
  - test_trading_order_draft.py (1场景)
  - test_trading_order_initiate.py (6场景)
  - test_trading_order_submit.py (4场景)
  - test_trading_order_update.py (6场景)
  - test_trading_order_cancel.py (6场景)
- ✅ 创建 README.md 文档

#### Client List 模块
- ✅ 创建 `api/client_list_api.py` - 9个接口封装
- ✅ 创建 8个测试文件，46个测试场景
  - test_client_list_list.py (9场景)
  - test_client_list_detail.py (4场景)
  - test_client_list_create.py (6场景)
  - test_client_list_update.py (5场景)
  - test_client_list_delete.py (4场景)
  - test_client_list_export.py (6场景)
  - test_client_list_historical_chart.py (7场景)
  - test_client_list_statistics.py (5场景)
- ✅ 创建 README.md 文档

### 配置更新
- ✅ 更新 `data/enums.py` - 新增6个枚举类
- ✅ 更新 `pytest.ini` - 新增5个marker
  - trading_order
  - client_list
  - export_api
  - chart_api
  - statistics_api
- ✅ 更新 `test_cases/conftest.py` - 新增4个模块映射
  - identity_security
  - account_opening
  - trading_order
  - client_list

### 统计数据

#### 本次新增
- 新增测试文件：17个
- 新增测试场景：101个（55 + 46）
- 新增API接口：18个（9 + 9）
- 新增API封装类：2个
- 新增枚举类型：6个
- 新增文档：2个README

#### 项目总计
- 总测试文件：64个
- 总测试方法：346个
- 总API封装类：14个
- 完成模块：12个（10个完成 + 2个新增）
- 接口总数：73+个

### 代码质量
- ✅ 所有代码通过语法检查
- ✅ 遵循项目代码规范
- ✅ 使用logger替代print
- ✅ 完整的docstring和注释
- ✅ 标记需要skip的测试
- ✅ 破坏性操作添加no_rerun标记

### 已知问题

#### Trading Order文档问题
1. order_type类型定义错误（int→string）
2. quantity类型不一致
3. Draft vs Initiate功能差异未说明
4. 部分响应字段未定义

#### Client List文档问题
1. 响应结构定义混乱（60+字段平铺）
2. 嵌套层级关系不清晰
3. 类型定义混乱
4. 分页字段命名不一致
5. Export接口URL示例错误
6. Historical Chart响应结构缺失

### 待完善工作
1. 补充真实数据的测试场景（当前大部分标记为skip）
2. 验证API实际响应结构（需要真实环境测试）
3. 补充数据准备逻辑（获取真实的account_id, security_id等）

### 下一步计划
- 运行完整测试套件
- 修复响应结构不匹配的问题
- 补充Account Opening模块测试
- 完善数据准备策略

---

## 历史记录

### 2026-02-04 - 框架升级v3.0
- 引入Loguru日志系统
- 添加.env环境配置
- 创建DAO数据库层
- 添加pytest失败重试

### 2026-02-04 - HTML报告5大问题修复
- 修复重复记录
- 修复翻译残留
- 添加动态统计
- 添加空数据提示
- 修复JavaScript垃圾代码

### 2026-02-04 - Counterparty模块补全
- 补充14个接口测试
- 新增38个测试场景
- 达到100%接口覆盖

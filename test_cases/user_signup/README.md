# User Sign Up 模块测试

## 模块概述
User Sign Up模块提供完整的用户注册流程，包括邮箱验证、短信验证和账户创建。这是一个多步骤流程，每步返回token用于下一步。

## API 接口列表（5个）

### 邮箱验证流程（2个）
1. **POST** `/api/v1/cores/{core}/user/auth/sign-up/email` - 发起邮箱验证
2. **POST** `/api/v1/cores/{core}/user/auth/sign-up/email/verification` - 验证邮箱码

### 短信验证流程（2个）
3. **POST** `/api/v1/cores/{core}/user/auth/sign-up/sms` - 发送短信验证码
4. **POST** `/api/v1/cores/{core}/user/auth/sign-up/sms/verification` - 验证短信码

### 创建用户（1个）
5. **POST** `/api/v1/cores/{core}/user/auth/sign-up/unifi-user` - 创建UniFi用户

## 测试文件列表（4个）

| 文件名 | 测试场景数 | 说明 |
|--------|-----------|------|
| `test_user_signup_email_verification.py` | 7 | 邮箱验证发起和验证 |
| `test_user_signup_sms_verification.py` | 6 | 短信验证发送和验证 |
| `test_user_signup_create_user.py` | 9 | 创建用户（条件必需字段） |
| `test_user_signup_complete_flow.py` | 5 | 完整注册流程 |

**总计：27个测试场景**

## 关键枚举类型

```python
class ClientType(str, Enum):
    """客户类型"""
    INDIVIDUAL_CLIENT = "Individual Client"  # ⚠️ 有空格
    BUSINESS = "Business"

class RecoveryQuestion(str, Enum):
    """安全问题（19个选项）"""
    DISLIKED_FOOD = "disliked_food"
    NAME_OF_FIRST_PLUSH_TOY = "name_of_first_plush_toy"
    # ... 等19个
```

## 注册流程说明

### 完整5步流程
```
Step 1: Initiate Email
  POST /email
  Request: {"email": "user@example.com"}
  Response: {"data": "token1"}
  
Step 2: Verify Email
  POST /email/verification
  Request: {"passcode": "123456", "enroll_token": "token1"}
  Response: {"data": "token2"}
  
Step 3: Send SMS
  POST /sms
  Request: {"phone": "+1234567890", "enroll_token": "token2"}
  Response: {"data": "token3"}
  
Step 4: Verify SMS
  POST /sms/verification
  Request: {"passcode": "654321", "enroll_token": "token3"}
  Response: {
    "data": {
      "enroll_token": "token4",
      "has_idp_user": false,
      "client_type": "Business",
      ...
    }
  }
  
Step 5: Create User
  POST /unifi-user
  Request: {
    "enroll_token": "token4",
    "first_name": "John",
    "last_name": "Doe",
    "email": "...",
    "phone": "...",
    "client_type": "Individual Client",
    "encoded_password": "...",  // 条件必需
    "recovery_question": "...", // 条件必需
    "recovery_answer": "..."    // 条件必需
  }
  Response: {"data": true}
```

## 条件必需字段规则

### company_name
- **条件**：`client_type = "Business"`时必需
- **长度**：最多80字符

### encoded_password, recovery_question, recovery_answer
- **条件**：`has_idp_user = false`时必需
- **当**：`has_idp_user = true`时"must be left empty"
  - ⚠️ 文档问题："left empty"含义不明（null?不传?空字符串?）

### recovery_answer长度
- **要求**：4-50字符

## 文档已知问题（25个）

### 🔴 严重问题（8个）
1. enroll_token描述不一致（接口间说明混乱）
3. token流转链说明不清晰
5. has_idp_user描述不完整
6. 条件必需字段规则不清（"must be left empty"）
10. recovery_question枚举值格式不统一
20. email已存在的处理未说明
21. phone重复处理未说明
24. "favorite_security_question"循环定义

### 🟡 中等问题（10个）
4. phone格式说明不一致
7. client_type枚举值不一致
8. company_name长度限制位置错误
9. recovery_answer长度限制描述混乱
11. password加密说明不够详细
15. 验证码格式未说明
16. token有效期未说明
17. 接口依赖关系未图示
22. encoded_password示例值可能截断
23. client_type枚举值命名有空格

### 🟢 轻微问题（7个）
2. 英文语法错误（"An token", "contine"）
12. 响应data字段类型不一致
13. Client-Id header说明不足
14. error和error_message字段冗余
18. 响应字段顺序不一致
19. 缺少失败示例
25. company_name条件说明位置混乱

## 特殊处理

### 1. Client-Id Header
此模块需要特殊的Client-Id header：
```python
api = UserSignUpAPI(client_id="your_client_id")
# 自动在所有请求中添加Client-Id header
```

### 2. Token流转管理
提供`complete_signup_flow()`辅助方法自动管理token流转：
```python
result = api.complete_signup_flow(
    email="...",
    phone="...",
    email_passcode="...",
    sms_passcode="...",
    ...
)
# 自动执行5步流程
```

### 3. 密码加密（不实现）
- RSA + PKCS1Padding加密
- 所有需要密码的测试skip
- 在README说明要求

### 4. 验证码接收（无法测试）
- 需要真实邮箱和手机号接收验证码
- 大部分测试skip
- 只测试错误处理

## Skip的测试

### 可运行（约8个场景）
- 无效邮箱格式
- 无效验证码
- 无效token
- 缺少必需字段
- 无效枚举值
- 长度限制验证

### Skip（约19个场景）
- 需要真实验证码（邮箱、短信）
- 需要密码加密
- 完整注册流程
- IdP用户流程

## 手机号格式

### E.164格式
```
+[country code][number]

美国号码示例：
+1234567890  // ✅ 正确（+1是国家码，后面10位）
+11234567890 // ❌ 文档示例错误（多了一个1）
```

### 限制
- **仅支持美国号码**
- 其他国家如何处理：文档未说明

## 密码要求

### 加密
- RSA + PKCS1Padding
- Base64编码
- 使用Dashboard的Encryption Key

### 原始密码（未说明）
- 长度要求？
- 复杂度要求？
- 特殊字符要求？

## 验证码格式（推测）

### 格式（文档未说明）
- **位数**：6位（从示例推测）
- **类型**：数字
- **有效期**：未知
- **重试限制**：未知

## 运行测试

```bash
# 运行所有User Sign Up测试
pytest test_cases/user_signup/ -v

# 运行特定文件
pytest test_cases/user_signup/test_user_signup_email_verification.py -v

# 按标记运行
pytest -m user_signup -v

# 只运行不需要skip的测试
pytest test_cases/user_signup/ -v -m "not skip"
```

## 测试策略

### 错误处理测试（可运行）
```python
# 格式验证
test_initiate_with_invalid_email_format()
test_phone_format_validation()

# 无效参数
test_verify_with_invalid_passcode()
test_verify_with_invalid_token()
test_invalid_client_type()

# 条件字段
test_missing_company_name_for_business()
test_recovery_answer_length_validation()
```

### 流程测试（skip）
```python
@pytest.mark.skip(reason="需要真实验证码")
test_initiate_email_verification_success()
test_verify_email_code_success()
test_complete_flow_individual_user()
```

## 注意事项

### has_idp_user逻辑
```python
# Step 4返回has_idp_user
if has_idp_user == true:
    # 用户已存在于IdP
    # Step 5不需要密码和安全问题
    create_user(
        ...,
        encoded_password=None,
        recovery_question=None,
        recovery_answer=None
    )
else:
    # 新用户
    # Step 5必须提供密码和安全问题
    create_user(
        ...,
        encoded_password="REQUIRED",
        recovery_question="REQUIRED",
        recovery_answer="REQUIRED"
    )
```

### 条件必需字段矩阵

| 字段 | client_type=Individual | client_type=Business |
|------|----------------------|---------------------|
| company_name | 可选 | **必需** |
| encoded_password | has_idp_user=false时**必需** | has_idp_user=false时**必需** |
| recovery_question | has_idp_user=false时**必需** | has_idp_user=false时**必需** |
| recovery_answer | has_idp_user=false时**必需** | has_idp_user=false时**必需** |

## API设计亮点

### complete_signup_flow辅助方法
自动管理完整流程：
- 自动传递token
- 根据has_idp_user自动调整参数
- 返回每步结果
- 适用于集成测试

### 智能条件参数
```python
# 根据has_idp_user自动处理
if not has_idp_user:
    payload["encoded_password"] = encoded_password
# has_idp_user=true时自动不传
```

## 已知限制

1. **无法获取真实验证码** - 大部分流程测试skip
2. **未实现密码加密** - 密码相关测试skip
3. **Client-Id获取方式未知** - 使用测试值
4. **token有效期未知** - 无法测试过期场景
5. **重复注册策略未知** - 无法完整测试

## 项目统计（完成User Sign Up后）

- 模块数：18 → 19
- 测试场景：518 → 545（+27）
- API接口：109 → 114（+5）
- 测试文件：92 → 96（+4）

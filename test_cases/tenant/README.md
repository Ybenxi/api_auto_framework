# Tenant 模块自动化测试

## 📁 文件结构

```
test_cases/tenant/
├── conftest.py                                    # Pytest 配置文件
├── test_tenant_retrieve_current_tenant.py         # Tenant Info 接口测试用例
└── README.md                                      # 本说明文档
```

## 🔍 测试用例说明

### 1. `test_tenant_retrieve_current_tenant.py`

测试 `GET /api/v1/cores/{core}/tenants/info` 接口，包含以下测试场景：

#### 测试场景列表

| 测试用例 | 验证点 | 说明 |
|---------|--------|------|
| `test_get_current_tenant_info_success` | 成功获取 Tenant 信息 | 验证接口返回 200，包含必需字段（id, name, description, status, timezone），status 为有效枚举值 |
| `test_get_current_tenant_info_response_structure` | 验证响应数据结构 | 验证响应是 JSON 对象，包含 code 和 data 字段，不是分页结构 |
| `test_get_current_tenant_info_field_types` | 验证字段数据类型 | 验证所有字段的数据类型正确（均为 string 类型） |
| `test_get_current_tenant_info_status_enum_values` | 验证 status 枚举值 | 验证 status 字段值为 ACTIVE/PENDING/INACTIVE 之一 |
| `test_get_current_tenant_info_timezone_format` | 验证 timezone 格式 | 验证 timezone 字段格式符合标准（如 America/Chicago） |
| `test_get_current_tenant_info_using_helper_method` | 使用辅助方法解析响应 | 验证 parse_tenant_response 辅助方法能正确解析响应 |

## 🚀 运行测试

### 激活虚拟环境并运行

```bash
# 进入项目目录
cd "/Users/mac/api auto/api_auto_framework"

# 激活虚拟环境
source .venv/bin/activate

# 运行所有 Tenant 测试用例
pytest test_cases/tenant/ -v

# 运行指定测试用例
pytest test_cases/tenant/test_tenant_retrieve_current_tenant.py -v

# 运行指定的测试方法
pytest test_cases/tenant/test_tenant_retrieve_current_tenant.py::TestTenantRetrieveCurrentTenant::test_get_current_tenant_info_success -v
```

### 使用 Marker 运行

```bash
# 运行所有 tenant 相关测试
pytest -m tenant -v

# 运行 tenant_info 相关测试
pytest -m tenant_info -v
```

## ⚠️ 已知问题

### 404 错误

目前在 DEV 环境运行测试时，接口返回 **404 Not Found** 错误：

```json
{
  "timestamp": "2026-02-03T16:08:25.692+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "",
  "path": "/api/v1/cores/actc/tenants/info"
}
```

**可能的原因：**

1. **接口未部署**：该接口在 DEV 环境（`api-dev.accelerationcloud.info`）可能还未部署
2. **路径错误**：实际接口路径可能与文档不一致
3. **Core 参数错误**：路径中的 `actc` 可能需要替换为其他值
4. **Beta 标记**：接口文档标注为 "Beta"，可能尚未正式发布

**解决方案：**

1. 确认接口在目标环境是否已部署
2. 与后端开发确认实际接口路径
3. 如果需要使用其他 core 值，可通过环境变量设置：
   ```bash
   export CORE=your_core_value
   pytest test_cases/tenant/ -v
   ```

## 📦 API 封装

API 封装位于 `api/tenant_api.py`，提供以下方法：

### `TenantAPI` 类

```python
from api.tenant_api import TenantAPI

# 初始化（使用登录会话）
tenant_api = TenantAPI(session=login_session)

# 获取当前 Tenant 信息
response = tenant_api.get_current_tenant_info()

# 解析响应
parsed = tenant_api.parse_tenant_response(response)
tenant_id = parsed['data']['id']
```

## 📝 响应示例

### 成功响应（预期）

```json
{
  "code": 200,
  "data": {
    "id": "f49e1771-fea8-4fa5-aab2-a6b0fb86d8b6",
    "name": "Example LLC",
    "description": "Example Description",
    "status": "ACTIVE",
    "timezone": "America/Chicago"
  }
}
```

### Status 枚举值

- `ACTIVE`: 激活状态
- `PENDING`: 待处理状态
- `INACTIVE`: 非激活状态

## 🔗 相关文档

- 接口文档：`GET /api/v1/cores/actc/tenants/info`
- 配置文件：`config/config.py`
- 全局 Fixture：`test_cases/conftest.py`

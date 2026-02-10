# 测试数据自动清理功能指南

## 📋 功能概述

自动清理测试过程中创建的垃圾数据，避免污染开发环境。

### 核心特性
- ✅ **自动清理**：测试结束后自动删除跟踪的ID
- ✅ **安全模式**：只删除名称以 "Auto TestYan" 开头的数据
- ✅ **模拟模式**：默认先模拟，确认无误后再执行
- ✅ **关联表处理**：自动处理主表和关联表的级联删除
- ✅ **事务回滚**：出错自动回滚，不留垃圾数据
- ✅ **详细日志**：所有操作都有日志记录

---

## 🔧 配置数据库

### 1. 编辑 `.env` 文件

```env
# 数据库配置（用于自动清理测试数据）
# ⚠️ 重要：这是DEV环境数据库，请勿配置生产环境！
DB_HOST=fta-database-dev.cda9xsygtbs2.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=developer
DB_PASSWORD=developer
DB_NAME=deokv2umqi87dr
```

### 2. 验证配置

```bash
python -c "from config.config import config; print(config.db_config)"
```

---

## 🎯 使用方式

### 方式1：自动清理（推荐）

在测试中使用 `track_created_id()` 跟踪创建的ID，测试结束后自动清理。

```python
def test_create_counterparty(counterparty_api, db_cleanup):
    """
    测试场景1：创建Counterparty
    """
    # 创建资源
    response = counterparty_api.create_counterparty(
        account_id="...",
        contact_name="Auto TestYan Counterparty 001",  # ⚠️ 必须以 "Auto TestYan" 开头
        email="auto.testyan.001@example.com",
        ...
    )
    
    assert_status_ok(response)
    
    # ⚠️ 重要：跟踪ID（测试结束后自动清理）
    created_id = response.json()["data"]["id"]
    track_created_id("counterparty", created_id)
    
    logger.info(f"✓ 创建成功，ID已跟踪: {created_id}")
    
    # 继续测试...
```

**特点**：
- ✅ 自动跟踪，测试结束自动清理
- ✅ 无需手动管理
- ✅ 适合大部分测试场景

---

### 方式2：手动清理指定ID

适用于需要立即清理或清理特定ID的场景。

```python
def test_cleanup_specific_counterparty(db_cleanup):
    """
    手动清理指定Counterparty
    """
    if db_cleanup is None:
        pytest.skip("数据库未配置")
    
    # 方法1: 清理单个ID
    stats = db_cleanup.cleanup_by_ids(
        "counterparty",
        ["251212054047057329"],
        dry_run=False  # False=实际执行，True=只模拟
    )
    
    logger.info(f"清理统计: {stats}")
    
    # 方法2: 清理多个ID
    stats = db_cleanup.cleanup_by_ids(
        "counterparty",
        ["251212054047057329", "251212054047057330", "251212054047057331"],
        dry_run=False
    )
```

---

### 方式3：批量清理脚本

适用于批量清理所有测试数据。

```bash
# 运行清理脚本
python scripts/cleanup_test_data.py
```

**执行流程**：
1. 扫描所有名称以 "Auto TestYan" 开头的数据
2. 显示将删除的数据统计
3. 等待用户确认
4. 执行实际清理
5. 显示清理结果

**示例输出**：
```
==========================================
🗑️  测试数据清理工具
==========================================

数据库连接信息:
  Host: fta-database-dev.cda9xsygtbs2.us-east-1.rds.amazonaws.com
  Port: 5432
  Database: deokv2umqi87dr
  User: developer

正在连接数据库...
✓ 数据库连接成功

==========================================
📊 步骤1: 模拟清理（查看将删除的数据）
==========================================

正在扫描测试数据（名称以 'Auto TestYan' 开头）...

==========================================
将删除以下数据
==========================================

📦 COUNTERPARTY 模块:
   - actc.t_share_recipient: 15 条
   - actc.t_share_recipient_account_relation: 8 条
   - actc.t_share_recipient_group_relation: 3 条

📦 CONTACT 模块:
   - actc.t_contact: 10 条

📊 总计: 36 条记录

==========================================
⚠️  确认清理
==========================================

请仔细检查上述统计信息，确认要删除这些数据吗？
提示: 只会删除名称以 'Auto TestYan' 开头的测试数据

输入 'yes' 确认执行清理，其他任意键取消: yes

==========================================
🗑️  步骤2: 执行清理
==========================================

正在清理数据...

✓ COUNTERPARTY 模块:
   - actc.t_share_recipient: 15 条
   - actc.t_share_recipient_account_relation: 8 条
   - actc.t_share_recipient_group_relation: 3 条

✓ CONTACT 模块:
   - actc.t_contact: 10 条

✅ 总计清理: 36 条记录

所有测试数据已清理完毕！
```

---

### 方式4：按名称前缀清理

适用于清理特定前缀的测试数据。

```python
def test_cleanup_by_prefix(db_cleanup):
    """
    按名称前缀清理
    """
    if db_cleanup is None:
        pytest.skip("数据库未配置")
    
    # 清理所有名称以 "Auto TestYan" 开头的 Counterparty
    stats = db_cleanup.cleanup_by_name_prefix(
        "counterparty",
        prefix="Auto TestYan",
        dry_run=False
    )
    
    logger.info(f"清理统计: {stats}")
```

---

## 🗄️ 支持的模块

当前支持以下模块的数据清理：

| 模块 | 主表 | 关联表 | 名称字段 |
|------|------|--------|---------|
| `counterparty` | t_share_recipient | 2个关联表 | contact_name |
| `contact` | t_contact | - | first_name |
| `sub_account` | t_sub_account | 1个关联表 | name |
| `financial_account` | t_financial_account | 1个关联表 | name |
| `trading_order` | t_trading_order | - | - |
| `client_list` | t_client_list | - | account_name |

### 添加新模块

在 `utils/data_cleanup.py` 中添加清理规则：

```python
CLEANUP_RULES = {
    "your_module": {
        "main_table": "actc.t_your_table",
        "id_field": "id",
        "related_tables": [
            {
                "table": "actc.t_your_related_table",
                "foreign_key": "your_module_id"
            }
        ],
        "name_field": "name"  # 用于按名称前缀查找
    }
}
```

---

## ⚠️ 安全注意事项

### 1. 只删除测试数据
- ✅ **必须**：名称以 "Auto TestYan" 开头
- ❌ **禁止**：删除真实业务数据

### 2. 数据库配置
- ✅ **必须**：只配置DEV环境数据库
- ❌ **禁止**：配置生产环境数据库

### 3. 先模拟后执行
```python
# ✅ 推荐：先模拟看看
stats = db_cleanup.cleanup_by_ids(module, ids, dry_run=True)
print(f"将删除: {stats}")

# ✅ 确认无误后执行
stats = db_cleanup.cleanup_by_ids(module, ids, dry_run=False)
```

### 4. 关联表顺序
- ✅ 自动处理：先删除关联表，再删除主表
- ✅ 防止外键约束错误

### 5. 事务回滚
- ✅ 出错自动回滚
- ✅ 不会留下部分删除的数据

---

## 📊 清理示例

### 示例1：Counterparty 清理

```python
def test_create_and_cleanup_counterparty(counterparty_api, db_cleanup):
    """创建并自动清理Counterparty"""
    
    # 1. 创建
    response = counterparty_api.create_counterparty(
        account_id="xxx",
        contact_name="Auto TestYan Counterparty 001",
        email="auto.testyan.001@example.com"
    )
    
    created_id = response.json()["data"]["id"]
    logger.info(f"创建成功: {created_id}")
    
    # 2. 跟踪ID
    track_created_id("counterparty", created_id)
    
    # 3. 测试业务逻辑...
    
    # 4. 测试结束后自动清理（无需手动删除）
```

**清理流程**：
1. 删除 `t_share_recipient_account_relation` 中的关联记录
2. 删除 `t_share_recipient_group_relation` 中的关联记录
3. 删除 `t_share_recipient` 中的主记录

---

### 示例2：批量清理

```python
def test_batch_cleanup(db_cleanup):
    """批量清理多个模块的测试数据"""
    
    if db_cleanup is None:
        pytest.skip("数据库未配置")
    
    # 清理所有模块的测试数据
    all_stats = db_cleanup.cleanup_all_test_data(dry_run=False)
    
    logger.info(f"清理统计: {all_stats}")
    # 输出: {'counterparty': {...}, 'contact': {...}, ...}
```

---

## 🐛 故障排查

### 问题1: 数据库连接失败

**错误**：
```
数据库连接池初始化失败: could not connect to server
```

**解决**：
1. 检查 `.env` 文件中的数据库配置是否正确
2. 确认网络能访问数据库（VPN、防火墙）
3. 验证数据库凭据（用户名、密码）

---

### 问题2: 没有找到需要清理的数据

**原因**：
- 数据名称不是以 "Auto TestYan" 开头
- 数据已经被清理过

**解决**：
```python
# 确保创建的数据使用正确的前缀
contact_name = f"Auto TestYan Counterparty {timestamp}"
```

---

### 问题3: 外键约束错误

**错误**：
```
update or delete on table violates foreign key constraint
```

**原因**：
- 关联表删除顺序错误

**解决**：
- 检查 `CLEANUP_RULES` 中的 `related_tables` 配置是否正确
- 确保先删除子表，再删除主表

---

### 问题4: 清理器返回None

**原因**：
- 数据库配置使用默认的 localhost（未实际配置）

**解决**：
```bash
# 在 .env 文件中配置真实的数据库连接
DB_HOST=fta-database-dev.cda9xsygtbs2.us-east-1.rds.amazonaws.com
```

---

## 📝 最佳实践

### 1. 命名规范

所有测试数据**必须**以 `Auto TestYan` 开头：

```python
✅ 正确
contact_name = "Auto TestYan Counterparty 001"
email = "auto.testyan.001@example.com"

❌ 错误
contact_name = "Test Counterparty"  # 不会被清理
email = "test@example.com"
```

### 2. 及时跟踪

创建资源后立即跟踪ID：

```python
✅ 推荐
response = api.create(...)
created_id = response.json()["data"]["id"]
track_created_id("counterparty", created_id)  # 立即跟踪

❌ 不推荐
response = api.create(...)
# ... 一堆其他操作 ...
# 忘记跟踪ID，导致无法清理
```

### 3. 使用db_cleanup fixture

在测试函数中添加 `db_cleanup` 参数：

```python
✅ 推荐
def test_something(counterparty_api, db_cleanup):
    # 可以使用自动清理功能

❌ 不推荐
def test_something(counterparty_api):
    # 无法使用自动清理
```

### 4. 定期运行清理脚本

```bash
# 每天运行一次清理脚本
python scripts/cleanup_test_data.py
```

---

## 🔄 清理流程图

```
测试开始
    ↓
创建测试数据（名称以 "Auto TestYan" 开头）
    ↓
track_created_id() 跟踪ID
    ↓
执行测试逻辑
    ↓
测试结束（pass/fail）
    ↓
db_cleanup fixture 自动触发
    ↓
按模块遍历跟踪的ID
    ↓
逐个模块清理：
  1. 删除关联表数据
  2. 删除主表数据
    ↓
记录清理统计
    ↓
清理完成
```

---

## 📞 获取帮助

遇到问题？

1. 查看日志文件：`logs/test_YYYY-MM-DD.log`
2. 查看清理统计：运行脚本会显示详细统计
3. 检查数据库配置：`.env` 文件

---

**功能状态**：✅ 已完成并测试  
**最后更新**：2026-02-09

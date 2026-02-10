# Scripts 脚本目录

## 📁 目录说明

存放项目的独立脚本文件。

## 📝 可用脚本

### 1. cleanup_test_data.py - 测试数据清理工具

**功能**：批量清理所有测试数据（名称以 "Auto TestYan" 开头）

**使用方法**：
```bash
python scripts/cleanup_test_data.py
```

或使用脚本权限：
```bash
chmod +x scripts/cleanup_test_data.py
./scripts/cleanup_test_data.py
```

**执行流程**：
1. 连接数据库
2. 扫描测试数据
3. 显示清理统计
4. 等待用户确认
5. 执行清理
6. 显示结果

**安全特性**：
- ✅ 只删除名称以 "Auto TestYan" 开头的数据
- ✅ 默认先模拟，需要用户确认
- ✅ 自动处理关联表
- ✅ 出错自动回滚

**适用场景**：
- 定期清理DEV环境的测试垃圾数据
- 测试完成后批量清理
- 手动清理特定模块的数据

---

## 🔧 配置要求

所有脚本都需要在 `.env` 文件中配置数据库连接：

```env
DB_HOST=fta-database-dev.cda9xsygtbs2.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=developer
DB_PASSWORD=developer
DB_NAME=deokv2umqi87dr
```

⚠️ **重要**：只配置DEV环境数据库！

---

## 📚 更多信息

查看完整的数据清理指南：`DATA_CLEANUP_GUIDE.md`

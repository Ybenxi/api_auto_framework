#!/usr/bin/env python3
"""
清理 Contact、Sub Account、FBO Account 测试数据
使用开发提供的备份函数，安全可靠
"""
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dao.db_manager import DBManager
from utils.data_cleanup import DataCleanup
from config.config import config

db = DBManager(config.db_config)
cleaner = DataCleanup(db)

print("=" * 60)
print("🗑️  Contact/Sub Account/FBO 数据清理工具（带备份）")
print("=" * 60)

# 步骤1: 全量备份
print("\n💾 步骤1: 全量备份...")
date_str = datetime.now().strftime("%m%d_%H%M")  # 格式: 0210_1200
backup_sql = f"""
SELECT public.backup_tables_daily(
    ARRAY['contact', 't_share_sub_account', 't_share_fbo_account'],
    '{date_str}',
    ARRAY['actc']
);
"""

try:
    db.execute_query(backup_sql)
    print(f"✓ 备份完成 → backup_data.actc_contact_{date_str}")
    print(f"✓ 备份完成 → backup_data.actc_t_share_sub_account_{date_str}")
    print(f"✓ 备份完成 → backup_data.actc_t_share_fbo_account_{date_str}")
    print(f"   （{date_str[:4]}={datetime.now().strftime('%m月%d日')}, {date_str[5:]}={datetime.now().strftime('%H:%M')}）")
except Exception as e:
    print(f"✗ 备份失败: {e}")
    print("终止清理以保证安全")
    sys.exit(1)

# 步骤2: 扫描测试数据
print("\n🔍 步骤2: 扫描测试数据...")
all_stats = {}

for module in ['contact', 'sub_account', 'fbo_account']:
    try:
        stats = cleaner.cleanup_by_name_prefix(module, 'Auto TestYan', dry_run=True)
        if stats:
            all_stats[module] = stats
            print(f"✓ {module}: {sum(stats.values())} 条")
    except Exception as e:
        print(f"⚠️  {module}: 跳过 ({e})")

if not all_stats:
    print("✓ 无测试数据")
    sys.exit(0)

# 步骤3: 显示统计
print("\n📊 将删除:")
total = sum(sum(s.values()) for s in all_stats.values())
for module, stats in all_stats.items():
    for table, count in stats.items():
        if count > 0:
            print(f"  - {table}: {count} 条")
print(f"\n总计: {total} 条")

# 步骤4: 确认
print("\n" + "=" * 60)
confirm = input("确认清理？输入 yes: ").strip().lower()
if confirm != 'yes':
    print("❌ 已取消")
    sys.exit(0)

# 步骤5: 执行清理
print("\n🗑️  执行清理...")
actual_total = 0
for module in all_stats.keys():
    try:
        actual_stats = cleaner.cleanup_by_name_prefix(module, 'Auto TestYan', dry_run=False)
        actual_total += sum(actual_stats.values())
    except Exception as e:
        print(f"✗ {module} 失败: {e}")

print(f"\n✅ 完成！删除 {actual_total} 条记录")
print(f"💾 备份位置: backup_data.actc_*_{date_str}")

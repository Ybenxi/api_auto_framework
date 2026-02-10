#!/usr/bin/env python3
"""
从备份表恢复数据
用于恢复误删的数据
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dao.db_manager import DBManager
from utils.logger import logger
from config.config import config


def list_backup_tables(db: DBManager):
    """列出所有备份表"""
    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'actc' 
      AND table_name LIKE '%_backup_%'
    ORDER BY table_name DESC
    """
    
    results = db.execute_query(sql)
    return [row['table_name'] for row in results]


def get_backup_count(db: DBManager, backup_table: str):
    """获取备份表的数据量"""
    sql = f"SELECT COUNT(*) as cnt FROM actc.{backup_table}"
    result = db.execute_query(sql)
    return result[0]['cnt'] if result else 0


def restore_from_backup(db: DBManager, backup_table: str, target_table: str):
    """从备份表恢复数据"""
    # 获取备份数据
    select_sql = f"SELECT * FROM actc.{backup_table}"
    backup_data = db.execute_query(select_sql)
    
    if not backup_data:
        print(f"⚠️  备份表 {backup_table} 为空")
        return 0
    
    # 恢复数据（使用INSERT）
    # 注意：这里简化处理，实际可能需要处理字段映射
    print(f"⚠️  注意：恢复功能需要手动执行SQL")
    print(f"建议SQL:")
    print(f"  INSERT INTO actc.{target_table}")
    print(f"  SELECT * FROM actc.{backup_table};")
    
    return len(backup_data)


def main():
    """主函数"""
    print("=" * 60)
    print("💾 数据恢复工具")
    print("=" * 60)
    
    try:
        db = DBManager(config.db_config)
        
        # 列出所有备份表
        print("\n🔍 查找备份表...")
        backup_tables = list_backup_tables(db)
        
        if not backup_tables:
            print("\n✓ 没有找到备份表")
            return
        
        print(f"\n找到 {len(backup_tables)} 个备份表:\n")
        
        for idx, table in enumerate(backup_tables, 1):
            count = get_backup_count(db, table)
            
            # 推测原表名
            original_table = table.split("_backup_")[0]
            
            print(f"{idx}. {table}")
            print(f"   原表: {original_table}")
            print(f"   数据量: {count} 条")
            print()
        
        # 提供恢复建议
        print("=" * 60)
        print("🔧 如何恢复数据")
        print("=" * 60)
        
        print("\n方法1：使用PostgreSQL客户端手动恢复")
        print("\n示例SQL:")
        if backup_tables:
            first_backup = backup_tables[0]
            original = first_backup.split("_backup_")[0]
            print(f"\n  -- 恢复 {first_backup}")
            print(f"  INSERT INTO actc.{original}")
            print(f"  SELECT * FROM actc.{first_backup};")
            print(f"\n  -- 删除备份表（恢复后）")
            print(f"  DROP TABLE actc.{first_backup};")
        
        print("\n方法2：保留备份表作为历史记录")
        print("  - 不删除备份表")
        print("  - 占用一定存储空间")
        print("  - 可随时查询历史数据")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        logger.error(f"恢复失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(0)

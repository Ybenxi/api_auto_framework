#!/usr/bin/env python3
"""
测试数据清理脚本
独立于测试框架，可直接运行

使用方法：
    python scripts/cleanup_test_data.py

功能：
    1. 自动查找所有名称以 "Auto TestYan" 开头的测试数据
    2. 先模拟清理，显示将删除的数据统计
    3. 用户确认后执行实际清理
    4. 支持清理所有模块或指定模块

⚠️ 安全提醒：
    - 只删除名称以 "Auto TestYan" 开头的数据
    - 默认先模拟，需要用户确认
    - 所有操作都有日志记录
    - 出错自动回滚
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dao.db_manager import DBManager
from utils.data_cleanup import DataCleanup
from utils.logger import logger
from config.config import config


def print_banner(text: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def main():
    """主函数"""
    print_banner("🗑️  测试数据清理工具")
    
    # 初始化数据库
    db_config = config.db_config
    
    print(f"\n数据库连接信息:")
    print(f"  Host: {db_config['host']}")
    print(f"  Port: {db_config['port']}")
    print(f"  Database: {db_config['database']}")
    print(f"  User: {db_config['user']}")
    
    # 检查是否是localhost（未配置）
    if db_config.get("host") == "localhost":
        print("\n❌ 错误：数据库未配置（使用默认localhost）")
        print("请在 .env 文件中配置数据库连接信息")
        sys.exit(1)
    
    try:
        print("\n正在连接数据库...")
        db = DBManager(db_config)
        cleaner = DataCleanup(db)
        print("✓ 数据库连接成功")
        
        # 1. 先模拟看看会删除多少
        print_banner("📊 步骤1: 模拟清理（查看将删除的数据）")
        print("\n正在扫描测试数据（名称以 'Auto TestYan' 开头）...\n")
        
        stats = cleaner.cleanup_all_test_data(dry_run=True)
        
        if not stats:
            print("✓ 没有找到需要清理的测试数据")
            print("   所有名称以 'Auto TestYan' 开头的数据已清理干净")
            return
        
        # 显示将删除的数据统计
        print_banner("将删除以下数据")
        
        total_records = 0
        for module, module_stats in stats.items():
            module_total = sum(module_stats.values())
            total_records += module_total
            
            print(f"\n📦 {module.upper()} 模块:")
            for table, count in module_stats.items():
                if count > 0:
                    print(f"   - {table}: {count} 条")
        
        print(f"\n📊 总计: {total_records} 条记录")
        
        # 2. 确认是否执行
        print_banner("⚠️  确认清理")
        print("\n请仔细检查上述统计信息，确认要删除这些数据吗？")
        print("提示: 只会删除名称以 'Auto TestYan' 开头的测试数据")
        print("")
        
        confirm = input("输入 'yes' 确认执行清理，其他任意键取消: ").strip().lower()
        
        if confirm != "yes":
            print("\n❌ 已取消清理")
            return
        
        # 3. 实际执行清理
        print_banner("🗑️  步骤2: 执行清理")
        print("\n正在清理数据...\n")
        
        actual_stats = cleaner.cleanup_all_test_data(dry_run=False)
        
        # 显示清理结果
        print_banner("✅ 清理完成")
        
        actual_total = 0
        for module, module_stats in actual_stats.items():
            module_total = sum(module_stats.values())
            actual_total += module_total
            
            print(f"\n✓ {module.upper()} 模块:")
            for table, count in module_stats.items():
                if count > 0:
                    print(f"   - {table}: {count} 条")
        
        print(f"\n✅ 总计清理: {actual_total} 条记录")
        print("\n所有测试数据已清理完毕！")
        
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        logger.error(f"清理失败: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断，已取消清理")
        sys.exit(0)

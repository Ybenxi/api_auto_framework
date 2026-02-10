"""
测试数据清理工具
用于清理测试过程中创建的垃圾数据

⚠️ 重要提醒：
1. 默认 dry_run=True（只模拟，不实际删除）
2. 只清理名称以 "Auto TestYan" 开头的测试数据
3. 所有操作都有日志记录
4. 出错自动回滚
"""
from typing import List, Dict, Optional
from dao.db_manager import DBManager
from utils.logger import logger


class DataCleanup:
    """
    数据清理器
    负责清理测试创建的垃圾数据
    """
    
    # 模块清理规则配置（主表 + 关联表）
    CLEANUP_RULES = {
        "counterparty": {
            "main_table": "actc.t_share_recipient",
            "id_field": "id",
            "related_tables": [
                {
                    "table": "actc.t_share_recipient_account_relation",
                    "foreign_key": "recipient_id"
                },
                {
                    "table": "actc.t_share_recipient_group_relation",
                    "foreign_key": "recipient_id"
                }
            ],
            "name_field": "recipient_name"  # 实际字段名是 recipient_name
        },
        "contact": {
            "main_table": "actc.contact",  # ⚠️ 没有 t_ 前缀
            "id_field": "sfid",  # ⚠️ 使用 sfid 而不是 id
            "related_tables": [],
            "name_field": "firstname"  # Salesforce字段名（小写无下划线）
        },
        "sub_account": {
            "main_table": "actc.t_share_sub_account",  # ⚠️ 正确的表名
            "id_field": "id",
            "related_tables": [],  # 暂时没有关联表
            "name_field": "name"
        },
        "fbo_account": {
            "main_table": "actc.t_share_fbo_account",  # ⚠️ 正确的表名
            "id_field": "id",
            "related_tables": [],
            "name_field": "name"
        },
        "financial_account": {
            "main_table": "actc.t_financial_account",
            "id_field": "id",
            "related_tables": [
                {
                    "table": "actc.t_financial_account_sub_account_relation",
                    "foreign_key": "financial_account_id"
                }
            ],
            "name_field": "name"
        },
        "trading_order": {
            "main_table": "actc.t_trading_order",
            "id_field": "id",
            "related_tables": [],
            "name_field": None  # 订单没有name字段
        },
        "client_list": {
            "main_table": "actc.t_client_list",
            "id_field": "id",
            "related_tables": [],
            "name_field": "account_name"
        }
    }
    
    def __init__(self, db_manager: DBManager):
        """
        初始化清理器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def cleanup_by_ids(self, module: str, ids: List[str], dry_run: bool = True) -> Dict[str, int]:
        """
        根据ID列表清理数据
        
        Args:
            module: 模块名称（如 "counterparty"）
            ids: 要删除的ID列表
            dry_run: 是否只模拟执行（默认True，不实际删除）⚠️
        
        Returns:
            删除统计 {"main_table": 删除数, "related_table_1": 删除数, ...}
        """
        if module not in self.CLEANUP_RULES:
            logger.error(f"未知模块: {module}")
            return {}
        
        if not ids:
            logger.warning("ID列表为空，跳过清理")
            return {}
        
        rule = self.CLEANUP_RULES[module]
        stats = {}
        
        logger.info(f"{'[模拟]' if dry_run else '[执行]'} 清理 {module} 模块数据，ID数量: {len(ids)}")
        logger.info(f"要{'模拟' if dry_run else '实际'}删除的ID: {ids}")
        
        try:
            # 1. 先删除关联表数据
            for related in rule.get("related_tables", []):
                table = related["table"]
                fk = related["foreign_key"]
                
                # 构建 IN 子句
                ids_str = "', '".join(ids)
                sql = f"DELETE FROM {table} WHERE {fk} IN ('{ids_str}')"
                
                if dry_run:
                    # 模拟：只查询会删除多少条
                    count_sql = f"SELECT COUNT(*) as cnt FROM {table} WHERE {fk} IN ('{ids_str}')"
                    result = self.db.execute_query(count_sql)
                    count = result[0]['cnt'] if result else 0
                    logger.info(f"  [模拟] {table}: 将删除 {count} 条")
                    stats[table] = count
                else:
                    # 实际删除
                    affected = self.db.execute_update(sql)
                    logger.info(f"  ✓ {table}: 删除 {affected} 条")
                    stats[table] = affected
            
            # 2. 最后删除主表数据
            main_table = rule["main_table"]
            id_field = rule["id_field"]
            ids_str = "', '".join(ids)
            sql = f"DELETE FROM {main_table} WHERE {id_field} IN ('{ids_str}')"
            
            if dry_run:
                count_sql = f"SELECT COUNT(*) as cnt FROM {main_table} WHERE {id_field} IN ('{ids_str}')"
                result = self.db.execute_query(count_sql)
                count = result[0]['cnt'] if result else 0
                logger.info(f"  [模拟] {main_table}: 将删除 {count} 条")
                stats[main_table] = count
            else:
                affected = self.db.execute_update(sql)
                logger.info(f"  ✓ {main_table}: 删除 {affected} 条")
                stats[main_table] = affected
            
            logger.info(f"{'[模拟]' if dry_run else '[完成]'} 清理统计: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"清理失败: {e}", exc_info=True)
            raise
    
    def cleanup_by_name_prefix(self, module: str, prefix: str = "Auto TestYan", dry_run: bool = True) -> Dict[str, int]:
        """
        根据名称前缀查找并清理数据（安全模式：只删除测试数据）
        
        Args:
            module: 模块名称
            prefix: 名称前缀（默认 "Auto TestYan"）⚠️
            dry_run: 是否只模拟执行（默认True）
        
        Returns:
            删除统计
        """
        if module not in self.CLEANUP_RULES:
            logger.error(f"未知模块: {module}")
            return {}
        
        rule = self.CLEANUP_RULES[module]
        name_field = rule.get("name_field")
        
        if not name_field:
            logger.warning(f"{module} 模块没有name_field，无法按名称清理")
            return {}
        
        # 1. 先查找匹配的ID
        main_table = rule["main_table"]
        id_field = rule["id_field"]
        
        find_sql = f"SELECT {id_field} FROM {main_table} WHERE {name_field} LIKE '{prefix}%'"
        
        try:
            results = self.db.execute_query(find_sql)
            ids = [str(row[id_field]) for row in results]
            
            if not ids:
                logger.info(f"未找到前缀为 '{prefix}' 的 {module} 数据")
                return {}
            
            logger.info(f"找到 {len(ids)} 条前缀为 '{prefix}' 的 {module} 数据")
            
            # 2. 调用ID清理方法
            return self.cleanup_by_ids(module, ids, dry_run=dry_run)
        
        except Exception as e:
            logger.error(f"按名称前缀清理失败: {e}", exc_info=True)
            raise
    
    def cleanup_all_test_data(self, dry_run: bool = True) -> Dict[str, Dict[str, int]]:
        """
        清理所有模块的测试数据（前缀为 "Auto TestYan"）
        
        Args:
            dry_run: 是否只模拟执行（默认True）⚠️
        
        Returns:
            每个模块的删除统计
        """
        all_stats = {}
        
        logger.info("=" * 60)
        logger.info(f"{'[模拟]' if dry_run else '[执行]'} 清理所有测试数据...")
        logger.info("=" * 60)
        
        for module in self.CLEANUP_RULES.keys():
            try:
                stats = self.cleanup_by_name_prefix(module, prefix="Auto TestYan", dry_run=dry_run)
                if stats:
                    all_stats[module] = stats
            except Exception as e:
                logger.error(f"清理 {module} 失败: {e}")
                continue
        
        logger.info("=" * 60)
        logger.info(f"{'[模拟]' if dry_run else '[完成]'} 全部清理统计: {all_stats}")
        logger.info("=" * 60)
        return all_stats


# 便捷函数
def cleanup_counterparty_by_id(counterparty_id: str, dry_run: bool = True):
    """
    快速清理单个Counterparty（便捷函数）
    
    Args:
        counterparty_id: Counterparty ID
        dry_run: 是否只模拟执行（默认True）⚠️
    
    Example:
        # 先模拟看看
        cleanup_counterparty_by_id("251212054047057329", dry_run=True)
        # 确认无误后实际执行
        cleanup_counterparty_by_id("251212054047057329", dry_run=False)
    """
    from config.config import config
    
    db_config = {
        "host": config.get_db_config("DB_HOST"),
        "port": int(config.get_db_config("DB_PORT", "5432")),
        "user": config.get_db_config("DB_USER"),
        "password": config.get_db_config("DB_PASSWORD"),
        "database": config.get_db_config("DB_NAME")
    }
    
    db = DBManager(db_config)
    cleaner = DataCleanup(db)
    
    return cleaner.cleanup_by_ids("counterparty", [counterparty_id], dry_run=dry_run)

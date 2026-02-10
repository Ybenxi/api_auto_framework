"""
数据清理功能使用示例

本文件展示如何使用自动数据清理功能
⚠️ 这是示例文件，所有测试都标记为skip（避免实际执行）
"""
import pytest
from utils.logger import logger
from test_cases.conftest import track_created_id


@pytest.mark.skip(reason="这是示例文件，演示如何使用数据清理功能")
class TestDataCleanupExample:
    """数据清理功能示例"""
    
    def test_auto_cleanup_example(self, counterparty_api, db_cleanup):
        """
        示例1：自动清理（推荐）
        
        创建资源后使用 track_created_id() 跟踪ID
        测试结束后会自动清理
        """
        logger.info("示例：创建Counterparty并自动清理")
        
        # 1. 创建资源
        response = counterparty_api.create_counterparty(
            account_id="xxx",
            contact_name="Auto TestYan Example Counterparty",  # ⚠️ 必须以 "Auto TestYan" 开头
            email="auto.testyan.example@example.com",
            mobile_phone="+1234567890"
        )
        
        # 2. 提取ID
        created_id = response.json()["data"]["id"]
        logger.info(f"创建成功: {created_id}")
        
        # 3. ⚠️ 重要：跟踪ID（测试结束后自动清理）
        track_created_id("counterparty", created_id)
        logger.info(f"✓ ID已跟踪，测试结束后将自动清理")
        
        # 4. 继续测试业务逻辑...
        # 无需手动删除，测试结束后自动清理
    
    def test_manual_cleanup_example(self, db_cleanup):
        """
        示例2：手动清理指定ID
        
        适用于需要立即清理或清理特定ID的场景
        """
        if db_cleanup is None:
            pytest.skip("数据库未配置")
        
        logger.info("示例：手动清理指定ID")
        
        # 假设这些ID是之前创建的
        ids_to_cleanup = ["251212054047057329", "251212054047057330"]
        
        # 先模拟看看会删除什么
        logger.info("步骤1：模拟清理...")
        stats = db_cleanup.cleanup_by_ids("counterparty", ids_to_cleanup, dry_run=True)
        logger.info(f"将删除: {stats}")
        
        # 确认无误后实际执行
        logger.info("步骤2：实际清理...")
        stats = db_cleanup.cleanup_by_ids("counterparty", ids_to_cleanup, dry_run=False)
        logger.info(f"已删除: {stats}")
    
    def test_cleanup_by_prefix_example(self, db_cleanup):
        """
        示例3：按名称前缀清理
        
        清理所有名称以指定前缀开头的数据
        """
        if db_cleanup is None:
            pytest.skip("数据库未配置")
        
        logger.info("示例：按名称前缀清理")
        
        # 清理所有名称以 "Auto TestYan" 开头的 Counterparty
        stats = db_cleanup.cleanup_by_name_prefix(
            "counterparty",
            prefix="Auto TestYan",
            dry_run=True  # 先模拟
        )
        
        logger.info(f"找到测试数据: {stats}")
    
    def test_cleanup_all_modules_example(self, db_cleanup):
        """
        示例4：批量清理所有模块
        
        清理所有支持的模块的测试数据
        """
        if db_cleanup is None:
            pytest.skip("数据库未配置")
        
        logger.info("示例：批量清理所有模块")
        
        # 清理所有模块的测试数据
        all_stats = db_cleanup.cleanup_all_test_data(dry_run=True)
        
        logger.info(f"所有模块的测试数据统计: {all_stats}")


@pytest.mark.skip(reason="这是示例文件，演示完整的创建-使用-清理流程")
class TestCompleteWorkflow:
    """完整工作流示例"""
    
    def test_complete_workflow(self, counterparty_api, db_cleanup):
        """
        完整工作流：创建 → 使用 → 自动清理
        
        这是最佳实践示例
        """
        logger.info("=" * 60)
        logger.info("完整工作流示例")
        logger.info("=" * 60)
        
        # 步骤1: 创建资源
        logger.info("\n步骤1: 创建测试数据...")
        response = counterparty_api.create_counterparty(
            account_id="xxx",
            contact_name="Auto TestYan Complete Workflow",
            email="auto.testyan.workflow@example.com",
            mobile_phone="+1234567890"
        )
        
        created_id = response.json()["data"]["id"]
        logger.info(f"✓ 创建成功: {created_id}")
        
        # 步骤2: 跟踪ID
        logger.info("\n步骤2: 跟踪ID...")
        track_created_id("counterparty", created_id)
        logger.info(f"✓ ID已跟踪")
        
        # 步骤3: 测试业务逻辑
        logger.info("\n步骤3: 测试业务逻辑...")
        
        # 3.1 查询详情
        detail_response = counterparty_api.get_counterparty_detail(created_id)
        logger.info(f"✓ 查询详情成功")
        
        # 3.2 更新
        update_response = counterparty_api.update_counterparty(
            counterparty_id=created_id,
            contact_name="Auto TestYan Updated Name"
        )
        logger.info(f"✓ 更新成功")
        
        # 3.3 列表查询
        list_response = counterparty_api.list_counterparties()
        logger.info(f"✓ 列表查询成功")
        
        # 步骤4: 测试结束
        logger.info("\n步骤4: 测试结束（自动清理）")
        logger.info("⚠️  测试结束后，db_cleanup fixture 会自动清理跟踪的ID")
        logger.info(f"   将删除: counterparty ID={created_id}")
        
        logger.info("\n" + "=" * 60)
        logger.info("完整工作流示例结束")
        logger.info("=" * 60)


# 便捷函数示例
@pytest.mark.skip(reason="这是示例函数")
def standalone_cleanup_example():
    """
    独立使用清理功能（不在pytest中）
    
    可以在Python脚本或交互式环境中使用
    """
    from utils.data_cleanup import cleanup_counterparty_by_id
    
    # 清理单个Counterparty
    stats = cleanup_counterparty_by_id("251212054047057329", dry_run=True)
    print(f"模拟清理: {stats}")
    
    # 确认无误后实际执行
    stats = cleanup_counterparty_by_id("251212054047057329", dry_run=False)
    print(f"实际清理: {stats}")

"""
测试数据清理工具 v2
============================

策略：按固定 FA/Account ID 精确定位，覆盖全部 19 张关联表，5 步由底向上删除。

固定锚点 ID（不会被删除）：
  - FA 1: 251212054048470568  （有固定 Sub 251212054048470660）
  - FA 2: 251212054048470574
  - FA 3: 251212054048470609  （不建 Sub）
  - Account 1: 251212054048470503
  - Account 2: 251212054048470507
  - Account 3: 251212054048470515  （High Risk）
  - BankInfo:  251212054048471047
  - Group 归属 accountid: 259124163505469218
"""
from typing import List, Dict
from dao.db_manager import DBManager
from utils.logger import logger


# ── 固定测试锚点 ID（不可删除）─────────────────────────────────────────────
FA_IDS = [
    "251212054048470568",  # Auto testyan FA 1（有固定 Sub）
    "251212054048470574",  # Auto testyan FA 2
    "251212054048470609",  # Auto testyan FA 3（no sub）
]
ACCOUNT_IDS = [
    "251212054048470503",  # Auto testyan account 1
    "251212054048470507",  # Auto testyan account 2
    "251212054048470515",  # Auto testyan account 3 (High Risk)
]
FIXED_SUB_ID     = "251212054048470660"   # FA1 下固定 Sub，保留不删
GROUP_ACCOUNT_ID = "259124163505469218"   # Group 数据归属的 accountid


def _in(ids: list) -> str:
    """生成 SQL IN 值串，如 '\'id1\',\'id2\''"""
    return "', '".join(ids)


class DataCleanup:
    """测试数据清理器 v2"""

    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self._tracked_ids: Dict[str, List[str]] = {}

    # ────────────────────────────────────────────────────────────────────────
    # 主入口
    # ────────────────────────────────────────────────────────────────────────

    def cleanup_all_test_data(self, dry_run: bool = True) -> Dict[str, Dict[str, int]]:
        """
        主清理入口（v2）。
        基于固定 FA/Account ID，5 步 19 张表，由底向上删除。
        dry_run=True 时只统计不实际删除。
        """
        return self.cleanup_by_fixed_ids(dry_run=dry_run)

    def cleanup_by_fixed_ids(self, dry_run: bool = True) -> Dict[str, Dict[str, int]]:
        """
        按固定锚点 ID 精确清理所有关联表。

        返回 dict（供平台 UI 展示）：
        {
          "money_movements": {"actc.t_payment_money_movement": N, ...},
          "groups":          {"actc.t_share_recipient_group": N, ...},
          "contacts":        {"actc.contact": N},
          "counterparties":  {"actc.t_share_recipient": N, ...},
          "subs":            {"actc.t_share_sub_account": N, ...},
        }
        """
        mode = "[模拟]" if dry_run else "[执行]"
        logger.info("=" * 60)
        logger.info(f"{mode} 开始清理测试数据（v2 固定 ID 方案）")
        logger.info(f"  FA IDs     : {FA_IDS}")
        logger.info(f"  Account IDs: {ACCOUNT_IDS}")
        logger.info(f"  保留 Sub   : {FIXED_SUB_ID}")
        logger.info("=" * 60)

        fa_in   = _in(FA_IDS)
        acct_in = _in(ACCOUNT_IDS)

        mm_sfid_subq = (
            f"SELECT sfid FROM actc.t_payment_money_movement "
            f"WHERE sleeve_account_sfid IN ('{fa_in}')"
        )
        new_sub_subq = (
            f"SELECT id FROM actc.t_share_sub_account "
            f"WHERE financial_account_id IN ('{fa_in}') "
            f"AND id != '{FIXED_SUB_ID}'"
        )
        group_subq = (
            f"SELECT id FROM actc.t_share_recipient_group "
            f"WHERE account_id = '{GROUP_ACCOUNT_ID}'"
        )
        recip_subq = (
            f"SELECT recipient_id FROM actc.t_share_recipient_account_relation "
            f"WHERE account_id IN ('{acct_in}')"
        )

        all_stats: Dict[str, Dict[str, int]] = {}

        # ── Step 1: MM 交易数据（11 张表）────────────────────────────────
        logger.info(f"{mode} Step 1: MM 交易数据")
        s1: Dict[str, int] = {}
        s1.update(self._del("actc.t_payment_money_movement_history",
            f"sleeve_account_sfid IN ('{fa_in}')", dry_run))
        s1.update(self._del("actc.t_payment_money_movement_reversal_history",
            f"original_money_movement_sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_payment_instant_payment_entry",
            f"money_movement_sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_payment_instant_payment_entry_log",
            f"money_movement_sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_payment_instant_request_for_payment_entry",
            f"money_movement_sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_payment_instant_request_for_payment_entry_log",
            f"money_movement_sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_share_transaction",
            f"sfid IN ({mm_sfid_subq})", dry_run))
        s1.update(self._del("actc.t_payment_bank_wire_transaction",
            f"financial_account_id IN ('{fa_in}')", dry_run))
        s1.update(self._del("actc.t_payment_deposit_check_detail",
            f"sma_sfid IN ('{fa_in}')", dry_run))
        s1.update(self._del("actc.t_share_financial_account_balance_history",
            f"financial_account_id IN ('{fa_in}')", dry_run))
        s1.update(self._del("actc.t_payment_money_movement",
            f"sleeve_account_sfid IN ('{fa_in}')", dry_run))
        all_stats["money_movements"] = s1

        # ── Step 2: Group 数据 ───────────────────────────────────────────
        logger.info(f"{mode} Step 2: Group 数据")
        s2: Dict[str, int] = {}
        s2.update(self._del("actc.t_share_recipient_group_relation",
            f"recipient_group_id IN ({group_subq})", dry_run))
        s2.update(self._del("actc.t_share_recipient_group",
            f"account_id = '{GROUP_ACCOUNT_ID}'", dry_run))
        all_stats["groups"] = s2

        # ── Step 3: Contact 数据 ─────────────────────────────────────────
        logger.info(f"{mode} Step 3: Contact 数据")
        s3: Dict[str, int] = {}
        s3.update(self._del("actc.contact",
            f"accountid IN ('{acct_in}')", dry_run))
        all_stats["contacts"] = s3

        # ── Step 4: Counterparty 数据 ────────────────────────────────────
        logger.info(f"{mode} Step 4: Counterparty 数据")
        s4: Dict[str, int] = {}
        s4.update(self._del("actc.t_share_recipient_status_log",
            f"recipient_id IN ({recip_subq})", dry_run))
        s4.update(self._del("actc.t_share_recipient",
            f"id IN ({recip_subq})", dry_run))
        s4.update(self._del("actc.t_share_recipient_account_relation",
            f"account_id IN ('{acct_in}')", dry_run))
        all_stats["counterparties"] = s4

        # ── Step 5: Sub + FBO 数据 ───────────────────────────────────────
        logger.info(f"{mode} Step 5: Sub + FBO 数据")
        s5: Dict[str, int] = {}
        s5.update(self._del("actc.t_share_fbo_account",
            f"sub_account_id IN ({new_sub_subq})", dry_run))
        s5.update(self._del("actc.t_share_sub_account",
            f"financial_account_id IN ('{fa_in}') AND id != '{FIXED_SUB_ID}'",
            dry_run))
        all_stats["subs"] = s5

        total = sum(sum(s.values()) for s in all_stats.values())
        logger.info("=" * 60)
        logger.info(f"{mode} 全部完成，共 {total} 条。分组统计：")
        for grp, grp_stats in all_stats.items():
            grp_total = sum(grp_stats.values())
            if grp_total:
                logger.info(f"  {grp}: {grp_total} 条")
        logger.info("=" * 60)
        return all_stats

    # ────────────────────────────────────────────────────────────────────────
    # track（接口保留，auto-cleanup 已禁用）
    # ────────────────────────────────────────────────────────────────────────

    def track(self, module: str, resource_id: str):
        """记录测试创建的 ID（auto-cleanup 已禁用，仅做记录）"""
        if module not in self._tracked_ids:
            self._tracked_ids[module] = []
        if resource_id:
            self._tracked_ids[module].append(str(resource_id))
            logger.debug(f"✓ 已跟踪 {module} ID: {resource_id}")

    # ────────────────────────────────────────────────────────────────────────
    # 内部辅助
    # ────────────────────────────────────────────────────────────────────────

    def _del(self, table: str, where: str, dry_run: bool) -> Dict[str, int]:
        """执行一条 DELETE（dry_run 时仅 COUNT）"""
        try:
            if dry_run:
                result = self.db.execute_query(
                    f"SELECT COUNT(*) AS cnt FROM {table} WHERE {where}"
                )
                cnt = int((result[0]["cnt"] if result else 0) or 0)
                if cnt:
                    logger.info(f"  [模拟] {table}: 将删除 {cnt} 条")
                return {table: cnt}
            else:
                affected = self.db.execute_update(
                    f"DELETE FROM {table} WHERE {where}"
                )
                affected = int(affected or 0)
                if affected:
                    logger.info(f"  ✓ {table}: 删除 {affected} 条")
                return {table: affected}
        except Exception as e:
            logger.error(f"  ✗ {table} 操作失败: {e}")
            return {table: 0}

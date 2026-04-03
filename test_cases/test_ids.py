"""
测试环境固定 ID 常量
====================
所有测试用例创建新数据时必须使用这里的 ID 作为锚点，
这样删除脏数据时才能被 v2 清理方案覆盖到。

不可删除的基础数据：
  Account 1 (主)  : 251212054048470503
  Account 2 (child): 251212054048470507
  Account 3 (child, High Risk): 251212054048470515
  FA 1 (有固定 Sub) : 251212054048470568
  FA 2             : 251212054048470574
  FA 3 (不建 Sub)   : 251212054048470609
  固定 Sub (FA1 下) : 251212054048470660
  BankInfo         : 251212054048471047
"""

# ── Account ────────────────────────────────────────────────────────
ACCOUNT_1_ID   = "251212054048470503"   # Auto testyan account 1（主）
ACCOUNT_2_ID   = "251212054048470507"   # Auto testyan account 2（child）
ACCOUNT_3_ID   = "251212054048470515"   # Auto testyan account 3（High Risk, child）

# 通用列表（用于 assign_account_ids、contact accountid 等）
TEST_ACCOUNT_IDS = [ACCOUNT_1_ID, ACCOUNT_2_ID, ACCOUNT_3_ID]

# ── Financial Account ──────────────────────────────────────────────
FA_1_ID        = "251212054048470568"   # Auto testyan FA 1（Managed，有 Sub）
FA_2_ID        = "251212054048470574"   # Auto testyan FA 2（Managed，无固定 Sub）
FA_3_ID        = "251212054048470609"   # Auto testyan FA 3（不建 Sub）

# 通用列表（用于 MM、sub、balance 等查询过滤）
TEST_FA_IDS    = [FA_1_ID, FA_2_ID, FA_3_ID]

# 主要 MM 测试用 FA（FA1 有 Sub，建议作为首选）
MAIN_FA_ID     = FA_1_ID
MAIN_SUB_ID    = "251212054048470660"   # FA1 下固定 Sub，保留不删，MM 可用

# ── BankInfo ───────────────────────────────────────────────────────
BANKINFO_ID    = "251212054048471047"   # Auto testyan bankinfo 1（ACH first_party）

# ── 越权 / 不可见 ID（用于 506/599 场景测试）─────────────────────
INVISIBLE_ACCOUNT_ID = "241010195849720143"   # 他人账户，visible 范围外

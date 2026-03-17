# API 自动化测试用例清单

> 生成日期：2026-03-16  
> 测试框架：Python + pytest + requests

---

## account_summary 模块

- test_account_summary_categorized.py（8 个测试场景）
- test_account_summary_flat.py（6 个测试场景）

---

## card 模块

### card / card_management

- test_card_detail.py（4 个测试场景）
- test_card_list_card_holders.py（6 个测试场景）
- test_card_list_cards.py（7 个测试场景）
- test_card_operations.py（12 个测试场景）
- test_card_remaining_usage.py（5 个测试场景）
- test_card_transactions.py（7 个测试场景）

### card / card_opening

- test_card_opening_application_detail.py（4 个测试场景）
- test_card_opening_debit_card.py（8 个测试场景）
- test_card_opening_list_applications.py（6 个测试场景）
- test_card_opening_reward_card.py（7 个测试场景）

### card / dispute_and_risk

- test_card_dispute_create.py（5 个测试场景）
- test_card_dispute_detail.py（4 个测试场景）
- test_card_dispute_list.py（6 个测试场景）
- test_risk_mcc_code.py（5 个测试场景）
- test_risk_spending_limit.py（7 个测试场景）

### card / sub_program

- test_nested_program_detail.py（4 个测试场景）
- test_nested_program_using_log.py（6 个测试场景）
- test_sub_program_detail.py（4 个测试场景）
- test_sub_program_list.py（7 个测试场景）
- test_sub_program_nested_programs.py（6 个测试场景）

---

## client_list 模块

- test_client_list_create.py（6 个测试场景）
- test_client_list_delete.py（4 个测试场景）
- test_client_list_detail.py（4 个测试场景）
- test_client_list_export.py（6 个测试场景）
- test_client_list_historical_chart.py（7 个测试场景）
- test_client_list_list.py（9 个测试场景）
- test_client_list_statistics.py（5 个测试场景）
- test_client_list_update.py（5 个测试场景）

---

## contact 模块

- test_contact_create_a_contact.py（9 个测试场景）
- test_contact_list_contacts.py（8 个测试场景）
- test_contact_retrieve_contact_detail.py（5 个测试场景）
- test_contact_retrieve_contact_ssn.py（5 个测试场景）
- test_contact_update_contact_detail.py（7 个测试场景）

---

## counterparty 模块

- test_counterparty_create_counterparty.py（6 个测试场景）
- test_counterparty_group_crud.py（7 个测试场景）
- test_counterparty_group_members.py（8 个测试场景）
- test_counterparty_list_counterparties.py（6 个测试场景）
- test_counterparty_list_groups.py（6 个测试场景）
- test_counterparty_mfa.py（7 个测试场景）
- test_counterparty_terminate.py（4 个测试场景）
- test_counterparty_transactions.py（6 个测试场景）
- test_counterparty_update.py（6 个测试场景）

---

## fbo_account 模块

- test_fbo_account_create.py（7 个测试场景）
- test_fbo_account_detail.py（4 个测试场景）
- test_fbo_account_list.py（6 个测试场景）

---

## financial_account 模块

- test_financial_account_list_financial_accounts.py（11 个测试场景）
- test_financial_account_retrieve_a_financial_account_payment_detail.py（3 个测试场景）
- test_financial_account_retrieve_financial_account_detail.py（4 个测试场景）
- test_financial_account_retrieve_related_money_movement_transactions.py（7 个测试场景）
- test_financial_account_retrieve_related_positions.py（5 个测试场景）
- test_financial_account_retrieve_related_settled_transactions.py（5 个测试场景）
- test_financial_account_retrieve_related_sub_accounts.py（5 个测试场景）

---

## identity_security 模块

- test_identity_mfa.py（7 个测试场景）
- test_identity_profile.py（7 个测试场景）
- test_identity_security.py（5 个测试场景）

---

## investment 模块

- test_investment_activity_summaries.py（6 个测试场景）
- test_investment_activity_trends.py（6 个测试场景）
- test_investment_asset_allocations.py（6 个测试场景）
- test_investment_asset_allocations_comparison.py（6 个测试场景）
- test_investment_performance_returns.py（7 个测试场景）
- test_investment_performance_risks.py（6 个测试场景）

---

## open_banking 模块

- test_open_banking_create_bank_account_connect_link.py（6 个测试场景）
- test_open_banking_create_open_banking_connect_link.py（5 个测试场景）
- test_open_banking_list_account_transactions.py（6 个测试场景）
- test_open_banking_list_authorized_accounts.py（6 个测试场景）
- test_open_banking_list_connected_external_accounts.py（6 个测试场景）

---

## payment_deposit 模块

### payment_deposit / account_transfer

- test_account_transfer_fee.py（4 个测试场景）
- test_account_transfer_financial_accounts.py（6 个测试场景）
- test_account_transfer_transactions.py（7 个测试场景）
- test_account_transfer_transfer.py（6 个测试场景）

### payment_deposit / ach_processing

- test_ach_batch_file.py（5 个测试场景）
- test_ach_cancel_reversal.py（7 个测试场景）
- test_ach_counterparties.py（2 个测试场景）
- test_ach_credit.py（5 个测试场景）
- test_ach_debit.py（3 个测试场景）
- test_ach_fee.py（4 个测试场景）
- test_ach_financial_accounts.py（7 个测试场景）
- test_ach_first_party_logic.py（6 个测试场景）
- test_ach_transactions.py（7 个测试场景）

### payment_deposit / instant_pay

- test_instant_pay_cancel_approve_reject.py（6 个测试场景）
- test_instant_pay_counterparties.py（2 个测试场景）
- test_instant_pay_fee.py（2 个测试场景）
- test_instant_pay_initiate_payment.py（6 个测试场景）
- test_instant_pay_initiate_request_payment.py（4 个测试场景）
- test_instant_pay_return.py（8 个测试场景）
- test_instant_pay_transactions.py（7 个测试场景）

### payment_deposit / internal_pay

- test_internal_pay_fee.py（5 个测试场景）
- test_internal_pay_payees.py（5 个测试场景）
- test_internal_pay_payers.py（6 个测试场景）
- test_internal_pay_transactions.py（7 个测试场景）
- test_internal_pay_transfer.py（7 个测试场景）

### payment_deposit / remote_deposit_check

- test_check_counterparties.py（3 个测试场景）
- test_check_fee.py（2 个测试场景）
- test_check_financial_accounts.py（7 个测试场景）
- test_check_scan_deposit.py（7 个测试场景）
- test_check_transactions.py（4 个测试场景）
- test_check_update_download.py（6 个测试场景）

### payment_deposit / wire_processing

- test_wire_counterparties.py（7 个测试场景）
- test_wire_domestic_payment.py（3 个测试场景）
- test_wire_fee.py（4 个测试场景）
- test_wire_financial_accounts.py（7 个测试场景）
- test_wire_international_payment.py（2 个测试场景）
- test_wire_request_payment.py（3 个测试场景）
- test_wire_transactions.py（6 个测试场景）

---

## profile_account 模块

- test_account_contacts.py（5 个测试场景）
- test_account_detail.py（4 个测试场景）
- test_account_financial.py（5 个测试场景）
- test_account_list.py（9 个测试场景）
- test_account_transactions.py（6 个测试场景）
- test_account_update.py（4 个测试场景）

---

## statement 模块

- test_statement_download.py（3 个测试场景）
- test_statement_list.py（6 个测试场景）

---

## sub_account 模块

- test_sub_account_create_a_sub_account.py（9 个测试场景）
- test_sub_account_list_sub_accounts.py（7 个测试场景）
- test_sub_account_retrieve_related_fbo_accounts.py（4 个测试场景）
- test_sub_account_retrieve_related_money_movement_transactions.py（6 个测试场景）
- test_sub_account_retrieve_related_positions.py（5 个测试场景）
- test_sub_account_retrieve_sub_account_detail.py（4 个测试场景）

---

## tenant 模块

- test_tenant_retrieve_current_tenant.py（6 个测试场景）

---

## trading_order 模块

- test_trading_order_cancel.py（6 个测试场景）
- test_trading_order_detail.py（3 个测试场景）
- test_trading_order_draft.py（1 个测试场景）
- test_trading_order_initiate.py（6 个测试场景）
- test_trading_order_list.py（7 个测试场景）
- test_trading_order_list_financial_accounts.py（5 个测试场景）
- test_trading_order_list_securities.py（6 个测试场景）
- test_trading_order_submit.py（4 个测试场景）
- test_trading_order_update.py（6 个测试场景）

---

## user_signup 模块

- test_user_signup_complete_flow.py（8 个测试场景）
- test_user_signup_create_user.py（9 个测试场景）
- test_user_signup_email_verification.py（7 个测试场景）
- test_user_signup_sms_verification.py（7 个测试场景）

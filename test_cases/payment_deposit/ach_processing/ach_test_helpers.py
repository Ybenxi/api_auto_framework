"""ACH 测试用公共小函数（避免从 conftest 循环导入）。"""


def ach_fp_false_credit_kwargs(ctx: dict, **extra) -> dict:
    """构建 initiate_credit(first_party=False) 参数；ctx['sub'] 为空时不传 sub_account_id。"""
    out = {
        "financial_account_id": ctx["fa"],
        "counterparty_id": ctx["cp"],
        "first_party": False,
        "same_day": False,
        **extra,
    }
    sub = ctx.get("sub")
    if sub:
        out["sub_account_id"] = sub
    return out

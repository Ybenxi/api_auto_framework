# Payment & Deposit 模块测试

## 模块概述
Payment & Deposit是项目中最重要的核心模块，负责所有支付和存款相关的业务功能。包含6个子模块，覆盖ACH处理、支票存款、内部转账、即时支付、电汇等完整的支付场景。

## 子模块划分（6个）

### 1. ACH Processing（ACH处理）
ACH（Automated Clearing House）自动清算所转账处理

### 2. Remote Deposit Check（远程支票存款）
通过拍照方式远程存入支票

### 3. Internal Pay（内部支付）✅
UniFi实例内的P2P支付，基于邮箱查找收款人

### 4. Instant Pay（即时支付）
即时到账的快速支付服务

### 5. Wire Processing（电汇处理）
国内和国际电汇转账处理

### 6. Account Transfer（账户转账）✅
UniFi平台内管理账户间的资金转移

## 已完成子模块（2个）

| 子模块 | 接口数 | 测试文件 | 测试场景 | 状态 |
|--------|--------|---------|---------|------|
| Internal Pay | 5 | 5 | 31 | ✅ |
| Account Transfer | 4 | 4 | 22 | ✅ |
| Wire Processing | 8 | 5 | 28 | ✅ |
| Remote Deposit Check | 9 | 6 | 28 | ✅ |
| Instant Pay | 15 | 6 | 33 | ✅ |
| ACH Processing | 11 | 7 | 40 | ✅ |
| **已完成小计** | **52** | **34** | **182** | **100%** |

## ✅ 所有子模块已完成！

Payment & Deposit大模块完成度：**100%** 🎉

## 模块结构

```
test_cases/payment_deposit/
├── conftest.py                    # 大模块配置
├── README.md                      # 本文档
│
├── internal_pay/                  # ✅ 已完成
│   ├── conftest.py
│   ├── README.md
│   └── test_*.py (5个文件)
│
├── account_transfer/              # ✅ 已完成
│   ├── conftest.py
│   ├── README.md
│   └── test_*.py (4个文件)
│
├── ach_processing/                # ⏳ 待开发
├── remote_deposit_check/          # ⏳ 待开发
├── instant_pay/                   # ⏳ 待开发
└── wire_processing/               # ⏳ 待开发
```

## Internal Pay vs Account Transfer 对比

| 特性 | Internal Pay | Account Transfer |
|------|-------------|-----------------|
| **使用场景** | P2P个人支付 | 账户间资金调配 |
| **收款人查找** | 基于邮箱 | 直接使用账户ID |
| **跨Profile** | 不明确 | ✅ 明确支持 |
| **接口数量** | 5个 | 4个 |
| **独有字段** | - | direction |
| **隐私保护** | 收款人账号脱敏 | 完整显示 |

## 共同特性

### 响应格式一致性问题
两个模块都存在响应格式不一致：
- **List接口**：无code包装层
- **Transfer接口**：无code包装层
- **Quote Fee接口**：有code包装层

parse方法已做兼容处理。

### 未定义的响应字段
两个模块都有相同的问题：
- fee
- completed_date
- transaction_id
- payer/payee_account_name（4个）
- transaction_type
- direction（Account Transfer独有）
- same_day（在fee响应中）

所有未定义字段已在代码中标注。

## 安全提醒

### ⚠️ 转账操作极度危险
- **会实际扣款**
- **不可撤销**
- **影响真实账户**

### 测试策略
- ✅ 所有transfer接口添加`@pytest.mark.no_rerun`
- ✅ 大部分转账测试skip
- ✅ 只测试错误处理（不实际转账）
- ✅ 如需实际测试，使用专门的测试账户

## 运行测试

```bash
# 运行整个Payment & Deposit模块
pytest test_cases/payment_deposit/ -v

# 运行特定子模块
pytest test_cases/payment_deposit/internal_pay/ -v
pytest test_cases/payment_deposit/account_transfer/ -v

# 按标记运行
pytest -m payment_deposit -v
pytest -m internal_pay -v
pytest -m account_transfer -v
```

## 项目统计（完成2个子模块后）

- Payment & Deposit子模块：2/6完成（33%）
- 测试场景：602个
- API接口：123个
- 待开发：ACH, RDC, Instant Pay, Wire（4个子模块）

---

**重要提示**：这是支付核心模块，每个子模块都涉及真实资金流动，开发时务必谨慎，测试时必须使用隔离的测试账户！

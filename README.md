# API 自动化测试框架

基于 `Python + pytest + requests + Streamlit` 的企业级 API 自动化测试框架，覆盖账户、支付、卡片、投资报表、客户管理、用户注册等核心业务模块，并内置自研报告系统、测试管理平台、数据库清理能力和多环境配置能力。

## 项目概览

- 当前项目已从基础脚手架演进为完整的 API 自动化测试平台，不再使用 Allure。
- 测试规模约为 `850+` 场景、`140+` 接口、`130+` 个测试文件。
- 代码层采用 `API Object` 模式，测试层基于 `pytest` 组织，报告层支持 `HTML Classic / HTML Pro / Excel / PDF`。
- 平台层基于 `Streamlit`，支持登录、语言切换、运行测试、查看历史报告、配置凭据和测试数据。

## 技术栈

- 测试框架：`pytest`、`pytest-rerunfailures`
- 接口请求：`requests`
- 日志系统：`loguru`
- 配置管理：`python-dotenv`
- 数据库：`SQLAlchemy`、`psycopg2-binary`
- 数据处理：`pandas`、`openpyxl`
- Web 平台：`streamlit`
- PDF 报告：`playwright`（Chromium）

## 当前能力

- `28` 个 API 封装文件（含 `auth_api.py`）
- `18` 个 `test_cases` 顶层模块目录
- `Payment & Deposit` 已拆分为 6 个子模块
- `Card` 已拆分为 4 个子模块
- 自动生成经典版和 Pro 版 HTML 报告
- 自动生成 Excel 用例清单和 PDF 摘要报告
- 支持失败重试；带 `@pytest.mark.no_rerun` 的测试会自动禁用重试
- 支持固定测试 ID 管理和 v2 精确脏数据清理

## 目录结构

```text
api_auto_framework/
├── api/                         # API 封装层
│   ├── auth_api.py
│   ├── account_api.py
│   ├── ach_processing_api.py
│   ├── card_management_api.py
│   ├── client_list_api.py
│   ├── counterparty_api.py
│   ├── investment_api.py
│   ├── trading_order_api.py
│   └── ...                      # 其余业务 API 类
├── assets/                      # 报告模板
│   ├── report_template.html
│   ├── report_template_pro.html
│   └── pdf_report_template.html
├── config/                      # 配置层
│   └── config.py
├── dao/                         # 数据库访问层
│   └── db_manager.py
├── data/                        # 枚举定义
│   └── enums.py
├── logs/                        # 日志目录
├── reports/                     # 测试报告输出目录
├── test_cases/                  # 测试用例
│   ├── conftest.py
│   ├── profile_account/
│   ├── financial_account/
│   ├── sub_account/
│   ├── fbo_account/
│   ├── payment_deposit/
│   ├── card/
│   ├── trading_order/
│   ├── client_list/
│   ├── user_signup/
│   └── ...                      # 其余业务模块
├── test_platform/               # Streamlit 测试管理平台
│   ├── 首页.py
│   ├── pages/
│   └── utils/
├── utils/                       # 通用工具
│   ├── assertions.py
│   ├── data_cleanup.py
│   ├── excel_reader.py
│   ├── generate_pdf_report.py
│   ├── logger.py
│   └── type_converters.py
├── .env.example                 # 环境变量模板
├── api_credentials.json         # 平台 API 凭据配置
├── auth_config.yaml             # 平台登录配置
├── email_config.json            # 邮件接收配置
├── environment_config.json      # 环境配置
├── test_data_config.json        # 固定测试数据配置
├── start_platform.sh            # 平台启动脚本
└── README.md
```

## 快速开始

### 1. 安装依赖

建议使用项目虚拟环境：

```bash
cd "/Users/mac/api auto/api_auto_framework"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

复制模板并填写本地配置：

```bash
cp .env.example .env
```

最常用配置项：

- `ENV`：环境标识，例如 `DEV` / `UAT`
- `BASE_URL`：接口域名
- `CORE`：业务 core，例如 `actc` / `fta`
- `TENANT_ID`、`USER_ID`、`BASIC_AUTH`
- `ACCOUNT_ID`、`CLIENT_ID`、`CLIENT_SECRET`、`ENCRYPTION_KEY`
- `DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`

说明：

- `config/config.py` 会优先从 `.env` 加载配置。
- 新版认证模型支持 `user_id / account_id / client_id / secret / core / encryption_key`。
- 若未显式提供 `BASIC_AUTH`，框架会尝试根据 `client_id:secret` 自动生成。

### 3. 运行测试

按模块运行：

```bash
pytest test_cases/contact/ -v -s
```

按文件运行：

```bash
pytest test_cases/payment_deposit/ach_processing/test_ach_credit.py -v -s
```

按 marker 运行：

```bash
pytest -m payment_deposit -v -s
```

运行全部测试：

```bash
pytest test_cases/ -v -s
```

## 报告系统

每次测试结束后，框架会自动生成以下报告文件：

- 经典 HTML 报告：`reports/benxi_report_YYYYMMDD_HHMMSS.html`
- 最新经典 HTML 副本：`reports/final_report.html`
- Pro HTML 报告：`reports/benxi_report_pro_YYYYMMDD_HHMMSS.html`
- Excel 用例清单：`reports/test_cases_YYYYMMDD_HHMMSS.xlsx`
- PDF 摘要报告：`reports/summary_report_YYYYMMDD_HHMMSS.pdf`
- 最新 PDF 副本：`reports/final_summary.pdf`

报告特性：

- 经典版和 Pro 版 HTML 报告同时生成
- 支持模块分组、文件分组、失败分析、QPS/TPS 指标
- 报告中的开始时间会根据浏览器本地时区动态展示
- 自动清理旧 HTML 报告，仅保留最近 5 次时间戳报告和固定副本

## 测试管理平台

### 启动方式

推荐使用启动脚本：

```bash
cd "/Users/mac/api auto/api_auto_framework"
./start_platform.sh
```

默认会启动两个服务：

- 平台地址：`http://localhost:8501`
- 报告静态服务：`http://localhost:8502`

也可以直接启动 Streamlit：

```bash
source .venv/bin/activate
streamlit run "test_platform/首页.py"
```

### 平台主要页面

- `首页`：项目统计、模块列表、快捷入口
- `Test Cases`：树形浏览测试用例、场景说明和源码
- `运行测试`：按模块 / 文件 / 全量执行测试，实时查看日志和统计
- `历史报告`：查看、下载、清理 HTML / PDF / Excel 报告
- `配置管理`：管理环境、凭据、邮箱白名单、固定测试数据、代码同步与脏数据清理

### 平台特性

- 登录鉴权：基于 `auth_config.yaml` + `bcrypt` + `HMAC-SHA256`
- 双语支持：默认英文，可通过右上角按钮切换中文
- 语言状态和登录态可通过 URL query 参数恢复
- 运行测试时会展示当前激活环境和激活凭据
- 平台可统计本次运行新增的脏数据数量

## 关键配置文件

### `.env`

本地运行时的底层配置来源，适合 CLI 运行 pytest。

### `environment_config.json`

测试平台使用的环境配置文件，当前预置：

- `DEV ACTC`
- `UAT ACTC`
- `UAT FTA`

其中 `active_env` 决定测试平台运行时注入的 `BASE_URL` 和 `CORE`。

### `api_credentials.json`

平台维护的 API 凭据文件。当前模型为：

- `user_id`
- `account_id`
- `client_id`
- `secret`
- `core`
- `encryption_key`（可选）

### `test_data_config.json`

平台维护的固定测试数据配置，按环境管理：

- `accounts`
- `financial_accounts`
- `sub_accounts`
- `bank_infos`

### `test_cases/test_ids.py`

Python 代码使用的固定测试 ID 常量文件。自动化创建数据时应优先围绕这些锚点构建，便于后续统一清理。

## 模块覆盖情况

### 账户与基础模块

- `profile_account`
- `financial_account`
- `sub_account`
- `fbo_account`
- `account_summary`
- `statement`
- `tenant`
- `open_banking`
- `contact`
- `identity_security`

### Payment & Deposit

- `internal_pay`
- `account_transfer`
- `wire_processing`
- `remote_deposit_check`
- `instant_pay`
- `ach_processing`

### Card

- `card_opening`
- `card_management`
- `sub_program`
- `dispute_and_risk`

### 其他业务模块

- `counterparty`
- `trading_order`
- `client_list`
- `investment`
- `user_signup`

### 未完全完成的模块

- `account_opening`
  - API 封装和基础架构已存在
  - 测试用例仍待补充

## 数据清理体系

当前项目使用 v2 精确清理方案，核心原则如下：

- 不再依赖名称前缀模糊匹配
- 改为围绕固定 `Account / FA / Sub / BankInfo` ID 做精确清理
- 覆盖 `money movements / groups / contacts / counterparties / subs` 等关联数据
- 正式清理前先做数据库备份
- 自动清理默认关闭，改为手动触发

建议通过测试平台 `配置管理 -> Operations` 页面执行扫描和清理。

## 框架约定

### 统一错误处理模式

UniFi API 的常见模式不是依赖 HTTP 状态码，而是：

- HTTP 通常返回 `200`
- 业务成功失败看响应体中的 `code`
- `code = 200` 表示成功
- `code = 506` 常表示可见性权限问题
- `code = 599` 常表示业务校验失败

### 响应格式兼容

不同模块存在多种响应格式：

- `{"code": 200, "data": {...}}`
- `{"content": [...], "page": 0, ...}`
- 直接数组 `[...]`

因此 API 封装和断言层已做兼容处理，编写新用例时不要假设所有接口结构一致。

### 日志与重试

- 禁止使用 `print()`，统一使用 `utils.logger.logger`
- 全局配置 `reruns = 2`
- 破坏性操作应加 `@pytest.mark.no_rerun`
- 无法安全自动化的正向场景应明确 `skip`

## 已知限制

以下场景当前通常会被 `skip` 或仅做错误路径验证：

- 需要真实验证码、真实邮箱、真实手机号的流程
- 需要真实图片 / 文件上传的流程
- 需要 RSA / PKCS1Padding 加密的密码或 PIN 场景
- 需要已结算交易才能继续的 reversal / return 场景
- 会产生真实资金流动或真实业务副作用的高风险操作

## 常用命令

运行单模块：

```bash
pytest test_cases/counterparty/ -v
```

运行单文件：

```bash
pytest test_cases/card/card_management/test_card_transactions.py -v
```

仅收集测试：

```bash
pytest --collect-only -q
```

启动平台：

```bash
./start_platform.sh
```

## GitHub

- 仓库地址：[https://github.com/Ybenxi/api_auto_framework.git](https://github.com/Ybenxi/api_auto_framework.git)
- 默认分支：`main`

## 备注

如果你要继续扩展新模块，建议优先遵循以下原则：

- 先补 `api/` 封装，再补 `test_cases/` 用例
- 尽量使用固定测试 ID 作为数据锚点
- 所有新增测试都写清楚中文场景描述和验证点
- 保持报告兼容性，避免破坏 HTML / PDF / Excel 产物

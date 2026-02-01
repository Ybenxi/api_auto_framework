# 接口自动化测试框架 (Python + Pytest + Requests + Allure)

这是一个企业级的接口自动化测试框架脚手架，基于 **API Object 模式** 设计，支持多环境切换、数据库交互和数据驱动。

## 1. 项目结构

```text
api_auto_framework/
├── api/                # API 定义层 (API Object)
│   ├── auth_api.py     # 登录认证接口封装
│   └── account_api.py  # 账户业务接口封装
├── test_cases/         # 业务用例层
│   ├── conftest.py     # Pytest Fixture (全局登录、数据库连接)
│   └── test_account_list.py # 账户列表测试用例
├── config/             # 配置层
│   └── config.py       # 多环境配置 (DEV, UAT, STG)
├── data/               # 数据层
│   └── test_data.xlsx  # Excel 测试数据 (预留)
├── utils/              # 工具层
│   ├── db_manager.py   # PostgreSQL 数据库封装
│   └── excel_reader.py # Excel 数据读取封装
├── reports/            # 测试报告目录
└── README.md           # 项目说明文档
```

## 2. 核心特性

- **多环境支持**：通过环境变量 `ENV` 切换环境（例如 `export ENV=UAT`）。
- **API Object 模式**：将接口请求细节封装在类中，用例层仅负责业务逻辑和断言。
- **自动登录机制**：利用 `pytest.fixture` 实现全局自动登录，并自动传递 Token。
- **数据库交互**：预留了 `DBManager` 工具类，支持 PostgreSQL 数据库操作。
- **数据驱动**：预留了 `ExcelReader` 工具类，支持从 Excel 读取测试数据。
- **美观报告**：集成 Allure 报告，支持测试步骤展示和严重程度分级。

## 3. 运行指南

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
# 默认在 DEV 环境运行
pytest test_cases/test_account_list.py --alluredir=reports/allure-results

# 切换到 UAT 环境运行
export ENV=UAT
pytest test_cases/test_account_list.py
```

### 查看报告
```bash
allure serve reports/allure-results
```

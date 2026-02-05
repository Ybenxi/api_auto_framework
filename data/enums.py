"""
枚举类管理模块
定义接口中使用的枚举类型，防止拼写错误，提高代码可维护性
"""
from enum import Enum


class CoreType(str, Enum):
    """
    Core 类型枚举
    不同的 Core 对应不同的 API 路径前缀
    """
    AUSTIN_CAPITAL = "actc"
    MODERN_RAILS = "modern-rails"
    STEARNS_BANK = "stearns_bank"
    ODT = "odt"
    YIELD = "yield"
    FAMILY_WEALTH = "familywealth"
    FINTECH = "fintech"
    ACCLOUD = "accloud"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class BusinessEntityType(str, Enum):
    """
    业务实体类型枚举
    对应 API 文档中的 business_entity_type 字段
    """
    C_CORP = "C-Corp"
    S_CORP = "S-Corp"
    PARTNERSHIP = "Partnership"
    LIMITED_PARTNERSHIP_LP = "Limited Partnership LP"
    SOLE_PROPRIETORSHIP = "Sole Proprietorship"
    UNINCORPORATED_BUSINESS = "Unincorporated Business"
    LLC = "LLC"
    TAX_EXEMPT = "Tax Exempt"
    PRIVATE_CORPORATION = "Private Corporation"
    NON_PROFIT = "Non Profit"
    CORPORATION = "Corporation"
    OTHER = "Other"
    LIMITED_LIABILITY_PARTNERSHIP = "Limited Liability Partnership"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class AccountStatus(str, Enum):
    """
    账户状态枚举
    对应 API 文档中的 status 字段
    """
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    SUSPENDED = "Suspended"
    CLOSED = "Closed"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class RecordType(str, Enum):
    """
    记录类型枚举
    对应响应中的 record_type 字段
    """
    BUSINESS = "Business"
    PERSONAL = "Personal"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class RiskLevel(str, Enum):
    """
    风险等级枚举
    对应响应中的 risk_level 字段
    """
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class FboAccountStatus(str, Enum):
    """
    FBO Account 状态枚举
    对应 API 文档中的 status 字段
    """
    OPEN = "Open"
    CLOSED = "Closed"
    PENDING = "Pending"
    DISCONNECT = "Disconnect"
    ON_HOLD = "OnHold"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class ApplicationStatus(str, Enum):
    """
    Account Opening Application 状态枚举
    """
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class BusinessStatus(str, Enum):
    """
    企业运营状态枚举
    """
    OPERATING = "Operating"
    NON_OPERATING = "Non-Operating"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class EmploymentStatus(str, Enum):
    """
    就业状态枚举
    """
    EMPLOYED = "Employed"
    NOT_EMPLOYED = "Not Employed"
    RETIRED = "Retired"
    SELF_EMPLOYED = "Self Employed"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class IssueType(str, Enum):
    """
    证券类型枚举（Trading Order & Client List）
    对应 API 文档中的 issue_type 字段
    """
    COMMON_STOCK = "Common Stock"
    ETF = "ETF"
    MUTUAL_FUNDS = "Mutual Funds"
    CRYPTO_CURRENCY = "Crypto Currency"
    BOND = "Bond"
    CERTIFICATES_OF_DEPOSIT = "Certificates of Deposit"
    COMMODITIES = "Commodities"
    COMMON_TRUST_FUNDS = "Common Trust Funds"
    HEDGE_FUNDS = "Hedge Funds and Private Equity"
    LIABILITIES = "Liabilities"
    MONEY_MARKET_FUND = "Money Market Fund"
    OTHER_ASSETS = "Other Assets"
    OTHER_FIXED_INCOME = "Other Fixed Income"
    REIT = "Real Estate Investment Trust"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class OrderAction(str, Enum):
    """
    订单动作枚举
    对应 Trading Order 中的 order_action 字段
    """
    BUY = "Buy"
    SELL = "Sell"
    SELL_ALL = "Sell_All"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class QuantityType(str, Enum):
    """
    数量类型枚举
    对应 Trading Order 中的 quantity_type 字段
    """
    SHARES = "Shares"
    DOLLARS = "Dollars"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class OrderType(str, Enum):
    """
    订单类型枚举
    对应 Trading Order 中的 order_type 字段
    ⚠️ 文档定义有误（说int实际是string），按示例使用string
    """
    MARKET_ORDER = "Market_Order"
    LIMIT_ORDER = "Limit_Order"
    STOP_ORDER = "Stop_Order"
    STOP_LIMIT = "Stop_Limit"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class OrderStatus(str, Enum):
    """
    订单状态枚举
    对应 Trading Order 中的 status 字段
    """
    NEW = "New"
    PENDING = "Pending"
    OVERNIGHT = "Overnight"
    IN_PROGRESS = "In_Progress"
    PARTIALLY_FILLED = "Partially_Filled"
    FILLED = "Filled"
    POSTED = "Posted"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class OMSCategory(str, Enum):
    """
    OMS 交易分类枚举
    对应 Client List 中的 oms_category 字段
    """
    EQUITY = "Equity"
    MUTUAL_FUND = "Mutual Fund"
    CRYPTO_CURRENCY = "Crypto Currency"
    CERTIFICATES_OF_DEPOSIT = "Certificates of Deposit"
    OTHERS = "Others"
    BOND = "Bond"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value

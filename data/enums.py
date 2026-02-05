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


class FeeType(str, Enum):
    """
    费用计算类型枚举
    对应 Investment Performance 接口中的 fee 参数
    """
    NET_OF_FEE = "NET_OF_FEE"      # 扣除费用后的金额
    GROSS_OF_FEE = "GROSS_OF_FEE"  # 扣除费用前的原始金额

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class IntervalType(str, Enum):
    """
    数据时间间隔枚举
    对应 Investment Performance Returns 接口中的 interval 参数
    """
    DAILY = "DAILY"
    QUARTERLY = "QUARTERLY"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class ClassificationMode(str, Enum):
    """
    账户摘要分类模式枚举
    对应 Account Summary 接口中的 classification_mode 参数
    """
    FLAT = "Flat"              # 扁平结构（无分组）
    CATEGORIZED = "Categorized" # 分类结构（按Asset/Liability分组）

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


# ==================== Card 模块相关枚举 ====================

class CardNetwork(str, Enum):
    """
    卡片网络枚举
    对应 Card 模块中的 network 字段
    """
    VISA = "Visa"
    MASTERCARD = "Mastercard"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class CardType(str, Enum):
    """
    卡片类型枚举
    对应 Card 模块中的 card_type 字段
    """
    DEBIT_CARD = "Debit_Card"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class CardStatus(str, Enum):
    """
    卡片状态枚举
    对应 Card 模块中的 card_status 字段
    """
    PENDING = "Pending"
    ACTIVE = "Active"
    RENEW = "Renew"
    LOCKED = "Locked"
    EXPIRED = "Expired"
    CLOSED = "Closed"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class LimitType(str, Enum):
    """
    限制类型枚举
    定义消费限制是基于日历周期还是卡片激活日期
    """
    CALENDAR_DATE = "Calendar_Date"
    ACTIVE_DATE = "Active_Date"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class SpendingLimitInterval(str, Enum):
    """
    消费限制时间间隔枚举
    对应 spending_limit 中的 interval 字段
    """
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"
    PER_AUTHORIZATION = "Per_Authorization"
    TOTAL = "Total"
    MCC = "MCC"  # 商户类别码限制

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class SubProgramStatus(str, Enum):
    """
    子项目状态枚举
    对应 Sub Program 中的 status 字段
    """
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    UNDER_REVIEW = "Under_Review"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class ClassificationType(str, Enum):
    """
    分类类型枚举
    标识子项目或卡片是商业还是消费类型
    """
    BUSINESS = "Business"
    CONSUMER = "Consumer"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class DisputeStatus(str, Enum):
    """
    争议状态枚举
    对应 Card Dispute 中的 status 字段
    """
    NEW = "New"
    SUBMITTED = "Submitted"
    RESULT = "Result"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class TransactionStatus(str, Enum):
    """
    交易状态枚举
    对应 Card Transaction 中的 status 字段
    """
    PENDING = "Pending"
    CANCEL = "Cancel"
    REJECTED = "Rejected"
    VOIDED = "Voided"
    SETTLED = "Settled"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class ReplaceReason(str, Enum):
    """
    卡片替换原因枚举
    对应 Replace Card 接口中的 reason 字段
    """
    REISSUED = "Reissued"
    LOST = "Lost"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value


class NestedProgramLogStatus(str, Enum):
    """
    嵌套项目使用日志状态枚举
    对应 Nested Program Using Log 中的 status 字段
    """
    COMPLETED = "Completed"
    CANCEL = "Cancel"
    PENDING = "Pending"

    def __str__(self):
        """返回枚举的实际值"""
        return self.value

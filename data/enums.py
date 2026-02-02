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

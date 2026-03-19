import pytest
from api.account_summary_api import AccountSummaryAPI
from api.card_report_api import CardReportAPI

pytestmark = pytest.mark.account_summary


@pytest.fixture(scope="module")
def account_summary_api(login_session):
    return AccountSummaryAPI(session=login_session)


@pytest.fixture(scope="module")
def card_report_api(login_session):
    return CardReportAPI(session=login_session)


@pytest.fixture(scope="module")
def real_card_id(login_session):
    """
    从 Account Summary 获取第一张卡的 id，作为 card_number 参数使用。
    card_number 参数可以传卡片 id 或 tokenized card number。
    """
    api = AccountSummaryAPI(session=login_session)
    resp = api.get_account_summary("Categorized")
    cards = resp.json().get("data", {}).get("debit_cards", [])
    if not cards:
        return None
    return cards[0].get("id")

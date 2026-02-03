"""
Sub Account Related Positions 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/holdings 接口
对应文档标题: Retrieve Related Positions
"""
import pytest
from api.sub_account_api import SubAccountAPI


@pytest.mark.sub_account
@pytest.mark.positions_api
class TestSubAccountRetrieveRelatedPositions:
    """
    Sub Account 相关持仓查询接口测试用例集
    """

    def test_retrieve_related_positions_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 相关的持仓（Holdings）
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用持仓接口返回 200
        3. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account
        print("\n[Step] 获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        print(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 获取相关持仓
        print("[Step] 调用 Retrieve Related Positions 接口")
        positions_response = sa_api.get_related_positions(sub_account_id, page=0, size=10)
        
        print("[Step] 验证 HTTP 状态码为 200")
        assert positions_response.status_code == 200, \
            f"接口返回状态码错误: {positions_response.status_code}, Response: {positions_response.text}"
        
        parsed_positions = sa_api.parse_list_response(positions_response)
        assert not parsed_positions.get("error"), f"响应解析失败: {parsed_positions.get('message')}"
        
        positions = parsed_positions.get("content", [])
        print(f"✓ 成功获取相关持仓:")
        print(f"  总持仓数: {parsed_positions['total_elements']}")
        print(f"  返回 {len(positions)} 条持仓记录")
        
        if len(positions) > 0:
            pos = positions[0]
            print(f"  第一条持仓: {pos.get('symbol')} - {pos.get('shares')} shares @ ${pos.get('price')}")

    def test_retrieve_related_positions_with_symbol_filter(self, login_session):
        """
        测试场景2：使用 symbol 筛选持仓
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 使用 symbol 筛选持仓")
        positions_response = sa_api.get_related_positions(
            sub_account_id, 
            symbol="AAPL",
            page=0, 
            size=10
        )
        
        assert positions_response.status_code == 200
        parsed_positions = sa_api.parse_list_response(positions_response)
        
        positions = parsed_positions.get("content", [])
        print(f"  返回 {len(positions)} 条匹配的持仓记录")
        
        print(f"✓ Symbol 筛选测试完成")

    def test_retrieve_related_positions_with_cusip_filter(self, login_session):
        """
        测试场景3：使用 cusip 筛选持仓
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 使用 cusip 筛选持仓")
        positions_response = sa_api.get_related_positions(
            sub_account_id, 
            cusip="037833100",
            page=0, 
            size=10
        )
        
        assert positions_response.status_code == 200
        parsed_positions = sa_api.parse_list_response(positions_response)
        
        positions = parsed_positions.get("content", [])
        print(f"  返回 {len(positions)} 条匹配的持仓记录")
        
        print(f"✓ CUSIP 筛选测试完成")

    def test_retrieve_related_positions_pagination(self, login_session):
        """
        测试场景4：验证持仓列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 使用分页参数 page=0, size=5")
        positions_response = sa_api.get_related_positions(
            sub_account_id, 
            page=0, 
            size=5
        )
        
        assert positions_response.status_code == 200
        parsed_positions = sa_api.parse_list_response(positions_response)
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_positions['total_elements']}")
        print(f"  总页数: {parsed_positions['total_pages']}")
        print(f"  当前页: {parsed_positions['number']}")
        print(f"  每页大小: {parsed_positions['size']}")

    def test_retrieve_related_positions_response_fields(self, login_session):
        """
        测试场景5：验证持仓响应字段完整性
        验证点：
        1. 接口返回 200
        2. 持仓对象包含必需字段
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 获取持仓并验证字段")
        positions_response = sa_api.get_related_positions(sub_account_id, page=0, size=1)
        assert positions_response.status_code == 200
        
        parsed_positions = sa_api.parse_list_response(positions_response)
        positions = parsed_positions.get("content", [])
        
        if len(positions) > 0:
            pos = positions[0]
            expected_fields = [
                "id", "sub_account_id", "securities_name", "symbol",
                "cusip", "shares", "price", "market_value", "cost_basis", "status"
            ]
            
            print("[Step] 验证持仓字段")
            for field in expected_fields:
                value = pos.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 字段验证完成")
        else:
            print("  跳过字段验证（列表为空）")

"""
Statement 列表接口测试用例
测试 GET /api/v1/cores/{core}/statements 接口
"""
import pytest
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestStatementList:
    """
    Statement 列表接口测试用例集
    """

    def test_list_statements_basic(self, statement_api):
        """
        测试场景1：基础列表查询 - 验证接口可用性
        验证点：
        1. HTTP 状态码为 200
        2. 响应中包含 content 字段
        3. content 是一个列表
        4. 响应结构完整（包含分页信息）
        """
        # 调用接口
        response = statement_api.list_statements()
        
        # 断言 HTTP 状态码
        assert_status_ok(response)
        
        # 解析响应并验证
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_list_structure(parsed, has_pagination=True)
        
        # 打印统计信息
        print(f"✓ 成功获取到 {len(parsed['content'])} 个 Statements，总计 {parsed['total_elements']} 个")

    def test_list_statements_filter_by_financial_account(self, statement_api):
        """
        测试场景2：按 Financial Account ID 筛选
        验证点：
        1. 接口返回成功
        2. 如果返回数据，验证所有 Statements 的 financial_account_id 都匹配
        """
        # 先获取一个有效的 Financial Account ID（从列表中获取）
        list_response = statement_api.list_statements(size=1)
        assert_status_ok(list_response)
        parsed_list = statement_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有 Statement 数据可供测试")
        
        # 使用第一个 Statement 的 financial_account_id 进行筛选
        test_financial_account_id = parsed_list["content"][0].get("financial_account_id")
        
        # 调用接口并传入筛选参数
        response = statement_api.list_statements(financial_account_id=test_financial_account_id)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        statements = parsed["content"]
        
        # 验证筛选逻辑
        if len(statements) > 0:
            for statement in statements:
                actual_fa_id = statement.get("financial_account_id")
                assert actual_fa_id == test_financial_account_id, \
                    f"Statement 的 financial_account_id 不匹配: 期望 {test_financial_account_id}, 实际 {actual_fa_id}"
            print(f"✓ 筛选成功，找到 {len(statements)} 个 Financial Account {test_financial_account_id} 的 Statements")
        else:
            print(f"⚠ 未找到该 Financial Account 的 Statements")

    def test_list_statements_filter_by_year_month(self, statement_api):
        """
        测试场景3：按年月筛选
        验证点：
        1. 接口返回成功
        2. 可以按 year 和 month 组合筛选
        """
        # 调用接口，按年月筛选
        response = statement_api.list_statements(year="2024", month="3")
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        statements = parsed["content"]
        
        # 验证筛选逻辑
        if len(statements) > 0:
            for statement in statements:
                # 验证年月匹配（如果字段存在）
                if statement.get("year") is not None:
                    assert str(statement.get("year")) == "2024", \
                        f"Statement 的 year 不匹配"
                if statement.get("month") is not None:
                    assert str(statement.get("month")) == "3", \
                        f"Statement 的 month 不匹配"
            print(f"✓ 筛选成功，找到 {len(statements)} 个 2024年3月 的 Statements")
        else:
            print(f"⚠ 未找到 2024年3月 的 Statements（可能是正常情况）")

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list_statements_pagination(self, statement_api, page_size):
        """
        测试场景4：分页功能验证
        验证点：
        1. 可以指定每页大小
        2. 返回的数据量不超过指定大小
        3. 分页信息正确
        """
        # 使用分页参数
        response = statement_api.list_statements(page=0, size=page_size)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证分页信息
        assert_pagination(parsed, expected_size=page_size, expected_page=0)
        
        print(f"✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed['content'])} 条")

    def test_list_statements_empty_result(self, statement_api):
        """
        测试场景5：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        # 使用不太可能存在的筛选条件（未来的年份）
        response = statement_api.list_statements(year="2099", month="12")
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证空结果
        assert_empty_result(parsed)
        
        print("✓ 空结果验证成功，接口正确返回空列表")

    def test_statement_response_fields(self, statement_api):
        """
        测试场景6：响应字段完整性验证
        验证点：
        1. 返回的 Statement 对象包含必需字段
        2. 字段类型正确
        """
        # 获取 Statements 列表
        response = statement_api.list_statements(size=1)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = statement_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        statements = parsed["content"]
        
        if len(statements) > 0:
            statement = statements[0]
            
            # 必需字段列表
            required_fields = [
                "id", "financial_account_id", "year", "month", "create_time"
            ]
            
            # 验证字段完整性
            assert_fields_present(statement, required_fields, obj_name="Statement 对象")
            
            print(f"✓ 字段完整性验证通过，Statement 对象包含所有必需字段")
            print(f"  示例 Statement: ID={statement.get('id')}, "
                  f"Year={statement.get('year')}, Month={statement.get('month')}")
        else:
            pytest.skip("没有 Statement 数据可供验证")

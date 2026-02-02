"""
测试用例扫描工具
自动扫描 test_cases/ 目录下的所有测试文件，生成 Excel 用例列表
"""
import os
import ast
import pandas as pd
from pathlib import Path


def extract_test_cases(test_cases_dir: str = "test_cases") -> list:
    """
    扫描测试用例目录，提取测试用例信息
    
    Args:
        test_cases_dir: 测试用例目录路径
        
    Returns:
        测试用例列表，每个元素是一个字典，包含以下字段：
        - Module: 文件名
        - Class: 测试类名
        - Function: 测试方法名
        - Description: 测试用例描述（从 Docstring 提取）
        - Markers: Pytest markers（如 @pytest.mark.contact）
    """
    test_cases = []
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    test_cases_path = project_root / test_cases_dir
    
    print(f"[INFO] 开始扫描测试用例目录: {test_cases_path}")
    
    # 遍历所有 test_*.py 文件
    for test_file in test_cases_path.rglob("test_*.py"):
        print(f"[INFO] 扫描文件: {test_file}")
        
        try:
            # 读取文件内容
            with open(test_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            # 使用 AST 解析代码
            tree = ast.parse(file_content)
            
            # 获取相对路径作为 Module 名称
            module_name = str(test_file.relative_to(test_cases_path))
            
            # 遍历 AST 节点
            for node in ast.walk(tree):
                # 查找测试类
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    # 提取类级别的 markers
                    class_markers = extract_markers(node)
                    
                    # 遍历类中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            function_name = item.name
                            
                            # 提取方法的 Docstring
                            description = extract_docstring(item)
                            
                            # 提取方法级别的 markers
                            method_markers = extract_markers(item)
                            
                            # 合并类和方法的 markers
                            all_markers = list(set(class_markers + method_markers))
                            
                            # 添加到测试用例列表
                            test_cases.append({
                                "Module": module_name,
                                "Class": class_name,
                                "Function": function_name,
                                "Description": description,
                                "Markers": ", ".join(all_markers) if all_markers else ""
                            })
                
                # 查找模块级别的测试函数（不在类中）
                elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    function_name = node.name
                    
                    # 提取 Docstring
                    description = extract_docstring(node)
                    
                    # 提取 markers
                    markers = extract_markers(node)
                    
                    # 添加到测试用例列表
                    test_cases.append({
                        "Module": module_name,
                        "Class": "",
                        "Function": function_name,
                        "Description": description,
                        "Markers": ", ".join(markers) if markers else ""
                    })
        
        except Exception as e:
            print(f"[ERROR] 解析文件 {test_file} 失败: {e}")
    
    print(f"[INFO] 扫描完成，共找到 {len(test_cases)} 个测试用例")
    
    return test_cases


def extract_docstring(node: ast.AST) -> str:
    """
    提取函数或类的 Docstring
    
    Args:
        node: AST 节点
        
    Returns:
        Docstring 内容（去除首尾空格）
    """
    docstring = ast.get_docstring(node)
    
    if docstring:
        # 去除首尾空格和多余的换行
        docstring = docstring.strip()
        
        # 提取第一行作为描述（通常是测试场景）
        lines = docstring.split("\n")
        
        # 查找 "测试场景：" 开头的行
        for line in lines:
            line = line.strip()
            if line.startswith("测试场景：") or line.startswith("测试场景:"):
                return line.replace("测试场景：", "").replace("测试场景:", "").strip()
        
        # 如果没有找到，返回第一行
        return lines[0].strip()
    
    return ""


def extract_markers(node: ast.AST) -> list:
    """
    提取 Pytest markers
    
    Args:
        node: AST 节点
        
    Returns:
        Marker 列表（如 ["contact", "list_api"]）
    """
    markers = []
    
    # 遍历装饰器
    if hasattr(node, "decorator_list"):
        for decorator in node.decorator_list:
            # 处理 @pytest.mark.xxx 形式
            if isinstance(decorator, ast.Attribute):
                if isinstance(decorator.value, ast.Attribute):
                    # pytest.mark.xxx
                    if (hasattr(decorator.value, "attr") and 
                        decorator.value.attr == "mark" and
                        hasattr(decorator.value, "value") and
                        isinstance(decorator.value.value, ast.Name) and
                        decorator.value.value.id == "pytest"):
                        markers.append(decorator.attr)
            
            # 处理 @pytest.mark.xxx() 形式（带括号）
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if isinstance(decorator.func.value, ast.Attribute):
                        if (hasattr(decorator.func.value, "attr") and 
                            decorator.func.value.attr == "mark" and
                            hasattr(decorator.func.value, "value") and
                            isinstance(decorator.func.value.value, ast.Name) and
                            decorator.func.value.value.id == "pytest"):
                            markers.append(decorator.func.attr)
    
    return markers


def generate_excel(test_cases: list, output_file: str = "test_cases.xlsx"):
    """
    生成 Excel 文件
    
    Args:
        test_cases: 测试用例列表
        output_file: 输出文件名
    """
    # 创建 DataFrame
    df = pd.DataFrame(test_cases)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    output_path = project_root / output_file
    
    # 生成 Excel 文件
    print(f"[INFO] 生成 Excel 文件: {output_path}")
    
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Test Cases")
        
        # 获取工作表
        worksheet = writer.sheets["Test Cases"]
        
        # 设置列宽
        worksheet.column_dimensions["A"].width = 30  # Module
        worksheet.column_dimensions["B"].width = 30  # Class
        worksheet.column_dimensions["C"].width = 50  # Function
        worksheet.column_dimensions["D"].width = 80  # Description
        worksheet.column_dimensions["E"].width = 30  # Markers
        
        # 设置表头样式
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # 设置内容对齐
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    
    print(f"[INFO] Excel 文件生成成功: {output_path}")
    print(f"[INFO] 共导出 {len(test_cases)} 个测试用例")


def main():
    """
    主函数
    """
    print("=" * 60)
    print("测试用例扫描工具")
    print("=" * 60)
    
    # 扫描测试用例
    test_cases = extract_test_cases()
    
    # 生成 Excel 文件
    if test_cases:
        generate_excel(test_cases)
        print("\n[SUCCESS] 测试用例列表生成完成！")
    else:
        print("\n[WARNING] 未找到任何测试用例")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

import openpyxl

class ExcelReader:
    """
    Excel 数据读取类
    用于从测试数据文件中读取用例参数
    """
    @staticmethod
    def read_excel(file_path, sheet_name):
        """
        读取 Excel 文件内容并返回字典列表
        """
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook[sheet_name]
            
            # 获取表头
            headers = [cell.value for cell in sheet[1]]
            data = []
            
            # 遍历数据行
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(row):  # 过滤空行
                    data.append(dict(zip(headers, row)))
            
            return data
        except Exception as e:
            print(f"Error reading Excel file {file_path}: {e}")
            return []

# 导出静态方法供调用
read_excel = ExcelReader.read_excel

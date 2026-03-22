"""
ACH Processing - Batch File 接口（跳过）
POST /money-movements/ach/batch-file

需要上传 ACH 格式批量文件（.csv），无法自动化，全部 skip
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
@pytest.mark.skip(reason="Upload ACH Batch 需要上传真实 ACH 格式文件，无法自动化")
class TestAchBatchFile:
    def test_upload_batch_skip(self, ach_processing_api):
        """⚠️ 跳过：需要 ACH 格式批量文件"""
        pass

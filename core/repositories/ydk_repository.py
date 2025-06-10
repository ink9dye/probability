# core/repository/ydk_repository.py

from .unified_repository import UnifiedRepository


class YDKRepository:
    """
    YDK 数据访问接口
    """

    def __init__(self):
        self.repo = UnifiedRepository()

    def load_ydk(self, file_path: str) -> dict:
        """
        加载 YDK 文件，返回 main / extra / side 卡牌 ID 列表
        """
        return self.repo.load(file_path, 'ydk')

    def save_ydk(self, file_path: str, ydk_data: dict):
        """
        保存 YDK 格式卡组
        :param file_path: 输出路径
        :param ydk_data: 包含 main/extras/side 的字典
        """
        self.repo.save(file_path, 'ydk', ydk_data)

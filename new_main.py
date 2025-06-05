# main.py

from services.deck_service import DeckService
from services.condition_service import ConditionService
from services.simulation_service import SimulationService


def main():
    """
    主函数，负责协调整个流程。
    使用服务层封装业务逻辑。
    """

    # 定义文件路径
    deck_file_path = "构筑与启动/征服斗魂构筑 .txt"
    condition_file_path = "构筑与启动/征服斗魂启动.txt"

    # 初始化服务实例
    deck_service = DeckService()
    condition_service = ConditionService()
    simulation_service = SimulationService()

    # 1️⃣ 加载卡池
    print("🔄 正在加载卡池...")
    card_pool = deck_service.load_deck_from_file(deck_file_path)
    if not card_pool:
        print("❌ 卡池加载失败，请检查文件路径或内容格式。")
        return

    # 2️⃣ 加载条件
    print("🔄 正在加载条件...")
    conditions_list = condition_service.load_conditions_from_file(condition_file_path)
    if not conditions_list:
        print("❌ 条件加载失败，请检查文件路径或内容格式。")
        return

    # 3️⃣ 设置模拟参数
    title = condition_service.get_comment_lines(condition_file_path)

    # 将解析结果传给模拟服务
    simulation_service.set_card_pool(card_pool)
    simulation_service.set_conditions_list(conditions_list)
    simulation_service.set_title(title)

    # 4️⃣ 开始模拟
    print("🎲 开始进行抽卡模拟...")
    probabilities = simulation_service.run_simulation()

    print("✅ 抽卡模拟已完成")


if __name__ == "__main__":
    main()

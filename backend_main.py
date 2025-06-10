# backend_main.py


from services.parser_service import parse_condition,parse_deck
from services.simulation_service import run_simulation

def main():
    """主控流程：加载构筑与启动条件，执行模拟"""
    deck_path = "data/构筑/征服斗魂构筑.txt"
    condition_path = "data/启动/征服斗魂启动.txt"

    # 加载卡池（按构筑文本解析）
    card_pool = parse_deck(deck_path, is_ydk=False, is_path=True)

    # 加载条件与标题
    conditions, titles = parse_condition(condition_path, is_path=True)

    # 执行抽卡模拟并报告
    run_simulation(
        card_pool=card_pool,
        conditions=conditions,
        draw_size=5,
        num_draws=100000,
        snapshot_interval=20000,
        titles=titles
    )

if __name__ == "__main__":
    main()

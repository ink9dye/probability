"""
YDK / 本地库页面占位。

请使用 gui.facade.AppFacade 实现 UI，不要照搬 probability 的 GUI（该项目 GUI 尚未落地）。
示例：
    facade = AppFacade()
    facade.export_ydk_txt("deck.ydk", "构筑/导出.txt")
    pool = facade.load_deck_txt("构筑/耀圣狱神构筑.txt")
    result = facade.run_simulation(deck_path=..., start_path=..., going_second=True)
"""

from gui.facade import AppFacade

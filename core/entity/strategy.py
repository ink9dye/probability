from typing import List, Callable, Dict, Any, Optional
import uuid

# 所有策略都注册在这里
STRATEGY_REGISTRY = {}




def register_strategy(name: str, strategy: 'Strategy'):
    """
    将策略注册到全局策略库中
    """
    STRATEGY_REGISTRY[name] = strategy




def get_strategy(name: str) -> Optional['Strategy']:
    """
    获取已注册的策略
    """
    return STRATEGY_REGISTRY.get(name)


def get_all_strategies() -> List['Strategy']:
    """
    获取所有已注册的策略
    """
    return list(STRATEGY_REGISTRY.values())


# core/entity/strategy.py

def apply_all_strategies(
    hand: List[str],
    pool: List[str],
    strategies: List['Strategy'] = None
) -> List[str]:
    if strategies is None:
        strategies = get_all_strategies()

    # 数值越小越优先，升序排列
    active_strategies = sorted(
        (s for s in strategies if s.enabled),
        key=lambda s: s.priority  # 默认升序排列
    )

    for strategy in active_strategies:
        hand = strategy.apply(hand, pool)

    return hand




class Strategy:
    def __init__(
            self,
            name: str,  # 策略名称，例如 "金满壶"
            condition_func: Callable[[List[str], List[str]], bool],  # 条件函数：接受 hand 和 pool，返回布尔值
            action_func: Callable[[List[str], List[str]], List[str]],  # 行为函数：接受 hand 和 pool，返回新的 hand
            description: str = "",  # 策略描述
            priority: int = 0,  # 策略优先级，数值越小越先执行
            strategy_id: str = None,  # 策略唯一 ID，可自定义，若为空则自动生成 UUID
        enabled: bool = True  # 是否启用，默认启用
    ):
        """
        策略实体类：包含策略的基本信息、触发逻辑与行为逻辑。

        :param name: 策略名称（如 "金满壶"）
        :param description: 策略描述文字
        :param condition_func: 判断是否触发策略的函数，输入是手牌和卡池
        :param action_func: 触发后执行的操作函数，输入手牌和卡池，返回新手牌
        :param priority: 策略优先级（越高越早执行）
        :param strategy_id: 唯一标识符，若未提供则使用 UUID 自动生成
        """
        self.strategy_id = strategy_id or str(uuid.uuid4())  # 如果没传 ID，就自动生成一个 UUID
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.action_func = action_func
        self.priority = priority if priority is not None else len(get_all_strategies())
        self.enabled = enabled  # 是否启用该策略
    def apply(self, hand: List[str], pool: List[str]) -> List[str]:
        """
        执行策略：如果条件函数返回 True，则执行行为函数；否则返回原手牌。

        :param hand: 当前手牌
        :param pool: 当前卡池
        :return: 新手牌（可能被修改）
        """
        if self.condition_func(hand, pool):
            return self.action_func(hand, pool)  # 满足条件则执行操作
        return hand  # 否则保持原状

    def to_dict(self) -> dict:
        """
        将策略对象序列化为字典形式，方便保存或传输。

        :return: dict 表示的策略对象
        """
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "condition": self._serialize_function(self.condition_func),  # 以函数名形式保存
            "action": self._serialize_function(self.action_func),
            "priority": self.priority,
            "enabled": self.enabled
        }

    @staticmethod
    def _serialize_function(func: Callable) -> str:
        """
        将函数序列化为其名称字符串（需要在使用时提前注册函数）。

        :param func: 要序列化的函数
        :return: 函数名称或字符串形式
        """
        if hasattr(func, "__name__"):
            return func.__name__
        return str(func)  # 如果没有 __name__，则用字符串形式保存

    @classmethod
    def from_dict(cls, data: dict, registry: Dict[str, Callable]) -> "Strategy":
        """
        从字典反序列化为 Strategy 对象，依赖于外部函数注册表。

        :param data: 字典形式的策略数据
        :param registry: 函数注册表，用于还原 condition_func 和 action_func
        :return: Strategy 实例对象
        """
        condition = registry.get(data["condition"])  # 从注册表中取出条件函数
        action = registry.get(data["action"])  # 从注册表中取出动作函数
        if not condition or not action:
            raise ValueError(f"无法找到对应的策略函数：{data}")
        return cls(
            strategy_id=data["strategy_id"],
            name=data["name"],
            description=data["description"],
            condition_func=condition,
            action_func=action,
            priority=data["priority"],
            enabled=data.get("enabled", True)
        )




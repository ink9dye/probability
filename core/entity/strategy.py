# class Strategy:
#     def __init__(self, name, condition_func, action_func, enabled=True):
#         self.name = name
#         self.condition_func = condition_func
#         self.action_func = action_func
#         self.enabled = enabled
#
#     def apply(self, hand, pool):
#         if self.enabled and self.condition_func(hand, pool):
#             return self.action_func(hand, pool)
#         return hand

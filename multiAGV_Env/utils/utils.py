

class Direction:
    """"
    define the relationship between action_str and action_value
    """
    def __init__(self):
        # five dimension
        self.str_value = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3, "STOP": 4}
        self.value_str = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT", 4: "STOP"}

        # four dimension
        # self.str_value = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
        # self.value_str = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}

    def action_num(self):
        # 如果只需要四维动作，可以手动更改这个值
        return 4
        # return len(self.str_value)

    def action_str_value(self, action_str):
        return self.str_value[action_str]

    def action_value_str(self, action_value):
        return self.value_str[action_value]


class ColorBox:
    def __init__(self):
        # variants for color
        self.GRAY_Color = (192, 192, 192)  # background color
        self.BLACK_COLOR = (0, 0, 0)
        self.WHITE_COLOR = (255, 255, 255)
        self.RED_COLOR = (200, 30, 30)
        self.BLUE_COLOR = (30, 30, 200)
        self.PINK_COLOR = (255, 153, 204)
        self.GREEN_COLOR = (0, 255, 0)



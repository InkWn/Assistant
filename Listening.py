import keyboard
from Resources import SpecialKeys


class Listening:
    def __init__(self, root, simplify, functions: dict, variables: dict):
        # 基本项
        self.root = root
        self.Simplify = simplify
        self.Functions = functions
        self.Variables = variables
        # 调用
        self.MouseEvents = self.Functions["MouseEvents"]
        self.KeyboardEvents = self.Functions["KeyboardEvents"]
        # 变量
        self.BoolMoving = False  # 移动中
        self.BoolClicking = False  # 点击中
        self.PressingShortKey = ""  # 短按按键
        self.PressingLongKey = ""  # 长按按键
        self.Allow_Stop_Short = False  # 允许停止模拟短按按键
        self.Allow_Stop_Long = False  # 允许停止模拟长按按键
        # 历史按键
        self.History_HotKeys = {"Specials": set(), "Words": None}  # 按过的按键

    # 关闭所有操作
    def close_all_operates(self):
        self.BoolMoving = False
        self.BoolClicking = False
        self.PressingShortKey = ""
        self.PressingLongKey = ""
        for i in range(4): self.Simplify.change_fg(i)  # 重置颜色
        self.KeyboardEvents.stop_all()  # 历史按键弹起一遍

    # 监听热键
    def start(self):
        def hook(event):
            if event.event_type == "down":
                # 如果正在模拟短按按键,且没有特殊键，按下的键也与正在模拟的键相同，则忽略
                if not self.History_HotKeys["Specials"] and event.name == self.PressingShortKey:
                    return
                if event.name in SpecialKeys:  # 此时按下的为特殊键，如[down]ctrl
                    self.History_HotKeys["Specials"].add(event.name)  # 记录特殊键
                else:
                    if self.History_HotKeys["Words"] is None:  # 单键为空时
                        self.History_HotKeys["Words"] = event.name  # 记录单键
                    else:
                        if self.PressingShortKey or self.PressingLongKey:  # 正在模拟按键
                            return  # 单键不为空，且正在模拟按键，不允许调用check_hotkey函数
                self.check_hotkey(self.History_HotKeys)

            elif event.event_type == "up":
                if event.name in SpecialKeys:  # 此时松开的为特殊键，如[up]ctrl
                    self.History_HotKeys["Specials"].discard(event.name)  # 移除特殊键
                else:
                    if event.name == self.History_HotKeys["Words"]:  # 此时松开的键为单键
                        self.History_HotKeys["Words"] = None  # 单键清除

        keyboard.hook(hook)

    # 辨别热键
    def check_hotkey(self, input_hot_keys: dict):
        def move_():
            if not self.BoolMoving:
                self.BoolMoving = True
                self.Simplify.change_fg(0, "red")
                self.mouse_move(self.Variables["Var_SpeedX"].get(), self.Variables["Var_SpeedY"].get())
            else:
                self.BoolMoving = False
                self.Simplify.change_fg(0)

        def click_():
            if not self.BoolClicking:
                self.BoolClicking = True
                button = {
                    "左键": "left", "右键": "right", "中键": "middle"
                }.get(self.Variables["Var_Click_Button"].get(), "left")
                self.Simplify.change_fg(1, "red")
                self.mouse_click(button, self.Variables["Var_Click_Interval"].get())
            else:
                self.BoolClicking = False
                self.Simplify.change_fg(1)

        def timer_1(): self.Allow_Stop_Short = True

        def timer_2(): self.Allow_Stop_Long = True

        # 判断是否为关闭所有操作的热键Close_All_Operates_HotKey，以下简称CA
        CA = self.Variables["Var_Close_All_Operates_HotKey"].get().split("+")
        # CA为单键
        if len(CA) == 1:
            if input_hot_keys["Words"] == CA[0]:  # 传入的单键与CA匹配
                self.close_all_operates()
                return
        # CA为组合键
        else:
            if input_hot_keys["Specials"] == set(CA[:-1]) and input_hot_keys["Words"] == CA[-1]:  # 传入的组合键与CA匹配
                self.close_all_operates()
                return
        # 不为CA，程序继续
        HotKeysGet_1 = (
            self.Variables["Var_Press_Short_HotKey"].get().split("+"),
            self.Variables["Var_Press_Long_HotKey"].get().split("+"))
        if self.PressingShortKey and self.Allow_Stop_Short:  # 正在模拟短按按键，且允许停止模拟，由timer函数计算时间
            if input_hot_keys["Specials"] == set(HotKeysGet_1[0]):  # 传入的特殊键与热键匹配
                self.PressingShortKey = ""  # 停止模拟短按按键
                self.Simplify.change_fg(2)
                self.Allow_Stop_Short = False
                return
        if self.PressingLongKey and self.Allow_Stop_Long:  # 正在模拟长按按键，且允许停止模拟，由timer函数计算时间
            if input_hot_keys["Specials"] == set(HotKeysGet_1[1]):
                self.key_press_long_stop()  # 停止模拟长按按键
                self.Allow_Stop_Long = False
                return
        if not self.PressingShortKey and not self.PressingLongKey:  # 无正在模拟的按键
            for i, hotkeys in enumerate(HotKeysGet_1):
                # 如果单键不为空且热键中的特殊键与函数hot_key["Specials"]匹配
                if (word := input_hot_keys["Words"]) is not None and input_hot_keys["Specials"] == set(hotkeys):
                    if i == 0 and not self.PressingShortKey:  # HotKeysGet_1[0],也就是i == 0为短按，且没有正在模拟短按按键
                        self.PressingShortKey = word  # 记录按键
                        self.key_press_short(word)  # 开始模拟短按按键
                        self.root.after(300, timer_1)  # 开始计时，0.3秒后self.Allow_Stop_Short变为True
                        self.Simplify.change_fg(2, "red")
                    elif i == 1:  # HotKeysGet_1[1],也就是i == 1为长按
                        self.PressingLongKey = word
                        self.key_press_long(word)
                        self.root.after(300, timer_2)
                        self.Simplify.change_fg(3, "red")
                    return  # 同个特殊键只会绑定一个热键，上述条件中，特殊键已经匹配了，所以没有下列代码的事了
        # 不为长按短按，开始判断鼠标操作的热键
        HotKeysGet_2 = (
            self.Variables["Var_Move_HotKey"].get().split("+"),
            self.Variables["Var_Click_HotKey"].get().split("+")
        )
        for i, hotkeys in enumerate(HotKeysGet_2):
            # 热键只有一个键，如r, f1
            if len(hotkeys) == 1:
                # input_hot_keys["Specials"]为空，且input_hot_keys["Words"]与热键中的单键匹配
                if not input_hot_keys["Specials"] and input_hot_keys["Words"] == hotkeys[0]:
                    if i == 0: move_()  # HotKeysGet_2[0],也就是i == 0为移动
                    elif i == 1: click_()  # HotKeysGet_2[1],也就是i == 1为点击
            else:  # 热键有多个键，如ctrl+f1,ctrl+shift+f1
                # 热键中的特殊键与input_hot_key["Specials"]匹配，且input_hot_key["Words"]与热键中的单键匹配
                if input_hot_keys["Specials"] == set(hotkeys[:-1]) and input_hot_keys["Words"] == hotkeys[-1]:
                    if i == 0: move_()
                    elif i == 1: click_()

    # 鼠标移动
    def mouse_move(self, x, y):
        if self.BoolMoving:
            self.MouseEvents.move(x, y)
            self.root.after(100, lambda: self.mouse_move(x, y))

    # 鼠标点击
    def mouse_click(self, button, interval):
        if self.BoolClicking:
            self.MouseEvents.click(button)
            self.root.after(int(interval * 1000), lambda: self.mouse_click(button, interval))

    # 键盘短按
    def key_press_short(self, key):
        if self.PressingShortKey:  # 不为空
            self.KeyboardEvents.press(key)
            self.root.after(
                int(self.Variables["Var_Press_Short_Interval"].get() * 1000),
                lambda: self.key_press_short(key)
            )

    # 键盘长按
    def key_press_long(self, key):
        def start():
            self.KeyboardEvents.hold(key)
            self.root.after(time_, self.key_press_long_stop)

        if (time_ := self.Variables["Var_Press_Long_Duration"].get()) == 0:
            time_ = 1000 * 60 * 60  # 0秒则持续时间为1小时
        else:
            time_ = int(time_ * 1000)  # 转换为毫秒
        # 暂停0.3秒后开始长按
        self.root.after(300, start)

    # 键盘长按结束
    def key_press_long_stop(self):
        self.KeyboardEvents.release(self.PressingLongKey)
        self.History_HotKeys["Words"] = None  # 单键清除
        self.PressingLongKey = ""  # 停止模拟长按按键
        self.Simplify.change_fg(3)

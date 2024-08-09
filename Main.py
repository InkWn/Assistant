# -*- coding: utf-8 -*-

import os
import re
import keyboard
import tkinter as tk
from tkinter import messagebox
from Resources import *
from Listening import Listening
from WinAPI import MouseEvents, KeyboardEvents
from ui_frame import FrameMouse, FrameKeyboard, FrameOther
from ui_toplevel import SimplifyDisplay, Settings, Explain, CalcDisplay


# 退出程序
def exit_program(exit_code: int):
    if exit_code == 0:  # 正常退出
        keyboard.unhook_all()
    elif exit_code == 1:  # 系统错误
        messagebox.showerror("错误", "请在Windows系统下运行")
    elif exit_code == 2:  # 程序已在运行
        messagebox.showerror("错误", "程序已在运行，请勿重复打开")
        raise SystemExit(0)  # 直接退出，不删除UniqueRunnerPath文件
    elif exit_code == 3:  # 读取配置文件时发生错误
        messagebox.showerror("错误", "配置文件读取失败")
    elif exit_code == 4:  # 检查配置文件时发生错误
        messagebox.showerror("错误", "配置文件参数错误")
    if os.path.exists(UniqueRunnerPath): os.remove(UniqueRunnerPath)
    raise SystemExit(0)


# 读取配置文件
class ConfigReader:
    def __init__(self, config: str):
        self.dict = {}
        self.read_config(config)

    # 读取配置文件
    def read_config(self, config_file: str):
        try:
            with open(config_file, 'r', encoding='utf-8') as _file_:
                content = _file_.read()
        except Exception: exit_program(3)
        p = r'\[([^\]]+)\]([^\[\r\n]+)'
        pattern = re.compile(p)
        for match in pattern.finditer(content):
            key, value = match.group(1), match.group(2)
            try:
                if '.' in value: value = float(value)
                else: value = int(value)
            except Exception: pass
            self.dict[key] = value

    # 检查配置文件
    def check_config(self) -> bool:
        Error = False
        ErrorInfo = "[Error]\n"

        def check01(name: str, hotkey_value: list):
            nonlocal Error, ErrorInfo
            if len(hotkey_value) == 1 and hotkey_value[0] in SpecialKeys:  # 单个特殊键
                Error = True
                ErrorInfo += f"{name}热键不能为单个特殊键\n"
                return
            if all(k in SpecialKeys for k in hotkey_value):  # 全部为特殊键
                Error = True
                ErrorInfo += f"{name}热键不能全部为特殊键\n"
                return
            get_special = [s for s in hotkey_value if s in SpecialKeys]  # 提取特殊键
            if get_special == hotkey_dict["Press_Short_HotKey"] or get_special == hotkey_dict["Press_Long_HotKey"]:
                Error = True
                ErrorInfo += f"{name}热键的特殊键与短按/长按的热键相同\n"
                return
            if hotkey_value[-1] in SpecialKeys and len(hotkey_value) != 1:  # 单键需在最后面
                Error = True
                ErrorInfo += f"{name}热键的单键需在最后面\n"
                return

        def check02(name: str, hotkey_value: list):
            nonlocal Error, ErrorInfo
            if not all(k in SpecialKeys for k in hotkey_value):  # 含有非特殊键
                Error = True
                ErrorInfo += f"{name}热键只能为特殊键\n"
                return

        try:
            # int类型检查
            for key in ("WinSizeX", "WinSizeY", "FontSize", "Protect_Time", "Move_SpeedX", "Move_SpeedY"):
                if not isinstance(self.dict[key], int):
                    Error = True
                    ErrorInfo += f"{key}参数类型应为int类型\n"
            # float类型检查
            for key in ("Click_Interval", "Press_Short_Interval", "Press_Long_Duration"):
                if not isinstance(self.dict[key], (float, int)):
                    Error = True
                    ErrorInfo += f"{key}参数类型应为float或int类型\n"
            hotkey_dict = {
                "Move_HotKey": tuple(self.dict["Move_HotKey"].split("+")),  # 值为元组，根据+号分割，如ctrl+t -> ("ctrl", "t")
                "Click_HotKey": tuple(self.dict["Click_HotKey"].split("+")),
                "Press_Short_HotKey": tuple(self.dict["Press_Short_HotKey"].split("+")),
                "Press_Long_HotKey": tuple(self.dict["Press_Long_HotKey"].split("+")),
                "Close_All_HotKey": tuple(self.dict["Close_All_HotKey"].split("+")),
            }
        except KeyError:  # 字典中找不到对应值
            with open("Error.log", "a", encoding="utf-8") as f:
                f.write(f"{ErrorInfo}缺少部分参数\n")
            return False
        # 移动与点击热键检查
        check01("移动", hotkey_dict["Move_HotKey"])
        check01("点击", hotkey_dict["Click_HotKey"])
        check01("关闭所有操作", hotkey_dict["Close_All_HotKey"])
        # 短按与长按热键检查
        check02("短按", hotkey_dict["Press_Short_HotKey"])
        check02("长按", hotkey_dict["Press_Long_HotKey"])
        if Error:
            with open("Error.log", "a", encoding="utf-8") as f:
                f.write(ErrorInfo)
            return False
        # 冲突检查
        seem_values = set()
        for key_name, value in hotkey_dict.items():
            if value in seem_values:
                with open("Error.log", "a", encoding="utf-8") as f:
                    f.write(f"[Error]\n{key_name}热键与其他热键冲突\n")
                return False
            seem_values.add(value)
        return True

    def get(self) -> dict: return self.dict


# 主窗口
class Display:
    def __init__(self, config_dict: dict):
        self.config_dict = config_dict
        # 窗口项
        self.Font = self.config_dict.get('Font', None)
        self.font_size = max(self.config_dict.get('FontSize', 13), Param_Ranges['FontSize']["min"])
        self.InkWn = self.config_dict.get('WinTitle', 'Assistant')
        sizex = max(self.config_dict.get('WinSizeX', 385), Param_Ranges['WinSizeX']["min"])
        sizey = max(self.config_dict.get('WinSizeY', 200), Param_Ranges['WinSizeY']["min"])
        self.WinBg = self.config_dict.get('WinBg', 'black')
        self.WinFg = self.config_dict.get('WinFg', 'white')
        self.OpenFrame = self.config_dict.get('OpenFrame', "鼠标专区")
        if self.OpenFrame not in ("鼠标专区", "键盘专区", "其他工具"): self.OpenFrame = "鼠标专区"
        # 简化窗口项
        self.Simplify_Show = self.config_dict.get('Simplify_Show', "False") == "True"
        self.SimplifyLayout = self.config_dict.get('Simplify_Layout', '布局-竖')
        self.SimplifyBgColor = self.config_dict.get('Simplify_Bg_Color', 'None')
        self.SimplifyFgColor = self.config_dict.get('Simplify_Fg_Color', 'black')
        # 显示项
        self.CommandBgColor = self.config_dict.get('Command_Bg_Color', 'black')
        self.CommandFgColor = self.config_dict.get('Command_Fg_Color', '#3A96DD')
        self.InputBgColor = self.config_dict.get('Input_Bg_Color', 'black')
        self.InputFgColor = self.config_dict.get('Input_Fg_Color', '#FFFFCC')
        self.OutputBgColor = self.config_dict.get('Output_Bg_Color', 'black')
        self.OutputFgColor = self.config_dict.get('Output_Fg_Color', '#13A1AA')
        # 鼠标移动项
        Move_HotKey = self.config_dict.get('Move_HotKey', "r")
        SpeedX = self.config_dict.get('Move_SpeedX', 1000)
        SpeedY = self.config_dict.get('Move_SpeedY', 20)
        # 鼠标点击项
        Click_HotKey = self.config_dict.get('Click_HotKey', "t")
        Click_Button = self.config_dict.get('Click_Button', "左键")
        Click_Interval = max(self.config_dict.get('Click_Interval', 0.1), Param_Ranges['Click_Interval']["min"])
        # 短按项
        Press_Short_HotKey = self.config_dict.get('Press_Short_HotKey', "ctrl")
        Press_Short_Interval = max(
            self.config_dict.get("Press_Short_Interval", 0.1),
            Param_Ranges['Press_Short_Interval']["min"]
        )
        # 长按项
        Press_Long_HotKey = self.config_dict.get('Press_Long_HotKey', "ctrl+shift")
        Press_Long_Duration = max(
            self.config_dict.get("Press_Long_Duration", 0),
            Param_Ranges['Press_Long_Duration']["min"]
        )
        # 关闭所有项热键
        Close_All_HotKey = self.config_dict.get('Close_All_HotKey', "esc")
        # 程序保护项
        Protect_Time = self.config_dict.get('Protect_Time', 0)
        if not (0 <= Protect_Time <= 600): Protect_Time = 600  # 保护时间，最短0秒(不保护)，最长10分钟
        # 窗口初始化
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口
        self.root.after(AfterTime, self.root.deiconify)  # 防止闪烁
        self.root_info = (sizex, sizey, 150, 100)
        # 窗口拓展
        self.root.geometry("{0}x{1}+{2}+{3}".format(*self.root_info))
        self.root.title(self.InkWn)
        with open(IconPath, 'wb') as f: f.write(ICO)
        self.root.iconbitmap(IconPath)
        if os.path.exists(IconPath): os.remove(IconPath)
        self.screen_info = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.root.minsize(sizex, sizey)
        self.root.maxsize(self.screen_info[0] // 2, self.screen_info[1] // 2)
        self.root['bg'] = self.WinBg
        self.root.bind("<Tab>", lambda e: "break")  # 禁止Tab切换
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        # 子窗口信息
        pos_x = (self.screen_info[0] - 600) // 2
        pos_y = (self.screen_info[1] - 300) // 2 - 50
        self.explain_info = (600, 300, pos_x, pos_y)
        self.settings_info = (
            x := (36 * self.font_size), y := (20 * self.font_size),
            (self.screen_info[0] - x) // 2,
            (self.screen_info[1] - y) // 2 - 50
        )
        self.calc_info = (600, 300, (self.screen_info[0] - 600) // 2, (self.screen_info[1] - 300) // 2 - 50)
        # Var变量
        self.Var_Setting_State = tk.BooleanVar(value=False)  # 设置开关状态
        self.Var_Explain_State = tk.BooleanVar(value=False)  # 说明开关状态
        self.Var_Calc_State = tk.BooleanVar(value=False)  # 圣遗物计算器开关状态
        self.Var_Move_HotKey = tk.StringVar(value=Move_HotKey)  # 移动热键
        self.Var_SpeedX = tk.IntVar(value=SpeedX)  # X轴移动速度
        self.Var_SpeedY = tk.IntVar(value=SpeedY)  # Y轴移动速度
        self.Var_Click_HotKey = tk.StringVar(value=Click_HotKey)  # 点击热键
        self.Var_Click_Button = tk.StringVar(value=Click_Button)  # 点击类型
        self.Var_Click_Interval = tk.DoubleVar(value=Click_Interval)  # 点击间隔
        self.Var_Press_Short_HotKey = tk.StringVar(value=Press_Short_HotKey)  # 短按热键
        self.Var_Press_Short_Interval = tk.DoubleVar(value=Press_Short_Interval)  # 短按间隔
        self.Var_Press_Long_HotKey = tk.StringVar(value=Press_Long_HotKey)  # 长按热键
        self.Var_Press_Long_Duration = tk.DoubleVar(value=Press_Long_Duration)  # 长按持续时间
        self.Var_Switch_Listen = tk.BooleanVar(value=True)  # 关闭或开启热键监听，默认开启
        self.Var_Close_All_Operates_HotKey = tk.StringVar(value=Close_All_HotKey)  # 关闭所有操作的热键
        self.Var_Listen_CalcDisplay_State = tk.BooleanVar(value=True)  # 打开计算器时是否关闭监听热键，默认开启
        self.Var_Protect_Time = tk.IntVar(value=Protect_Time)  # 程序保护时间
        self.Var_Protect_Timer = tk.BooleanVar(value=False)  # 开始计时，默认关闭
        self.Var_Surplus_Time = tk.IntVar(value=Protect_Time)  # 剩余保护时间
        # 调用函数
        self.MouseEvents = MouseEvents()
        self.KeyboardEvents = KeyboardEvents()
        self.Simplify = SimplifyDisplay(
            self.root, self.Font, self.font_size,
            self.SimplifyBgColor, self.SimplifyFgColor,
            self.SimplifyLayout
        )
        self.Listening = Listening(
            self.root, self.Simplify,
            functions={
                "MouseEvents": self.MouseEvents,
                "KeyboardEvents": self.KeyboardEvents
            },
            variables={
                "Var_SpeedX": self.Var_SpeedX, "Var_SpeedY": self.Var_SpeedY,
                "Var_Click_Button": self.Var_Click_Button,
                "Var_Click_Interval": self.Var_Click_Interval,
                "Var_Close_All_Operates_HotKey": self.Var_Close_All_Operates_HotKey,
                "Var_Press_Short_Interval": self.Var_Press_Short_Interval,
                "Var_Press_Long_Duration": self.Var_Press_Long_Duration,
                "Var_Move_HotKey": self.Var_Move_HotKey,
                "Var_Click_HotKey": self.Var_Click_HotKey,
                "Var_Press_Short_HotKey": self.Var_Press_Short_HotKey,
                "Var_Press_Long_HotKey": self.Var_Press_Long_HotKey,
            },
        )
        # 比例
        for i in range(3): self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=6)
        # 控件
        self.Menu = tk.Menu(self.root)
        self.root["menu"] = self.Menu
        if not self.Simplify_Show: self.Simplify.root.withdraw()  # 隐藏简化窗口

        self.ShowFrames = (
            FrameMouse(
                master=self.root,
                winbg=self.WinBg, winfg=self.WinFg,
                font=self.Font, font_size=self.font_size,
                variables={
                    "Var_SpeedX": self.Var_SpeedX,
                    "Var_SpeedY": self.Var_SpeedY,
                    "Var_Move_HotKey": self.Var_Move_HotKey,
                    "Var_Click_Button": self.Var_Click_Button,
                    "Var_Click_Interval": self.Var_Click_Interval,
                    "Var_Click_HotKey": self.Var_Click_HotKey,
                }
            ),
            FrameKeyboard(
                master=self.root,
                winbg=self.WinBg, winfg=self.WinFg,
                font=self.Font, font_size=self.font_size,
                variables={
                    "Var_Press_Short_Interval": self.Var_Press_Short_Interval,
                    "Var_Press_Short_HotKey": self.Var_Press_Short_HotKey,
                    "Var_Press_Long_Duration": self.Var_Press_Long_Duration,
                    "Var_Press_Long_HotKey": self.Var_Press_Long_HotKey,
                }
            ),
            FrameOther(
                master=self.root,
                winbg=self.WinBg, winfg=self.WinFg,
                font=self.Font, font_size=self.font_size,
                component={
                    "Win_Simplify": self.Simplify
                },
                functions={
                    "listen_hotkey": self.Listening.start,
                    "unlisten_hotkey": keyboard.unhook_all,
                    "close_all_operates": self.Listening.close_all_operates,
                    "simplify_change_layout": self.Simplify.change_layout,
                    "start_protect": self.start_protect,
                },
                variables={
                    "Simplify_Show": self.Simplify_Show,
                    "Var_Switch_Listen": self.Var_Switch_Listen,
                    "Var_Close_All_Operates_HotKey": self.Var_Close_All_Operates_HotKey,
                    "Var_Listen_CalcDisplay_State": self.Var_Listen_CalcDisplay_State,
                    "Var_Protect_Time": self.Var_Protect_Time,
                    "Var_Protect_Timer": self.Var_Protect_Timer,
                    "Var_Surplus_Time": self.Var_Surplus_Time,
                },
            ),
        )

    def run(self):
        self.menu()
        self.notebook()
        self.KeyboardEvents.press("shift")  # 切换输入法的中英文
        self.Listening.start()
        self.root.mainloop()

    def close(self):
        self.Listening.close_all_operates()
        self.root.destroy()
        exit_program(0)

    # 保护模式
    def start_protect(self):
        if self.Var_Protect_Timer.get() and self.Var_Protect_Time.get() > 0:  # 保护模式开启且时间不为0
            if (surplus := self.Var_Surplus_Time.get()) == 0:
                self.close()
            else:
                self.Var_Surplus_Time.set(surplus - 1)
                self.root.after(1000, self.start_protect)

    # 组件
    def notebook(self):
        def switch_frame(id_):
            FrameMapping = {0: (1, 2), 1: (0, 2), 2: (0, 1)}
            Buttons[id_]["relief"] = "sunken"
            Buttons[FrameMapping[id_][0]]["relief"] = "raised"
            Buttons[FrameMapping[id_][1]]["relief"] = "raised"
            self.ShowFrames[id_].grid(column=0, row=1, columnspan=3, sticky='nsew', pady=(3, 0))
            self.ShowFrames[FrameMapping[id_][0]].grid_forget()
            self.ShowFrames[FrameMapping[id_][1]].grid_forget()

        Buttons = [
            tk.Button(
                self.root, text=value,
                font=(self.Font, self.font_size),
                bg=self.WinBg, fg=self.WinFg,
                command=lambda idx=idx: switch_frame(idx)
            ) for idx, value in {0: "鼠标专区", 1: "键盘专区", 2: "其他工具"}.items()
        ]
        for idx, button in enumerate(Buttons): button.grid(column=idx, row=0, sticky='nsew')
        switch_frame({"鼠标专区": 0, "键盘专区": 1, "其他工具": 2}.get(self.OpenFrame, 0))  # 初始显示

    # 菜单
    def menu(self):
        def open_setting():
            if not self.Var_Setting_State.get():
                def func():
                    self.Var_Switch_Listen.set(True)  # 开启监听热键
                    self.Listening.start()  # 启动监听热键

                # 为了实时更新值
                modifiable = {
                    "Protect_Time": self.Var_Protect_Time,
                    "Move_HotKey": self.Var_Move_HotKey,
                    "Move_SpeedX": self.Var_SpeedX, "Move_SpeedY": self.Var_SpeedY,
                    "Click_HotKey": self.Var_Click_HotKey,
                    "Click_Button": self.Var_Click_Button, "Click_Interval": self.Var_Click_Interval,
                    "Press_Short_HotKey": self.Var_Press_Short_HotKey,
                    "Press_Short_Interval": self.Var_Press_Short_Interval,
                    "Press_Long_HotKey": self.Var_Press_Long_HotKey,
                    "Press_Long_Duration": self.Var_Press_Long_Duration,
                    "Close_All_HotKey": self.Var_Close_All_Operates_HotKey,
                }
                self.Var_Setting_State.set(True)  # 打开了设置
                self.Var_Switch_Listen.set(False)  # 关闭监听热键
                keyboard.unhook_all()  # 关闭监听热键
                self.Listening.close_all_operates()  # 关闭所有操作
                self.Settings = Settings(
                    root=self.root, info=self.settings_info, font=self.Font, font_size=self.font_size,
                    kwargs={"change_state": self.Var_Setting_State, "listen_start": func},
                    config_dict=self.config_dict,
                    modifiable=modifiable, bg=self.WinBg, fg=self.WinFg,
                )
                # 等待窗口关闭
                self.Settings.root.wait_window(self.Settings.root)
            else:
                try: self.Settings.root.focus_set()
                except Exception: pass

        def open_explain():
            if not self.Var_Explain_State.get():
                self.Var_Explain_State.set(True)
                self.Explain = Explain(self.root, self.explain_info, self.Font, self.font_size, self.Var_Explain_State)
            else:
                try: self.Explain.root.focus_set()
                except Exception: pass

        def open_donate():
            def show():
                root.geometry(
                    "+{}+{}".format(
                        (self.screen_info[0] - root.winfo_width()) // 2,
                        (self.screen_info[1] - root.winfo_height()) // 2
                    )
                )
                root.deiconify()

            root = tk.Toplevel(self.root)
            root.withdraw()
            root.title("")
            root.attributes("-toolwindow", True)
            root.focus_set()
            root.resizable(False, False)
            tk.Label(root, text="理性打赏，感谢您的支持！", font=(self.Font, self.font_size), fg=self.WinFg, bg=self.WinBg).pack()
            tk.Label(root, text="微信扫码支持作者！", font=(self.Font, self.font_size), fg=self.WinFg, bg=self.WinBg).pack()
            with open(DonatePath, 'wb') as f: f.write(DonateImg)
            img = tk.PhotoImage(file=DonatePath)
            if os.path.exists(DonatePath): os.remove(DonatePath)
            label = tk.Label(root, image=img)
            label.image = img
            label.pack()
            root.after(AfterTime, show)

        def open_calc():
            if not self.Var_Calc_State.get():
                self.Var_Calc_State.set(True)
                if self.Var_Listen_CalcDisplay_State.get():  # 打开计算器时，关闭监听热键
                    self.Var_Switch_Listen.set(False)
                    self.Listening.close_all_operates()  # 关闭所有操作
                    keyboard.unhook_all()  # 关闭监听热键
                self.CalcDisplay = CalcDisplay(
                    self.root, self.calc_info, self.Font, self.font_size,
                    self.InputFgColor, self.InputBgColor,
                    self.OutputFgColor, self.OutputBgColor,
                    self.CommandFgColor, self.CommandBgColor,
                    self.Var_Calc_State
                )
            else:
                try: self.CalcDisplay.root.focus_set()
                except Exception: pass

        self.Menu.add_command(label="设置", command=open_setting)
        self.Menu.add_command(label="说明", command=open_explain)
        self.Menu.add_command(label="赞赏开发者", command=open_donate)
        self.Menu.add_command(label="圣遗物计算", command=open_calc)


if __name__ == '__main__':
    if os.name != 'nt': exit_program(1)  # 非Windows系统
    if not os.path.exists(UniqueRunnerPath):  # 防止多开
        with open(UniqueRunnerPath, 'w') as f_: f_.write('')
    else: exit_program(2)
    if not os.path.exists(TempPath):
        with open(TempPath, 'w') as f_: f_.write('')
        E = Explain(None, (600, 300), "宋体", 13, None)
        E.root.wait_window()
    config_reader = ConfigReader(ConfigPath)
    _dict_ = config_reader.get()
    if not config_reader.check_config(): exit_program(4)
    display = Display(_dict_)
    display.run()

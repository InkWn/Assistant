# -*- coding: utf-8 -*-

import os
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from Resources import *


# 设置
class Settings:
    def __init__(
            self, root, info: tuple, font: str, font_size: int,
            bg: str, fg: str, modifiable: dict,
            # change_state: tk.BooleanVar, listen_start,
            kwargs: dict, config_dict: dict,
    ):
        """
        :param root: 父窗口
        :param info: 窗口信息
        :param font: 字体信息
        :param font_size: 字体大小
        :param bg: 背景颜色
        :param fg: 前景颜色
        :param modifiable: 可直接修改参数字典，根据里面的Var.set()修改
        # :param change_state: 用于传递关闭状态
        # :param listen_start: 开启监听
        :param kwargs: 功能函数
        :param config_dict: 配置字典
        """
        # 窗口
        self.root = tk.Toplevel(root)
        self.root.withdraw()
        self.root.after(100, self.root.deiconify)
        self.root.title('设置')
        with open(IconPath, 'wb') as f: f.write(ICO)
        self.root.iconbitmap(IconPath)
        if os.path.exists(IconPath): os.remove(IconPath)
        self.root.geometry("{0}x{1}+{2}+{3}".format(*info))
        self.root.resizable(False, False)
        self.root.minsize(400, 200)
        self.root.protocol("WM_DELETE_WINDOW", self.to_close)
        self.root.bind("<Tab>", lambda e: "break")  # 禁止Tab切换
        self.root.focus_set()
        # 参数
        self.Font, self.font_size = font, font_size
        self.Bg, self.Fg = bg, fg
        self.Info = info
        width, height = int(self.Info[0] * 0.7), int(self.Info[1] * 0.6)
        pos_x = (self.root.winfo_screenwidth() - width) // 2
        pos_y = (self.root.winfo_screenheight() - height) // 2
        self.InkWn_Info = (width, height, pos_x, pos_y)
        # 其他
        self.Kwargs = kwargs  # 部分参数
        self.ConfigDict = config_dict  # 配置
        self.OpenSetHotKey = False  # 是否打开了设置热键的窗口
        # 全部转换为str
        for key, value in self.ConfigDict.items():
            self.ConfigDict[key] = str(value)
        self.ModifiableDict = modifiable  # 可直接修改参数字典
        # 组件
        self.Menu = tk.Menu(self.root, tearoff=0)
        self.root["menu"] = self.Menu
        self.Canvas = tk.Canvas(self.root, highlightthickness=0, bg=self.Bg)
        self.Canvas.bind("<Configure>", lambda e: self.Canvas.configure(scrollregion=self.Canvas.bbox("all")))
        self.Canvas.bind_all("<MouseWheel>", self.wheel)
        self.Canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        Scroll = tk.Scrollbar(self.Canvas, width=16, orient=tk.VERTICAL, command=self.Canvas.yview)
        self.Canvas.configure(yscrollcommand=Scroll.set)
        Scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.FrameInfo = (self.Info[0] - 20, self.Info[1] * 2.6)  # Frame框大小，减去滚动条宽度和间距
        self.Frame = tk.Frame(self.Canvas, bg=self.Bg, width=self.FrameInfo[0], height=self.FrameInfo[1])
        for i in range(2): self.Frame.columnconfigure(i, weight=1)
        for i in range(22): self.Frame.rowconfigure(i, weight=1)
        self.Canvas.create_window(
            (3, 5), window=self.Frame, anchor=tk.NW,
            width=self.FrameInfo[0], height=self.FrameInfo[1]
        )  # 画布
        # 画线
        self.Canvas.create_line(0, 3, self.FrameInfo[0] + 3, 3, width=2, fill=self.Fg, dash=(4, 4))  # 顶部
        self.Canvas.create_line(0, 3, 0, self.FrameInfo[1] + 3, width=2, fill=self.Fg, dash=(4, 4))  # 左侧
        # 样式
        ttk.Style().configure("TMenubutton", font=(self.Font, self.font_size), background=bg, foreground=fg)
        ttk.Style().configure("TCheckbutton", font=(self.Font, self.font_size), background=bg, foreground=fg)
        # All_Frames，布局
        self.All_Frames = [tk.Frame(self.Frame, bg=self.Bg, relief="groove", borderwidth=2) for _ in range(36)]
        # 控件All_Entrys，用于收集参数
        self.All_Entrys = {
            "WinTitle": tk.Entry(self.All_Frames[1], font=(font, font_size), bg=bg, fg=fg, width=25),
            "WinSizeX": tk.Entry(self.All_Frames[2], font=(font, font_size), bg=bg, fg=fg, width=8),
            "WinSizeY": tk.Entry(self.All_Frames[3], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Font": tk.Entry(self.All_Frames[4], font=(font, font_size), bg=bg, fg=fg, width=8),
            "FontSize": tk.Entry(self.All_Frames[5], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Protect_Time": tk.Entry(self.All_Frames[7], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Move_SpeedX": tk.Entry(self.All_Frames[22], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Move_SpeedY": tk.Entry(self.All_Frames[23], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Click_Interval": tk.Entry(self.All_Frames[27], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Press_Short_Interval": tk.Entry(self.All_Frames[28], font=(font, font_size), bg=bg, fg=fg, width=8),
            "Press_Long_Duration": tk.Entry(self.All_Frames[29], font=(font, font_size), bg=bg, fg=fg, width=8),
        }
        # 变量，临时储存，用于显示参数
        self.TempVariables = {
            "OpenFrame": tk.StringVar(value=self.ConfigDict["OpenFrame"]),
            "Simplify_Show": tk.BooleanVar(value=self.ConfigDict["Simplify_Show"]),
            "Simplify_Layout": tk.StringVar(value=self.ConfigDict["Simplify_Layout"]),
            "Click_Button": tk.StringVar(value=self.ConfigDict["Click_Button"]),
            "Move_HotKey": tk.StringVar(value=self.ConfigDict["Move_HotKey"]),
            "Click_HotKey": tk.StringVar(value=self.ConfigDict["Click_HotKey"]),
            "Press_Short_HotKey": tk.StringVar(value=self.ConfigDict["Press_Short_HotKey"]),
            "Press_Long_HotKey": tk.StringVar(value=self.ConfigDict["Press_Long_HotKey"]),
            "Close_All_HotKey": tk.StringVar(value=self.ConfigDict["Close_All_HotKey"]),
            # 颜色
            "WinBg": tk.StringVar(value=self.ConfigDict["WinBg"]),
            "WinFg": tk.StringVar(value=self.ConfigDict["WinFg"]),
            "Simplify_Bg_Color": tk.StringVar(value=self.ConfigDict["Simplify_Bg_Color"]),
            "Simplify_Fg_Color": tk.StringVar(value=self.ConfigDict["Simplify_Fg_Color"]),
            "Command_Bg_Color": tk.StringVar(value=self.ConfigDict["Command_Bg_Color"]),
            "Command_Fg_Color": tk.StringVar(value=self.ConfigDict["Command_Fg_Color"]),
            "Input_Bg_Color": tk.StringVar(value=self.ConfigDict["Input_Bg_Color"]),
            "Input_Fg_Color": tk.StringVar(value=self.ConfigDict["Input_Fg_Color"]),
            "Output_Bg_Color": tk.StringVar(value=self.ConfigDict["Output_Bg_Color"]),
            "Output_Fg_Color": tk.StringVar(value=self.ConfigDict["Output_Fg_Color"]),
        }
        # 颜色的标签
        self.Colors_Label = {
            "Win": [
                tk.Label(
                    self.All_Frames[11], text="主窗口背景颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["WinBg"], fg=self.ConfigDict["WinFg"]),
                tk.Label(
                    self.All_Frames[12], text="主窗口字体颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["WinBg"], fg=self.ConfigDict["WinFg"]),
            ],
            "Command": [
                tk.Label(
                    self.All_Frames[13], text="提示框背景颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Command_Bg_Color"], fg=self.ConfigDict["Command_Fg_Color"]),
                tk.Label(
                    self.All_Frames[14], text="提示框字体颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Command_Bg_Color"], fg=self.ConfigDict["Command_Fg_Color"]),
            ],
            "Input": [
                tk.Label(
                    self.All_Frames[15], text="输入框背景颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Input_Bg_Color"], fg=self.ConfigDict["Input_Fg_Color"]),
                tk.Label(
                    self.All_Frames[16], text="输入框字体颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Input_Bg_Color"], fg=self.ConfigDict["Input_Fg_Color"]),
            ],
            "Output": [
                tk.Label(
                    self.All_Frames[17], text="输出框背景颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Output_Bg_Color"], fg=self.ConfigDict["Output_Fg_Color"]),
                tk.Label(
                    self.All_Frames[18], text="输出框字体颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Output_Bg_Color"], fg=self.ConfigDict["Output_Fg_Color"]),
            ],
            "Simplify": [
                tk.Label(
                    self.All_Frames[19], text="简化窗口背景颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Simplify_Bg_Color"], fg=self.ConfigDict["Simplify_Fg_Color"]),
                tk.Label(
                    self.All_Frames[20], text="简化窗口字体颜色", font=(self.Font, self.font_size),
                    bg=self.ConfigDict["Simplify_Bg_Color"], fg=self.ConfigDict["Simplify_Fg_Color"]),
            ],
        }
        # 颜色标签映射字典
        self.Color_Map = {
            "WinBg": "Win", "WinFg": "Win",
            "Command_Bg_Color": "Command", "Command_Fg_Color": "Command",
            "Input_Bg_Color": "Input", "Input_Fg_Color": "Input",
            "Output_Bg_Color": "Output", "Output_Fg_Color": "Output",
            "Simplify_Bg_Color": "Simplify", "Simplify_Fg_Color": "Simplify",
        }
        # 构建
        self.build_of_basic()
        self.build_of_color()
        self.build_of_functions()
        self.build_of_hotkey()
        self.build_of_menu()

    def build_of_basic(self):
        # ------------------------------frames[0]------------------------------
        tk.Label(
            self.All_Frames[0], text="基本项", bg=self.Bg, fg=self.Fg,
            font=(self.Font, self.font_size + 2)
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Frames[0]["relief"] = "flat"
        self.All_Frames[0].grid(row=0, column=0, sticky="nsew")
        # ------------------------------frames[1]------------------------------

        def f1():
            self.All_Entrys["WinTitle"].delete(0, tk.END)
            self.All_Entrys["WinTitle"].insert(0, self.ConfigDict["WinTitle"])

        tk.Label(
            self.All_Frames[1], text="窗口名称：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["WinTitle"].insert(0, self.ConfigDict["WinTitle"])
        self.All_Entrys["WinTitle"].pack(side=tk.LEFT, fill=tk.X)
        tk.Button(
            self.All_Frames[1], text="重置名称", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg, command=f1
        ).pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[1].grid(row=1, column=0, columnspan=2, sticky="nsew")
        # ------------------------------frames[2]------------------------------
        tk.Label(
            self.All_Frames[2], text="窗口宽度：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["WinSizeX"].insert(0, self.ConfigDict["WinSizeX"])
        self.All_Entrys["WinSizeX"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[2].grid(row=2, column=0, sticky="nsew")
        # ------------------------------frames[3]------------------------------
        tk.Label(
            self.All_Frames[3], text="窗口高度：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["WinSizeY"].insert(0, self.ConfigDict["WinSizeY"])
        self.All_Entrys["WinSizeY"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[3].grid(row=2, column=1, sticky="nsew")
        # ------------------------------frames[4]------------------------------
        tk.Label(
            self.All_Frames[4], text="字体样式：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["Font"].insert(0, self.ConfigDict["Font"])
        self.All_Entrys["Font"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[4].grid(row=3, column=0, sticky="nsew")
        # ------------------------------frames[5]------------------------------
        tk.Label(
            self.All_Frames[5], text="字体大小：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["FontSize"].insert(0, self.ConfigDict["FontSize"])
        self.All_Entrys["FontSize"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[5].grid(row=3, column=1, sticky="nsew")
        # ------------------------------frames[6]------------------------------

        def f2(v): self.TempVariables["OpenFrame"].set(v)

        tk.Label(
            self.All_Frames[6], text="初始显示页面", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        menu1 = tk.Menu(self.All_Frames[7], tearoff=0)
        menu1.add_command(label="鼠标专区", command=lambda: f2("鼠标专区"))
        menu1.add_command(label="键盘专区", command=lambda: f2("键盘专区"))
        menu1.add_command(label="其他工具", command=lambda: f2("其他工具"))
        ttk.Menubutton(
            self.All_Frames[6], menu=menu1, textvariable=self.TempVariables["OpenFrame"],
        ).pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[6].grid(row=4, column=0, sticky="nsew")
        # ------------------------------frames[7]------------------------------
        tk.Label(
            self.All_Frames[7], text="保护时间(秒)", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.All_Entrys["Protect_Time"].insert(0, self.ConfigDict["Protect_Time"])
        self.All_Entrys["Protect_Time"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[7].grid(row=4, column=1, sticky="nsew")
        # ------------------------------frames[8]------------------------------
        tk.Label(
            self.All_Frames[8], text="启动时显示简化窗口", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, padx=5)
        ttk.Checkbutton(
            self.All_Frames[8], variable=self.TempVariables["Simplify_Show"],
        ).pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[8].grid(row=5, column=0, sticky="nsew")
        # ------------------------------frames[9]------------------------------

        def f3(v): self.TempVariables["Simplify_Layout"].set(v)

        tk.Label(
            self.All_Frames[9], text="简化窗口布局", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        menu2 = tk.Menu(self.All_Frames[10], tearoff=0)
        menu2.add_command(label="布局-横", command=lambda: f3("布局-横"))
        menu2.add_command(label="布局-竖", command=lambda: f3("布局-竖"))
        ttk.Menubutton(
            self.All_Frames[9], menu=menu2, text="布局-横", textvariable=self.TempVariables["Simplify_Layout"],
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 5))
        self.All_Frames[9].grid(row=5, column=1, sticky="nsew")

    def build_of_color(self):
        def change_color(name: str, tempvar: str, ground: str):
            # ground: "bg" or "fg"
            color = colorchooser.askcolor(parent=self.root, title="选择颜色")[1]  # 获取16进制颜色值
            if color is not None:
                self.Colors_Label[name][0][ground] = color  # 改变背景颜色
                self.Colors_Label[name][1][ground] = color  # 改变字体颜色
                self.TempVariables[tempvar].set(color)

        # frames[10]大标签
        tk.Label(
            self.All_Frames[10], text="颜色设置", bg=self.Bg, fg=self.Fg,
            font=(self.Font, self.font_size + 2)
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Frames[10]["relief"] = "flat"
        self.All_Frames[10].grid(row=6, column=0, sticky="nsew")
        # 按钮对应的参数
        button_dict = {
            11: ("Win", "WinBg", "bg"),
            12: ("Win", "WinFg", "fg"),
            13: ("Command", "Command_Bg_Color", "bg"),
            14: ("Command", "Command_Fg_Color", "fg"),
            15: ("Input", "Input_Bg_Color", "bg"),
            16: ("Input", "Input_Fg_Color", "fg"),
            17: ("Output", "Output_Bg_Color", "bg"),
            18: ("Output", "Output_Fg_Color", "fg"),
            19: ("Simplify", "Simplify_Bg_Color", "bg"),
            20: ("Simplify", "Simplify_Fg_Color", "fg"),
        }
        # 标签布局
        for i in set(self.Color_Map.values()):
            self.Colors_Label[i][0].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.Colors_Label[i][1].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        # 按钮布局
        for i in button_dict:
            tk.Button(
                self.All_Frames[i], text="选择", font=(self.Font, self.font_size), relief="groove",
                bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
                command=lambda index=i: change_color(*button_dict[index])
            ).pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        # frames布局
        Column, Row = 0, 7
        for i in range(11, 21):
            self.All_Frames[i].grid(row=Row, column=Column, sticky="nsew")
            Column += 1
            if Column == 2:
                Column = 0
                Row += 1

    def build_of_functions(self):
        # ------------------------------frames[21]------------------------------
        tk.Label(
            self.All_Frames[21], text="功能项", bg=self.Bg, fg=self.Fg,
            font=(self.Font, self.font_size + 2)
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Frames[21]["relief"] = "flat"
        self.All_Frames[21].grid(row=12, column=0, sticky="nsew")
        # ------------------------------frames[22]------------------------------
        tk.Label(
            self.All_Frames[22], text="X轴移动速度：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Entrys["Move_SpeedX"].insert(0, self.ConfigDict["Move_SpeedX"])
        self.All_Entrys["Move_SpeedX"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[22].grid(row=13, column=0, sticky="nsew")
        # ------------------------------frames[23]------------------------------
        tk.Label(
            self.All_Frames[23], text="Y轴移动速度：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Entrys["Move_SpeedY"].insert(0, self.ConfigDict["Move_SpeedY"])
        self.All_Entrys["Move_SpeedY"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[23].grid(row=13, column=1, sticky="nsew")
        # ------------------------------frames[24]------------------------------

        def f1(v): self.TempVariables["Click_Button"].set(v)

        tk.Label(
            self.All_Frames[24], text="点击类型：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        menu = tk.Menu(self.All_Frames[24], tearoff=0)
        menu.add_command(label="左键", command=lambda: f1("左键"))
        menu.add_command(label="右键", command=lambda: f1("右键"))
        menu.add_command(label="中键", command=lambda: f1("中键"))
        ttk.Menubutton(
            self.All_Frames[24], menu=menu, textvariable=self.TempVariables["Click_Button"],
        ).pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[24].grid(row=14, column=0, sticky="nsew")
        # ------------------------------frames[27]------------------------------
        tk.Label(
            self.All_Frames[27], text="点击间隔：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Entrys["Click_Interval"].insert(0, self.ConfigDict["Click_Interval"])
        self.All_Entrys["Click_Interval"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[27].grid(row=14, column=1, sticky="nsew")
        # ------------------------------frames[28]------------------------------
        tk.Label(
            self.All_Frames[28], text="短按间隔：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Entrys["Press_Short_Interval"].insert(0, self.ConfigDict["Press_Short_Interval"])
        self.All_Entrys["Press_Short_Interval"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[28].grid(row=15, column=0, sticky="nsew")
        # ------------------------------frames[29]------------------------------
        tk.Label(
            self.All_Frames[29], text="长按持续时间：", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Entrys["Press_Long_Duration"].insert(0, self.ConfigDict["Press_Long_Duration"])
        self.All_Entrys["Press_Long_Duration"].pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))
        self.All_Frames[29].grid(row=15, column=1, sticky="nsew")

    def build_of_hotkey(self):
        # ------------------------------frames[30]------------------------------
        tk.Label(
            self.All_Frames[30], text="热键设置", bg=self.Bg, fg=self.Fg,
            font=(self.Font, self.font_size + 2)
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        self.All_Frames[30]["relief"] = "flat"
        self.All_Frames[30].grid(row=16, column=0, sticky="nsew")
        # ------------------------------frames[31]------------------------------
        tk.Label(
            self.All_Frames[31], text="移动热键 |", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        tk.Label(
            self.All_Frames[31], textvariable=self.TempVariables["Move_HotKey"],
            font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            self.All_Frames[31], text="|", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Button(
            self.All_Frames[31], text="设置", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
            command=lambda: self.set_hotkey("Move_HotKey")
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        self.All_Frames[31].grid(row=17, column=0, columnspan=2, sticky="nsew")
        # ------------------------------frames[32]------------------------------
        tk.Label(
            self.All_Frames[32], text="点击热键 |", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        tk.Label(
            self.All_Frames[32], textvariable=self.TempVariables["Click_HotKey"],
            font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            self.All_Frames[32], text="|", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Button(
            self.All_Frames[32], text="设置", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
            command=lambda: self.set_hotkey("Click_HotKey")
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        self.All_Frames[32].grid(row=18, column=0, columnspan=2, sticky="nsew")
        # ------------------------------frames[33]------------------------------
        tk.Label(
            self.All_Frames[33], text="短按热键 |", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        tk.Label(
            self.All_Frames[33], textvariable=self.TempVariables["Press_Short_HotKey"],
            font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            self.All_Frames[33], text="|", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Button(
            self.All_Frames[33], text="设置", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
            command=lambda: self.set_hotkey("Press_Short_HotKey")
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        self.All_Frames[33].grid(row=19, column=0, columnspan=2, sticky="nsew")
        # ------------------------------frames[34]------------------------------
        tk.Label(
            self.All_Frames[34], text="长按热键 |", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        tk.Label(
            self.All_Frames[34], textvariable=self.TempVariables["Press_Long_HotKey"],
            font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            self.All_Frames[34], text="|", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Button(
            self.All_Frames[34], text="设置", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
            command=lambda: self.set_hotkey("Press_Long_HotKey")
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        self.All_Frames[34].grid(row=20, column=0, columnspan=2, sticky="nsew")
        # ------------------------------frames[35]------------------------------
        tk.Label(
            self.All_Frames[35], text="关闭所有操作热键 |", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        tk.Label(
            self.All_Frames[35], textvariable=self.TempVariables["Close_All_HotKey"],
            font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            self.All_Frames[35], text="|", font=(self.Font, self.font_size), bg=self.Bg, fg=self.Fg,
        ).pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Button(
            self.All_Frames[35], text="设置", font=(self.Font, self.font_size), relief="groove",
            bg=self.Bg, fg=self.Fg, activebackground=self.Bg, activeforeground=self.Fg,
            command=lambda: self.set_hotkey("Close_All_HotKey")
        ).pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        self.All_Frames[35].grid(row=21, column=0, columnspan=2, sticky="nsew")

    def build_of_menu(self):
        self.Menu.add_command(label="保存并退出", command=self.to_save)
        self.Menu.add_command(label="重置参数", command=self.to_reset)
        self.Menu.add_command(label="直接退出", command=lambda: self.to_close(True))

    # 设置热键
    def set_hotkey(self, type1: str):
        History_Specials = set()  # 历史特殊键
        TempVar = tk.StringVar(value=self.TempVariables[type1].get())  # 临时热键变量

        def hook(event):
            if event.event_type == "down":
                if event.name in SpecialKeys:  # 此时按下的为特殊键，如[down]ctrl
                    History_Specials.add(event.name)  # 记录特殊键
                if {event.name} == History_Specials: TempVar.set(event.name)  # 输入键与历史键一致
                else:
                    if not History_Specials: TempVar.set(event.name)  # 单键
                    else:
                        if event.name in SpecialKeys:  # 特殊键组合, 如shift+ctrl
                            TempVar.set("+".join(History_Specials))
                        else:  # 特殊键+单键组合, 如shift+a
                            TempVar.set("+".join(History_Specials) + "+" + event.name)

            elif event.event_type == "up":
                if event.name in SpecialKeys:  # 此时松开的为特殊键，如[up]ctrl
                    History_Specials.discard(event.name)  # 移除特殊键

        def enter():
            get_hotkey = TempVar.get()
            dic = {
                "Move_HotKey": self.TempVariables["Move_HotKey"],
                "Click_HotKey": self.TempVariables["Click_HotKey"],
                "Press_Short_HotKey": self.TempVariables["Press_Short_HotKey"],
                "Press_Long_HotKey": self.TempVariables["Press_Long_HotKey"],
                "Close_All_HotKey": self.TempVariables["Close_All_HotKey"]
            }
            if not get_hotkey:  # 输入为空
                messagebox.showerror("错误", "热键不能为空", parent=InkWn)
                return
            if type1 in ("Move_HotKey", "Click_HotKey", "Close_All_HotKey"):  # Move和Click和Close_All的热键只能为单键或组合键
                if len(get_hotkey.split("+")) == 1 and get_hotkey in SpecialKeys:  # get_hotkey为特殊键的单键
                    messagebox.showerror("错误", "该热键只能为单键或组合键，如r，f1，ctrl+r", parent=InkWn)
                    return
                if all(k in SpecialKeys for k in get_hotkey.split("+")):  # get_hotkey全部为特殊键
                    messagebox.showerror("错误", "该热键不能全由特殊键组成", parent=InkWn)
                    return
                # 加一个判断，特殊键不能与短按和长按的特殊键冲突
                get_special = [s for s in get_hotkey.split("+") if s in SpecialKeys]  # 提取特殊键
                if get_special == dic["Press_Short_HotKey"].get().split("+"):
                    messagebox.showerror("错误", "特殊键与短按的热键冲突", parent=InkWn)
                    return
                elif get_special == dic["Press_Long_HotKey"].get().split("+"):
                    messagebox.showerror("错误", "特殊键与长按的热键冲突", parent=InkWn)
                    return
            elif type1 in ("Press_Short_HotKey", "Press_Long_HotKey"):  # 长按和短按的热键只能为特殊键
                if not all(_ in SpecialKeys for _ in get_hotkey.split("+")):  # get_hotkey中有非特殊键
                    messagebox.showerror("错误", "该热键只能为特殊键，如ctrl，shift+ctrl等", parent=InkWn)
                    return
            for t, v in dic.items():
                if t != type1:  # 排除当前热键
                    if v.get() == get_hotkey:  # 热键冲突
                        messagebox.showerror("错误", "当前热键与其他热键冲突", parent=InkWn)
                        return
            self.TempVariables[type1].set(get_hotkey)
            close_set_hotkey()

        def close_set_hotkey():
            self.OpenSetHotKey = False
            keyboard.unhook_all()
            InkWn.destroy()

        if self.OpenSetHotKey: return  # 窗口已打开
        self.OpenSetHotKey = True
        InkWn = tk.Toplevel()
        InkWn.overrideredirect(True)
        InkWn.geometry("{0}x{1}+{2}+{3}".format(*self.InkWn_Info))
        InkWn.attributes("-topmost", True)
        # 开始监听热键
        keyboard.unhook_all()
        keyboard.hook(hook)
        tk.Label(
            InkWn, textvariable=TempVar, font=(self.Font, self.font_size), bg="yellow", fg="black",
        ).pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)
        tk.Button(
            InkWn, text="确定", font=(self.Font, self.font_size), relief="groove", command=enter
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        tk.Button(
            InkWn, text="取消", font=(self.Font, self.font_size), relief="groove", command=close_set_hotkey
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=5)
        InkWn.focus_set()

    def wheel(self, event):
        # 如果窗口存在，则滚动
        if self.root.winfo_exists():
            self.Canvas.yview_scroll(int(-(event.delta / 60)), "units")

    # 检查参数
    def check_config(self) -> bool:
        Error = False  # 是否有错误参数
        # 检查输入框每一项
        for name, value in self.All_Entrys.items():
            # 转换类型
            if Param_Ranges[name]["type"] is int:  # 整数
                try:
                    value = int(value.get())
                    # 提取最小值和最大值
                    min_value, max_value = Param_Ranges[name]["min"], Param_Ranges[name]["max"]
                    # 如果最大值或最小值不为None，则检查范围
                    if min_value is not None and value < min_value or max_value is not None and value > max_value:
                        self.All_Entrys[name]["bg"] = "red"
                        Error = True
                    else: self.All_Entrys[name]["bg"] = self.Bg  # 输入正确，恢复默认颜色
                except ValueError:  # 输入不是数字
                    self.All_Entrys[name]["bg"] = "red"
                    Error = True
            elif Param_Ranges[name]["type"] is float:  # 浮点数
                try:
                    value = float(value.get())
                    # 提取最小值和最大值
                    min_value, max_value = Param_Ranges[name]["min"], Param_Ranges[name]["max"]
                    # 如果最大值或最小值不为None，则检查范围
                    if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                        self.All_Entrys[name]["bg"] = "red"
                        Error = True
                    else: self.All_Entrys[name]["bg"] = self.Bg  # 输入正确，恢复默认颜色
                except ValueError:  # 输入不是数字
                    self.All_Entrys[name]["bg"] = "red"
                    Error = True
        if Error: return False
        return True  # 参数没问题

    # 保存
    def to_save(self) -> bool:
        if not self.check_config(): return False
        for name, entry in self.All_Entrys.items():
            self.ConfigDict[name] = entry.get()
        for name, var in self.TempVariables.items():
            self.ConfigDict[name] = str(var.get())
        for name, var in self.ModifiableDict.items():
            get = self.ConfigDict[name]
            try:
                if '.' in get: get = float(get)
                else: get = int(get)
            except Exception: pass
            self.ModifiableDict[name].set(get)
        # 清空配置文件
        with open(ConfigPath, "w", encoding="utf-8") as f:
            f.seek(0)
            f.truncate()
        # 写入配置
        f = open(ConfigPath, "a", encoding="utf-8")
        for key, value in self.ConfigDict.items():
            f.write(f"[{key}]{value}\n")
        f.close()
        self.to_close(True)
        return True

    # 重置
    def to_reset(self):
        if messagebox.askyesno("提示", "是否重置设置？", parent=self.root, default='no'):
            for name, value in self.ConfigDict.items():
                if name in self.All_Entrys.keys():
                    self.All_Entrys[name].delete(0, tk.END)
                    self.All_Entrys[name].insert(0, value)
                    self.All_Entrys[name]["bg"] = self.Bg
                elif name in self.TempVariables.keys():
                    self.TempVariables[name].set(value)  # 改变临时变量的值
                    if name in self.Color_Map.keys():  # 颜色标签
                        index = self.Color_Map[name]
                        if "Bg" in name:  # 背景色
                            self.Colors_Label[index][0]["bg"] = value
                            self.Colors_Label[index][1]["bg"] = value
                        elif "Fg" in name:  # 字体色
                            self.Colors_Label[index][0]["fg"] = value
                            self.Colors_Label[index][1]["fg"] = value

    # 关闭
    def to_close(self, skip: bool = False):
        # skip：是否直接关闭，不检查参数是否有更改
        if not skip:
            for name, value in self.ConfigDict.items():
                if name in self.All_Entrys.keys():  # 键匹配
                    get = self.All_Entrys[name].get()
                    if get != value:
                        break  # 更改过
                elif name in self.TempVariables.keys():
                    get = self.TempVariables[name].get()
                    if type(get) is bool:  # 布尔值
                        get = str(get)
                    if get != value:
                        break  # 更改过
            else:  # 全部没有被更改过，直接关闭
                self.Kwargs["change_state"].set(False)
                self.Kwargs["listen_start"]()
                self.root.destroy()
                return
            if messagebox.askyesno("提示", "是否保存设置？", parent=self.root, default='yes'):
                if not self.to_save(): return  # 参数有问题，不保存且不退出
        self.Kwargs["change_state"].set(False)
        self.Kwargs["listen_start"]()
        self.root.destroy()


# 说明
class Explain:
    def __init__(self, root, info: tuple, font: str, font_size: int, change_state: tk.BooleanVar):
        if root is not None:
            self.root = tk.Toplevel(root)
        else:
            self.root = tk.Tk()
            width, height = info[0], info[1]
            pos_x = (self.root.winfo_screenwidth() - width) // 2
            pos_y = (self.root.winfo_screenheight() - height) // 2 - 50
            info = (width, height, pos_x, pos_y)

        if change_state is not None: self.ChangeState = change_state
        else: self.ChangeState = None
        self.root.title('说明')
        self.root.geometry("{0}x{1}+{2}+{3}".format(*info))
        self.root.attributes("-toolwindow", True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.focus_set()
        self.FontInfo = [font, font_size]
        frame01 = tk.Frame(self.root)
        frame01.pack(side=tk.TOP, fill=tk.X)
        frame02 = tk.Frame(self.root)
        frame02.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_font_plus = tk.Button(frame01, text="字体+", font=self.FontInfo, command=self.plus)
        self.button_font_plus.pack(side=tk.LEFT)
        self.button_font_minus = tk.Button(frame01, text="字体-", font=self.FontInfo, command=self.minus)
        self.button_font_minus.pack(side=tk.LEFT)
        self.text = tk.Text(frame02, font=self.FontInfo)
        self.text.insert(tk.END, ExplainText)
        self.text.tag_config("sel", background="#EDEDED", foreground="black")
        self.text.tag_config("red", foreground="red")
        self.text.tag_add("red", "6.3", "6.end")
        self.text["state"] = tk.DISABLED
        self.text.pack(fill=tk.BOTH, expand=True)

    def plus(self):
        if self.FontInfo[1] <= 30:
            self.FontInfo[1] += 2
        self.text["font"] = self.FontInfo
        self.button_font_plus["font"] = self.FontInfo
        self.button_font_minus["font"] = self.FontInfo

    def minus(self):
        if self.FontInfo[1] >= 12:
            self.FontInfo[1] -= 2
        self.text["font"] = self.FontInfo
        self.button_font_plus["font"] = self.FontInfo
        self.button_font_minus["font"] = self.FontInfo

    def close(self):
        if self.ChangeState is not None: self.ChangeState.set(False)
        self.root.destroy()


# 圣遗物计算器
class CalcDisplay:
    def __init__(
            self, root, info: tuple,
            font: str, font_size: int,
            input_fg_color: str, input_bg_color: str,
            output_fg_color: str, output_bg_color: str,
            command_fg_color: str, command_bg_color: str,
            change_state: tk.BooleanVar
    ):
        self.ChangeState = change_state
        self.root = tk.Toplevel(root)
        self.root.title('圣遗物计算')
        self.root.geometry("{0}x{1}+{2}+{3}".format(*info))
        with open(IconPath, 'wb') as f: f.write(ICO)
        self.root.iconbitmap(IconPath)
        if os.path.exists(IconPath): os.remove(IconPath)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.focus_set()

        self.Font, self.font_size = font, font_size
        self.InputFgColor, self.InputBgColor = input_fg_color, input_bg_color
        self.OutputFgColor, self.OutputBgColor = output_fg_color, output_bg_color
        self.CommandFgColor, self.CommandBgColor = command_fg_color, command_bg_color

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=3)

        self.block01()
        self.block02()
        self.block03()

    def close(self):
        self.ChangeState.set(False)
        self.root.destroy()

    # 处理输入
    def process_input(self, content: str) -> str:
        try: type_, number = content.split('-', 1)
        except ValueError: return "E1-格式错误"
        if not type_ or not number: return "E2-不能为空"
        try: number = float(number)
        except ValueError: return "E3-数值错误"
        if type_ in ("3", "7", "8", "9"):
            index = int(type_) - 1
            remainder = 0
        elif type_ in ("1", "2", "4", "5", "6"):
            index = int(type_) - 1
            remainder = 1
        else: return "E4-类型错误"
        calclist = CalcList[index]
        if number > calclist[1] * 6: return "E5-数值过大"
        elif number <= 2.6: return "E6-数值过小"  # 因为2.7是所有参数中的最小值，所以弄个2.6杠杠的
        elif number == round(calclist[1] * 6, remainder): return f"{calclist[1]:.2f}[4] " * 6
        elif number <= calclist[1] + 0.05:
            for num in calclist:
                if round(num, remainder) == number:
                    return f"{num:.2f}[{5 - calclist.index(num)}]"
            return "E7-数值不存在"
        response = self.calc(target=number, remainder=remainder, calclist=calclist)
        if not response: return "E7-数值不存在"
        return response

    @staticmethod
    def calc(target: int | float, remainder: int, calclist: tuple | list) -> str:
        for k in range(1, 5):
            num1 = calclist[k]
            for i in range(1, 5):
                for u in range(5):
                    for g in range(5):
                        for d in range(5):
                            for r in range(5):
                                num2 = calclist[i]
                                num3 = calclist[u]
                                num4 = calclist[g]
                                num5 = calclist[d]
                                num6 = calclist[r]
                                if round((num1 + num2 + num3 + num4 + num5 + num6), remainder) == target:
                                    combination = [
                                        f"{num1:.2f}[{5 - calclist.index(num1)}]",
                                        f"{num2:.2f}[{5 - calclist.index(num2)}]",
                                    ]
                                    if num3 != 0: combination.append(f"{num3:.2f}[{5 - calclist.index(num3)}]")
                                    if num4 != 0: combination.append(f"{num4:.2f}[{5 - calclist.index(num4)}]")
                                    if num5 != 0: combination.append(f"{num5:.2f}[{5 - calclist.index(num5)}]")
                                    if num6 != 0: combination.append(f"{num6:.2f}[{5 - calclist.index(num6)}]")
                                    return " ".join(combination)
        return ""

    def block01(self):
        Frame = tk.Frame(self.root)
        Frame.grid(column=0, row=0, sticky='nsew')
        Text = tk.Text(
            Frame, font=(self.Font, self.font_size),
            bg=self.CommandBgColor, fg=self.CommandFgColor,
            width=1, height=1,
        )
        Text.insert(tk.END, CommandText1)
        Text.bind("<KeyPress>", lambda e: "break")
        Text.bind("<Control-c>", lambda e: Text.event_generate("<<Copy>>"))
        Text.pack(fill=tk.BOTH, expand=True)

    def block02(self):
        Frame = tk.Frame(self.root)
        Frame.grid(column=1, row=0, sticky='nsew')
        Text = tk.Text(
            Frame, font=(self.Font, self.font_size),
            bg=self.CommandBgColor, fg=self.CommandFgColor,
            width=1, height=1,
        )
        Text.insert(tk.END, CommandText2)
        Text.bind("<KeyPress>", lambda e: "break")
        Text.bind("<Control-c>", lambda e: Text.event_generate("<<Copy>>"))
        Text.pack(fill=tk.BOTH, expand=True)

    def block03(self):
        Frame = tk.Frame(self.root)
        Frame.grid(column=0, row=1, columnspan=2, sticky='nsew')
        HistoryInput = []
        InputIndex = 0
        OutputIndex = 1

        def f1(event):
            nonlocal InputIndex
            content = EntryInput.get()
            if len(content) < 3: EntryInput.insert(0, ">>>")
            if event.keysym == "Return":
                EntryHistory.delete(0, 'end')
                EntryHistory.insert(0, f"Last Input: [{content[3::]}]")
                nonlocal OutputIndex
                InputIndex = 0
                EntryInput.delete(0, 'end')
                EntryInput.insert(0, ">>>")
                if content[3::]: HistoryInput.append(content[3::])
                if content[3::] in ["cc", "clear", "cls"]:
                    ListboxOutput.delete(0, 'end')
                    OutputIndex = 1
                    return "break"
                elif content[3::] in ["exit", "E!"]:
                    self.close()
                    return "break"
                elif content[3::] in ["Top", "TP"]:
                    self.root.attributes("-topmost", True)
                    ListboxOutput.insert(tk.END, f"[{OutputIndex:02d}]: 已置顶\n")
                    ListboxOutput.yview_moveto(1)
                    OutputIndex += 1
                    return "break"
                elif content[3::] in ["CancelTop", "CT"]:
                    self.root.attributes("-topmost", False)
                    ListboxOutput.insert(tk.END, f"[{OutputIndex:02d}]: 取消置顶\n")
                    ListboxOutput.yview_moveto(1)
                    OutputIndex += 1
                    return "break"
                response = self.process_input(content[3::])
                ListboxOutput.insert(tk.END, f"[{OutputIndex:02d}]: {response}\n")
                if response[0] == "E":  # 错误信息
                    ListboxOutput.itemconfig(tk.END, fg="red")
                ListboxOutput.yview_moveto(1)
                OutputIndex += 1

            elif event.keysym == "BackSpace":
                if len(content) <= 3: return "break"

            elif event.keysym == "Up":
                if HistoryInput:
                    if InputIndex < len(HistoryInput): InputIndex += 1
                    EntryInput.delete(0, 'end')
                    EntryInput.insert(0, f">>>{HistoryInput[-InputIndex]}")

            elif event.keysym == "Down":
                if HistoryInput:
                    if InputIndex > 1: InputIndex -= 1
                    EntryInput.delete(0, 'end')
                    EntryInput.insert(0, f">>>{HistoryInput[-InputIndex]}")

            elif event.keysym == "Prior":
                try: type_, num = content[3::].split("-", 1)
                except Exception: return "break"
                if not num: return "break"
                for _ in num:
                    if _ not in "1234567890.": return "break"
                try:
                    if "." in num: num = round(float(num) + 0.1, 1)
                    else: num = int(num) + 1
                except Exception: return "break"
                EntryInput.delete(0, 'end')
                EntryInput.insert(0, f">>>{type_}-{num}")

            elif event.keysym == "Next":
                try: type_, num = content[3::].split("-", 1)
                except Exception: return "break"
                if not num: return "break"
                for _ in num:
                    if _ not in "1234567890.": return "break"
                try:
                    if "." in num: num = max(round(float(num) - 0.1, 1), 0)
                    else: num = max(int(num) - 1, 0)
                except Exception: return "break"
                EntryInput.delete(0, 'end')
                EntryInput.insert(0, f">>>{type_}-{num}")

        frame = tk.Frame(Frame)
        frame.pack(side=tk.TOP, fill=tk.X)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        EntryInput = tk.Entry(
            frame, font=(self.Font, self.font_size),
            bg=self.InputBgColor, fg=self.InputFgColor,
            width=1
        )
        EntryInput['insertbackground'] = 'white'
        EntryInput.insert(0, ">>>")
        EntryInput.bind("<Key>", f1)
        EntryInput.focus_set()
        EntryInput.bind("<Control-space>", lambda e: "break")
        EntryInput.grid(column=0, row=0, sticky='nsew')

        EntryHistory = tk.Entry(
            frame, font=(self.Font, self.font_size),
            bg=self.InputBgColor, fg=self.InputFgColor,
            width=1
        )
        EntryHistory.bind("<KeyPress>", lambda e: "break")
        EntryHistory.bind("<Control-c>", lambda e: EntryHistory.event_generate("<<Copy>>"))
        EntryHistory.insert(0, "Last Input: ")
        EntryHistory.grid(column=1, row=0, sticky='nsew')

        ListboxOutput = tk.Listbox(
            Frame, font=(self.Font, self.font_size),
            bg=self.OutputBgColor, fg=self.OutputFgColor,
            width=1, height=1,
            selectbackground=self.OutputBgColor,
            activestyle="none",
            highlightthickness=0,
        )
        ListboxOutput.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ListboxOutput.insert(tk.END, f"[Info]: {Info}\n")
        ListboxOutput.bind("<KeyPress>", lambda e: "break")
        ListboxOutput.bind("<Control-c>", lambda e: ListboxOutput.event_generate("<<Copy>>"))


# 简化显示器
class SimplifyDisplay:
    def __init__(
            self, root,
            font: str, font_size: int,
            bg: str = "SystemButtonFace", fg: str = "black",
            layout: str = "布局-横"
    ):
        # 窗口
        self.root = tk.Toplevel(root)
        self.root.geometry("+0+0")
        self.root.attributes("-topmost", True)  # 置顶
        self.root.overrideredirect(True)  # 无边框
        self.root.wm_attributes('-transparentcolor', 'SystemButtonFace')  # 透明背景
        # 常量与变量
        self.Fg = fg
        if bg == "None": self.Bg = "SystemButtonFace"
        else: self.Bg = bg
        self.Font, self.font_size = font, font_size
        self.clickX, self.clickY = 0, 0  # 鼠标位置
        if layout not in ("布局-横", "布局-竖"): layout = "布局-横"
        self.layout = layout  # 布局格式
        # 窗口组件
        self.Label_State = [
            tk.Label(self.root, text="■", font=(self.Font, self.font_size), fg="white", bg=self.Bg)
            for _ in range(4)
        ]
        self.Label_Content = [
            tk.Label(self.root, text=_, font=(self.Font, self.font_size), fg=self.Fg, bg=self.Bg,)
            for i, _ in {1: "移动状态", 2: "点击状态", 3: "短按状态", 4: "长按状态"}.items()
        ]
        # 构建
        self.build_of_move()
        self.build_of_simplify()

    def change_fg(self, idx: int, fg: str = "white"):
        self.Label_State[idx]["fg"] = fg

    def change_layout(self, layout: str):
        self.layout = layout
        for i in range(4):
            self.Label_Content[i].grid_forget()
            self.Label_State[i].grid_forget()
        self.build_of_simplify()

    def build_of_move(self):
        def click(event):
            self.clickX, self.clickY = event.x, event.y

        def move_(event):
            new_x = self.root.winfo_x() + event.x - self.clickX
            new_y = self.root.winfo_y() + event.y - self.clickY
            self.root.geometry(f'+{new_x}+{new_y}')

        Label_Move = tk.Label(
            self.root, text='Move', bg="black", fg="white",
            font=(self.Font, self.font_size), cursor='fleur'
        )
        Label_Move.grid(column=0, row=0, columnspan=2, sticky='nsew')
        Label_Move.bind('<ButtonPress-1>', click)
        Label_Move.bind('<B1-Motion>', move_)

    def build_of_simplify(self):
        if self.layout == "布局-竖":  # 垂直布局
            for i in range(4):
                self.Label_Content[i].grid(column=0, row=i + 1)
                self.Label_State[i].grid(column=1, row=i + 1)
        else:  # 水平布局
            for i in range(4):
                self.Label_Content[i].grid(column=2 * i + 2, row=0)
                self.Label_State[i].grid(column=2 * i + 3, row=0)

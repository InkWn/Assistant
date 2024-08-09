# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk


Interval_Int: int = 10  # 滚轮 加减 整型间隔
Interval_Float: float = 0.1  # 滚轮 加减 浮点型间隔


class FrameMouse(tk.Frame):
    def __init__(self, master, winbg: str, winfg: str, font: str, font_size: int, variables: dict):
        super().__init__(master)
        self.WinBg, self.WinFg, = winbg, winfg
        self.Font, self.font_size = font, font_size
        self.Variables = variables
        # 初始化
        self['bg'] = self.WinBg
        self.columnconfigure(0, weight=1)
        for i in range(2): self.rowconfigure(i, weight=1)
        # 移动Frame
        self.FrameMove = tk.Frame(self, bg=winbg, relief="ridge")
        for i in range(3): self.FrameMove.columnconfigure(i, weight=1)
        self.FrameMove.rowconfigure(0, weight=1)
        self.FrameMove.grid(row=0, column=0, sticky="nsew", pady=2)
        # 点击Frame
        self.FrameClick = tk.Frame(self, bg=winbg, relief="ridge")
        for i in range(3): self.FrameClick.columnconfigure(i, weight=1)
        self.FrameClick.rowconfigure(0, weight=1)
        self.FrameClick.grid(row=1, column=0, sticky="nsew")
        # 构建
        self.build_of_move()
        self.build_of_click()

    @staticmethod
    def rool(event, var, idx):
        num = var.get()
        if idx == 1:  # 鼠标移动
            if event.delta > 0: var.set(num + Interval_Int)
            elif event.delta < 0: var.set(num - Interval_Int)
        elif idx == 2:  # 鼠标点击
            if event.delta > 0: var.set(round(var.get() + Interval_Float, 3))
            elif event.delta < 0 and num > 0.1: var.set(round(num - Interval_Float, 3))

    # 创建Frame
    def create_frame(self, master, column: int, row: int):
        fe = tk.Frame(master, bg=self.WinBg, width=1, height=1, relief="groove", borderwidth=3)
        fe.grid(column=column, row=row, sticky="nsew")
        fe.columnconfigure(0, weight=1)
        for i in range(3): fe.rowconfigure(i, weight=1)
        return fe

    def build_of_move(self):
        FrameTitle = self.create_frame(self.FrameMove, 0, 0)  # 标签
        FrameValue = self.create_frame(self.FrameMove, 1, 0)  # 值
        FrameUnit = self.create_frame(self.FrameMove, 2, 0)  # 单位
        # 标签
        for i, text in enumerate(("X轴移动速度：", "Y轴移动速度：", "热键：")):
            tk.Label(
                FrameTitle, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))
        # 值
        for i, text in enumerate(("Var_SpeedX", "Var_SpeedY")):
            Label_Speed = tk.Label(
                FrameValue, textvariable=self.Variables[text],
                font=(self.Font, self.font_size),
                bg=self.WinBg, fg=self.WinFg, relief='sunken'
            )
            Label_Speed.bind("<MouseWheel>", lambda e, t=text: self.rool(e, self.Variables[t], 1))
            Label_Speed.grid(column=0, row=i, sticky='nsew')
        tk.Label(
            FrameValue, textvariable=self.Variables["Var_Move_HotKey"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        ).grid(column=0, row=2, sticky='nsew', pady=(3, 0))
        # 单位
        for i, text in enumerate(("像素/0.1s", "像素/0.1s", "键")):
            tk.Label(
                FrameUnit, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))

    def build_of_click(self):
        FrameTitle = self.create_frame(self.FrameClick, 0, 0)  # 标签
        FrameValue = self.create_frame(self.FrameClick, 1, 0)  # 值
        FrameUnit = self.create_frame(self.FrameClick, 2, 0)  # 单位
        # ------------------------------标签------------------------------
        for i, text in enumerate(("点击类型：", "点击间隔：", "热键：")):
            tk.Label(
                FrameTitle, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))
        # ------------------------------值------------------------------
        menu = tk.Menu(FrameValue, tearoff=0)
        menu.add_command(label="左键", command=lambda: self.Variables["Var_Click_Button"].set("左键"))
        menu.add_command(label="右键", command=lambda: self.Variables["Var_Click_Button"].set("右键"))
        menu.add_command(label="中键", command=lambda: self.Variables["Var_Click_Button"].set("中键"))
        ttk.Style().configure(
            "TMenubutton", font=(self.Font, self.font_size), background=self.WinBg, foreground=self.WinFg
        )
        ttk.Menubutton(
            FrameValue, menu=menu, textvariable=self.Variables["Var_Click_Button"],
        ).grid(column=0, row=0, sticky='nsew')
        Label_Interval = tk.Label(
            FrameValue, textvariable=self.Variables["Var_Click_Interval"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        )
        Label_Interval.bind("<MouseWheel>", lambda e: self.rool(e, self.Variables["Var_Click_Interval"], 2))
        Label_Interval.grid(column=0, row=1, sticky='nsew')
        tk.Label(
            FrameValue, textvariable=self.Variables["Var_Click_HotKey"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        ).grid(column=0, row=2, sticky='nsew')
        # ------------------------------单位------------------------------
        for i, text in enumerate((" 类型", "秒", "键")):
            tk.Label(
                FrameUnit, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))


class FrameKeyboard(tk.Frame):
    def __init__(self, master, winbg: str, winfg: str, font: str, font_size: int, variables: dict):
        super().__init__(master)
        self.WinBg, self.WinFg, = winbg, winfg
        self.Font, self.font_size = font, font_size
        self.Variables = variables
        self['bg'] = self.WinBg
        self.columnconfigure(0, weight=1)
        for i in range(2): self.rowconfigure(i, weight=1)
        # 短按
        self.FrameShort = tk.Frame(self, bg=winbg, relief="ridge", borderwidth=1)
        for i in range(3): self.FrameShort.columnconfigure(i, weight=1)
        for i in range(2): self.FrameShort.rowconfigure(i, weight=1)
        self.FrameShort.grid(row=0, column=0, sticky="nsew")
        # 长按
        self.FrameLong = tk.Frame(self, bg=winbg, relief="ridge", borderwidth=1)
        for i in range(3): self.FrameLong.columnconfigure(i, weight=1)
        self.FrameLong.rowconfigure(0, weight=1)
        self.FrameLong.grid(row=1, column=0, sticky="nsew")
        # 构建
        self.build_of_short()
        self.build_of_long()

    @staticmethod
    def rool(event, var, idx):
        num = var.get()
        if idx == 1:  # 最小值不为0
            if event.delta > 0:  var.set(round(num + Interval_Float, 3))
            elif event.delta < 0 and num > 0.1: var.set(round(num - Interval_Float, 3))
        elif idx == 2:  # 最小值为0
            if event.delta > 0: var.set(round(num + Interval_Float, 3))
            elif event.delta < 0 and num >= 0.1: var.set(round(num - Interval_Float, 3))

    # 创建Frame
    def create_frame(self, master, column: int, row: int, rowspan: int):
        fe = tk.Frame(master, bg=self.WinBg, width=1, height=1, relief="groove", borderwidth=3)
        fe.grid(column=column, row=row, rowspan=rowspan, sticky="nsew")
        fe.columnconfigure(0, weight=1)
        for i in range(2): fe.rowconfigure(i, weight=1)
        return fe

    def build_of_short(self):
        tk.Label(
            self.FrameShort, text=f"短按，例：[{self.Variables['Var_Press_Short_HotKey'].get()}+e]：连点e键",
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg,
        ).grid(column=0, row=0, columnspan=3, sticky='nsew')
        FrameTitle = self.create_frame(self.FrameShort, 0, 1, 2)  # 标签
        FrameValue = self.create_frame(self.FrameShort, 1, 1, 2)  # 值
        FrameUnit = self.create_frame(self.FrameShort, 2, 1, 2)  # 单位
        # 标签
        for i, text in enumerate(("间隔：", "热键：")):
            tk.Label(
                FrameTitle, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))
        # 值
        Label_Interval = tk.Label(
            FrameValue, textvariable=self.Variables["Var_Press_Short_Interval"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        )
        Label_Interval.grid(column=0, row=0, sticky='nsew')
        Label_Interval.bind("<MouseWheel>", lambda e: self.rool(e, self.Variables["Var_Press_Short_Interval"], 1))
        tk.Label(
            FrameValue, textvariable=self.Variables["Var_Press_Short_HotKey"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        ).grid(column=0, row=1, sticky='nsew')
        # 单位
        for i, text in enumerate(("秒", "键")):
            tk.Label(
                FrameUnit, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))

    def build_of_long(self):
        tk.Label(
            self.FrameLong, text=f"长按，例：[{self.Variables['Var_Press_Long_HotKey'].get()}+w]：按住w键",
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg,
        ).grid(column=0, row=0, columnspan=3, sticky='nsew')
        FrameTitle = self.create_frame(self.FrameLong, 0, 1, 1)  # 标签
        FrameValue = self.create_frame(self.FrameLong, 1, 1, 1)  # 值
        FrameUnit = self.create_frame(self.FrameLong, 2, 1, 1)  # 单位
        # 标签
        for i, text in enumerate(("持续时间：", "热键：")):
            tk.Label(
                FrameTitle, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))
        # 值
        Label_Duration = tk.Label(
            FrameValue, textvariable=self.Variables["Var_Press_Long_Duration"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        )
        Label_Duration.grid(column=0, row=0, sticky='nsew')
        Label_Duration.bind("<MouseWheel>", lambda e: self.rool(e, self.Variables["Var_Press_Long_Duration"], 2))
        tk.Label(
            FrameValue, textvariable=self.Variables["Var_Press_Long_HotKey"],
            font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief='sunken'
        ).grid(column=0, row=1, sticky='nsew')
        # 单位
        for i, text in enumerate(("秒", "键")):
            tk.Label(
                FrameUnit, text=text, font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            ).grid(column=0, row=i, sticky='nsew', pady=(3, 0))


class FrameOther(tk.Frame):
    def __init__(
            self, master, winbg: str, winfg: str,
            font: str, font_size: int,
            component: dict, functions: dict, variables: dict,
    ):
        super().__init__(master)
        self.master = master  # 主窗口
        self.Component = component  # 组件
        self.Functions = functions  # 功能
        self.Variables = variables  # 变量
        self.WinBg, self.WinFg = winbg, winfg
        self.Font, self.font_size = font, font_size
        # 变量
        self.Var_TopMost = tk.BooleanVar(value=False)  # 窗口置顶
        self.Var_Show_Simplify = tk.BooleanVar(value=self.Variables["Simplify_Show"])  # 简化窗口
        self.Var_Scale_Int = tk.IntVar(value=10)  # 整数型滚轮加减量
        self.Var_Scale_Float = tk.DoubleVar(value=0.1)  # 浮点型滚轮加减量
        self.Var_Simplify_Layout = tk.StringVar()  # 简化窗口布局
        layout = self.Component["Win_Simplify"].layout
        if layout == "布局-横": self.Var_Simplify_Layout.set("布局-横")
        elif layout == "布局-竖": self.Var_Simplify_Layout.set("布局-竖")
        # 外观
        self['bg'] = winbg
        ttk.Style().configure("TCheckbutton", font=(font, font_size), background=winbg, foreground=winfg)
        ttk.Style().configure("TScale", font=(font, font_size), background=winbg, foreground=winfg)
        ttk.Style().configure("TButton", font=(font, font_size - 2), background=winbg, foreground=winfg)
        ttk.Style().configure("TMemubutton", font=(font, font_size), background=winbg, foreground=winfg)
        # 构建
        self.build_of_other()

    # 窗口置顶
    def top_most(self):
        if self.Var_TopMost.get(): self.master.attributes("-topmost", True)
        else: self.master.attributes("-topmost", False)

    # 显示简化窗口
    def show_simplify(self):
        try:
            if self.Var_Show_Simplify.get(): self.Component["Win_Simplify"].root.deiconify()
            else: self.Component["Win_Simplify"].root.withdraw()
        except Exception: pass

    # 开关监听
    def switch_listen(self):
        if self.Variables["Var_Switch_Listen"].get(): self.Functions["listen_hotkey"]()
        else: self.Functions["unlisten_hotkey"]()

    def build_of_other(self):
        self.columnconfigure(0, weight=1)
        for i in range(6): self.rowconfigure(i, weight=1)
        frames = [tk.Frame(self, bg=self.master['bg'], relief="groove", borderwidth=2) for _ in range(7)]
        for i in range(6):
            frames[i].grid(column=0, row=i, sticky="nsew")
            frames[i].rowconfigure(0, weight=1)
        # -----------------------------------

        def change_layout(value):
            self.Var_Simplify_Layout.set(value)
            self.Functions["simplify_change_layout"](value)

        frames[0].columnconfigure(0, weight=4)
        frames[0].columnconfigure(1, weight=2)
        frames[0].columnconfigure(2, weight=4)
        frames[0].columnconfigure(3, weight=1)
        frames[0].columnconfigure(4, weight=6)
        check01 = ttk.Checkbutton(
            frames[0], text="窗口置顶", variable=self.Var_TopMost, command=self.top_most
        )
        check01.bind("<space>", lambda e: "break")  # 防止按空格时触发
        check01.grid(column=0, row=0, sticky="nsew", padx=(5, 0))
        tk.Label(
            frames[0], text="||", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=1, row=0)
        check02 = ttk.Checkbutton(
            frames[0], text="简化窗口", variable=self.Var_Show_Simplify, command=self.show_simplify
        )
        check02.bind("<space>", lambda e: "break")
        check02.grid(column=2, row=0, sticky="nse")
        tk.Label(
            frames[0], text="|", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
         ).grid(column=3, row=0, padx=(5, 0))
        menu = tk.Menu(frames[0], tearoff=0)
        menu.add_command(label="布局-横", command=lambda: change_layout("布局-横"))
        menu.add_command(label="布局-竖", command=lambda: change_layout("布局-竖"))
        ttk.Menubutton(
            frames[0], menu=menu, textvariable=self.Var_Simplify_Layout
        ).grid(column=4, row=0, sticky="nsw")
        # -----------------------------------
        for i in range(3): frames[1].columnconfigure(i, weight=1)
        check03 = ttk.Checkbutton(
            frames[1], text="开启热键监听", variable=self.Variables['Var_Switch_Listen'], command=self.switch_listen
        )
        check03.bind("<space>", lambda e: "break")
        check03.grid(column=0, row=0, padx=5, sticky="nsew")
        tk.Label(
            frames[1], text="|", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=1, row=0)
        check04 = ttk.Checkbutton(
            frames[1], text="使用计算器时关闭监听", variable=self.Variables["Var_Listen_CalcDisplay_State"],
        )
        check04.bind("<space>", lambda e: "break")
        check04.grid(column=2, row=0, padx=5, sticky="nsew")
        # -----------------------------------
        for i in range(4): frames[2].columnconfigure(i, weight=1)
        tk.Button(
            frames[2], text="关闭所有操作", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            relief="solid", borderwidth=1, command=self.Functions["close_all_operates"],
            activebackground=self.WinBg, activeforeground=self.WinFg,
        ).grid(column=0, row=0, padx=(5, 0), sticky="nsew")
        tk.Label(
            frames[2], text="|", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=1, row=0)
        tk.Label(
            frames[2], text="热键:", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=2, row=0, padx=(0, 5), sticky="nse")
        tk.Label(
            frames[2], textvariable=self.Variables["Var_Close_All_Operates_HotKey"],
            font=(self.Font, self.font_size), width=10,
            bg=self.WinBg, fg=self.WinFg, relief='groove', borderwidth=3,
        ).grid(column=3, row=0, sticky="nsw")
        # -----------------------------------

        def change_scale_1(value):
            global Interval_Int
            num = int(value.split(".")[0])
            # 个位数大于5进1，小于舍去
            if num % 10 > 5: num += (10 - num % 10)
            else: num -= num % 10
            self.Var_Scale_Int.set(num)
            Interval_Int = self.Var_Scale_Int.get()

        frames[3].columnconfigure(0, weight=3)
        frames[3].columnconfigure(1, weight=2)
        frames[3].columnconfigure(2, weight=1)
        tk.Label(
            frames[3], text="整数型滚轮加减量", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=0, row=0, padx=(5, 0), sticky="nsew")
        ttk.Scale(
            frames[3], from_=10, to=100, variable=self.Var_Scale_Int, command=lambda x: change_scale_1(x)
        ).grid(column=1, row=0, sticky="nsw")
        tk.Label(
            frames[3], textvariable=self.Var_Scale_Int,
            font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            relief='ridge', borderwidth=2, width=6
        ).grid(column=2, row=0, sticky="nsw")
        # -----------------------------------

        def change_scale_2(value):
            global Interval_Float
            num = round(float(value), 1)
            self.Var_Scale_Float.set(num)
            Interval_Float = self.Var_Scale_Float.get()

        frames[4].columnconfigure(0, weight=3)
        frames[4].columnconfigure(1, weight=2)
        frames[4].columnconfigure(2, weight=1)
        tk.Label(
            frames[4], text="浮点型滚轮加减量", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=0, row=0, padx=(5, 0), sticky="nsew")
        ttk.Scale(
            frames[4], from_=0.1, to=1.0, variable=self.Var_Scale_Float, command=lambda x: change_scale_2(x)
        ).grid(column=1, row=0, sticky="nsw")
        tk.Label(
            frames[4], textvariable=self.Var_Scale_Float,
            font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg,
            relief='ridge', borderwidth=2, width=6
        ).grid(column=2, row=0, sticky="nsw")
        # -----------------------------------
        for i in range(7): frames[5].columnconfigure(i, weight=1)
        check05 = ttk.Checkbutton(
            frames[5], text="保护模式", variable=self.Variables["Var_Protect_Timer"],
            command=self.Functions["start_protect"],
        )
        check05.bind("<space>", lambda e: "break")
        check05.grid(column=0, row=0, padx=(5, 0), sticky="nsew")
        tk.Label(
            frames[5], text="|", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=1, row=0)
        tk.Label(
            frames[5], text="剩余时间:", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=2, row=0)
        tk.Label(
            frames[5], textvariable=self.Variables["Var_Surplus_Time"],
            font=(self.Font, self.font_size), width=6,
            bg=self.WinBg, fg=self.WinFg, relief='ridge', borderwidth=2
        ).grid(column=3, row=0, sticky="nsw")
        tk.Label(
            frames[5], text="秒", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=4, row=0, padx=(5, 0), sticky="nsew")
        tk.Label(
            frames[5], text="|", font=(self.Font, self.font_size), bg=self.WinBg, fg=self.WinFg
        ).grid(column=5, row=0)
        tk.Button(
            frames[5], text="重置时间", font=(self.Font, self.font_size),
            bg=self.WinBg, fg=self.WinFg, relief="solid", borderwidth=1,
            activebackground=self.WinBg, activeforeground=self.WinFg,
            command=lambda: self.Variables["Var_Surplus_Time"].set(self.Variables["Var_Protect_Time"].get()),
        ).grid(column=6, row=0, padx=5, sticky="nsew")

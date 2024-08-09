# -*- coding: utf-8 -*-

import ctypes
User32 = ctypes.windll.user32


class MouseEvents:
    def __init__(self):
        # 鼠标事件
        self.MouseEvents = User32.mouse_event
        self.MouseEvents.argtypes = (ctypes.c_ulong, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_ulong)
        self._down_ = {'left': 0x02, 'right': 0x08, 'middle': 0x20}
        self._up_ = {'left': 0x04, 'right': 0x10, 'middle': 0x40}

    def move(self, x: int, y: int):
        self.MouseEvents(0x01, x, y, 0, 0)

    def click(self, button: str):
        self.MouseEvents(self._down_.get(button, 0x02), 0, 0, 0, 0)
        self.MouseEvents(self._up_.get(button, 0x04), 0, 0, 0, 0)


class KeyboardEvents:
    def __init__(self):
        # 键盘事件
        self.keybd = User32.keybd_event
        self.keybd.argtypes = (ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
        self.keybd.restype = ctypes.c_uint
        # 特殊键码
        self.SpecialKeys = {
            "shift": 0x10, "ctrl": 0x11, "control": 0x11, "alt": 0x12, "enter": 0x0D, "backspace": 0x08,
            "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
        }
        # 历史按键
        self.history = set()

    # 转为虚拟键码
    def convert(self, key: str) -> int | None:
        if len(key) == 1:
            key_code = ord(key.upper())
            self.history.add(key_code)
            return key_code
        key_code = self.SpecialKeys.get(key.lower(), None)
        if key_code is not None: self.history.add(key_code)
        return key_code

    # 短按按键
    def press(self, key: str):
        if (key := self.convert(key)) is not None:
            self.keybd(key, 0, 0x0000, 0)
            self.keybd(key, 0, 0x0002, 0)

    # 按住按键
    def hold(self, key: str):
        if (key := self.convert(key)) is not None:
            self.keybd(key, 0, 0x0000, 0)

    # 释放按键
    def release(self, key: str):
        if (key := self.convert(key)) is not None:
            self.keybd(key, 0, 0x0002, 0)

    # 释放所有历史按键
    def stop_all(self):
        for key in self.history:
            self.keybd(key, 0, 0x0002, 0)

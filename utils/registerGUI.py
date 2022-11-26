#!/bin/bash/python3
# _*_ coding: utf-8 _*_


"""
此处的代码主要是用来进行界面创建的s
"""

from tkinter import *
import tkinter.messagebox


class RegisterMain:
    """注册界面类"""

    def __init__(self, title="授权信息", version=None, auth="ccplayer"):
        self.root = Tk()  # 生成一个窗口对象
        self.title = title
        self.version = version
        self.auth = auth
        self.root.title("%s-%s by %s" % (self.title, self.version, self.auth))  # 设置窗口名称
        # self.root.iconbitmap('G:\\Python Project\\spiderM3U8\\img\\spider.ico') # 设置窗口图标
        self.w = 350
        self.h = 200

        Label(self.root, text='请将[机器码]发送给管理员换取[注册码]', font=("Lucida Grande", 11)).grid(padx=30, pady=10)

        frame1 = Frame(self.root)
        Label(frame1, text='机器码:  ').grid(row=0, column=0)

        # register1 = register.Register()
        # ma1 = register1.getCombinNumber()  # 获得本机机器码，并将其显示在界面上
        self.jiqma_s = ""
        # 文本框控件https://blog.csdn.net/qq_41556318/article/details/85112829
        self.jiqma = Text(frame1, width=30, height='2')
        self.jiqma.insert('insert', self.jiqma_s)  # 添加信息
        self.jiqma.grid(row=0, column=1)
        self.jiqma.config(state=DISABLED)  # 机器码不可编辑

        frame2 = Frame(self.root)
        Label(frame2, text='注册码:  ').grid(row=0, column=0)

        self.message_s = ""
        # 文本框控件https://blog.csdn.net/qq_41556318/article/details/85112829
        self.message = Text(frame2, width=30, height='4')
        self.message.insert('insert', self.message_s)  # 添加信息
        # self.message.pack(side='left', fill='y')            #pack布局，显示在最左侧
        self.message.grid(row=0, column=1)

        frame1.grid(padx=20)
        frame2.grid(pady=10)

        # 定义按钮控件（显示在容器self.frm中）https://blog.csdn.net/qq_41556318/article/details/85080617
        self.button_start = Button(self.root, text="激活注册", width=12, font=("Lucida Grande", 11))
        self.button_start.place(x=120, y=160)

        # 令此程序的窗口居中显示https://blog.csdn.net/yql_617540298/article/details/101427313
        ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # 获取本地电脑屏幕的大小
        self.root.geometry(
            '%dx%d+%d+%d' % (self.w, self.h, (ws / 2) - (self.w / 2), (hs / 2) - (self.h / 2)))  # 使得程序窗口居中显示
        self.root.resizable(0, 0)  # 限制此程序窗口更改其大小
        # self.root.mainloop()

    # 该函数用来在文本框上显示文字等信息，多行显示
    def alert(self, m):
        print("%s" % m)
        if m:
            self.jiqma.config(state=NORMAL)  # state=NORMAL可以修改文本框中的内容（响应键盘和鼠标事件）
            self.jiqma.insert(END, m)  # 在末尾添加换行符
            # 确保scrollbar在底部
            self.jiqma.see(END)  # 滚动内容，确保 index 指定的位置可见
            self.jiqma.config(state=DISABLED)  # state=DISABLED无法修改文本框中内容
        self.root.update()  # 用于更新窗口，使添加的内容不断刷新显示

    # 用来清空文本框上的文字内容
    def clear_alert(self):
        self.message.config(state=NORMAL)
        self.message.delete('1.0', 'end')  # 用于删除文本框所有内容
        self.message.config(state=DISABLED)
        self.root.update()  # 更新窗口

    def show_info(self, m):
        tkinter.messagebox.showinfo(self.title, m)  # 显示提示框，用于提示信息

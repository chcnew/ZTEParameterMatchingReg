#!/bin/bash/python3
# _*_ coding: utf-8 _*_


import base64
import os.path
import sys
import time

import wmi
from pyDes import *

from utils import mainGUI
from utils import registerGUI
from utils.variables import BASE_DIR

rgGUI = None

yxtime = ""  # 有效期

Des_key = "cc158854"  # Key,需八位
Des_IV = "\x11\2\x2a\3\1\x27\2\0"  # 自定IV向量
# Date_Time = "2021-07-20 00:01:22"  # 定义截止日期

# 获取硬件信息，输出macode
# 1、CPU序列号（ID）  2、本地连接 无线局域网 以太网的MAC  3.硬盘序列号（唯一） 4.主板序列号（唯一）
s = wmi.WMI()


# cpu序列号
def get_CPU_info():
    cpu = []
    cp = s.Win32_Processor()
    for u in cp:
        cpu.append(
            {
                "Name": u.Name,
                "Serial Number": u.ProcessorId,
                "CoreNum": u.NumberOfCores
            }
        )
    return cpu


# 硬盘序列号
def get_disk_info():
    disk = []
    for pd in s.Win32_DiskDrive():
        disk.append(
            {
                "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(),  # 获取硬盘序列号，调用另外一个win32 API
                "ID": pd.deviceid,
                "Caption": pd.Caption,
                "size": str(int(float(pd.Size) / 1024 / 1024 / 1024))
            }
        )
    return disk


# mac地址（包括虚拟机的）
def get_network_info():
    network = []
    for nw in s.Win32_NetworkAdapterConfiguration():
        if nw.MacAddress != None:
            network.append(
                {
                    "MAC": nw.MacAddress,
                    "ip": nw.IPAddress
                }
            )
    return network


# 主板序列号
def get_mainboard_info():
    mainboard = []
    for board_id in s.Win32_BaseBoard():
        mainboard.append(board_id.SerialNumber.strip().strip('.'))
    return mainboard


# 由于机器码框太长，故选取机器码字符串部分字符（此处获得机器码用于传给管理员）
def getCombinNumber():
    a = get_network_info()
    b = get_CPU_info()
    c = get_disk_info()
    d = get_mainboard_info()
    machinecode_str = ""
    machinecode_str = machinecode_str + a[0]['MAC'] + b[0]['Serial Number'] + c[0]['Serial'] + d[0]
    # print(machinecode_str)
    selectIndex = [8, 10, 15, 16, 17, 30, 32, 38, 43, 46]
    macode = ""
    for i in selectIndex:
        macode = macode + machinecode_str[i]
        # print(machinecode_str[i])
    return macode


# 合并得到授权码（包含机器码和日期）
def get_ComMacdate():
    Date_Time = input('请输入限定时间【格式=2031-07-22 00:07:22】：')
    macDateCode = getCombinNumber() + Date_Time
    return macDateCode


# DES+base64加密机器码+授权时间
def Encryted(tr):
    k = des(Des_key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)
    EncryptStr = k.encrypt(tr)
    return base64.b32encode(EncryptStr)  # 转base64编码返回


# base64+DES解密机器码+授权时间
def Dncryted(EncryptStr):
    bas1 = base64.b32decode(EncryptStr)  # 先对加密后的对象解密
    k = des(Des_key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)
    tr = k.decrypt(bas1)
    return tr


# 从加密后的授权码中将日期解析出来（传入字符串即可，里面自动转换成bytes类型，好用于解码）
def jiexi_datetime(jiami_macDateCode):
    # 对从注册文件中的进行还原成bytes类型
    jiami_macDateCode = bytes(jiami_macDateCode, encoding='utf-8')
    # print(jiami_macDateCode)
    # 将解密得到机器码+日期
    try:
        jiemi_macDateCode = Dncryted(jiami_macDateCode)
    except:
        return None
    # print('jiemi_macDateCode',jiemi_macDateCode)
    jiemi_macDateCode = str(jiemi_macDateCode).replace("b'", '').replace("'", '')  # 将授权码变成字符串

    maccode = getCombinNumber()  # 获得本机的机器码
    maccode = str(maccode).replace("b'", '').replace("'", '')  # 将机器码变成字符串
    # print('本机机器码',maccode)             :001B6AXH8
    # 如果本机机器码在授权码中
    if maccode in jiemi_macDateCode:
        Datetime = jiemi_macDateCode.replace(maccode, '')  # 将机器码替换就得到日期了
    else:
        return None
    return Datetime  # 2018-10-26 00:00:00


# 判断当前日期是否过于有效截止期
def check_time(Datetime):
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if nowtime > Datetime:
        # print("已过期，无法正常使用")
        return False
    else:
        # print("未过期，可正常使用")
        return True


# 用于检查验证注册信息的唯一及有效日期
def checkAuthor():
    global rgGUI
    global yxtime
    try:
        with open(os.path.join(BASE_DIR, "register.txt"), 'r') as f:  # 无此文件时会报错，直接返回False
            key = f.read()  # 读取所有信息
    except:
        return False

    key = key.strip()  # 去除换行符的影响
    print(key)
    # print(type(key))
    datetime = jiexi_datetime(key)  # 对key的内容解析，解析成功不是None，说明是本机唯一验证码，接下来就是判断有效期了
    if not datetime:
        print("非本机注册码，无效")
        return False
    else:
        if check_time(datetime):
            print("已激活，可正常使用")
            yxtime = datetime  # 获得截止日期
            return True
        else:
            print("已过期，无法使用")
            return False


# 用于点击按钮进行注册（即保存注册信息）
def regis():
    global rgGUI
    global yxtime
    key = rgGUI.message.get('0.0', 'end')  # 获取text中的全部内容
    print(key)

    # 读写文件要加判断(将内容写入注册文件中)
    with open(os.path.join(BASE_DIR, "register.txt"), 'w') as f:
        f.write(key)

    # 注册信息后立即进行验证
    if checkAuthor():
        rgGUI.root.destroy()  # 销毁窗口并进入下一环节
        # 进入主界面
        maingui = mainGUI.MainGUI()
        maingui.yxqL['text'] = "有效期截止到：" + yxtime
        maingui.root.mainloop()
    else:
        # 验证失败返回到注册界面
        return


# 显示注册窗口
def show_reg():
    ma1 = getCombinNumber()  # 获得本机机器码，并将其显示在界面上:001B6AXH8
    global rgGUI
    rgGUI = registerGUI.RegisterMain(version="1.0")  # 创建界面窗口对象（包含窗口及其各个控件）
    rgGUI.button_start.bind("<Button-1>", lambda x: regis())  # 点击注册
    rgGUI.alert(ma1)  # 将机器码显示在窗口界面
    # 手动加入消息队列
    rgGUI.root.mainloop()  # 不断刷新窗口，使其显示b'3T6RJFINXWUI4VWKQTNCX2MKCU======'机器码（:001B6AXH8）


def run():
    global yxtime
    # 最开始启动先身份验证，若成功则进入下一个窗口,失败则进行窗口显示
    if checkAuthor():
        # 进入主界面
        maingui = mainGUI.MainGUI()
        maingui.yxqL['text'] = "有效期截止到：" + yxtime
        maingui.root.mainloop()
        return
    else:
        show_reg()  # 显示注册窗口
        rgGUI.root.protocol("WM_DELETE_WINDOW", sys.exit(0))


if __name__ == '__main__':
    run()
    print(get_disk_info())
    print(get_network_info())
    print(get_mainboard_info())
    print(getCombinNumber())  # 此为此程序自动获得的机器码，使用下方的加密功能（注册机）即可得到注册码进行注册

    # 加密解密机器码测试
    jiami = Encryted(get_ComMacdate())
    print('生成的授权码：', jiami)
    jiemi = Dncryted(jiami)
    print('解密：', jiemi)

    # 下方对加密解密授权码测试（机器码+授权日期）
    jiami = Encryted(get_ComMacdate())
    print('jiami', jiami)  # b'3T6RJFINXWUI4BYVRLDGTMYL4MCJZR2PJIJORPQKWGGRNDZMZDPA===='
    jiemi = Dncryted(jiami)
    print('jiemi', jiemi)  # b':001B6AXH82018-10-26 00:00:00'
    jietime = jiexi_datetime(jiami)  # 可以得到解密的日期
    print('jietime', jietime)
    check_time(jietime)  # 检查日期
    regist()
    checkAuthored()

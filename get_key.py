#!/bin/bash/python3
# _*_ coding: utf-8 _*_


from utils.register import get_ComMacdate, Encryted

jiami = Encryted(get_ComMacdate())
print('生成的授权码：', jiami)

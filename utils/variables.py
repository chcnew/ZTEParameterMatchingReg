#!/bin/bash/python3
# _*_ coding: utf-8 _*_

"""
设置全局变量
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # 项目根目录
IN_DATAfile_DIR = os.path.join(BASE_DIR, "data_all", "in_datafiles")
OUT_DATAfile_DIR = os.path.join(BASE_DIR, "data_all", "out_datafiles")

if __name__ == '__main__':
    print(BASE_DIR)
    print(IN_DATAfile_DIR)
    print(OUT_DATAfile_DIR)

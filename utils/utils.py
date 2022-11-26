#!/bin/bash/python3
# _*_ coding: utf-8 _*_
import os
import json


class Tool(object):
    """工具类"""

    @staticmethod
    def data_processing(file_name):
        """
        excel转换json, json转换dict

        :param file_name: 文件名
        """
        f_json = open(file_name, 'r', encoding='utf-8')
        j_dict = json.load(f_json)
        del j_dict["TemplateInfo"]
        del j_dict["Index"]
        return j_dict

    @staticmethod
    def df_replace(aa_series, x, y):
        """
        列表元素替换字符

        :param aa_series: series列
        :param x: 被替换字符
        :param y: 替换字符
        """
        aa_series = [i_aa.replace(x, y) for i_aa in aa_series]
        return aa_series

    @staticmethod
    def df_split(bb_series, a, b):
        """
        二维列表，取第一个元素，组成新列表

        :param bb_series: 列表
        :param a:
        :param b:
        :return:
        """
        bb_series = [i_bb.split(a, b)[0] for i_bb in bb_series]
        return bb_series

    @staticmethod
    def ret_path(*args):
        """路径拼接"""
        return os.path.join(*args)

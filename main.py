#!/bin/bash/python3
# _*_ coding: utf-8 _*_

import gc
import json
import re
import time

import pandas as pd

from utils.utils import Tool
from utils.register import run
from utils.variables import BASE_DIR, IN_DATAfile_DIR, OUT_DATAfile_DIR

# 注册程序
run()

if True:
    # 第一部分：ENB-CI-measCfgIdx-thresholdOfRSRP-eventId
    # 记录开始运行的当前时间
    start = time.perf_counter()  # 程序运行起始时间

    tool = Tool()
    dict_TDD1 = tool.data_processing(tool.ret_path(IN_DATAfile_DIR, 'ICMDATA-TDD1.json'))
    dict_TDD2 = tool.data_processing(tool.ret_path(IN_DATAfile_DIR, 'ICMDATA-TDD2.json'))
    dict_FDD1 = tool.data_processing(tool.ret_path(IN_DATAfile_DIR, 'ICMDATA-FDD1.json'))
    dict_FDD2 = tool.data_processing(tool.ret_path(IN_DATAfile_DIR, 'ICMDATA-FDD2.json'))
    TDD_keys = list(dict_TDD1.keys())
    FDD_keys = list(dict_FDD1.keys())

    # print(TDD_keys)
    # EUtranCellTDD
    # PrachTDD
    # PowerControlULTDD
    # PowerControlDLTDD
    # ECellEquipmentFunctionTDD
    # EUtranReselectionTDD
    # UeEUtranMeasurementTDD
    # CellMeasGroupTDD
    # EUtranCellMeasurementTDD
    # ENBFunctionTDD
    # VoLTEConfigCellTDD
    # UeTimer
    # GlobleSwitchInformation
    # ControlPlaneTimerTDD

    # 全局变量声明
    # TDD
    global Df_EUtranCellTDD
    global Df_PrachTDD
    global Df_PowerControlULTDD
    global Df_PowerControlDLTDD
    global Df_ECellEquipmentFunctionTDD
    global Df_EUtranReselectionTDD
    global Df_UeEUtranMeasurementTDD
    global Df_CellMeasGroupTDD
    global Df_EUtranCellMeasurementTDD
    global Df_ENBFunctionTDD
    global Df_VoLTEConfigCellTDD
    global Df_UeTimerTDD
    global Df_GlobleSwitchInformationTDD
    global ControlPlaneTimer
    # FDD
    global Df_FDD_EUtranCellTDD
    global Df_FDD_PrachTDD
    global Df_FDD_PowerControlULTDD
    global Df_FDD_PowerControlDLTDD
    global Df_FDD_ECellEquipmentFunctionTDD
    global Df_FDD_EUtranReselectionTDD
    global Df_FDD_UeEUtranMeasurementTDD
    global Df_FDD_CellMeasGroupTDD
    global Df_FDD_EUtranCellMeasurementTDD
    global Df_FDD_ENBFunctionTDD
    global Df_FDD_VoLTEConfigCellTDD
    global Df_FDD_UeTimerTDD
    global Df_FDD_GlobleSwitchInformationTDD
    global ControlPlaneTimerTDD

    # DataFrame TDD汇总
    for key in TDD_keys:
        globals()['Df_' + key] = pd.concat([pd.DataFrame(dict_TDD1[key]), pd.DataFrame(dict_TDD2[key])], axis=0)
    # DataFrame FDD汇总
    for key in FDD_keys:
        globals()['Df_FDD_' + key] = pd.concat([pd.DataFrame(dict_FDD1[key]), pd.DataFrame(dict_FDD2[key])], axis=0)

    # FDD整理每个表的表头且合并
    for key1, key2 in zip(TDD_keys, FDD_keys):
        globals()['Df_FDD_' + key1] = globals()['Df_FDD_' + key2]
        globals()['Df_FDD_' + key1].columns = globals()['Df_' + key1].columns.values.tolist()
        globals()['Df_' + key1] = pd.concat([globals()['Df_' + key1], globals()['Df_FDD_' + key1]], axis=0)
        # 行索引重置
        globals()['Df_' + key1] = globals()['Df_' + key1].reset_index()
        # 删除多余变量 释放内存
        del globals()['Df_FDD_' + key1]
        del globals()['Df_FDD_' + key2]
    gc.collect()

    # 第一部分：小区对应切换事件
    # 合并出ENB-CI
    Df_EUtranCellMeasurementTDD['ENB-CI'] = Df_EUtranCellMeasurementTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_EUtranCellMeasurementTDD['description'], 'cellLocalId=', '')
    # V出 inteFHOMeasCfg 配置号列表
    Df_EUtranCellMeasurementTDD = pd.merge(Df_EUtranCellMeasurementTDD, Df_CellMeasGroupTDD.loc[:, ['MOI', 'interFHOMeasCfg']], how='left', left_on='refCellMeasGroupTDD', right_on='MOI')
    # ;替换为,
    Df_EUtranCellMeasurementTDD['eutranMeasParas_interCarriFreq'] = tool.df_replace(Df_EUtranCellMeasurementTDD['eutranMeasParas_interCarriFreq'], ';', ',')
    Df_EUtranCellMeasurementTDD['interFHOMeasCfg'] = tool.df_replace(Df_EUtranCellMeasurementTDD['interFHOMeasCfg'], ';', ',')
    # 测量频点、测量配置号存为二维列表 [[a,b],[c,d]]
    ew_lst_eu = [i_aa.split(',') for i_aa in Df_EUtranCellMeasurementTDD['eutranMeasParas_interCarriFreq']]
    ew_lst_in = [i_bb.split(',') for i_bb in Df_EUtranCellMeasurementTDD['interFHOMeasCfg']]

    # 获取每个表格测量频点长度存为列表
    len_lst = [len(x_a) for x_a in ew_lst_eu]

    # 匹配每个表格号列表，清除多余未互操作的配置号
    ew_lst_in = [ew_lst_in[x_b][:len_lst[x_b]] for x_b in range(len(ew_lst_in))]

    # 每个配置号改为ENB&配置号
    lst_enb = [x_c for x_c in Df_EUtranCellMeasurementTDD['ENBFunctionTDD']]
    num_aa = 0
    for x_d in ew_lst_in:
        for x_e in range(len(x_d)):
            x_d[x_e] = lst_enb[num_aa] + '-' + x_d[x_e]
        num_aa = num_aa + 1
    # ew_lst_in 已经变为ENB&配置号  [[1,2],[3,4]]

    # EUtranCellMeasurementTDD中ENB&配置号作为一列添加
    Df_EUtranCellMeasurementTDD['ENBpzh'] = ew_lst_in
    Df_EUtranCellMeasurementTDD['ENBpzh'] = [','.join(s_aa) for s_aa in Df_EUtranCellMeasurementTDD['ENBpzh']]

    # UeEUtranMeasurementTDD中ENB&配置号作为str的和作为新的一列
    Df_UeEUtranMeasurementTDD['ENBpzh'] = Df_UeEUtranMeasurementTDD['ENBFunctionTDD'] + '-' + Df_UeEUtranMeasurementTDD['measCfgIdx']
    # print(Df_UeEUtranMeasurementTDD.shape[0])  # 行数test
    # Df_UeEUtranMeasurementTDD以'ENBpzh'列去重，否则会出现行数增多错误
    Df_UeEUtranMeasurementTDD.drop_duplicates(subset=['ENBpzh'], keep='first', inplace=True)
    # print(Df_UeEUtranMeasurementTDD.shape[0])  # 行数test

    # 分列 序号0，1，2...
    Df_New = Df_EUtranCellMeasurementTDD['ENBpzh'].str.split(',', expand=True)
    ls = Df_New.shape[1]  # 列数

    # 分别插入2列空列且命名索引，再V出门限和事件
    loa = 1
    num_bb = 0
    while loa <= ls * 3:
        # V事件及门限
        Df_New = pd.merge(Df_New, Df_UeEUtranMeasurementTDD.loc[:, ['ENBpzh', 'eventId', 'thresholdOfRSRP']], how='left', left_on=num_bb, right_on='ENBpzh').drop('ENBpzh', axis=1)
        # 插入替换、位置调整
        Df_New.insert(loa, str(num_bb) + '列门限', Df_New.pop('thresholdOfRSRP'))
        Df_New.insert(loa, str(num_bb) + '列事件' + '\n' + 'long:0:A1,1:A2,2:A3,3:A4,4:A5,5:A6;default:0', Df_New.pop('eventId'))
        num_bb = num_bb + 1
        loa = loa + 3

    # 处理Df_EUtranCellMeasurementTDD
    Df_CellMeasGroupTDD['A1:ENBpzh'] = Df_CellMeasGroupTDD['ENBFunctionTDD'] + '-' + tool.df_split(Df_CellMeasGroupTDD['closedInterFMeasCfg'], ';', 1)
    Df_CellMeasGroupTDD = pd.merge(Df_CellMeasGroupTDD, Df_UeEUtranMeasurementTDD.loc[:, ['ENBpzh', 'thresholdOfRSRP']], how='left', left_on='A1:ENBpzh', right_on='ENBpzh').drop('ENBpzh', axis=1)
    Df_CellMeasGroupTDD['A2:ENBpzh'] = Df_CellMeasGroupTDD['ENBFunctionTDD'] + '-' + tool.df_split(Df_CellMeasGroupTDD['openInterFMeasCfg'], ';', 1)
    Df_CellMeasGroupTDD = pd.merge(Df_CellMeasGroupTDD, Df_UeEUtranMeasurementTDD.loc[:, ['ENBpzh', 'thresholdOfRSRP']], how='left', left_on='A2:ENBpzh', right_on='ENBpzh', suffixes=('_A1', '_A2')).drop('ENBpzh', axis=1)
    Df_CellMeasGroupTDD['打开系统间测量:ENBpzh'] = Df_CellMeasGroupTDD['ENBFunctionTDD'] + '-' + tool.df_split(Df_CellMeasGroupTDD['openRatFMeasCfg'], ';', 1)
    Df_CellMeasGroupTDD = pd.merge(Df_CellMeasGroupTDD, Df_UeEUtranMeasurementTDD.loc[:, ['ENBpzh', 'thresholdOfRSRP']], how='left', left_on='打开系统间测量:ENBpzh', right_on='ENBpzh').drop('ENBpzh', axis=1)
    Df_CellMeasGroupTDD['重定向测量:ENBpzh'] = Df_CellMeasGroupTDD['ENBFunctionTDD'] + '-' + tool.df_split(Df_CellMeasGroupTDD['openRedMeasCfg'], ';', 1)
    Df_CellMeasGroupTDD = pd.merge(Df_CellMeasGroupTDD, Df_UeEUtranMeasurementTDD.loc[:, ['ENBpzh', 'thresholdOfRSRP']], how='left', left_on='重定向测量:ENBpzh', right_on='ENBpzh', suffixes=('_打开系统间测量', '_重定向测量')).drop('ENBpzh', axis=1)

    Df_EUtranCellMeasurementTDD = pd.merge(Df_EUtranCellMeasurementTDD, Df_CellMeasGroupTDD.loc[:, ['MOI', 'A1:ENBpzh', 'thresholdOfRSRP_A1', 'A2:ENBpzh', 'thresholdOfRSRP_A2', '打开系统间测量:ENBpzh', 'thresholdOfRSRP_打开系统间测量', '重定向测量:ENBpzh', 'thresholdOfRSRP_重定向测量']], how='left', left_on='refCellMeasGroupTDD', right_on='MOI')
    name_lst = ['MEID', 'ENB-CI', 'A1:ENBpzh', 'thresholdOfRSRP_A1', 'A2:ENBpzh', 'thresholdOfRSRP_A2', '打开系统间测量:ENBpzh', 'thresholdOfRSRP_打开系统间测量', '重定向测量:ENBpzh', 'thresholdOfRSRP_重定向测量', 'eutranMeasParas_interCarriFreq', 'interFHOMeasCfg']
    # Df_New插入数据
    for name in reversed(name_lst):
        Df_New.insert(0, name, Df_EUtranCellMeasurementTDD[name])

    # 导出为Excel
    Df_EUtranCellTDD.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'EUtranCellTDD报表.xlsx'))
    Df_EUtranCellMeasurementTDD.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-measCfgIdx报表.xlsx'), index=False)
    Df_New.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-measCfgIdx-thresholdOfRSRP-eventId报表.xlsx'))
    del ew_lst_in, len_lst, lst_enb, num_aa, num_bb, name, ls, Df_New, name_lst
    gc.collect()
    # 查看耗时
    print('第1部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第二部分：MEID-ENB-CI-pb-DRX-flagSwiMode
    Df_EUtranCellTDD['ENB-CI'] = Df_EUtranCellTDD['ENBFunctionTDD'] + '-' + tool.df_replace(
        Df_EUtranCellTDD['description'], 'cellLocalId=', '')
    Df_New1 = Df_EUtranCellTDD.loc[:, ['MEID', 'ENB-CI', 'pb', 'switchForGbrDrx', 'switchForNGbrDrx', 'flagSwiMode']]
    Df_New1.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-pb-DRX-flagSwiMode报表.xlsx'))
    del Df_New1
    gc.collect()
    print('第2部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第三部分：MEID-ENB-CI-ncs
    Df_PrachTDD['ENB-CI'] = Df_PrachTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_PrachTDD['description'], 'cellLocalId=', '')
    Df_New2 = Df_PrachTDD.loc[:, ['MEID', 'ENB-CI', 'ncs']]
    Df_New2.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-ncs报表.xlsx'))
    del Df_New2
    gc.collect()
    print('第3部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第四部分：MEID-ENB-CI-p0NominalPUSCH-poNominalPUSCH1-poNominalPUCCH
    Df_PowerControlULTDD['ENB-CI'] = Df_PowerControlULTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_PowerControlULTDD['description'], 'cellLocalId=', '')
    Df_New3 = Df_PowerControlULTDD.loc[:, ['MEID', 'ENB-CI', 'p0NominalPUSCH', 'poNominalPUSCH1', 'poNominalPUCCH']]
    Df_New3.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-p0NominalPUSCH-poNominalPUSCH1-poNominalPUCCH报表.xlsx'))
    del Df_New3
    gc.collect()
    print('第4部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第五部分：MEID-ENB-CI-paForDTCH
    Df_PowerControlDLTDD['ENB-CI'] = Df_PowerControlDLTDD['ENBFunctionTDD'] + '-' + tool.df_replace(
        Df_PowerControlDLTDD['description'], 'cellLocalId=', '')
    Df_New4 = Df_PowerControlDLTDD.loc[:, ['MEID', 'ENB-CI', 'paForDTCH']]
    Df_New4.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-paForDTCH报表.xlsx'))
    del Df_New4
    gc.collect()
    print('第5部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第六部分：MEID-ENB-CI-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr
    Df_ECellEquipmentFunctionTDD['ENB-CI'] = Df_ECellEquipmentFunctionTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_ECellEquipmentFunctionTDD['description'], 'cellLocalId=', '')
    Df_New5 = Df_ECellEquipmentFunctionTDD.loc[:, ['MEID', 'ENB-CI', 'maxCPTransPwr', 'cpTransPwr', 'cpSpeRefSigPwr']]
    Df_New5.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr报表.xlsx'))
    del Df_New5
    gc.collect()
    print('第6部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第七部分：MEID-ENB-CI-selQrxLevMin
    Df_EUtranReselectionTDD['ENB-CI'] = Df_EUtranReselectionTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_EUtranReselectionTDD['description'], 'cellLocalId=', '')
    Df_New6 = Df_EUtranReselectionTDD.loc[:, ['MEID', 'ENB-CI', 'selQrxLevMin']]
    Df_New6.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-selQrxLevMin报表.xlsx'))
    del Df_New6
    gc.collect()
    print('第7部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第八部分：MEID-ENB-CI-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr
    Df_ECellEquipmentFunctionTDD['ENB-description'] = Df_ECellEquipmentFunctionTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_ECellEquipmentFunctionTDD['description'], 'cellLocalId=', '')
    # RRU使用RE模块保留,Rack=后边的数字即1 or 51 or 52 or 53...
    # 创建空DataFrame
    lst_ru = [re.compile(r'(?<=,Rack=)+\d+\.?\d*').findall(n_a) for n_a in Df_ECellEquipmentFunctionTDD['refRfDevice']]
    Df_ECellEquipmentFunctionTDD['RRU'] = [set(n_b) for n_b in lst_ru]  # 样式 [{1}, {51}， {51,52}, ...]
    Df_New7 = Df_ECellEquipmentFunctionTDD.loc[:, ['MEID', 'ENB-description', 'MOI', 'maxCPTransPwr', 'cpTransPwr', 'cpSpeRefSigPwr', 'RRU']]
    Df_New7.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-description-MOI-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr-RRU报表.xlsx'))
    print('第8部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第九部分：MEID-ENB-CI-refECellEquipmentFunctionTDD-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr-RRU
    # 分列 序号0，1，2...
    Df_EUtranCellTDD['ENB-CI'] = Df_EUtranCellTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_EUtranCellTDD['description'], 'cellLocalId=', '')
    Df_New8 = Df_EUtranCellTDD['refECellEquipmentFunctionTDD'].str.split(';', expand=True)
    ls = Df_New8.shape[1]  # 列数
    loa = 1
    num_bb = 0
    while loa <= ls * 5:
        # V事件及门限
        Df_New8 = pd.merge(Df_New8, Df_New7.loc[:, ['MOI', 'RRU', 'cpSpeRefSigPwr', 'cpTransPwr', 'maxCPTransPwr']],
                           how='left', left_on=num_bb, right_on='MOI').drop('MOI', axis=1)
        Df_New8.insert(loa, str(num_bb) + '_RRU', Df_New8.pop('RRU'))
        Df_New8.insert(loa, str(num_bb) + '_cpSpeRefSigPwr', Df_New8.pop('cpSpeRefSigPwr'))
        Df_New8.insert(loa, str(num_bb) + '_cpTransPwr', Df_New8.pop('cpTransPwr'))
        Df_New8.insert(loa, str(num_bb) + '_maxCPTransPwr', Df_New8.pop('maxCPTransPwr'))
        num_bb = num_bb + 1
        loa = loa + 5
    Df_X = Df_EUtranCellTDD.loc[:, ['MEID', 'ENB-CI']]
    Df_New8 = pd.concat([Df_X, Df_New8], axis=1, ignore_index=False)
    Df_New8.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-CI-refECellEquipmentFunctionTDD-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr-RRU报表.xlsx'), index=False)
    del Df_New7
    del Df_New8
    gc.collect()
    print('第9部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十部分：MEID-ENB-volteQualityDetectPrd-SubNetwork
    Df_New9 = Df_ENBFunctionTDD.loc[:, ['MEID', 'ENBFunctionTDD', 'volteQualityDetectPrd', 'SubNetwork']]
    Df_New9.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'MEID-ENB-volteQualityDetectPrd-SubNetwork报表.xlsx'))
    del Df_New9
    gc.collect()
    print('第10部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十一部分：VoLTEConfigCellTDD
    Df_VoLTEConfigCellTDD['ENB-CI'] = Df_VoLTEConfigCellTDD['ENBFunctionTDD'] + '-' + tool.df_replace(Df_VoLTEConfigCellTDD['description'], 'cellLocalId=', '')
    Df_New10 = Df_VoLTEConfigCellTDD.loc[:, ['MEID', 'ENB-CI', 'SubNetwork', "VoLTEConfigCellTDD", "voLTEHarqNumUl", "voLTEHarqNumDl", "switchOfFreqSel4Ni", "rlcSegmentUl", "volteCmrSwch", "piecesMinNum4ULVoLTE", "piecesMaxNum4ULVoLTE", 'mCSThrd4VoLTEBetterDL', 'mCSThrd4VoLTEWorseDL', "sINRThrd4VoLTEWorseUL", "sINRThrd4VoLTEbetterUL", 'abUserIdntfyNumThrd']]
    Df_New10.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'VoLTEConfigCellTDD报表.xlsx'))
    del Df_New10
    gc.collect()
    print('第11部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十二部分：ENBFunctionTDD
    Df_New11 = Df_ENBFunctionTDD.loc[:, ['MEID', 'ENBFunctionTDD', 'volteQualityDetectPrd']]
    Df_New11.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'ENBFunctionTDD报表.xlsx'))
    del Df_New11
    gc.collect()
    print('第12部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十三部分：UetimerTDD
    Df_New12 = Df_UeTimerTDD.drop(['MODIND', 'MOI'], axis=1)
    Df_New12.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'UetimerTDD报表.xlsx'))
    del Df_New12
    gc.collect()
    print('第13部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十四部分：GlobleSwitchInformationTDD
    Df_New13 = Df_GlobleSwitchInformationTDD.drop(['MODIND', 'MOI'], axis=1)
    Df_New13.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'GlobleSwitchInformationTDD报表.xlsx'))
    del Df_New13
    gc.collect()
    print('第14部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    # 第十五部分：GlobleSwitchInformationTDD
    Df_New14 = Df_ControlPlaneTimerTDD.drop(['MODIND', 'MOI'], axis=1)
    Df_New14.to_excel(tool.ret_path(OUT_DATAfile_DIR, 'ControlPlaneTimerTDD报表.xlsx'))
    del Df_New14
    gc.collect()
    print('第15部分完成，目前总耗时:', time.perf_counter() - start)  # 程序运行结束时间

    print('已导出完毕！')

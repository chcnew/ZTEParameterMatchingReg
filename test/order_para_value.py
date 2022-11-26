#!/bin/bash/python3
# _*_ coding: utf-8 _*_
import os.path

import pandas as pd
from utils import variables
from utils.utils import Tool


def run():
    print("正在生成工单参数，请稍等...")
    tool = Tool()
    df = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'EUtranCellTDD报表.xlsx'), sheet_name=0)
    df1 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'MEID-ENB-CI-ncs报表.xlsx'), sheet_name=0)
    df2 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'ControlPlaneTimerTDD报表.xlsx'), sheet_name=0)
    df3 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'MEID-ENB-CI-refECellEquipmentFunctionTDD-maxCPTransPwr-cpTransPwr-cpSpeRefSigPwr-RRU报表.xlsx'), usecols='B,F', sheet_name=0)
    df3['cpSpeRefSigPwr'] = df3['0_cpSpeRefSigPwr']
    df4 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'MEID-ENB-CI-selQrxLevMin报表.xlsx'), usecols='C:D', sheet_name=0)
    df5 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'UetimerTDD报表.xlsx'), usecols='E,J,L', sheet_name=0)
    df6 = pd.read_excel(tool.ret_path(variables.OUT_DATAfile_DIR, 'MEID-ENB-CI-measCfgIdx-thresholdOfRSRP-eventId报表.xlsx'), usecols='C,E,G', sheet_name=0)

    df['description'] = tool.df_replace(df['description'], 'cellLocalId=', '')
    df['description'] = df['description'].astype('str')
    df['ENB-CI'] = df['ENBFunctionTDD'].astype('str') + '-' + df['description']
    df = df.loc[:, ['ENB-CI', 'MEID', 'ENBFunctionTDD', 'pb', 'switchForGbrDrx', 'switchForNGbrDrx', 'flagSwiMode']]
    df = pd.merge(df, df1.loc[:, ['ENB-CI', 'ncs']], how='left', on='ENB-CI')
    df = pd.merge(df, df2.loc[:, ['ENBFunctionTDD', 'rrcReEstTimer']], how='left', on='ENBFunctionTDD')
    df = pd.merge(df, df3.loc[:, ['ENB-CI', 'cpSpeRefSigPwr']], how='left', on='ENB-CI')
    df = pd.merge(df, df4, how='left', on='ENB-CI')
    df = pd.merge(df, df5, how='left', on='ENBFunctionTDD')
    df = pd.merge(df, df6, how='left', on='ENB-CI')

    df.to_excel(tool.ret_path(variables.OUT_DATAfile_DIR, '工单参数报表.xlsx'))
    print("导出完毕。")


if __name__ == '__main__':
    run()

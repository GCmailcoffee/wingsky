# -*- coding:utf-8 -*-
"""
@file name  : deal.py
@author     : Chris.Ma
@date       : 2024-7-02
@brief      : 
    从相关目录读取000，001文件
    分析文件（文件版本，文件对应关系，是否包含已分类信息）
    写入文件
"""
import time
import os
import torchvision
import torchvision.transforms as transforms
import torch
import torch.nn as nn
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import platform
import shutil
import utils.file_utils as file_utils
import classification as cls
from utils.cls_constants import Constants

if platform.system() == 'Linux':
    matplotlib.use('TkAgg')

defect_dict = {"Block_Etch": 3, "Buried_PD": 5, "Micro_sc": 9, "Residue": 13, "Damage": 29, "Hole": 34, "Poly_Residue": 50}

def get_args_parser(add_help=True):
    import argparse

    # 解析参数
    parser = argparse.ArgumentParser(description="PyTorch Judge Image Batch", add_help=add_help)

    # 输入文件的基础目录
    parser.add_argument("--img-path", default=r"/home/amhs/toolid/test", type=str, help="dataset path")

    # 预训练的模型文件
    parser.add_argument("--ckpt-path", default=r"/home/amhs/wingsky/pths/wingsky_best.pth", type=str, help="ckpt path")
    
    # 训练模型，默认resnet
    parser.add_argument("--model", default="resnet50", type=str,
                        help="model name; resnet50/convnext/convnext-tiny")
    
    # 有无显卡
    parser.add_argument("--device", default="cpu", type=str, help="device (Use cuda or cpu Default: cuda)")

    # 输出基础目录
    parser.add_argument("--output-dir", default=r"/home/amhs/toolid/img_classify/defectlink/AYSEV01", type=str, help="path to save outputs")

    # 训练数据集目录
    parser.add_argument("--datasets-dir", default="./Result", type=str, help="path to save outputs")

    return parser

def move_file(root, file, subdir):
    fulldir = os.path.join(root, subdir)
    if not os.path.exists(fulldir):
        os.makedirs(fulldir,  exist_ok=False)
    
    fullfile = os.path.join(root, file)
    shutil.move(fullfile, fulldir)

def main(args):
    device = args.device
    path_img = args.img_path
    output_dir = args.output_dir
    ckpt_path = args.ckpt_path

    # ------------------------------------ step1: tranverse directory get klarf files------------------------------------
    suffix_list = ['001', '000']    # klarf文件后缀名暂定为这两种
    for file in file_utils.get_files_by_suffix(path_img, suffix_list):
        file_type = file_utils.judge_file_version(file)
        if (file_type == Constants.VERSION_12):
            # 处理1.2版本
            # 读取klarf文件中的defectlist信息 循环优化暂不考虑
            titleLine, defectlist = file_utils.get_defect_from_file(file)

            if not defectlist:
                continue

            for line_number, defe in enumerate(defectlist):
                path = os.path.join(path_img, defe.file_name)
                # 如果文件存在，需要分析文件
                if os.path.isfile(path):
                    if path.endswith("jpg") or path.endswith("png") or path.endswith("jpeg") or path.endswith("tif"):
                        for index, dtl in enumerate(defe.defect_list):
                            columns, old_value = file_utils.get_classnumber_from_line(dtl.content, 10)
                            res, prob = cls.classify_bypth(path, "resnet50", ckpt_path)
                            value = defect_dict.get(res, "0")
                            new_str = file_utils.replace_classnumber(columns, 10, columns[10] + " " + str(value))
                            new_str = file_utils.del_columns_after_column_number(new_str, 11)
                            defe.defect_list[index].content = new_str + '\n'
                    else:
                        continue
                else:
                    continue    
                defectlist[line_number] = defe

            out_path = os.path.join(output_dir, os.path.basename(file))
            
            #处理标题行的替换
            new_title = file_utils.replace_classnumber(titleLine.title.split(), 12, "TEST AUTOONSEMCLASS")
            new_title = file_utils.del_columns_after_column_number(new_title, 13 )
            new_title = file_utils.replace_classnumber(new_title.split(), 1, "12") + '\n'
            titleLine.title = new_title
            file_utils.modify_and_save_file(file, out_path, defectlist, titleLine)

        if (file_type == Constants.VERSION_18):
            # 处理1.8版本，文件是json格式
            defectlist = file_utils.get_defect_from_file(file)

if __name__ == "__main__":
    args = get_args_parser().parse_args()
    args.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    main(args)

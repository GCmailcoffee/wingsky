# -*- coding:utf-8 -*-
"""
@file name  : file_utils.py
@author     : Chris.Ma
@date       : 2024-05-30
@brief      : 读取文件和解析文件要素
"""
import shutil
import os
from typing import List, Tuple
from .cls_constants import Constants

class TitleLine:
    def __init__(self, title: str, title_line: int, defect_start, defect_end):
        self.title = title                      # defectlist的columns定义行
        self.title_line = title_line            # defectlist的columns定义行的起始行
        self.defect_start = defect_start        # defectlist起始行
        self.defect_end = defect_end            # defectlist终止行

class DefectLine:
    def __init__(self, content: str, leading_spaces: int):
        self.content = content
        self.leading_spaces = leading_spaces

class DefectList:
    # 一张图片可能有多个defectlist
    def __init__(self, file_name, start_line):
        self.file_name = file_name              # 文件名
        self.start_line = start_line            # defectlist的起始行
        self.defect_list: List[DefectLine] = []
    
    def add_defect(self, element: DefectLine):
        self.defect_list.append(element)

def get_files_by_suffix(directory, suffixes):
    matching_files = []
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lstrip('.') in suffixes:
            matching_files.append(os.path.join(directory, filename))
    return matching_files

def get_layer_from_file(file_path):
    """
    从文件中获取layer
    :param file_path:  文件全路径
    :return: 从文件中获取的layer
    """    
    last_columns = "" 
    with open(file_path, "r") as file:
        for line in file:
            print(line)
            # 判断字符串是否以特定的子字符串开头
            tmp = line.replace('\r', '').replace('\n', '')
            if tmp.startswith("StepID"):
                last_columns = tmp.rstrip().rsplit(maxsplit=1)[-1].replace('"', '').replace(';', '')
                break
    return last_columns

def get_defect_from_file(file_path) -> Tuple[TitleLine, List[DefectList]]:
    # 用于处理1.2的文件版本
    array_list = []
    is_begin = False
    titleLine = None
    global tmp_stru    

    with open(file_path, "r") as file:
        # 读取行号, 从0开始计数
        for line_number, line in enumerate(file, start=0):
            tmp = line

            # 需要修改列定义行
            if (tmp.startswith("DefectRecordSpec")):
                titleLine = TitleLine(line, line_number, 0, 0)

            if (tmp.startswith("DefectList;")):
                if titleLine != None:
                    titleLine.defect_start = line_number

            # 最后一条数据了
            if (is_begin == True and tmp.startswith("SummarySpec")):
                array_list.append(tmp_stru)
                titleLine.defect_end = line_number
                is_begin = False

            # 判断字符串是否以特定的子字符串开头
            if tmp.startswith("TiffFileName"):
                # 上一条defectlist数据获取结束，添加到数组中
                if (is_begin == True):
                    array_list.append(tmp_stru)
                    is_begin = False

                file_name = tmp.rstrip().rsplit(maxsplit=1)[-1].replace(';', '')
                #初始化defectList结构
                tmp_stru = DefectList(file_name, 0)
                
            # 要开始读取下一行的defectList了
            if tmp.startswith("DefectList") and not tmp.startswith("DefectList;"):
                is_begin = True
                continue

            # 记录起始行
            if (is_begin == True):
                if (len(tmp_stru.defect_list) == 0):
                    tmp_stru.start_line = line_number

                tmp_defect = DefectLine(tmp, len(line) - len(line.lstrip()))
                tmp_stru.add_defect(tmp_defect)

    return titleLine, array_list

def get_dict_from_file(file_path):
    dict = {}
    is_begin = False

    with open(file_path, "r") as file:
         for line in file:
            tmp = line.replace('\r', '').replace('\n', '')
            if tmp.startswith("ClassLookup"):
                is_begin = True
                continue
            
            if (is_begin == True and tmp.startswith(" ")):
                tmp_dict = tmp.split()
                dict[int(tmp_dict[0])] = tmp_dict[1].replace('"', '')

            # 结束循环
            if (is_begin == True and not tmp.startswith(" ")):
                is_begin = False
                break
    
    return dict

def get_classnumber_from_line(defect_line, column_number):
    # 获取已有的class分类，和其他列的数据
    tmp_columns = defect_line.split()
    if (bool(tmp_columns) is False):
        return -1 
    
    if (len(tmp_columns) < column_number):
        return -1
    
    return tmp_columns, tmp_columns[column_number - 1]

def replace_classnumber(defect_columns, column_number, replacestr):
    # 不改变出参
    columns = defect_columns
    if 0 <= column_number < len(columns):   
        columns[column_number] = replacestr
    
    modified_line = " ".join(columns)

    return modified_line

def is_dir_exists(path):
    return os.path.exists(path) and os.path.isdir(path)

def is_file_exists(file):
    return os.path.exists(file) and os.path.isfile(file)

def move_file(root, file, subdir):
    fulldir = os.path.join(root, subdir)
    if not os.path.exists(fulldir):
        os.makedirs(fulldir,  exist_ok=False)
    
    fullfile = os.path.join(root, file)
    shutil.move(fullfile, fulldir)

def judge_file_version(file_path):
    # 判断klarf文件是哪个版本
    # version12_string = "target_striFileVersion 1 2;"
    version18_string = "Record FileRecord  \"1.8\""
    ret = Constants.VERSION_12

    with open(file_path, "r") as f:
        first_line = f.readline()  # 读取文件的第一行
        if version18_string in first_line:
            ret = Constants.VERSION_18

    return ret

def del_columns_after_column_number(data: str, column_index: int):
    delimiter = ' '  # 可以替换成任意分隔符

    count = 0
    index = -1

    for i, char in enumerate(data):
        if char == delimiter:
            count += 1
            if count == column_index + 1:
                index = i
                break

    # 根据找到的索引截断字符串
    # 如果分隔符不够多，保留整个字符串
    if index != -1:
        trimmed_data = data[:index]
    else:
        trimmed_data = data  

    return trimmed_data

def modify_and_save_file(input_file, output_file, modify_list: List[DefectList], title_line: TitleLine):
    # 读取文件并修改指定行
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # 修改defectlist的标题行
    lines[title_line.title_line] = title_line.title

    # 修改目标行
    for tmp in modify_list:
        for index, defe in enumerate(tmp.defect_list):
            lines[tmp.start_line + index] = ' ' * defe.leading_spaces + defe.content

    filtered_lines = []
    # 最后删除包含图片名称的行
    for line in lines:
        if line.startswith("DefectList;"):
            filtered_lines.append("DefectList" + "\n")
            continue
        elif line.startswith("DefectList") and not line.startswith("DefectList;"):
            continue
        elif line.startswith("TiffFileName"):
            continue
        else:
            filtered_lines.append(line)
            continue

    # 将修改后的内容写入新文件
    with open(output_file, 'w') as out:
        out.writelines(filtered_lines)

if __name__ == "__main__":
    # print(get_layer_from_file(r"D:\Test\walfa\AYSEV01\A005169#010827084553.001"))
    # for defect in get_defect_from_file(r"D:\Test\walfa\AYSEV01\A005169#010827084553.001"):
    #     print(defect.file_name)
    #     for temp in defect.defect_list:
    #         print(temp)

    # print(get_dict_from_file(r"D:\Test\walfa\AYSEV01\A005169#010827084553.001"))
    #columns, value = get_classnumber_from_line(" 41 3466.882 1522.202 -7 34 3.750 3.200 12.000000 3.750 13 1 13 0 0.000000 0 0.000000 0.000000 0.000000 0.000000 0.000000 0 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 4 4 1 0 2 0 3 0 4 0;", 10)
    #print(replace_classnumber(columns, 10, 'aaa'))

    # print(judge_file_version(r"C:\Users\chris.ma\Desktop\鼎泰匠芯\T0136A_A006512_A006512#01.001"))
    print(del_columns_after_column_number(" 41 3466.882 1522.202 -7 34 3.750 3.200 12.000000 3.750 13 1 13 0 0.000000 0 0.000000 0.000000 0.000000 0.000000 0.000000 0 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 4 4 1 0 2 0 3 0 4 0;", 12))
    
    # suffix_list = ['001', '000'] 
    # print(get_files_by_suffix(r"D:\Test\walfa\AYSEV01", suffix_list))

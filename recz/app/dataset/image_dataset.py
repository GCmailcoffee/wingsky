# -*- coding:utf-8 -*-
"""
@file name  : image_dataset.py
@author     : Chris.Ma
@date       : 2024-05-21
@brief      : image 数据集读取
"""
import os
import numpy as np
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision.transforms import transforms


class ImageDataset(Dataset):
    """
    数据目录组织结构为文件夹划分train/test，2个类别标签通过文件夹名称获得
    """

    def __init__(self, root_dir, transform=None):
        """
        获取数据集的路径、预处理的方法，此时只需要根目录即可，其余信息通过文件目录获取
        """
        self.root_dir = root_dir
        self.transform = transform
        self.img_info = []  # [(path, label), ... , ]
        self.label_array = None
        # 由于标签信息是string，需要一个字典转换为模型训练时用的int类型
        #self.str_2_int = {"Normal": 0, "Edge-Loc": 1, "Edge-Ring": 2, "Check-Ok": 3,  "Regular-Type": 4, "Even-Many": 5, "Block-Shape": 6, "Full-Damage": 7, "Arc-Shape": 8, "Line": 9, "Central-Ring": 10}
        self.str_2_int = {"Block_Etch":0, "Buried_PD":1, "Damage":2, "Hole":3, "Micro_sc":4, "Poly_Residue":5, "Residue":6}

        self._get_img_info()

    def __getitem__(self, index):
        """
        输入标量index, 从硬盘中读取数据，并预处理，to Tensor
        :param index:
        :return:
        """
        path_img, label = self.img_info[index]
       
        img = Image.open(path_img).convert('RGB')

        if self.transform is not None:
            if 'albumentations' in str(type(self.transform)):
                img = np.array(img)
                img = self.transform(image=img)['image']
            else:
                img = self.transform(img)

        return img, label

    def __len__(self):
        if len(self.img_info) == 0:
            raise Exception("\ndata_dir:{} is a empty dir! Please checkout your path to images!".format(
                self.root_dir))  # 代码具有友好的提示功能，便于debug
        return len(self.img_info)

    def _get_img_info(self):
        """
        实现数据集的读取，将硬盘中的数据路径，标签读取进来，存在一个list中
        path, label
        :return:
        """
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith("jpg") or file.endswith("png") or file.endswith("jpeg") or file.endswith("tiff"):
                    path_img = os.path.join(root, file)
                    sub_dir = os.path.basename(root)
                    label_int = self.str_2_int[sub_dir]
                    self.img_info.append((path_img, label_int))


if __name__ == "__main__":
    root_dir_train = r"D:\Test\walfa\test\train"  # path to your data
    root_dir_valid = r"D:\Test\walfa\test\valid"   # path to your data

    #normMean = [0.5]
    #normStd = [0.5]

    normMean = [0.5]
    normStd = [0.5]
    normTransform = transforms.Normalize(normMean, normStd)
    train_transform = transforms.Compose([
        transforms.Resize((200, 200)),
        transforms.CenterCrop(200),
        transforms.ToTensor(),
        normTransform
    ])

    # train_transform = transforms.Compose([
    #     transforms.Resize((32, 32)),
    #     transforms.RandomCrop(32, padding=2),
    #     transforms.ToTensor(),
    #     normTransform
    # ])    
    valid_transform = transforms.Compose([
        transforms.Resize((200, 200)),
        transforms.ToTensor(),
        normTransform
    ])

    train_set = ImageDataset(root_dir_train, transform=train_transform)
    valid_set = ImageDataset(root_dir_valid, transform=valid_transform)

    train_loader = DataLoader(dataset=train_set, batch_size=2, shuffle=True)
    for i, (inputs, target) in enumerate(train_loader):
        print(i, inputs.shape, inputs, target.shape, target)

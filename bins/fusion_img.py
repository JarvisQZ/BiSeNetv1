# -*- coding: utf-8 -*-
"""
@Time : 2021/9/22 21:55 
@Author : Zhi QIN 
@File : fusion_img.py 
@Software: PyCharm
@Brief : portrait数据集做前景 ， coco数据集做背景
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pylab as pl
import cv2
from tools.coco_tool import CocoImg
import random
import shutil


def get_img_list(root):
    """
    读取portrait2000的（图片路径，标签路径）
    :param root:
    :return:
    """
    file_list = os.listdir(root)
    file_list = list(filter(lambda x: x.endswith("_matte.png"), file_list))
    label_lst = [os.path.join(root, name) for name in file_list]
    img_lst = [string.replace("_matte.png", ".png") for string in label_lst]
    data_lst = [(path_img, path_label) for path_img, path_label in zip(img_lst, label_lst)]
    return data_lst


def fusion(fore_path, mask_path, back_path):
    """
    融合图片
    :param fore_path: portrait2000中的原图图片路径
    :param mask_path: portrait2000中的标签图片路径
    :param back_path: coco数据集中的图片路径
    :return:
    """
    raw_img = cv2.imread(fore_path)
    mask_img = cv2.imread(mask_path) / 255
    back_img = cv2.imread(back_path)

    fore_img = np.clip(raw_img * mask_img, a_min=0, a_max=255).astype(np.uint8)

    h, w, c = fore_img.shape
    back_img = cv2.resize(back_img, (w, h))

    result = np.clip(fore_img * mask_img + back_img * (1 - mask_img), a_min=0, a_max=255).astype(np.uint8)

    return result


def gen_img(img_list, coco_genertor, out_dir, img_num=100):
    """
    生成融合的图片
    :param img_list: portrait2000的 (人像图片路径，标签图片路径) 列表
    :param coco_genertor: CocoImg实例，用于获取coco数据集图片路径
    :param out_dir: 输出的目录
    :param img_num: 生成数据集的数据量
    :return:
    """
    for i in range(img_num):
        fore_path, mask_path = random.choice(img_list)
        # fore_path, mask_path = img_list[0]  # 调试用，仅用1张前景生成多张图
        _, back_path = random.choice(coco_genertor)
        fusion_img = fusion(fore_path, mask_path, back_path)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        img_name = "{0:08d}.png".format(i)
        msk_name = "{0:08d}_matte.png".format(i)
        img_path = os.path.join(out_dir, img_name)
        mask_path_dst = os.path.join(out_dir, msk_name)
        cv2.imwrite(img_path, fusion_img)
        shutil.copyfile(mask_path, mask_path_dst)
        print(f"{i}/{img_num}")


if __name__ == '__main__':
    img_num = 3400  # 生成数据集的数据量
    out_dir = r"D:\PythonCode\BiSeNet\data\data_aug_{}".format(img_num)
    portarit_root = r"D:\PythonCode\BiSeNet\data\portrait_2000\training"
    coco_root = r"E:\Datasets\coco_2017"
    data_type = "val2017"  # train2017::118287 张图片, val2017::5000
    super_cats_in = ["outdoor", "indoor"]
    super_cats_out = ["person"]

    # step1：创建coco数据集生成器
    coco_genertor = CocoImg(coco_root, data_type, super_cats_in, super_cats_out)

    # step2: 获取portrait imglist
    img_list = get_img_list(portarit_root)

    # step3：执行生成
    gen_img(img_list, coco_genertor, out_dir, img_num=img_num)

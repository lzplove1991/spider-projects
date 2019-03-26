#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = '刘支培'

import itchat
import os
# 导入腾讯优图，用来实现人脸检测等功能
import TencentYoutuyun
from pyecharts import Pie
import math
import PIL.Image as Image


# 获取头像
def get_image():
    itchat.auto_login()
    friends = itchat.get_friends(update=True)

    #  在当前位置创建一个用于存储头像的目录headImages
    base_path = 'headImages'
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    # 获取所有好友头像
    for friend in friends:
        img_data = itchat.get_head_img(userName=friend['UserName'])  # 获取头像数据
        img_name = friend['RemarkName'] if friend['RemarkName'] != '' else friend['NickName']
        img_file = os.path.join(base_path, img_name + '.jpg')
        print(img_file)
        with open(img_file, 'wb') as file:
            file.write(img_data)


# 分析头像
def analyse_image():
    # 向腾讯优图平台申请的开发密钥
    appid = '***********'
    secret_id = '*********************************'
    secret_key = '*********************************'
    userid = '***********'

    end_point = TencentYoutuyun.conf.API_YOUTU_END_POINT  # 优图开放平台
    youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, userid, end_point)

    use_face = 0
    not_use_face = 0

    base_path = 'headImages'
    for file_name in os.listdir(base_path):
        result = youtu.DetectFace(os.path.join(base_path, file_name))  # 人脸检测与分析
        # print(result)  # 参考 https://open.youtu.qq.com/legency/#/develop/api-face-analysis-detect
        # 判断是否使用人像
        if result['errorcode'] == 0:  # errorcode为0表示图片中存在人像
            use_face += 1
            gender = '男' if result['face'][0]['gender'] >= 50 else '女'
            age = result['face'][0]['age']
            beauty = result['face'][0]['beauty']  # 魅力值
            glasses = '不戴眼镜 ' if result['face'][0]['glasses'] == 0 else '戴眼镜'
            # print(file_name[:-4], gender, age, beauty, glasses, sep=',')
            with open('header.txt', mode='a', encoding='utf-8') as f:
                f.write('%s,%s,%d,%d,%s\n' % (file_name[:-4], gender, age, beauty, glasses))
        else:
            not_use_face += 1

    attr = ['使用人脸头像', '未使用人脸头像']
    value = [use_face, not_use_face]
    pie = Pie('好友头像分析', '', title_pos='center')
    pie.add('', attr, value, radius=[30, 75], is_label_show=True,
            is_legend_show=True, legend_top='bottom')
    # pie.show_config()
    pie.render('好友头像分析.html')


# 拼接头像
def join_image():
    base_path = 'headImages'
    files = os.listdir(base_path)
    each_size = int(math.sqrt(float(640 * 640) / len(files)))
    lines = int(640 / each_size)
    image = Image.new('RGB', (640, 640))
    x = 0
    y = 0
    for file_name in files:
        img = Image.open(os.path.join(base_path, file_name))
        img = img.resize((each_size, each_size), Image.ANTIALIAS)
        image.paste(img, (x * each_size, y * each_size))
        x += 1
        if x == lines:
            x = 0
            y += 1
    image.save('all.jpg')
    itchat.send_image('all.jpg', 'filehelper')


if __name__ == '__main__':
    # get_image()
    # analyse_image()
    join_image()

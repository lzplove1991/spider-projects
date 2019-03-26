#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = '刘支培'

# 导入Pie组件，用于生成饼图
from pyecharts import Pie

# 获取所有性别
sex = []
with open('friends.txt', mode='r', encoding='utf-8') as f:
    rows = f.readlines()
    for row in rows:
        sex.append(row.split(',')[2])
# print(sex)

# 统计每个性别的数量
attr = ['帅哥', '美女', '未知']
value = [sex.count('1'), sex.count('2'), sex.count('0')]

pie = Pie('好友性别比例', '好友总人数：%d' % len(sex), title_pos='center')
pie.add('', attr, value, radius=[30, 75], rosetype='area', is_label_show=True,
        is_legend_show=True, legend_top='bottom')
# pie.show_config()
pie.render('好友性别比例.html')

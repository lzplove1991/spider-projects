#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = '刘支培'

# 导入jieba模块，用于中文分词
import jieba
# 导入Counter类，用于统计值出现的次数
from collections import Counter
from pyecharts import Bar

# 获取备注名
remarkNames = []
with open('friends.txt', mode='r', encoding='utf-8') as f:
    rows = f.readlines()
    for row in rows:
        remarkName = row.split(',')[1]
        if remarkName != '':
            remarkNames.append(remarkName)

# 设置分词
words = [x for x in jieba.cut(str(remarkNames), cut_all=False) if x not in ['-', ',', '(', ')', '（', '）', ' ', "'"]]  # 排除短横线、逗号、空格、单引号
data_top10 = Counter(words).most_common(10)  # 返回出现次数最多的10条
print(data_top10)

bar = Bar('好友分类TOP10', '', title_pos='center', width=1200, height=600)
attr, value = bar.cast(data_top10)
bar.add('', attr, value, visual_range=[0, 200], is_visualmap=True, is_label_show=True)
bar.render('好友分类TOP10.html')

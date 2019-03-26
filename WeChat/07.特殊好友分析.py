#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = '刘支培'
from pyecharts import Bar

# 获取特殊好友
star_list = []  # 星标朋友
deny_see_list = []  # 不让他看我的朋友圈
no_see_list = []  # 不看他的朋友圈

with open('friends.txt', mode='r', encoding='utf-8') as f:
    rows = f.readlines()
    for row in rows:
        # # 获取好友名称
        name = row.split(',')[1] if row.split(',')[1] != '' else row.split(',')[0]
        # 获取星标朋友
        star = row.split(',')[6]
        if star == '1':
            star_list.append(name)
        # 获取设置了朋友圈权限的朋友
        flag = row.split(',')[7].replace('\n', '')
        if flag in ['259', '33027', '65795']:
            deny_see_list.append(name)
        if flag in ['65539', '65795']:
            no_see_list.append(name)

print('星标好友：', star_list)
print('不让他看我的朋友圈：', deny_see_list)
print('不看他的朋友圈：', no_see_list)

attr = ['星标朋友', '不让他看我的朋友圈', '不看他的朋友圈']
value = [len(star_list), len(deny_see_list), len(no_see_list)]

bar = Bar('特殊好友分析', '', title_pos='center')
bar.add('', attr, value, is_visualmap=True, is_label_show=True)
bar.render('特殊好友分析.html')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = '刘支培'

# 导入Counter类，用于统计值出现的次数
from collections import Counter
# 导入Geo组件，用于生成地理坐标类图
from pyecharts import Geo
import json
# 导入Bar组件，用于生成柱状图
from pyecharts import Bar


# 数据可视化
def render():
    # 获取所有城市
    cities = []
    with open('friends.txt', mode='r', encoding='utf-8') as f:
        rows = f.readlines()
        for row in rows:
            city = row.split(',')[4]
            if city != '':  # 去掉城市名为空的值
                cities.append(city)

    # 对城市数据和坐标文件中的地名进行处理
    handle(cities)

    # 统计每个城市出现的次数
    data = Counter(cities).most_common()  # 使用Counter类统计出现的次数，并转换为元组列表
    print(data)

    # 根据城市数据生成地理坐标图
    geo = Geo('好友位置分布', '', title_color='#fff', title_pos='center', width=800, height=500,
              background_color='#404a59')
    attr, value = geo.cast(data)
    geo.add('', attr, value, visual_range=[0, 500],
            visual_text_color='#fff', symbol_size=15,
            is_visualmap=True, is_piecewise=True)
    geo.render('好友位置分布.html')

    # 根据城市数据生成柱状图
    data_top20 = Counter(cities).most_common(20)  # 返回出现次数最多的20条
    bar = Bar('好友所在城市TOP20', '', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data_top20)
    bar.add('', attr, value, is_visualmap=True, visual_text_color='#fff', is_more_utils=True,
            is_label_show=True)
    bar.render('好友所在城市TOP20.html')


# 处理地名数据，解决坐标文件中找不到地名的问题
def handle(cities):
    # 获取坐标文件中所有地名
    with open(
            '/Users/wangbo/PycharmProjects/python-spider/venv/lib/python3.6/site-packages/pyecharts/datasets/city_coordinates.json',
            mode='r', encoding='utf-8') as f:
        data = json.loads(f.read())  # 将str转换为json

    # 循环判断处理
    data_new = data.copy()  # 拷贝所有地名数据
    for city in set(cities):  # 使用set去重
        count = 0
        for k in data.keys():
            count += 1
            if k == city:
                break
            if k.startswith(city):  # 处理简写的地名，如 达州市 简写为 达州
                # print(k, city)
                data_new[city] = data[k]
                break
            if k.startswith(city[0:-1]) and len(city) >= 3:  # 处理行政变更的地名，如县改区 或 县改市等
                data_new[city] = data[k]
                break
        # 处理不存在的地名
        if count == len(data):
            while city in cities:
                cities.remove(city)

    # print(len(data), len(data_new))

    # 写入覆盖坐标文件
    with open(
            '/Users/wangbo/PycharmProjects/python-spider/venv/lib/python3.6/site-packages/pyecharts/datasets/city_coordinates.json',
            mode='w', encoding='utf-8') as f:
        f.write(json.dumps(data_new, ensure_ascii=False))  # 将json转换为str，指定ensure_ascii=False支持中文


if __name__ == '__main__':
    render()

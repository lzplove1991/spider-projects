#-*- coding:utf-8 -*-
# author : Zhipei Liu

import cv2
import time
import numpy as np
from selenium import webdriver
from urllib import request
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import random
import json
import requests

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--profile-directory=Default')
# chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--disable-plugins-discovery")
# chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
brower = webdriver.Chrome(chrome_options=chrome_options)

def loadpage(userid, password):
    # url = 'https://home.jd.com/'
    url = "https://passport.jd.com/new/login.aspx?"
    brower.get(url)
    time.sleep(3)
    s1 = r'//div/div[@class="login-tab login-tab-r"]/a'
    userlogin = brower.find_element_by_xpath(s1)
    userlogin.click()
    # time.sleep(5)
    username = brower.find_element_by_id("loginname")
    username.send_keys(userid)
    userpswd = brower.find_element_by_id("nloginpwd")
    userpswd.send_keys(password)
    # time.sleep(5)
    brower.find_element_by_id("loginsubmit").click()
    time.sleep(3)
    # while 'shortcut_userico_ico' in brower.page_source:
    #     print(brower.page_source)
    #     print('登陆成功----')
    while True:
        try:
            getPic()
        except Exception as e:
            print(e)
            print("登陆成功----")
            break
    brower.find_element_by_class_name("nickname").click()
    cookies = brower.get_cookies()
    print(cookies)
    print(brower.page_source)
    cookies = json.dumps(cookies, ensure_ascii=False)
    with open('jdCookie.json', 'w') as f:
        f.write(cookies)
    time.sleep(5)

def jdhome():
    url='https://home.jd.com/'
    cookie=read_cookie()
    print(cookie)
    print('===')
    header={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'referer': 'https://www.jd.com/',
        'cookie':cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    response = requests.get(url, verify=False, headers=header).text
    print(response)

def read_cookie():
    with open('jdCookie.json', 'r', encoding='utf-8') as f:
        listCookies = json.loads(f.read())
    cookie = [item["name"] + "=" + item["value"] for item in listCookies]
    cookiestr = '; '.join(item for item in cookie)
    return cookiestr


def getPic():
    # 用于找到登录图片的大图
    s2 = r'//div/div[@class="JDJRV-bigimg"]/img'
    # 用来找到登录图片的小滑块
    s3 = r'//div/div[@class="JDJRV-smallimg"]/img'
    bigimg = brower.find_element_by_xpath(s2).get_attribute("src")
    smallimg = brower.find_element_by_xpath(s3).get_attribute("src")
    # print(smallimg + '\n')
    # print(bigimg)
    # 背景大图命名
    backimg = "backimg.png"
    # 滑块命名
    slideimg = "slideimg.png"
    # 下载背景大图保存到本地
    request.urlretrieve(bigimg, backimg)
    # 下载滑块保存到本地
    request.urlretrieve(smallimg, slideimg)

    image2=Image.open('backimg.png')
    print(image2.size)
    image1=sourse_img(image2)
    offset=get_gap(image1,image2)
    print(offset)
    # # 获取图片并灰度化
    # block = cv2.imread(slideimg, 0)
    # template = cv2.imread(backimg, 0)
    # # 二值化后的图片名称
    # blockName = "block.jpg"
    # templateName = "template.jpg"
    # # 将二值化后的图片进行保存
    # cv2.imwrite(blockName, block)
    # cv2.imwrite(templateName, template)
    # block = cv2.imread(blockName)
    # block = cv2.cvtColor(block, cv2.COLOR_RGB2GRAY)
    # block = abs(255 - block)
    # cv2.imwrite(blockName, block)
    # block = cv2.imread(blockName)
    # template = cv2.imread(templateName)
    # # 获取偏移量
    # result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED) # 查找block在template中的位置，返回result是一个矩阵，是每个点的匹配结果
    # x, y = np.unravel_index(result.argmax(), result.shape)
    # print("x方向的偏移", int(y * 0.4 + 18), 'x:', x, 'y:', y)
    # 获取滑块
    # tracks = get_tracks(offset*0.95)
    track=[get_track1,get_track2,get_track3,get_track4]
    tracks=track[random.randint(0,2)](offset)
    # tracks=get_track4(offset)
    # tracks=get_track1(offset)
    element = brower.find_element_by_xpath(s3)
    ActionChains(brower).click_and_hold(on_element=element).perform()
    # random.shuffle(tracks)
    for y in tracks:
        ActionChains(brower).move_by_offset(xoffset=y, yoffset=0).perform()
        # time.sleep(random.random()/10.0)
    # ActionChains(brower).move_by_offset(xoffset=-4, yoffset=0).perform()
    # time.sleep(0.5)
    # ActionChains(brower).move_by_offset(xoffset=-1, yoffset=0).perform()
    # time.sleep(0.7)
    # ActionChains(brower).move_by_offset(xoffset=-1.6, yoffset=0).perform()
    time.sleep(2)
    ActionChains(brower).release(on_element=element).perform()
    time.sleep(3)

#找到原图
def sourse_img(backimg):
    img1 = backimg.crop((0, 0, 38, 140))
    ret=None
    for i in range(1, 11):
        print('当前是第%d张图' %i)
        image=Image.open('./index/{}.png'.format(i))
        img2=image.crop((0, 0, 38, 140))
        if classfiy_histogram_with_split(img1, img2)==100:
            ret=image
            break
    return ret




#对比两张图片是否大致相同
def classfiy_histogram_with_split(image1, image2, size=(256, 256), part_size=(64, 64)):
    '''
     'image1' 和 'image2' 都是Image 对象.
     可以通过'Image.open(path)'进行创建。
     'size' 重新将 image 对象的尺寸进行重置，默认大小为256 * 256 .
     'part_size' 定义了分割图片的大小.默认大小为64*64 .
     返回值是 'image1' 和 'image2'对比后的相似度，相似度越高，图片越接近，达到100.0说明图片完全相同。
    '''
    img1 = image1.resize(size).convert("RGB")
    sub_image1 = split_image(img1, part_size)

    img2 = image2.resize(size).convert("RGB")
    sub_image2 = split_image(img2, part_size)

    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)

    x = size[0] / part_size[0]
    y = size[1] / part_size[1]

    pre = round((sub_data / (x * y)), 6)
    print(u"相似度为:", (pre * 100))
    return pre * 100


def split_image(image, part_size):
    pw, ph = part_size
    w, h = image.size

    sub_image_list = []

    assert w % pw == h % ph == 0, "error"

    for i in range(0, w, pw):
        for j in range(0, h, ph):
            sub_image = image.crop((i, j, i + pw, j + ph)).copy()
            sub_image_list.append(sub_image)

    return sub_image_list


def calculate(image1, image2):
    g = image1.histogram()
    s = image2.histogram()
    assert len(g) == len(s), "error"

    data = []

    for index in range(0, len(g)):
        if g[index] != s[index]:
            data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
        else:
            data.append(1)

    return sum(data) / len(g)


def get_gap(image1, image2):
    """
    获取缺口偏移量
    :param image1: 不带缺口图片
    :param image2: 带缺口图片
    :return:
    """
    # 从图片中横坐标位65处开始便利图片像素点
    left = 0
    time.sleep(2)
    for i in range(left, image1.size[0]):
        for j in range(image1.size[1]):
            if not is_pixel_equal(image1, image2, i, j):
                left = i
                print(left)
                return left

def is_pixel_equal(image1, image2, x, y):
    """
    判断两个像素是否相同
    :param image1: 图片1
    :param image2: 图片2
    :param x: 位置x
    :param y: 位置y
    :return: 像素是否相同
    """
    # 取两个图片的像素点
    pixel1 = image1.load()[x, y]
    pixel2 = image2.load()[x, y]
    threshold = 60
    # 判断像素点之间的RGB值是不是在可接受范围
    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                    pixel1[2] - pixel2[2]) < threshold:
        return True
    else:
        return False

def get_track1(distance):
    print('get_track1')
    distance*=0.76
    """
    根据偏移量获取移动轨迹（使用加速度与减速度来模拟，当然并不是每个网站都可以使用加速度来解决的，
    如有妖气使用的顶象验证还会判断是否是存在加速度与加速度，毕竟人手动的速度是有波动的）
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.3
    # 初速度
    v = 0
    while current < distance:
        if current < mid:
            # 加速度为正4，实验多次得到的较为准确的速度
            a = 4
        else:
            # 加速度为负5
            a = -5
        # 初速度v0
        v0 = v
        # 当前速度v = v0 + at
        v = v0 + a * t
        # 移动距离x = v0t + 1/2 * a * t^2
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
        random.shuffle(track)
    print(track, sum(track))
    return track

def get_track2(distance):#这是滑动轨迹的，京东的滑动轨迹很恶心，这个也是有时可以有时不行
    print('get_track2')
    distance*=0.9
    tracks = []
    current = 0
    mid = distance * 4 / 5
    t = 0.2
    v = 0
    while current < distance:
        if current < mid:
            a = random.uniform(2, 5)
        else:
            a = -(random.uniform(12.5, 13.5))
        v0 = v
        v = v0 + a * t
        x = v0 * t + 1 / 2 * a * (t ** 2)
        current += x
        if 0.6 < current - distance < 1:
            x = x - 0.53
            tracks.append(round(x, 2))
        elif 1 < current - distance < 1.5:
            x = x - 1.4
            tracks.append(round(x, 2))
        elif 1.5 < current - distance < 3:
            x = x - 1.8
            tracks.append(round(x, 2))
        else:
            tracks.append(round(x, 2))
    if sum(tracks) > distance:
        i = sum(tracks) - distance
        tracks[-1] = round(tracks[-1] - i, 2)
    i = random.uniform(1, 3  )
    i = round(i, 2)
    zz = random.uniform(0.1, 0.3)
    tracks[-1] = round(tracks[-1] + i, 2)
    i = round(i - zz, 2)
    tracks.append(-i)
    if sum(tracks) < distance:
        si = distance - sum(tracks)
        tracks.append(round(si, 2))
    print(tracks, sum(tracks))
    return tracks

def get_track3(distance):
    print('get_track3')
    distance*=0.9
    """
    根据偏移量和手动操作模拟计算移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    tracks = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 时间间隔
    t = 0.2
    # 初始速度
    v = 0

    while current < distance:
        if current < mid:
            a = random.uniform(2, 5)
        else:
            a = -(random.uniform(12.5, 13.5))
        v0 = v
        v = v0 + a * t
        x = v0 * t + 1 / 2 * a * t * t
        current += x

        if 0.6 < current - distance < 1:
            x = x - 0.53
            tracks.append(round(x, 2))

        elif 1 < current - distance < 1.5:
            x = x - 1.4
            tracks.append(round(x, 2))
        elif 1.5 < current - distance < 3:
            x = x - 1.8
            tracks.append(round(x, 2))

        else:
            tracks.append(round(x, 2))

    print(tracks, sum(tracks))
    return tracks

def get_track4(distance):
    print('get_track4')
    distance*=0.9
    random=np.random.RandomState(int(time.time()))
    states=random.uniform(-1.0,3.0,size=50)
    alpha=distance/sum(states)
    tracks=states*alpha
    print(tracks,sum(tracks))
    return tracks

if __name__ == '__main__':
    # get_track4(150)
    id = "*********" # 用户账号
    passwd = "**********" # 用户密码
    loadpage(id, passwd)
    # jdhome()
#-*- coding : utf-8 -*-
'''
author='Liu Zhipei'
Logining for Meituan
get data from Meituan take-away
'''

import json
import re
import requests
import zlib
import time
import base64
import hashlib
from bs4 import BeautifulSoup
from Cryptodome import Random
from Cryptodome.Cipher import AES
from hashlib import md5

class Meituan():
    def __init__(self, user, password=None):
        self.user = user
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        self.user_id = ''
        self.agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

    def pad(self,data):
        length = 16 - (len(data) % 16)
        return data.encode() + (chr(length)*length).encode()

    def unpad(self,data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def bytes_to_key(self,data, salt, output=48):
        assert len(salt) == 8, len(salt)
        data = data.encode()
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def encrypt(self,message, passphrase):
        #模拟Crypto-Js加密
        salt = Random.new().read(8)
        key_iv = self.bytes_to_key(passphrase, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self.pad(message)))

    def decrypt(self,encrypted, passphrase):
        #解密模块
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self.bytes_to_key(passphrase, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self.unpad(aes.decrypt(encrypted[16:]))

    def login(self, r, url, username, password, csrf, captcha):
        t=time.time()
        #conUrl=[url.find('continue')]
        #conUrl=base64.b64encode(zlib.compress(conUrl))
        conUrl = 'eJw9i8sKwyAQAP8lUI++8g5Ib4V+RRFd6BKyBl2bfn4DgV6GOcw0IREjVXBv5r0sSh0eN49yA+TqSYa0KR9CqsSqAHNage7/6WYfBMfJ63pShK/IWNbX7jMTZKdFgfzBAO5KRK0YnYG5Df0Qx9nqrh3H2QyTNH3fmm6y06lSS938AMxdNNs='
        decodedToken = {
            'sign': conUrl,
            'brR': [[1920, 1080], [1920, 1040], 24, 24],
            'ssT': 1,
            'uA': self.agent,
            'fSign': 'eJxVUcuO2zAM/BVhz+xH1ME22W4cGJWzxZ4KRmZkorIUyHLT/H2p2E6Vg8nh8GWOXr5GRgd3qyqH5veCDxhjuMIGHZ8iix/E4epVjamHTRjYKI1+VLWWyI/B4Shgikxx9epAV9hSiFb6d+T+UGKD8DZc0CTYT4Y7VFVk2z+ieRStYd5QYtXeLnSNnGRJSR89m9AR1GxiGMM5zbSmyGeotdqG1LPJqPkPn0tm0KDDxD6ovZgky0CTDaSayD4tWJvIlzU4vj2A9ORLHqGmgU/BdQVzG4SAFvswILQ80DjbrJT6IaSHNtJpMj2lrOwHxQ49wk/2tpNPJEbfYcS75gl9yi8T4okcvMrzyNRv6K0O3sIWhZBngXfklqFGZyf/UAKjo5QKwXbS7PCGBfW9J293xAWV/7NFVvupFLvp0Y5N2XqvKUs+8XnQJ6sKOWXK2z0ff+3e9UZ/ef2bqpVaArklOEa/1uus5HrGh6okCQfNg548NE+tQualS252S+bmzkj+5R97rhFq',
            'ver': '1.0.6',
            'wR': 'WebKit WebGL',
            'kT': ['V,INPUT,492707', '\x11,BODY,492238'],
            'buttons': [],
            'cV': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAADHUlEQVRIS62XX2iOURzHP4eM/NneMTJ/aqUQZkppk39zISltURS1vGmZRFtcuHTLhTW5MmyLsonsQlKkNEOKMqxIuNC4EluWDTv6Pc85c3b2Ptuz931/dXp7nuf8fp/z53t+v/MqtNaI3WyGxjq4+z14jG39CdhfD+0HYrtIRxWAG5qhNgnngKPj+B+K+P4EeBWfrbjVpNmVBJn3A6A8TbC4if/7eHBFTp5m8EfY+y2wNAPwEHADGLVbucBx4DrwJgAowrmG9hOYngFYXD8A9/0Y44E3Ah1AAlgDbDG/FU6gqD12WVeBfvfFeOCoycogmswg4oAfAd3ZANsYp4Aeb3R2o2TTrPUk4PZp50UzsH2MPY4jyDJglVGH9BewVYqFDyyEFnn4DEwFqoFiwvMq4sr1xBUHLH12A3NMZwt2B/EXuOQGWwTUAZcjVB0XLFCBW5j1szP/YzQxHC9dcaUa0DagaMRh/L/kvVOg7bfj5YO3prnUEnKtaan2+OMMuCdJwdpK4JjZY0lt1RmAC4GdETPurIDu50ZcdrbzHXHtywCcA0hBcsVlJ9haAb07zNNXoNEo26TM4nRVLSEt2N9/OUF3xlDpCmBDIIc8DaZIxFW19LNL7frIMWo1OT9VrFJgdfhBQZOG5ESQYV8rLtdTioMUCd9mAuvNKTDfFMgNRFLaBOH2OFnIY+C1RywARNBSat2UGj6aqw/tRi0xln0SsASYB8hsXgB9wGzT5gKLgWnRC+mApdMnQCpBS7yll0y4ycDjeQz38sD2vQxAVkCaXCdemg8lsDwBeyuhvBI2S+pKzyLAEcHqgdr0QL6XKi3Uv55+CWpXtJUQ6k8uBNmxDrneFsy6RldfG4XBqj4E8ryrT2V2aCaKJOuyUORaSx5qAGqyihgd7CJwBKUGR54urQV8Hpic5QFITqtBKQEH5h3rYPbLgBNAlcnImYxBivIV4AxKya192EaD7Set5ZSeBA6OnQpSjkuK8QXgLEpJ2eBwF/mDAxTpIYb6FvAuGuzG01queHuAdUC+aXL7FhNJSvsGdAb/JZR65g/HB/8DVgPbDALJSUEAAAAASUVORK5CYII=',
            'cts': t+100,
            'dnT': '1',
            'brVD': [1468, 969],
            'broP': ['Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client'],
            'lsT': 1,
            'bI': [url, ''],
            'hH': {'server': 'Tengine', 'content-type': 'text/html; charset=utf-8', 'x-version': '1.2.1',
                    'date': r.headers['Date'], 'content-encoding': 'gzip', 'connection': 'keep-alive'},
            'inputs': [{'keyboardEvent': '0-0-0-0', 'inputName': 'commit', 'editStartedTimeStamp': 1553084036836,
                        'editFinishedTimeStamp': 1553084036925},
                        {'keyboardEvent': '0-1-1-0', 'inputName': 'password', 'editStartedTimeStamp': 1553084034393,
                        'editFinishedTimeStamp': 1553084036836},
                        {'keyboardEvent': '0-1-1-0', 'inputName': 'email', 'editStartedTimeStamp': 1553083550949,
                        'editFinishedTimeStamp': 1553083552708}],
            'loC': '',
            'pSign': 'eJyLVnLOKMrPTVUIcHFTCMgpTc/MU9JBFgvLTC1PLQKK+SWWZJalKjjnZKbmlSjFAgASzxKU',
            'ts': t,
            'wV': 'WebKit',
            'ckE': 'yes',
            'tT': [],
            'mT': [ '761,364,493765', '761,365,493759', '761,366,493253', '762,366,493215', '763,366,493078',
                    '764,366,492982', '765,366,492949', '765,365,492932', '765,363,492915', '765,361,492898',
                    '764,359,492892', '763,355,492881', '758,349,492865', '754,344,492862', '749,339,492848',
                    '738,325,492832', '725,309,492816', '715,294,492799', '707,284,492782', '706,283,492765',
                    '706,282,492548', '706,286,492531', '706,287,492518', '706,288,492511', '706,289,492494',
                    '706,290,492406', '706,291,492390', '706,292,492365', '707,293,492348', '708,294,492332',
                    '711,299,492314', '713,307,492298', '713,320,492282', '712,336,492265', '708,351,492248',
                    '705,358,492238', '701,364,492231', '687,377,492215', '664,392,492200', '618,415,492183',
                    '577,432,492164', '529,451,492149', '484,469,492133', '439,494,492114', '395,527,492100',
                    '361,561,492081', '334,596,492064', '314,627,492048', '304,646,492031', '298,661,492014',
                    '295,670,491999', '295,673,491990', '295,675,491911', '295,675,491862', '296,675,491833',
                    '297,671,491814', '303,656,491798', '306,648,491782', '311,615,491765', '311,593,491749'],
            'aM': '',
            'fL': 'Arial,Arial Black,Arial Narrow,Calibri,Cambria,Cambria Math,Comic Sans MS,Consolas,Courier,Courier New,Georgia,Helvetica,Impact,Lucida Bright,Lucida Console,Lucida Sans,Lucida Sans Typewriter,Lucida Sans Unicode,Microsoft Sans Serif,MS Gothic,MS PGothic,MS Sans Serif,MS Serif,Palatino Linotype,Segoe Print,Segoe Script,Segoe UI,Segoe UI Light,Segoe UI Semibold,Segoe UI Symbol,Tahoma,Times,Times New Roman,Trebuchet MS,Verdana,Wingdings,Candara,Constantia,Corbel,Ebrima,FangSong,Gabriola,KaiTi,Malgun Gothic,Marlett,Microsoft Himalaya,Microsoft JhengHei,Microsoft New Tai Lue,Microsoft PhagsPa,Microsoft Tai Le,Microsoft YaHei,Microsoft Yi Baiti,MingLiU_HKSCS-ExtB,MingLiU-ExtB,Mongolian Baiti,MS UI Gothic,MV Boli,NSimSun,PMingLiU-ExtB,SimHei,SimSun,SimSun-ExtB,Sylfaen',
            'aT': [ '761,364,INPUT,495102', '706,282,INPUT,492645', '295,675,HTML,491949', '732,273,INPUT,488189',
                    '784,273,INPUT,481014', '747,279,INPUT,473592', '731,287,INPUT,11021', '721,223,INPUT,9245',
                    '1059,188,A,1765']
    }
        #压缩编码token
        decodedToken = json.dumps(decodedToken)
        form = zlib.compress(decodedToken.encode())
        encodedToken = base64.b64encode(form)
        #构造登录表单
        loginForm = {
            'email' : username,
            'password': self.encrypt(password, 'mtdp').decode(),
            'captcha' : captcha,
            'origin' : 'account-login',
            'fingerprint' : '0-5-1-3qd|294|1p',
            'csrf' : csrf,
            '_token' : encodedToken
        }
        header = {
            'User-Agent' : self.agent,
            'X-Client' : 'javascript',
            'X-CSRF-Token' : csrf,
            'X-Requested-With' : 'XMLHttpRequest'
        }
        res = self.session.post(url, headers=header, data=loginForm)
        # print('登录状态码：%s' %res.status_code)
        # print('登录返回数据: %s' %res.text)
        status=json.loads(res.text)
        if list(status.keys())[0] !='error':
            return res.cookies
        else:
            print(status[list(status.keys())[0]]['code'],':',status[list(status.keys())[0]]['message'])
            return None

    def captchaOCR(self,cUrl):
        #验证码识别接口，网上打码平台可以用100次，有时候识别不准
        timestamp = str(int(time.time()))
        uid = '110588' #用户ID
        pdkey = '0MWzTrJX6BR90HxkYauc1BOjj1HMZ93L' #密钥
        predict_type = '30400'
        img_data = requests.get(cUrl).content
        md5 = hashlib.md5()
        md5.update((timestamp + pdkey).encode())
        csign = md5.hexdigest()
        md5 = hashlib.md5()
        md5.update((uid + timestamp + csign).encode())
        csign = md5.hexdigest()
        # with open('abc.png','wb') as f:
        #     f.write(img_data)
        data = {'user_id': '110588', 'timestamp': timestamp, 'sign': csign, 'app_id': '', 'asign': '',
                'predict_type': predict_type, 'up_type': 'mt'
        }
        file = {
                'img_data':('img_data',img_data)
        }
        header = {
                'User-Agent': 'Mozilla/5.0',
        }
        m = requests.post('http://pred.fateadm.com/api/capreg', data=data, headers=header, files=file)
        code = json.loads(m.text)['RspData']
        code = json.loads(code)
        return code['result']

    def get_orderpage(self):
        #请求代理
        #referer = 'https://passport.meituan.com/account/unitivelogin?risk_partner=0&uuid=0508e7f769f746669a7b.1553081774.1.0.0&service=waimai&continue=http%3A%2F%2Fwaimai.meituan.com%2Faccount%2Fsettoken'
        url = 'https://passport.meituan.com/account/unitivelogin?service=waimai&continue=https%3A%2F%2Fwaimai.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3D%252Fnew%252FwaimaiIndex'
        username = self.user
        password = self.password

        #预登录获取csrf，token，验证码url等需要的参数
        res = self.session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        csrf = soup.find(class_ = 'form-field form-field--ops').find_all(value=True)[2].get('value')
        cUrl = soup.find(class_ = 'login-captcha-img').get('src')
        #识别验证码
        captcha = self.captchaOCR(cUrl)
        #登录并获取登录的cookie
        cookie = self.login(res, url, username, password, csrf, captcha)
        #更新cookie
        if cookie:
            self.session.cookies.update(requests.utils.dict_from_cookiejar(cookie))
        else:
            return
        query = self.session.get('http://waimai.meituan.com/customer/order/list', headers = {'User-Agent':self.agent})
        restr = r'订单号：([0-9]+)'
        order_num=re.findall(restr,query.text)
        # order_list=[urlstr + str(i) for i in order_num]
        # print('订单页状态码：%s' %query.status_code)
        # print('订单页返回数据: %s' %query.text)
        # print(order_num)
        data={}
        if len(order_num)>0:
            for order in order_num:
                url = 'http://waimai.meituan.com/customer/order/list?viewid=%s' % order
                res=self.session.get(url,headers = {'User-Agent':self.agent})
                ret=self.page_data(order,res)
                data[order]=ret
        return data

    def page_data(self,order_num,page):
        #解析网页数据
        soup = BeautifulSoup(page.content, 'lxml')
        soup = soup.select_one('div[data-viewid="%s"]' % order_num)
        name = soup.find(class_='contact').find_all('p')[1].text
        if name[-3:-1] == '先生':
            sex = '男'
        elif name[-4:-2] == ('小姐' or '女士'):
            sex = '女'
        else:
            sex = 'NA'
        addr = soup.find(class_='contact').find_all('p')[0].text[3:]
        phone_num = soup.find(class_='contact').find_all('p')[2].text[3:]
        shop_name = soup.select("span[class=poi-name]")[0].get_text()
        shop_phone = soup.select("span[class=order-total]")[0].get_text()
        shop_img = soup.find('img').get('data-src')
        order_time = soup.select("span[class=order-total]")[1].get_text()
        order_money = soup.select("span[class=order-money-num]")[0].get_text()
        order_list = soup.select("div[class=food-na]")
        dish_list = [dish_list.get_text().strip() for dish_list in order_list]
        food_count = soup.select("span[class=food-count]")
        count_list = [count.get_text() for count in food_count]
        food_price = soup.find_all('span', class_='food-pri')
        price_list = [price.get_text()[1:] for price in food_price]
        order_status = soup.select("p[class=bold]")[-1].get_text()

        food_list = []
        mid = map(list, zip(dish_list, count_list, price_list))
        for item in mid:
            ord_dict = dict(zip(['food', 'count', 'price'], item))
            food_list.append(ord_dict)

        user = {'name': name[3:-4], 'sex': sex, 'addr': addr, 'phone': phone_num}
        shop = {'name': shop_name, 'shop-phone': shop_phone, 'shop-img': shop_img}
        order = {'food': food_list, 'money': order_money[1:].strip(), 'time': order_time, 'status': order_status}
        data = {'order_number': order_num, 'order_data': {'user': user, 'shop': shop, 'order': order}}
        return data

if __name__=='__main__':
    user=input('user or email:')
    pwd=input('password:')
    login=Meituan(user,pwd)
    data=login.get_orderpage()
    print(data)



'''
data:
{'26265322117705535': 
    {'order_number': '26265322117705535', 
     'order_data': 
        {'user': 
            {'name': '刘支培', 'sex': '男', 'addr': '袁旗寨村7号楼 (四排一号301)', 'phone': '***********'}, 
        'shop': 
            {'name': '岐味居（烧烤）', 'shop-phone': '13991978624', 'shop-img': 'https://p0.meituan.net/120.0/business/3fce380058de60a3cfe07b027ca5bf5531585.jpg'}, 
        'order': 
            {'food': 
                [{'food': '烤鸡翅', 'count': '1', 'price': '6'}, 
                 {'food': '烤鸡翅', 'count': '1', 'price': '6'}, 
                 {'food': '红柳签烤羊羔肉', 'count': '5', 'price': '4'}, 
                 {'food': '烤牛肉筋', 'count': '2', 'price': '13'}, 
                 {'food': '烤牛肉筋', 'count': '1', 'price': '13'}], 
            'money': '67.2', 
            'time': '2019-01-21 23:10', 
            'status': '订单完成'
            }
        }
    }
}
'''
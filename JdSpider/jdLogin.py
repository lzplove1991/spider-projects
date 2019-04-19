#-*- coding:utf-8 -*-
# author : Zhipei Liu
import requests
import execjs
import base64
import re
import time
from settings import *
import json
from PIL import Image
import math,random
import pandas as pd
import matplotlib.pyplot as plt

class JD(object):
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.session=requests.session()

    def login(self):
        #获取登录需要post的data
        print('------------Start login--------------')
        data=self._compele_login_data()
        url = 'https://plogin.m.jd.com/cgi-bin/mm/domlogin'  # post_url
        main_url = 'https://home.m.jd.com/myJd/newhome.action?sid={}'.format(self.session.cookies['sid'])  # 我的京东页面
        headers['Host'] = 'plogin.m.jd.com'
        try:
            response = self.session.post(url, data=data, headers=headers).json()
            if response['errcode'] == 0:
                print('登录成功！')
                # headers['Host'] = 'home.m.jd.com'
                # html = session.get(main_url,headers=headers)
                html = self.session.get('https://m.jd.com/', headers=headers)
                return True
            print('登录失败:', response['message'])
            return False
        except Exception as er:
            print(er)
        finally:
            print('-------------Login end---------------')

    def user_base(self):
        now = int(time.time() * 1000)
        home_url = 'https://wq.jd.com/user/info/QueryJDUserInfo?sceneid=11110&_t=83761342&_={}&sceneval=2&g_login_type=1&callback=jsonpCBKG&g_ty=ls'.format(
            now)
        headers['Referer'] = 'https://home.m.jd.com/myJd/newhome.action'
        home_res = self.session.get(home_url, headers=headers)
        # print(home_res)
        if 'jsonpCBKG' in home_res.text:
            # user=eval(home_res[14:-13])
            user = eval(re.findall('try{jsonpCBKG\((.*)\);', home_res.text, re.S)[0])
            # user_base=dict()
            # #用户名称
            # user_base['userName']=user['base']['nickname']
            # #用户京东账号
            # user_base['userID']=user['base']['curPin']
            # #用户手机号码
            # user_base['mobile'] = user['base']['mobile']
            # #用户等级
            # user_base['userLevel'] = user['base']['userLevel']
            # #用户等级称号
            # user_base['levelName'] = user['base']['levelName']
            # #用户金豆值
            # user_base['jdNum'] = user['base']['jdNum']
            #京享值
            #user_base['jXiang'] = user['base']['jvalue']
            user_base=user['base']
            # print(user_base)
            return user_base
        else:
            return ' '

    def bought_info(self):
        """获取已购买商品的信息"""
        headers.pop('Host')
        print('Begin shopping list_info !')
        # car_url = 'https://p.m.jd.com/cart/cart.action'
        base_deal_list_url = 'https://wqdeal.jd.com/bases/orderlist/deallist?callersource=mainorder&order_type=3&start_page=%d&page_size=10&last_page=%d&callback=dealListCbA&isoldpin=0&utfswitch=1&traceid={}&t={}&sceneval=2&&g_ty=ls&g_tk={}'
        # print(self.session.cookies)
        if 'wq_skey' in self.session.cookies:
            wq_skey = self.session.cookies['wq_skey']
        else:
            wq_skey = ''
        headers['Referer'] = 'https://wqs.jd.com/order/orderlist_merge.shtml?tab=1&ptag=7155.1.11&sceneval=2'
        now = int(time.time() * 1000)
        # file = open(r'get_traceid.js').read()
        with open(r'get_traceid.js') as f:
            file = f.read()
        traceid = execjs.compile(file).call('e')
        # print('>' * 30 + '\n', traceid, now, self.time33(wq_skey))
        base_deal_list_url = base_deal_list_url.format(traceid, now, self.time33(wq_skey))
        deal_list_url_1 = base_deal_list_url % (1, 0)
        try:
            html = self.session.get(deal_list_url_1, headers=headers).text
            result = eval(re.findall('{.+}', html, re.S)[0])
            if 'deal_list' in result:
                # print(f"result:{result}")
                yield result
            n = 2
            while True:
                deal_list_url_2 = base_deal_list_url % (n, 1)
                html = self.session.get(deal_list_url_2, headers=headers).text
                if not int(re.findall('total_count.*?\"(\d+)\"', html)[0]):
                    break
                n += 1
                result=eval(re.findall('{.+}', html, re.S)[0])
                if 'deal_list' in result:
                    # print(f"result:{result}")
                    yield result
        except Exception as e:
            print('订单信息请求出错:',e)

    def save_goods_info(self):
        df = pd.DataFrame()
        for i in self.bought_info():
            # print('已购买商品：', i)
            # print('\n')
            deal_list = i['deal_list']
            for each in deal_list:
                seller_info = dict()
                seller_info['deal_id'] = each['deal_id']
                seller_info['date'] = pd.to_datetime(each['dateSubmit'])
                seller_info['price'] = float(each['total_price']) / 100
                seller_info['state'] = each['stateName']
                seller_info['number'] = len(each['trade_list'])
                seller_info['title'] = [i['item_title'] for i in each['trade_list']]
                df = df.append(seller_info, ignore_index=True)
        df.to_excel('jd_goods.xlsx')
        print('Get jd_good successfully', 'The End!', sep='\n')

    def goods_data(self):
        data=dict()
        for goods in self.bought_info():
            # print(goods)
            deal_list=goods['deal_list']
            for each in deal_list:
                seller_info = dict()
                seller_info['date'] = each['dateSubmit']
                seller_info['price'] = float(each['total_price']) / 100
                seller_info['state'] = each['stateName']
                seller_info['trade_list'] = [i['item_title'] for i in each['trade_list']]
                data[each['deal_id']]=seller_info
        return data

    def baitiao(self):
        now = int(time.time() * 1000)
        baitiaoUrl = 'https://wq.jd.com/user/smsmsg/QueryIOUsLimit?_={}&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls'.format(now)
        baitiaoRes = self.session.get(baitiaoUrl, headers=headers)
        # print(baitiaoRes)
        try:
            res=eval(re.findall('try{jsonpCBKB\((.*)\);', baitiaoRes.text, re.S)[0])
            # print(res)
            baitiao=dict()
            #白条可用额度
            baitiao['unpaid']=res['data']['unpaidForAll']
            #白条已用额度
            baitiao['paid']=res['data']['availableLimit']
            #白条总额度
            baitiao['limit']=float(baitiao['unpaid'])+float(baitiao['paid'])
            return baitiao
        except Exception as e:
            print('白条信息请求出错：',e)

    def goods_addr(self):
        data=self.goods_data()
        now = int(time.time() * 1000)
        with open(r'get_traceid.js') as f:
            file = f.read()
        if 'wq_skey' in self.session.cookies:
            wq_skey = self.session.cookies['wq_skey']
        else:
            wq_skey = ' '
        for deal_id in data.keys():
            traceid = execjs.compile(file).call('e')
            g_tk=self.time33(wq_skey)
            goodsUrl = 'https://wqdeal.jd.com/bases/orderdetail/detailview?callersource=mainorder&utfswitch=1&deal_id={}&callback=detailFirCbA&traceid={}&t={}&g_ty=ls&g_tk={}&isoldpin=0&sceneval=2'
            goodsUrl=goodsUrl.format(deal_id,traceid,now,g_tk)
            goods = self.session.get(goodsUrl, headers=headers).text
            result = eval(re.findall('{.+}', goods, re.S)[0])
            # print(result)
            if result['errCode'] == '0':
                #收货人
                data[deal_id]['recvName']=result['dealinfo']['recvName']
                #收货人地址
                data[deal_id]['recvAddr'] = result['dealinfo']['recvAddr']
                #收货人电话
                data[deal_id]['recvMobile'] = result['dealinfo']['recvMobile']
            else:
                continue
        return data

    def user_data_test(self):
        now = int(time.time() * 1000)
        home_url = 'https://wq.jd.com/user/info/QueryJDUserInfo?sceneid=11110&_t=83761342&_={}&sceneval=2&g_login_type=1&callback=jsonpCBKG&g_ty=ls'.format(now)
        headers['Referer'] = 'https://home.m.jd.com/myJd/newhome.action'
        home_res = self.session.get(home_url, headers=headers)
        print(type(home_res.text))
        print(home_res.text)
        baitiaoUrl = 'https://wq.jd.com/user/smsmsg/QueryIOUsLimit?_={}&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls'.format(
            now)
        baitiaoRes = self.session.get(baitiaoUrl, headers=headers)
        print(type(baitiaoRes.text))
        print(baitiaoRes.text)
        if 'wq_skey' in self.session.cookies:
            wq_skey = self.session.cookies['wq_skey']
        else:
            wq_skey = ' '
        addrUrl = 'https://wqdeal.jd.com/deal/recvaddr/getrecvaddrlistV3?adid=433459132&locationid=undefined&callback=cbLoadAddressListA&reg=1&r=0.559772858673103&g_tk={}&g_ty=ls'.format(
            self.time33(wq_skey))
        if 'sid' in self.session.cookies:
            sid = self.session.cookies['sid']
            print(sid)
        else:
            sid = ' '
        headers['Referer'] = 'https://wqs.jd.com/my/my_address.shtml?sceneval=2&sid={}&source=4'.format(sid)
        addr = self.session.get(addrUrl, headers=headers)
        # print(type(addr.text))
        # print(addr.text)
        goodsUrl = 'https://wqdeal.jd.com/bases/orderdetail/detailview?callersource=mainorder&utfswitch=1&deal_id=85576508057&callback=detailFirCbA&traceid=620959835118272778&t=1555489239820&g_ty=ls&g_tk=5381&isoldpin=0&sceneval=2'
        goods = self.session.get(goodsUrl, headers=headers)
        # print(goods.text)

    def user_data(self):
        if self.login():
            #bought必须放在第一条
            bought = self.goods_addr()
            base = self.user_base()
            baitiao=self.baitiao()
            user_data={
                'base_data':base,
                'baitiao':baitiao,
                'bought':bought
            }
            self.data_analyze(bought)
            return user_data

    def data_analyze(self,data):
        now=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        recvData=[]
        for data in data.values():
            if data['state'] == '完成' and 'recvAddr' in data.keys():
                recvData.append(data)
        #已完成订单按时间排序
        sorted_data=sorted(recvData,key=lambda x:x['date'],reverse=True)
        addrList=[k['recvAddr'] for k in sorted_data]
        addrCount={}
        for i in set(addrList):
            addrCount.update({i:addrList.count(i)})
        #地址使用频繁度排序
        sorted_add_count=sorted(addrCount.items(),key=lambda x:x[1],reverse=True)
        print('地址使用频繁度：',sorted_add_count,'\n','->'*30)
        print('订单按时间排序：',sorted_data,'\n','->'*30)

    def visualization(self):
        df = pd.read_excel('jd_goods.xlsx')
        df.sort_values(by='date', inplace=True)
        a = df.resample(rule='12M', closed='left', on='date').sum()  # on针对dateframe对象的参数
        a.plot(kind='bar')
        for i, j in enumerate(a['price']):
            plt.text(i + 0.12, j + 8, int(j), horizontalalignment='center')
        plt.xticks(rotation=270)
        plt.ylim([0, 8000])
        plt.ylabel('price')
        plt.title('Date-Price-relationship')
        b = df.groupby('state').count()
        print('总消费:', df['price'].sum())
        a['percent'] = a['price'].div(df['price'].sum())
        a.sort_values(by='price', ascending=False, inplace=True)
        print(a)
        b = df[(df['date'] > pd.to_datetime('2014-12-31')) & (df['date'] <= pd.to_datetime('2015-12-31'))].loc[:,
            ['price', 'title']]
        print(b)
        plt.tight_layout()
        plt.show()

    def _get_args(self):
        #登录需要post的data
        url = 'https://home.m.jd.com/myJd/home.action'
        try:
            html = self.session.get(url, headers=headers).text
            token = re.findall('str_kenString = \'(.*?)\'', html)
            token = token[0] if token else None
            md5Fun = re.findall('function getDat.*?\}', html)[0]
            rsaString = re.findall('str_rsaString = \'(.*?)\'', html)[0]
            sessionId = re.findall('var jcap_sid = \'(.*?)\'', html)[0]
            return token, rsaString, md5Fun, sessionId
        except Exception as e:
            print(e)

    def _compele_login_data(self):
        """登录需要post的data"""
        url = 'https://payrisk.jd.com/m.html'
        token, rsaString, md5Fun, sessionId = self._get_args()
        data['verifytoken'] = self._parse_verifyCode(sessionId)
        finger_token = re.findall('var jd_risk_token_id = \'(.*?)\'', self.session.get(url, headers=headers).text)[0]
        name, pwd = self._get_username_pwd(rsaString)
        # file = open(r'md5.js').read()
        with open(r'md5.js') as f:
            file = f.read()
        file += md5Fun
        dat = execjs.compile(file).call('getDat', name, pwd)
        data['s_token'] = token
        data['dat'] = dat
        data['wlfstk_datk'] = dat
        data['risk_jd[token]'] = finger_token
        data['username'] = name
        data['pwd'] = pwd
        return data

    def _download_pic(self, arg, st, sessionId, Codejs):
        # 验证码验证获取verify_token
        verifyurl = 'https://jcap.m.jd.com/cgi-bin/api/check'
        results = json.loads(arg)
        pic1 = results['b1'].replace('data:image/jpg;base64,', '')
        pic2 = results['b2'].replace('data:image/jpg;base64,', '')
        with open('fullpic.png', 'wb') as f:
            f.write(base64.b64decode(pic1.encode()))
        with open('target.png', 'wb') as f:
            f.write(base64.b64decode(pic2.encode()))
        print('step_2:Get pic successfully')
        pos = self._find_position()
        pos_arg = json.dumps({"ht": 171, "wt": 293, "x": pos[0], "y": pos[1]}, ensure_ascii=False)
        print('图片坐标：', pos_arg)
        ctData = Codejs.call('get_tk', st, sessionId, pos_arg)
        html_3 = self.session.post(verifyurl, data=ctData, headers=headers).json()
        return html_3

    def _parse_verifyCode(self, sessionId):
        """验证码解析函数
            sessionId:网页中返回的参数
        """
        initurl = 'https://jcap.m.jd.com/cgi-bin/api/fp'
        verifyurl = 'https://jcap.m.jd.com/cgi-bin/api/check'  # 登录时图片验证码
        refreshurl = 'https://jcap.m.jd.com/cgi-bin/api/refresh'
        # file = open(r'code_verify.js').read()
        with open(r'code_verify.js') as f:
            file = f.read()
        Codejs = execjs.compile(file)
        ctData = Codejs.call('get_ct', sessionId)
        try:
            # 初始化获得一个st码用于第二步获得验证码图片
            html_1 = self.session.post(initurl, data=ctData, headers=headers).json()
            print('step_1:Get st/fp successfully!')
            # post提交获得验证码图片，保存到本地
            ctData = Codejs.call('get_tk', html_1['st'], sessionId, '')
            html_2 = self.session.post(verifyurl, data=ctData, headers=headers).json()
            html_3 = self._download_pic(html_2['img'], html_2['st'], sessionId, Codejs)
            while html_3['code'] != 0:
                refresh_arg = json.dumps({'nonce': self.x(16), 'token': html_2['st'], 'sid': sessionId},
                                         ensure_ascii=False)
                se = Codejs.call('get_se', refresh_arg)
                rf_data['si'] = sessionId
                rf_data['se'] = se
                html_2 = self.session.post(refreshurl, data=rf_data, headers=headers).json()
                if html_2['code'] == 0:
                    html_3 = self._download_pic(html_2['img'], html_2['st'], sessionId, Codejs)
                print('正在重试！')
                time.sleep(0.5)
            print('step_3:Get verifyToken successfully!')
            return html_3['vt']
        except Exception as er:
            print(er)

    def _find_position(self):
        """寻找位置参数
        使用列表添加相似点，求均值近似求出位置
        """
        prob = list()
        full_pic = Image.open('fullpic.png')
        pos_pic = Image.open('target.png')
        width_1, height_1 = pos_pic.size
        width_2, height_2 = full_pic.size
        n = (height_1 // 2) - 3
        for i in range(width_2):
            for j in range(height_2):
                f_pix = full_pic.getpixel((i, j))
                p_pix = pos_pic.getpixel((width_1 // 2, n))
                if abs(f_pix[0] - p_pix[0]) < threshold and abs(f_pix[1] - p_pix[1]) < threshold and abs(
                                f_pix[2] - p_pix[2]) < threshold:
                    prob.append((i, j))
        if prob:
            x = sum([i[0] for i in prob]) // len(prob)
            y = sum([i[1] for i in prob]) // len(prob)
            return x, y
        else:
            return 10, 10

    def _get_username_pwd(self, rsaString):
        """密码用户名加密
            rsaString:网页返回的rsaString字符串
        """
        with open(r'sj_jd_pwd.js') as f:
            file = f.read()
        # file = open(r'sj_jd_pwd.js').read()
        js = execjs.compile(file)
        name_pwd = js.call('enc_pwd_name', rsaString, self.username, self.password)
        name = name_pwd['username']
        pwd = name_pwd['pwd']
        return name, pwd

    def x(self, a):
        """验证码更新时需要的nonce参数"""
        c = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
             "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        t = ''
        e = 0
        while e < a:
            t += c[math.floor(35 * random.random())]
            e += 1
        return t

    def time33(self, e):
        t = 5381
        a = 0
        r = len(e)
        while a < r:
            t += (t << 5) + ord(e[a])
            a += 1
        return 2147483647 & t

def data_analyze(data):
    pass

if __name__=='__main__':
    username=input('请输入您的京东账号：')
    password=input('请输入您的密码：')
    jd=JD(username,password)
    data=jd.user_data()
    if data:
        print(data)
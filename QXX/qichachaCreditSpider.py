from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import re
from scrapy import Selector
import requests
import base64
import yundama
import json
from PIL import Image
from urllib import parse
import os
from http import cookiejar


class QichachaCreditNetwork(object):
    # 登陆  拿到cookie
    def __init__(self,keyword):
        self.keyword=keyword


    def login(self):
        # 初始化模拟浏览器
        options = webdriver.ChromeOptions()
        # 是否调用可视化chrome浏览器
        # options.add_argument('--headless')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
        browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)
        # 填入登陆信息
        browser.get("https://www.qichacha.com/user_login")
        browser.find_element_by_id('normalLogin').click()
        # 账号密码记得换成产品提供的会员账号
        browser.find_element_by_id("nameNormal").send_keys("13360544020")
        browser.find_element_by_id("pwdNormal").send_keys("123456789a")
        # 滑动模块验证
        button = browser.find_element_by_id('nc_1_n1z')
        action = ActionChains(browser)
        action.click_and_hold(button).perform()
        action.reset_actions()
        action.move_by_offset(308, 0).perform()
        time.sleep(3)
        # 弹窗文字验证
        while True:
            # base64图片格式转流形式
            yanzhen_img_bs64 = Selector(text=browser.page_source).xpath(
                '//div[@class="imgCaptcha_img"]/img/@src').extract_first()
            imgContent = base64.b64decode(re.sub('^data:image/.+;base64,', '', yanzhen_img_bs64))
            # imgContent.save("yanzheng2.jpg")
            # yanzhen = input("输入：")
            print("正在调用云打码平台")
            ydm = yundama.YDMHttp()
            result = ydm.decode(imgContent)
            if result[0] == -3003:
                print("打码失败，正在重试")
                continue
            browser.find_element_by_id("nc_1_captcha_input").send_keys(result[1])
            browser.find_element_by_id("nc_1_scale_submit").click()
            time.sleep(3)
            if "<b>验证通过</b>" in browser.page_source:
                browser.find_element_by_tag_name("button").click()
                print("验证成功，将跳转登陆页面")
                time.sleep(3)
                cookies = browser.get_cookies()
                print(cookies)
                cookies = json.dumps(cookies,ensure_ascii=False)
                with open('qichachaCookie.json','w') as f:
                    f.write(cookies)
                # cookieStr = ""
                # for cookie in cookies:
                #     if cookie["name"] == "acw_tc":
                #         # 结尾留个空格，不然cookie登陆不上，很迷
                #         cookieStr = cookieStr + "acw_tc={}; ".format(cookie["value"])
                #     elif cookie["name"] == "QCCSESSID":
                #         cookieStr = cookieStr + "QCCSESSID={};".format(cookie["value"])
                # # 本地存储cookie，线上可换成redis存储
                # with open("qichahcaCookie.txt", "w") as f:
                #     f.write(cookieStr)
                userName = re.findall("name:  '(.*?)',", browser.page_source)
                if userName:
                    print("登陆成功\n用户名为：" + userName[0] + "\ncookie为：" + cookies)
                break
            else:
                print("验证失败,正在重试")
        browser.quit()

    @staticmethod
    def cookie():
        with open('qichachaCookie.json', 'r', encoding='utf-8') as f:
            listCookies = json.loads(f.read())
        cookie = [item["name"] + "=" + item["value"] for item in listCookies]
        cookiestr = '; '.join(item for item in cookie)
        return cookiestr

    # 查询关键词
    def search(self):
        companyData=[]
        cookie=self.cookie()
        url = "https://www.qichacha.com/search?key={}".format(self.keyword)
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.qichacha.com",
            "Cookie": cookie,
            "Referer": "https://www.qichacha.com/",
        }
        response = requests.get(url, verify=False, headers=header).text
        status=Selector(text=response).xpath('/html/body/header/div/ul/li[5]/a/text()').extract_first()
        if status =='登录':
            self.login()
            self.search()
        # 提取公司名字  登陆成功一页结果最多20个
        companyNameList = Selector(text=response).xpath(
            "//tbody[@id='search-result']/tr/td[3]/a[@class='ma_h1']").xpath("string(.)").extract()
        companyUrlList=Selector(text=response).xpath(
                "//tbody[@id='search-result']/tr/td[3]/a/@href").extract()
        companyCount=len(companyNameList)
        for i in range(1,companyCount+1):
            companyName = Selector(text=response).xpath(
                "//tbody[@id='search-result']/tr[{}]/td[3]/a[@class='ma_h1']".format(i)).xpath("string(.)").extract_first()
            companyUrl = Selector(text=response).xpath(
                "//tbody[@id='search-result']/tr[{}]/td[3]/a/@href".format(i)).extract_first()
            #提取法人名称
            legalPerson=Selector(text=response).xpath(
                "//tbody[@id='search-result']/tr[{}]/td[3]/p[1]/a[@class='text-primary']".format(i)).xpath("string(.)").extract_first()
            data={
                'companyName':companyName,
                'legalPerson':legalPerson,
                'companyUrl':"https://www.qichacha.com"+companyUrl,
                  }
            companyData.append(data)
        return companyData

    #去除空格
    def trip(self,str):
        return str.strip() if str is not None else ' '

    def get_key(self,str):
        keyDict={
            '电话':'phone'
        }

    #获取首页公司数据
    def company_data(self):
        companyData={}
        companyList=self.search()
        cookie=self.cookie()
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.qichacha.com",
            "Cookie": cookie,
            "Referer": parse.quote("https://www.qichacha.com/search?key={}".format(self.keyword)),
        }
        for com in companyList:
            response = requests.get(com['companyUrl'], verify=False, headers=header).text
            #公司名称
            comanyName = Selector(text=response).xpath(
                '//*[@id="company-top"]/div[2]/div[2]/div[1]/h1/text()').extract_first()
            #邮箱
            mail = Selector(text=response).xpath(
                '//*[@id="company-top"]/div[2]/div[2]/div[3]/div[2]/span[1]/span[2]/a/text()').extract_first()
            #电话
            phone = Selector(text=response).xpath(
                '//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[1]/span[2]/span/text()').extract_first()
            #官网地址
            website = Selector(text=response).xpath(
                '//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[3]/text()').extract_first()
            #公司地址
            companyAddr = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[10]/td[2]/text()').extract_first()
            #注册资本
            registCapital = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[1]/td[2]/text()').extract_first()
            #实缴资本
            contributedCapital = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[1]/td[4]/text()').extract_first()
            #公司状态
            status = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[2]/td[2]/text()').extract_first()
            #成立日期
            registTime = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[2]/td[4]/text()').extract_first()
            #统一社会信用代码
            creditCode = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[3]/td[2]/text()').extract_first()
            #纳税人识别号
            registNum = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[3]/td[4]/text()').extract_first()
            #注册号
            registCode = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[4]/td[2]/text()').extract_first()
            #组织机构代码
            organizationCode = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[4]/td[4]/text()').extract_first()
            #公司类型
            companyType = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[5]/td[2]/text()').extract_first()
            #所属行业
            industry = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[5]/td[4]/text()').extract_first()
            #核准日期
            dateApproved = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[6]/td[2]/text()').extract_first()
            #登记机关
            registAuthority = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[6]/td[4]/text()').extract_first()
            #所属地区
            areaName = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[7]/td[2]/text()').extract_first()
            #英文名
            englishName = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[7]/td[4]/text()').extract_first()
            #人员规模
            staffSize = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[8]/td[2]/text()').extract_first()
            #参保人数
            busnissTerm = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[8]/td[4]/text()').extract_first()
            #经营范围
            businessScope = Selector(text=response).xpath(
                '//section[@id="Cominfo"]/table[2]/tr[11]/td[2]/text()').extract_first()
            #董事长
            chairman = Selector(text=response).xpath(
                '//section[@id="partnerslist"]/table/tr[2]/td[2]/table/tr/td[2]/a/h3/text()').extract_first()
            #董事长关联公司
            chairmanUrl = Selector(text=response).xpath(
                '//section[@id="partnerslist"]/table/tr[2]/td[2]/table/tr/td[3]/a/@href').extract_first()
            chairmanUrl='https://www.qichacha.com'+chairmanUrl if chairmanUrl is not None else ' '
            #股东成员
            people = Selector(text=response).xpath(
                '//*[@id="partnerslist"]/table/tr/td[2]/table/tr/td[2]/a/h3/text()').extract()
            #持股比例
            stockPer = Selector(text=response).xpath('//*[@id="partnerslist"]/table/tr/td[3]/text()').extract()
            #认缴出资额
            amountOfContribut = Selector(text=response).xpath('//*[@id="partnerslist"]/table/tr/td[4]/text()').extract()
            mid = map(list, zip(map(self.trip,people),
                                map(self.trip,[i for i in stockPer if i !=' ']),
                                map(self.trip,[i for i in amountOfContribut if i !=' '])))
            #公司股东成员
            groupMembers=[]
            for mem in mid:
                groupMembers.append(dict(zip(['name', 'stockPer', 'amountOfContribut'], mem)))
            data={
                'legalPerson':com['legalPerson'],'phone':phone,'mail':mail,
                'website':website,'companyAddr':companyAddr,'registCapital':registCapital,
                'contributedCapital':contributedCapital,'status':status,
                'registTime':registTime,'creditCode':creditCode,'registNum':registNum,
                'registCode':registCode,'organizationCode':organizationCode,
                'companyType':companyType,'industry':industry,'dateApproved':dateApproved,
                'registAuthority':registAuthority,'areaName':areaName,
                'englishName':englishName,'staffSize':staffSize,'busnissTerm':busnissTerm,
                'businessScope':businessScope,'chairman':chairman,'chairmanUrl':chairmanUrl
            }
            for key in data.keys():
                data.update({key:self.trip(data[key])})
            data.update({'groupMembers':groupMembers})
            companyData.update({comanyName:data})
        return companyData

    #裁剪图片
    def cut_photo(self,img, x0, y0, x1, y1):
        img = Image.open(img)
        width = img.size[0]
        height = img.size[1]
        img = img.crop((
            y0,
            x0,
            width - x1,
            height - y1
        ))
        return img

    #需要会员才能查看
    def people_photo(self):
        companyData=self.company_data()
        companyList=companyData.keys()
        print(companyData)
        with open('qichachaCookie.json', 'r', encoding='utf-8') as f:
            cookie = json.loads(f.read())
        # print(cookie)
        options = webdriver.FirefoxOptions()
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
        browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)
        browser.set_window_size(1100, 900)
        browser.get("https://www.qichacha.com/user_login")
        browser.delete_all_cookies()
        for cook in cookie:
            browser.add_cookie(cook)

        for data in companyList:
            url=companyData[data]['chairmanUrl']
            if url:
                browser.get(url)
                kik = browser.find_element_by_xpath('//*[@id="fixtab"]/ul/li[6]/a/h2')
                action = ActionChains(browser)
                action.click(kik).perform()
                time.sleep(1)
                browser.save_screenshot(companyData[data]['chairman']+'-股权透视图.png')
                self.cut_photo(companyData[data]['chairman']+'-股权透视图.png', 100, 10, 110, 120).save(companyData[data]['chairman']+'-股权透视图.png')
                browser.execute_script("""
                               (function () {
                                    window.scrollBy(0, -580);
                               })();
                           """)
                time.sleep(1)
                browser.save_screenshot(companyData[data]['chairman']+'-关联图谱.png')
                self.cut_photo(companyData[data]['chairman']+'-关联图谱.png', 100, 10, 110, 100).save(companyData[data]['chairman']+'-关联图谱.png')
                browser.execute_script("""
                               (function () {
                                    window.scrollBy(0, -700);
                               })();
                           """)
                time.sleep(1)
                browser.save_screenshot(companyData[data]['chairman']+'-数据分析.png')
                self.cut_photo(companyData[data]['chairman']+'-数据分析.png', 100, 10, 120, 0).save(companyData[data]['chairman']+'-数据分析.png')
            else:
                continue
        browser.close()

    def main(self):
        if not os.path.exists('qichachaCookie.json'):
            self.login()
        companyData = self.company_data()
        print(companyData)


if __name__ == '__main__':
    keyword=input('keyword:')
    qichachaCredit = QichachaCreditNetwork(keyword)
    qichachaCredit.main()

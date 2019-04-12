import requests
import re
from scrapy import Selector
import json
import yundama


class ShenzhenCreditNetwork(object):
    def __init__(self):
        self.session = requests.Session()

    # 验证码
    def verificationCode(self):
        self.session = requests.Session()
        url = "https://www.szcredit.com.cn/xy2.outside/WebPages/Member/CheckCode.aspx"
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.szcredit.com.cn",
            "Referer": "https://www.szcredit.com.cn/xy2.outside/gspt/ShowCheckCode.aspx",
            "Origin": "https://www.szcredit.com.cn",
        }
        content = self.session.get(url, verify=False, headers=header).content
        with open("yzm2.png", "wb") as f:
            f.write(content)
        # 调用打码平台 数字加减的打码类型是6300
        ydm = yundama.YDMHttp(code_type=6300)
        result = ydm.decode(content)
        if result[0] == -3003:
            return None
        return result[1]

    # 传入查询的关键词和验证码
    def keywordSearch(self, keyword, code):
        url = "https://www.szcredit.com.cn/xy2.outside/AJax/Ajax.ashx"
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.szcredit.com.cn",
            "Origin": "https://www.szcredit.com.cn",
        }
        body = {"action": "GetEntList", "ckfull": "false", "keyword": keyword, "source": "", "type": "query",
                "yzmResult": code}
        textJson = self.session.post(url, verify=False, headers=header, data=body).text
        textDict = json.loads(textJson)
        if textDict["status"] == "ok":
            return textDict["resultlist"]
        else:
            return None

    def main(self, keyword):
        while True:
            code = self.verificationCode()
            if code:
                data = self.keywordSearch(keyword, code)
                if data:
                    print("查询成功：" + str(data))
                    return data
                else:
                    print("查询失败，等待重试")
            else:
                print("打码失败，等待重试")


if __name__ == '__main__':
    shenzhenCredit = ShenzhenCreditNetwork()
    shenzhenCredit.main("腾讯")

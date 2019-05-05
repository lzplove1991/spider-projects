# coding: utf-8
import time

import requests


class YDMHttp(object):
    """云打码"""

    api_url = "http://api.yundama.com/api.php"  # 接口
    code_type = 5000  # 打码类型
    timeout = 10  # 超时

    username = ""  # 用户名
    password = ""  # 密码

    app_id = 4988  # 开发者账号APP_ID
    app_key = ""  # 开发者账号APP_KEY

    def __init__(self, code_type=None):
        self.code_type = code_type or self.code_type

    def get_payload(self, **kwargs):
        payload = {
            "method": "",
            "username": self.username,
            "password": self.password,
            "appid": self.app_id,
            "appkey": self.app_key,
            "codetype": self.code_type,
            "timeout": self.timeout,
            "cid": "",
            "flag": "0",
        }
        payload.update(kwargs)
        return payload

    def request(self, data, files=None):
        for _ in range(3):
            try:
                response = requests.post(self.api_url, data=data, files=files)
                if response:
                    return response.json()
            except Exception:
                continue
        else:
            return {}

    def login(self):
        """登录"""
        payload = self.get_payload(method="login")
        response = self.request(payload)
        if response:
            if response.get("ret") and response["ret"] < 0:
                return response["ret"]
            else:
                return response["uid"]
        else:
            return -9001

    def balance(self):
        """查询题分余额"""
        payload = self.get_payload(method="balance")
        response = self.request(payload)
        if response:
            if response.get("ret") and response["ret"] < 0:
                return response["ret"]
            else:
                return response["balance"]
        else:
            return -9001

    def decode(self, byte_stream, code_type=None):
        """打码入口"""
        if code_type:
            self.code_type = code_type

        cid = self.upload(byte_stream)
        if cid > 0:
            for i in range(self.timeout):
                result = self.result(cid)
                if result != "":
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ""
        else:
            return cid, ""

    def upload(self, byte_stream):
        """上传图片验证码"""
        payload = self.get_payload(method="upload")
        response = self.request(payload, {"file": byte_stream})
        if response:
            if response.get("ret") and response["ret"] < 0:
                return response["ret"]
            else:
                return response["cid"]
        else:
            return -9001

    def result(self, cid):
        """获取打码结果"""
        payload = self.get_payload(method="result", cid=cid)
        response = self.request(payload)
        return response.get("text", "")

    def report(self, cid):
        """打码错误反馈"""
        payload = self.get_payload(method="report", cid=cid)
        response = self.request(payload)
        if response:
            return response["ret"]
        else:
            return -9001


if __name__ == '__main__':
    ydm = YDMHttp(code_type=1005)
    with open('./a.gif', 'rb') as f:
        _, captcha = ydm.decode(f.read())
        print(captcha)
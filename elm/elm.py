# coding: utf-8
import requests
import base64


class UserInfo(object):
    def __init__(self):
        self.name = ''
        self.phone = ''
        self.address = ''
        self.total_amount = ''
        self.created_time = ''


class H5Elm(object):
    def __init__(self, mobile, password=None):
        self.mobile = mobile
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            "origin": "https://h5.ele.me",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        self.user_id = ''

    def get_captcha(self):
        url = 'https://h5.ele.me/restapi/eus/v3/captchas'
        data = {'captcha_str': self.mobile}
        response = self.session.post(url, json=data)
        json_data = response.json()
        if response.status_code != 200:
            print(json_data)
            return False
        captcha_hash = json_data.get('captcha_hash')
        captcha_image = json_data.get('captcha_image')
        return {'captcha_hash': captcha_hash, 'captcha_image': captcha_image}

    def mobile_send_code(self, hash=None, image=None):
        url = 'https://h5.ele.me/restapi/eus/login/mobile_send_code'
        data = {"mobile": self.mobile, "captcha_value": "", "captcha_hash": "", "scf": "ms"}
        if hash and image:
            captcha = base64.b64decode(image)
            with open('captcha.jpg', 'wb')as f:
                f.write(captcha)
            captcha = input("图片验证码: ")
            data.update({'captcha_value': captcha, 'captcha_hash': hash})

        response = self.session.post(url, json=data)
        json_data = response.json()
        if response.status_code != 200:
            return False
        validate_token = json_data.get('validate_token')
        return validate_token

    def send_sms(self):
        is_need_captcha = self.mobile_send_code()
        if not is_need_captcha:
            data = self.get_captcha()
            hash = data.get('captcha_hash')
            image = data.get('captcha_image')
            is_need_captcha = self.mobile_send_code(hash, image)
        return is_need_captcha

    def login_by_phone(self, token):
        code = input(': ')
        url = 'https://h5.ele.me/restapi/eus/login/login_by_mobile'
        data = {"mobile": self.mobile, "validate_code": code,
                "validate_token": token, "scf": "ms"}
        response = self.session.post(url, json=data)
        json_data = response.json()

        if json_data.get('need_bind_mobile'):
            print(json_data)
            return False
        self.user_id = json_data.get('user_id')
        return True

    def login_by_password(self):
        pass

    def order_list(self):

        data_list = []

        def _parse(offset):
            url = f'https://www.ele.me/restapi/bos/v2/users/{self.user_id}/orders'
            # 'https://www.ele.me/restapi/bos/v2/users/1922906945/orders?limit=3&offset=0'
            param_data = {
                'limit': '10',
                'offset': offset,
            }
            response = self.session.get(url, params=param_data)
            json_data = response.json()
            if response.status_code != 200:
                return []
            li = []
            for i in json_data:
                unique_id = i.get('unique_id')
                li.append(unique_id)
            return li

        offset = 0
        result = _parse(offset)
        data_list.extend(result)

        while len(result) >= 10:
            offset += 10
            result = _parse(offset)
            data_list.extend(result)

        return data_list

    def order_details(self, unique_id):
        # "https://www.ele.me/restapi/v2/users/1922906945/orders/1228217942352101596"
        # param_data = {
        #     quote('extras[]'): 'rate_info',
        #     quote('extras[]'): 'restaurant',
        #     quote('extras[]'): 'basket',
        #     quote('extras[]'): 'detail_info',
        #     quote('extras[]'): 'operation_pay',
        #     quote('extras[]'): 'operation_rate',
        # }
        li = []
        for i in unique_id:
            url = f'https://www.ele.me/restapi/v2/users/{self.user_id}/orders/{i}?' \
                  f'extras%5B%5D=rate_info&extras%5B%5D=restaurant&extras%5B%5D=' \
                  f'basket&extras%5B%5D=detail_info&extras%5B%5D=operation_pay&extras%5B%5D=operation_rate'
            response = self.session.get(url)
            json_data = response.json()
            if response.status_code != 200:
                print(json_data)
                pass
            info = UserInfo()
            detail_info = json_data.get('detail_info')
            info.name = detail_info.get('consignee')  # 姓名
            info.address = detail_info.get('address')  # 地址
            info.phone = detail_info.get('phone')  # 收件人手机
            info.created_time = detail_info.get('settled_at')  # 下单时间
            info.total_amount = json_data.get('total_amount')  # 费用
            li.append(info.__dict__)
        return li


if __name__ == '__main__':
    h = H5Elm('')
    token = h.send_sms()
    h.login_by_phone(token)
    result = h.order_list()
    result = h.order_details(result)
    print(result)

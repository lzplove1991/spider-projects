# coding: utf-8
import uuid
from datetime import datetime
import requests
from scrapy import Selector
import re
import base64

from app.model.meituan import UserInfoDoc
from app.spider.eleme.base import ResponseObj
from .base import encrypt, get_token
from app.utils.proxies import get_proxies
from app.utils.log import get_logger

logger = get_logger(__name__)


class MeiTuanSpider:

    def __init__(self, phone=None, request_id=None, *args, **kwargs):
        self.session = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

        self.requestId = request_id or str(uuid.uuid4())
        self.phone = phone
        self.hash = ""
        self.validate_token = ""
        self.user_id = ""
        self.model = UserInfoDoc()
        # self.model.meta.id = phone  # 如果要实现数据更新，就启用这个
        self.image_url = ""

    def init(self, **kwargs):
        pass

    def first_request(self):
        self.session.proxies = get_proxies()
        url = 'https://passport.meituan.com/account/unitivelogin?service=waimai&continue=https%3A%2F%2Fwaimai.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3D%252Fnew%252FwaimaiIndex'
        response = self.session.get(url, headers=self.headers)
        csrf = ""
        image_url = ""
        for _ in range(5):
            if response.status_code != 200:
                continue

            selector = Selector(text=response.content)
            csrf = selector.css(".form-field.form-field--ops input")[2].css("::attr(value)").extract_first("")
            image_url = selector.css(".login-captcha-img ::attr(src)").extract_first("")
            break

        return response, csrf, image_url

    def refresh_login_image(self, **kwargs):
        response = self.session.get(url=self.image_url, headers=self.headers)
        img_data = base64.b64encode(response.content).decode()

        return "data:image/jpg;base64,{}".format(img_data)

    def login_by_password(self, **kwargs):
        resp_obj = ResponseObj(
            requestId=self.requestId,
            isSuccessful=False,
            msg='',
            needImageCaptcha=False,
            needSmsCode=False,
            needPassword=False,
        )

        url = 'https://passport.meituan.com/account/unitivelogin?service=waimai&continue=https%3A%2F%2Fwaimai.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3D%252Fnew%252FwaimaiIndex'
        username = kwargs.get("username")
        self.model.phone = username
        password = kwargs.get("password")

        for _ in range(5):
            first_response, csrf, image_url = self.first_request()
            token = get_token(self.headers["User-Agent"], url, first_response)

            data = {
                'email': username,
                'password': encrypt(password, 'mtdp').decode(),
                'captcha': "",
                'origin': 'account-login',
                'fingerprint': '0-5-1-3qd|294|1p',
                'csrf': csrf,
                '_token': token
            }
            headers = {
                "User-Agent": self.headers["User-Agent"],
                'X-Client': 'javascript',
                'X-CSRF-Token': csrf,
                'X-Requested-With': 'XMLHttpRequest'
            }
            try:
                self.session.proxies = get_proxies()
                response = self.session.post(url, headers=headers, data=data)
            except:
                continue

            if response.status_code != 200:
                continue

            json_data = response.json()
            if "error" in json_data:
                if "验证码" in json_data:
                    resp_obj.msg = json_data['error']['message']
                    resp_obj.needImageCaptcha = True
                    break
            else:
                login_token = json_data['data']['token']
                order_list, details = self.order_list()

                if order_list:
                    self.order_details(order_list, details)

                else:
                    self.model.orderList = []

                self.model.updateTime = datetime.now()
                self.model.save()

                resp_obj.msg = "成功"
                resp_obj.isSuccessful = True
                break

        return resp_obj.to_dict()

    def order_list(self):
        url = "http://waimai.meituan.com/customer/order/list"
        details = {}
        self.session.proxies = get_proxies()
        response = self.session.get(url, headers=self.headers)
        order_list = re.findall(r'订单号：([0-9]+)', response.text)

        selector = Selector(text=response.content)

        orders_list = selector.css(".orders-list .order-v")
        for data in orders_list:
            restaurant = data.css(".content .rest-name.clearfix .poi-name ::text").extract_first('')
            restaurantPhone = data.css(".content .rest-name.clearfix .order-total ::text").extract_first('')
            totalPrice = data.css(".content .rest-name.clearfix .order-money-num ::text").extract_first('')

            orderId = data.css(".content .rest-detail .order-id ::text").extract_first('').split("：")[1]
            orderCreateTime = data.css(".content .rest-detail .order-total ::text").extract_first('')

            details[orderId] = {
                "restaurant": restaurant,
                "restaurantPhone": restaurantPhone,
                "totalPrice": totalPrice,
                "orderId": orderId,
                "orderCreateTime": orderCreateTime,
            }

        return order_list, details

    def order_details(self, order_list, details):

        data_list = []
        url = "http://waimai.meituan.com/customer/order/list"
        for order in order_list:
            data = {"viewid": order}

            for _ in range(5):
                self.session.proxies = get_proxies()
                response = self.session.get(url, headers=self.headers, params=data)
                if response is None or response.status_code != 200:
                    continue

                selector = Selector(text=response.content)
                self.model.userId = ""
                receiverAddress = selector.css(".detail-intro.clearfix .fl.dishes .contact p")[0].css(
                    "::text").extract_first("")
                receiverName = selector.css(".detail-intro.clearfix .fl.dishes .contact p")[1].css(
                    "::text").extract_first("")
                receiverPhone = selector.css(".detail-intro.clearfix .fl.dishes .contact p")[2].css(
                    "::text").extract_first("")
                dishName = selector.css(".detail-intro.clearfix .field.clearfix .food-na ::text").extract_first("")

                data_list.append({
                    "receiverAddress": receiverAddress,
                    "receiverName": receiverName,
                    "receiverPhone": receiverPhone,
                    "dishName": dishName,
                    "restaurant": details[order]['restaurant'],
                    "restaurantPhone": details[order]["restaurantPhone"],
                    "totalPrice": details[order]["totalPrice"],
                    "orderId": order,
                    "orderCreateTime": details[order]["orderCreateTime"],
                })
                break

        self.model.orderList = data_list
        return data_list


if __name__ == '__main__':
    m = MeiTuanSpider()
    m.first_request()
    pass

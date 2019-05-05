# coding: utf-8
import sys
sys.path.append('./')
sys.path.append('../')

import time
import random
import base64
import requests
import config

# from urllib import parse
from fdfs_client.client import Fdfs_client

client = Fdfs_client('./client.conf')
img_name = './card_font.jpg'

Default_Header = {
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'http://iac.zjac.org/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

UA_LIST = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
]


class retry(object):
    def __init__(self, max_retries=3, wait=0, exceptions=(Exception,)):
        self.max_retries = max_retries
        self.exceptions = exceptions
        self.wait = wait

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            for i in range(self.max_retries + 1):
                try:
                    result = f(*args, **kwargs)
                except self.exceptions as e:
                    print('waitting', e)
                    time.sleep(self.wait)
                    print('retry %s' % (i + 1))
                    continue
                else:
                    return result
        return wrapper


@retry(2, 0.2)
def download_img(url):
    global client
    Default_Header['User-Agent'] = random.choice(UA_LIST)
    res = requests.get(url, stream=True, headers=Default_Header, timeout=6)
    # print(res.status_code)
    if not res.content or res.status_code != 200:
        print('downerror:', url)
        return None
    else:
        with open(img_name, 'wb') as file:
            file.write(res.content)
        try:
            result = client.upload_by_filename(img_name)
            file_url = result['Remote file_id']
        except:
            client = Fdfs_client('./client.conf')
            result = client.upload_by_filename(img_name)
            file_url = result['Remote file_id']
        # print('file_url:', file_url)
        return file_url


if __name__ == '__main__':
    download_img(url='http://buket-zjac-prod.oss-cn-shenzhen.aliyuncs.com/normal_case_respondent_idfile/299/68659/1046201707270073470008216355_190329151026_%E8%A2%AB%E7%94%B3%E8%AF%B7%E4%BA%BA%E8%BA%AB%E4%BB%BD%E8%AF%81_%E8%A2%AB%E7%94%B3%E8%AF%B7%E4%BA%BA%E8%BA%AB%E4%BB%BD%E8%AF%81_1.jpg?Expires=1554868061&OSSAccessKeyId=LTAIxExjA30dQUr8&Signature=b0KPW%2FxCLD59AdraXEsgENRaVj4%3D')
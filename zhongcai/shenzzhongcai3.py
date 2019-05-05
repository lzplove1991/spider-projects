# coding: utf-8
import sys
sys.path.append('./')
sys.path.append('../')

import re
import time
import random
import json
import requests
import redis
from datetime import datetime

from log import Logger
from model import MXXZjacDoc
from ydm import YDMHttp
from download_img import download_img

import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, password=config.REDIS_PASSWORD, db=4)
rds = redis.Redis(connection_pool=pool)

logfile = "./zjacV2.log"
logger = Logger(logname=logfile, logger="仲裁").getlog()

ydm = YDMHttp(code_type=1005)
reg_tag = re.compile('|'.join(['利率', '金额', '本金', '利息']))
reg_tag2 = re.compile('\d+\.\d+')

property_map = {'借款年利率': 'annualInterestOfBorrowing',
                '合同金额': 'contractAmount',
                '放款金额': 'loanAmount',
                '合同签订时间': 'contractTime  ',
                '借款开始时间': 'borrowingStartTime',
                '借款结束时间': 'borrowingEndTime',
                '借款时常': 'borrowingOften',
                '借款时长单位': 'borrowingTimeUnit',
                '违约时间': 'defaultTime',
                '尚欠本金': 'stillOwedPrincipal',
                '尚欠利息': 'interestOwed',
                '仲裁协议签订时间': 'arbitrationAgreementTime',
                '是否分期（分批）': 'whetherStaging',
                '居间方': 'intermediaryParty',
                '借款用途': 'usageLoan',
                '还款方式': 'repaymentWay',
                '是否涉外': 'whetherForeign',
                }


class ZjacSpider:
    def __init__(self):
        self.post_url = "http://iac.zjac.org/enterprise/loginByAccount"
        self.capt_url = "http://iac.zjac.org/enterprise/captcha/?t="
        self.list_url = "http://iac.zjac.org/enterprise/batchCase/selectCaseByZipId"
        self.detail_url = "http://iac.zjac.org/enterprise/batchCase/getAppBatchCaseDtlById"
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Host': 'iac.zjac.org',
            'Referer': 'http://iac.zjac.org/',
            #'Cookie': '__guid=217509518.4187708485208935000.1554263963760.978; monitor_count=3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

    def login(self):
        payload = {
            'account': '账号',
            'code': '密码',
            'key': 'null',
            'password': '000000',
        }
        while True:
            try:
                resp = self.session.get(self.capt_url+str(int(time.time()*1000)), headers={'User-Agent': self.headers['User-Agent']})
                _, captcha = ydm.decode(resp.content)
                payload['code'] = captcha
                resp = self.session.post(self.post_url, headers=self.headers, data=json.dumps(payload))
                print(resp.status_code)
                json_obj = resp.json()
                print(json_obj)
                self.headers['Authorization'] = json_obj['data']['token']
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '登录成功！')
                break
            except Exception as e:
                print(e)

    def request_list(self, page_number=2855):
        limit = 20
        payload = {
            'id': None,
            'limit': limit,
            'offset': 0,
            'order': 'desc',
            'sort': 'ctime',
        }
        for i in range(page_number):
            logger.debug('currt page:%d' % i)
            print('currt page:%d' % i)
            payload['offset'] = i * limit
            pages = limit if i < page_number - 1 else 0
            while True:
                try:
                    resp = self.session.post(self.list_url, headers=self.headers, data=json.dumps(payload))
                    json_obj = json.loads(resp.text)
                    lens = len(json_obj['rows'])
                    print('rows_len:', lens)
                    logger.info(f"rows_len: {lens}")
                    if lens >= pages:
                        break
                except Exception as e:
                    print('get page err:', e)
                    self.login()
            for item in json_obj['rows']:
                self.request_detail(caseId=str(item['caseId']), ctime=item['ctime'][:19])

    def request_detail(self, caseId, ctime):
        rds.rpush('zjac:_id_reqs', caseId)
        amount = None
        case_info2 = case_info3 = None
        payload = json.dumps({'caseId': caseId})
        for _ in range(4):
            try:
                resp = self.session.post(self.detail_url, headers=self.headers, data=payload)
                json_data = resp.json()
                if resp.status_code == 200 and json_data['code'] == 1:
                    break
            except Exception as e:
                logger.exception(f"err {e}")
                time.sleep(1 + random.random())
        else:
            rds.rpush('zjac:_id_err:', caseId)
            return
        # json_data = resp.json()
        applicant = json_data['data']['appList'][0]['name']

        if 'caseBatchSupplement' in json_data['data']:
            case_info = json_data['data']['caseBatchSupplement']
            case_info2 = dict()
            for key, value in zip(case_info['title'].split('|'), case_info['content'].split('|')):
                if reg_tag.search(key) or reg_tag2.search(value):
                    value = float(value)
                if '时间' in key:
                    try:
                        value = datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")
                    except:
                        pass
                if key == '借款时常':
                    value = eval(value)

                case_info2[key] = value
            case_info3 = dict()
            for key, value in property_map.items():
                case_info3[value] = case_info2[key]

        else:
            amount = float(json_data['data']['baseInfo']['controversyAmount'])
        # respondent = json_data['data']['resList'][0]
        respondent_list = []
        for respondent in json_data['data']['resList']:
            respondent2 = dict()
            respondent2['name'] = respondent['name']
            respondent2['certAddress'] = respondent['certAddress']
            respondent2['phone'] = respondent['phone']
            respondent2['email'] = respondent['email']
            respondent2['otherAddress'] = respondent['otherAddress']
            respondent2['idcard'] = respondent['idcard']
            if 'partyIdfileList' in respondent and len(respondent['partyIdfileList']) > 0:
                if len(respondent['partyIdfileList']) == 1:
                    if '.pdf' in respondent['partyIdfileList'][0]['aliyunOssHref']:
                        return
                    else:
                        card_font = download_img(url=respondent['partyIdfileList'][0]['aliyunOssHref'])
                        if card_font:
                            respondent2['card_front'] = card_font
                else:
                    card_font = download_img(url=respondent['partyIdfileList'][0]['aliyunOssHref'])
                    card_nfont = download_img(url=respondent['partyIdfileList'][1]['aliyunOssHref'])
                    if card_font:
                        respondent2['card_front'] = card_font
                    if card_nfont:
                        respondent2['card_nfront'] = card_nfont
            respondent_list.append(respondent2)
        timeStamp = int(time.mktime(time.strptime(ctime, "%Y-%m-%d %H:%M:%S")))
        # final_data = {'caseId': caseId, 'ctime': ctime, 'timeStamp': timeStamp, 'applicant': applicant, 'respondent': respondent_list}
        case_info3 = case_info3 if case_info3 else None
        amount = amount if amount else None
        result = MXXZjacDoc.make_doc(caseId, ctime, timeStamp, applicant, respondent_list, case_info3, amount)
        print(result)
        # time.sleep(random.random()/3)


if __name__ == '__main__':
    zjac = ZjacSpider()
    zjac.login()
    zjac.request_list()

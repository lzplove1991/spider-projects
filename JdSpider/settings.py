#-*- coding:utf-8 -*-
# author : Zhipei Liu

'''
配置文件，全局参数
'''

# Dalvik/1.6.0 (Linux; U; Android 4.4.2; H60-L03 Build/HDH60-L03)
headers = {
		'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
		'Content-Type': 'application/x-www-form-urlencoded'
		}
#登录时post的数据，不用设置
data = {
		'username':'',
		'pwd':'',
		'remember': 'true',
		's_token': '',
		'dat':'',
		'wlfstk_datk':'',
		'risk_jd[eid]': 'a78174c01e2c4e61abd157e81cbe56f2168545174',
		'risk_jd[fp]': '927e4a3562f7e3ccc7b89cfaedc93a55',
		'risk_jd[token]':'',
		'verifytoken': ''
		}
#更新验证码时post的数据，不用设置
rf_data = {
		'si':'',
		'version': 1,
		'se':'',
		'lang':''
		}

#检测像素点相似度的阈值
threshold = 6

#防止使用eval函数时出错
global false, null, true
false = null = true = ''
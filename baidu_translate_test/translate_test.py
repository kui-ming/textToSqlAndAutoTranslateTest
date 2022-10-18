#
import hashlib
import requests
import time
import tools

baidu_appid = '20221013001390820'
secret_key = 'QaauYH2crzb8xL2_KMIw'

headers = {'Content-Type': 'application/x-www-form-urlencoded'}


def translate(query, auto=False):
    body = {
        'q': '',  # 待翻译原文本
        'from': 'auto',  # 中文，可设为自动判断
        'to': 'en',  # 转英文
        'appid': baidu_appid,
        'salt': '',
        'sign': '',
        'tts': 0,
        'dict': 0,
    }
    # 检查源文本，判断是否返回中文或英文
    if not tools.is_contains_chinese(query) and auto:  # 是否存在中文，并且自动转换开启
        body['to'] = 'zh'   # 源文本不存在中文则转为英文
    body['q'] = query
    body['salt'] = str(int(time.time()))
    body['sign'] = sign(query, body['salt'])
    res = requests.post('http://api.fanyi.baidu.com/api/trans/vip/translate', body, headers=headers)
    res.close()
    return res.json()


def sign(query, salt):
    text = baidu_appid+query+salt+secret_key
    md5 = hashlib.md5(text.encode('utf8'))
    return md5.hexdigest()  # 32位小写md5值



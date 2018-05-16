#!/usr/bin/env python
# coding:utf-8
import requests, re, time


def yima_getphonenum():
    username = ''  # 填入易码的用户名
    passwords = ''  # 填入易码的密码
    login_data = {'action': 'login', 'username': username, 'password': passwords}
    response = requests.get(url, params=login_data)
    if 'success' not in response.text:
        print response.text
        print u'易码登录失败'
        exit()
    else:
        TOKEN = response.text.replace('success|', '')
        getmobile_data = {'action': 'getmobile', 'token': TOKEN, 'itemid': 304}
        response = requests.get(url, params=getmobile_data)
        if 'success' not in response.text:
            print response.text
            print u'获取手机号失败'
            exit()
        else:
            phonenum = response.text.replace('success|', '')
            return TOKEN, phonenum


def yima_getsms(TOKEN, phonenum):
    getsms_data = {'action': 'getsms', 'token': TOKEN, 'itemid': 304, 'mobile': int(phonenum), 'release': 1}
    response = requests.get(url, params=getsms_data)
    for i in range(8):
        if 'success' in response.text:
            try:
                code = re.search(u'验证码为：(.{6})，该验证码', response.text).group(1)
                print u'验证码为：' + code
                return code
            except Exception, e:
                print e
                print u'接收验证码失败'
                yima_numrelease(TOKEN, phonenum)
                exit()
        elif '3001' in response.text:
            print u'正在获取验证码中...'  # 短信尚未到达
        else:
            print response.text
            print u'接收验证码失败'
            yima_numrelease(TOKEN, phonenum)
            exit()
        time.sleep(5)
    print u'接收验证码超时'
    yima_numrelease(TOKEN, phonenum)
    exit()


def yima_numrelease(TOKEN, phonenum):
    release_data = {'action': 'addignore', 'token': TOKEN, 'itemid': 304, 'mobile': int(phonenum)}
    response = requests.get(url, params=release_data)
    if 'success' not in response.text:
        print response.text
        print u'拉黑号码失败'
        exit()
    else:
        print u'已释放号码'


if __name__ == '__main__':
    url = 'http://api.fxhyd.cn/UserInterface.aspx'

    header = {'Host': 'login.zbj.com',
              'Origin': 'https://login.zbj.com',
              'Referer': 'https://login.zbj.com/register?fromurl=https%3A%2F%2Fwww.zbj.com%2F',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    token, phonenum = yima_getphonenum()
    print u'已获取手机号：' + phonenum
    verify_data = [('sacc', phonenum), ('gt_type', 'register')]

    r = requests.session()
    response = r.post('https://login.zbj.com/register/sendRegisterCode', data=verify_data, headers=header)  # 发送验证码
    if u'发送成功' in response.text:
        print u'验证码已发送'
    elif u'请先进行验证' in response.text:
        print u'该ip获取验证码次数较多，需换ip后重试'
        yima_numrelease(token, phonenum)
        exit()
    else:
        print response.text
        print u'验证码发送失败'
        yima_numrelease(token, phonenum)
        exit()

    code = yima_getsms(token, phonenum)  # 接收到的验证码
    password = str(phonenum)[5:11]  # 左闭右开

    union = 'referer=&first_page=https%3A%2F%2Fwww.zbj.com%2F&pmcode=&adunion_lead_id=&stt=&uncode=&uncode_extid=&pub_page=https%3A%2F%2Flogin.zbj.com%2Fregister%3Ffromurl%3Dhttps%253A%252F%252Fwww.zbj.com%252F'
    regist_data = [('sacc', phonenum), ('password', password), ('code', code), ('intention', '1'), ('union', union)]
    response = r.post('https://login.zbj.com/register/register', data=regist_data, headers=header)  # 注册
    print response.text

    response = r.get('https://i.zbj.com/registersuccess?fromUrl=https%3A%2F%2Fwww.zbj.com%2F', headers=header)
    if u'注册成功' in response.text:
        print u'注册成功\n账号是：%s\n密码是：%s' % (phonenum, password)
    else:
        print response.text
        print u'注册失败'

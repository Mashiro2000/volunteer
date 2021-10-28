# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/20
# @Author  : MashiroF
# @File    : index.py
# @Software: PyCharm

# 系统自带库
import os
import sys
import hmac
import time
import base64
import random
import hashlib
import urllib.parse

# 第三方库
try:
    import requests
except ModuleNotFoundError:
    print("缺少requests依赖！程序将尝试安装依赖！")
    os.system("pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

# 配信文件
try:
    from sendNotify import send
except Exception as error:
    print('推送文件导入失败')
    print(f'失败原因:{error}')
    sys.exit(0)

# 用户文件
try:
    from account import accounts
except Exception as error:
    print('用户导入失败')
    print(f'失败原因:{error}')
    sys.exit(0)

# 配信内容格式
allMess = ''
def notify(content=None):
    global allMess
    allMess = allMess + content + '\n'
    print(content)

# 日志录入时间
notify(f"任务:志愿汇益动星空\n时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")

class Volunteer:
    def __init__(self,dic):
        self.AccessKeyId = '16437d7b750546789da84ee4d50e92f2'       # 不可修改
        self.app = "android"                                        # 无IOS，不清楚
        self.city = ''                                              # 城市id，可修改
        self.dic = dic                                              # 账号信息，不可改
        self.key = '928c5f59f3ce40b1a3850b828685a816'               # 密钥，不可改
        self.version = '4.8.5'                                      # 版本号
        self.sess = requests.session()                              # 以下UA可自定义
        self.sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; P40 Build/NZH54D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
        })

    # HMAC-SHA1加密
    def calculateSignature(self,key,stringToSign):
        return base64.b64encode(hmac.new(key.encode('utf-8'), stringToSign.encode('utf-8'), hashlib.sha1).digest()).decode()

    # URL编码
    def percentEncode(self,value,flag='str'):
        '''flag=0 -> encodeStr (default)
            flag=1 -> encodeDict'''
        if flag == 'str':
            return urllib.parse.quote(string=value,encoding='utf-8').replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        elif flag == 'dic':
            return urllib.parse.urlencode(query=value,encoding='utf-8').replace("+", "%20").replace("*", "%2A").replace("%7E", "~")

    # 获取签名
    def getSignature(self,data,key):
        newData = {}
        for each in sorted(data):
            newData[each] = data[each]
        str = '' + self.percentEncode(value=newData,flag='dic')
        params ="POST&" + urllib.parse.quote('/', safe='') + "&" + self.percentEncode(value=str,flag='str')
        return self.calculateSignature(key=key + '&',stringToSign=params)

    # 获取令牌
    def getToken(self):
        url = 'https://api.zyh365.com/api/volunteer/login_app.do'
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "token": "",
            "appid": self.app,
            "version": self.version,
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "api.zyh365.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        data = {
            'AccessKeyId':self.AccessKeyId,
            'CurrentVersion':self.version,
            'Format':'json',
            'SignatureMethod':'HMAC-SHA1',
            'SignatureNonce':'1234567890',
            'SignatureVersion':'1.0',
            'Timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            'app_city':self.city,
            'app_id':self.app,
            'app_zyzid':'',
            'password':self.dic['password'],
            'sourceid':self.app,
            'username':self.dic['username']
        }
        data.update({
            "Signature":self.getSignature(data=data, key=self.key)
        })
        response = self.sess.post(url=url,headers=headers,data=data).json()
        time.sleep(random.randint(5,7))
        if response['errCode'] == '0000':
            self.loginData = response
            notify(f"账号:{self.dic['nickname']}\t状态:获取Token成功")
            return True
        else:
            notify(f"账号:{self.dic['nickname']}\t状态:获取Token失败！\t原因:{response}")
            return False

    # 获取活动CK(访问该页面表示登录)
    def getStarCookie(self):
        url = 'https://m.zyh365.com/html/2021/hottest-public-welfare-campus-activities/index.html'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "m.zyh365.com",
            "X-Requested-With": "com.zzw.october",
            "__zyh_app_token__": self.loginData['shareToken']
        }
        cookies = {
            '__zyh_app_id__':self.app,
            '__zyh_app_token__':self.loginData['shareToken'],
            '__zyh_app_city_id__':self.city,
            '__zyh_app_version__':self.version
        }
        params = {
            "app_city": self.city,
            "app_id": self.app,
            "app_token": self.loginData['shareToken'],
            "app_zyzid": self.loginData['zyzid'],
            "apptype": "client",
            "time": round(time.time() * 1000),
            "version": self.version
        }
        self.sess.post(url=url,headers=headers,cookies=cookies,params=params)
        time.sleep(random.randint(3,5))
        if self.sess.cookies.get_dict():
            self.ActivityCK = self.sess.cookies.get_dict()
            return True
        else:
            return False

    # 获取能量值，学校ID等信息
    def getEnergy(self):
        url = 'https://m.zyh365.com/other-school5/zyz-detail'
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/2021/hottest-public-welfare-campus-activities/schools.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        cookies = {
            "HWWAFSESTIME": self.ActivityCK['HWWAFSESTIME'],
            "__zyh_app_token__": self.loginData['shareToken'],
            "app_zyzid": self.loginData['zyzid'],
            "HWWAFSESID": self.ActivityCK['HWWAFSESID']
        }
        params = {
            'app_id':'h5'
        }
        data = {
            'zyzid':self.loginData['zyzid']
        }
        response = self.sess.post(url=url,headers=headers,cookies=cookies,params=params,data=data).json()
        if response['errCode'] == '0000':
            self.energyInfo = response['data']
            notify(f"账号:{self.dic['nickname']}\t能量总数:{self.energyInfo['totalCharged']}\t待用能量:{self.energyInfo['energy']}")
            time.sleep(random.randint(3,5))
            if self.energyInfo['energy'] != 0:
                return True
            else:
                return False
        else:
            notify(f"{self.dic['nickname']}\t充能失败\t原因:{response}")
            return False


    # 充飞船能
    def pushEnergy(self):
        url = 'https://m.zyh365.com/other-school5/school-charged'
        params = {
            'app_id':'h5'
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/2021/hottest-public-welfare-campus-activities/schools.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        cookies = {
            "HWWAFSESTIME": self.ActivityCK['HWWAFSESTIME'],
            "__zyh_app_token__": self.loginData['shareToken'],
            "app_zyzid": self.loginData['zyzid'],
            "sid": self.energyInfo['sid'],
            "HWWAFSESID": self.ActivityCK['HWWAFSESID']
        }
        data = {
            "energy": self.energyInfo['energy'],
            "schoolid": self.energyInfo['sid'],
            "zyzid": self.loginData['zyzid']
        }
        response = self.sess.post(url=url,params=params,headers=headers,cookies=cookies,data=data).json()
        if response['errCode'] == '0000':
            notify(f"账号:{self.dic['nickname']}\t状态:充能成功")
        else:
            notify(f"账号:{self.dic['nickname']}\t状态:充能失败\t原因:{response}")
        time.sleep(random.randint(3,5))

    # 获取视频
    def getVideo(self):
        url = 'https://m.zyh365.com/zycollege/index-course-list'
        params = {
            'app_id':'h5'
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/2020/zhihuiSchool/project/",
            "X-Requested-With": "com.zzw.october"
        }
        cookies = {
            "HWWAFSESTIME": self.ActivityCK['HWWAFSESTIME'],
            "__zyh_app_token__": self.loginData['shareToken'],
            "app_zyzid": self.loginData['zyzid'],
            "HWWAFSESID": self.ActivityCK['HWWAFSESID'],
            "__zyh_app_zyzid__":self.loginData['zyzid']
        }
        response = self.sess.post(url=url,params=params,headers=headers,cookies=cookies).json()
        if response['errCode'] == '0000':
            for each in response['data']:
                if each['specialName'] == '免费专区':
                    self.getVideoInfo(random.choice(each['list']))
                    # for index in each['list']:
                    #     if index['title'] == '绿色公开课':
                    #         self.getVideoInfo(index)
            time.sleep(random.randint(3,5))

    # 获取视频信息
    def getVideoInfo(self,video):
        url = 'https://m.zyh365.com/zycollege/course-detail'
        params = {
            'app_id':'h5'
        }
        data = {
            "cid": video['cid'],
            "token": self.loginData['shareToken']
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/2020/zhihuiSchool/project/",
            "X-Requested-With": "com.zzw.october"
        }
        cookies = {
            "HWWAFSESTIME": self.ActivityCK['HWWAFSESTIME'],
            "__zyh_app_token__": self.loginData['shareToken'],
            "app_zyzid": self.loginData['zyzid'],
            "HWWAFSESID": self.ActivityCK['HWWAFSESID'],
            "__zyh_app_zyzid__":self.loginData['zyzid']
        }
        response = self.sess.post(url=url,params=params,data=data,headers=headers,cookies=cookies).json()
        if response['errCode'] == '0000':
            notify(f"账号:{self.dic['nickname']}\t视频系列:{response['data']['title']}\t开始观看...")
            for each in response['data']['courseList']:
                self.uploadTime(each)
        time.sleep(random.randint(3,5))

    # 上传观看时长
    def uploadTime(self,dic):
        url = 'https://m.zyh365.com/zycollege/course-time'
        params = {
            'app_id':'h5'
        }
        data = {
            "lid": dic['lid'],
            "token":self.loginData['shareToken'],
            "viewTime": random.randint(60,100)
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/2020/zhihuiSchool/project",
            "X-Requested-With": "com.zzw.october"
        }
        cookies = {
            "HWWAFSESTIME": self.ActivityCK['HWWAFSESTIME'],
            "__zyh_app_token__": self.loginData['shareToken'],
            "__zyh_app_zyzid__": self.loginData['zyzid'],
            "app_zyzid": self.loginData['zyzid'],
            "HWWAFSESID": self.ActivityCK['HWWAFSESID']
        }
        response = self.sess.post(url=url,params=params, headers=headers,data=data,cookies=cookies).json()
        if response['errCode'] != '0000':
            notify(f"账号:{self.dic['nickname']}\t视频:{dic['title']}\t分P:{dic['no']}\t浏览失败，原因:{response}")
        time.sleep(random.randint(1,3))

    # 获取答案
    def getAnswer(self,subjectId):
        answerUrl = 'https://m.zyh365.com/other-knowledge/subject-answer'
        params = {
            'app_id':'h5'
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/publicWelfareClass/index.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        for index in range(1,3):
            answerData = {
                'app_zyzid':'',
                'subjectid':subjectId,
                'answer':index
            }
            result = requests.post(url=answerUrl, headers=headers, data=answerData,params=params).json()
            if result['errCode'] == '0000' and  result['message'] == '回答正确':
                return index
            time.sleep(random.randint(3,5))

    # 小课堂
    def answerQuestion(self):
        detailUrl = 'https://m.zyh365.com/other-knowledge/subject-detail'
        answerUrl = 'https://m.zyh365.com/other-knowledge/subject-answer'
        params = {
            'app_id':'h5'
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "m.zyh365.com",
            "Origin": "https://m.zyh365.com",
            "Referer": "https://m.zyh365.com/html/publicWelfareClass/index.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        detailData = {
            'zyzid':self.loginData['zyzid'],
        }
        subjectData = requests.post(url=detailUrl, headers=headers, data=detailData,params=params).json()
        if subjectData['data']['answer'] == 1:
            notify(f"账号:{self.dic['nickname']}\t问题:已回答")
            return None
        else:
            notify(f"账号:{self.dic['nickname']}\t问题:{subjectData['data']['subject']}")
            answerData = {
                'zyzid':self.loginData['zyzid'],
                'subjectid':subjectData['data']['subjectid'],
                'answer':self.getAnswer(subjectData['data']['subjectid'])
            }
            response = requests.post(url=answerUrl, headers=headers, data=answerData,params=params).json()
            notify(f"账号:{self.dic['nickname']}\t回答结果:{response['message']}")

# 适配云函数
def main_handler(event, context):
    for each in accounts:
        if all(each.values()):
            volunteer = Volunteer(each)
            if volunteer.getToken() == True:                # 获取登录Token
                if volunteer.getStarCookie() == True:       # 获取星空活动CK
                    volunteer.getVideo()                    # 观看视频
                    volunteer.answerQuestion()              # 回答问题
                    if volunteer.getEnergy() == True:       # 获取能量值
                        volunteer.pushEnergy()              # 为飞船充能
            time.sleep(random.randint(3,5))
            notify('*' * 28 + '\n')
    send('志愿汇益动星空',allMess)

if __name__ == '__main__':
    main_handler(None,None)
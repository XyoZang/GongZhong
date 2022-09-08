# -*- coding: UTF-8 -*-
 
from ast import While
import datetime
from datetime import date
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from time import time, localtime
from requests import get, post
import sys
import os
import http.client, urllib
import json

# **************************参数设置**********************
debug = True
# ************姨妈期持续时间*******
jq_last = 6
JQ_LAST = jq_last - 1
JQ_LAST_OMEGA = 0
# ************姨妈周期************
JQ_CYCLE = 35
JQ_CYCLE_OMEGA = -1
# 姨妈后几天到排卵期
PL_PRE = 10
# 排卵期持续时间
PL_LAST = 9

# ************变量定义*************

today = datetime.datetime.now()

start_date = '2020-11-14'
city = '西青区'
birthday = '10-01'
app_id = 'wx5ce3f89272cc2282'
app_secret = '5f17e2de6d20c64204c0a3b53552d99d'
user_id1 = 'o8xxF6JSERgFERmnVAKKsxRaiT_g'
user_id2 = 'o8xxF6I7IEthBN2mezw_LMsfZyeE'
template_id1 = 'CcOtAUWSHMkGA7_or2F6yDEGWjK-Z_Sw-HrgDVaf4PY'
template_id_aq = 'XKGDzS55Uxx0kLeBt7kSmvDuB78SrBL3TgPtRA_6fIQ'
template_id_pl = 'dRuAtLAI2KFRRWVYJ5jj6x7BRf0ipLy5qbQ3gAsuQ60'
template_id_jq = 't9RPYCzYcgEF7O_ETZHz65K1yz4E1xohOVa4ynz5UXk'
template_id_wan = '_6xW1solFvsRTZm20mZ7rK5ep9o_mMVKn27mk6Wa_d0'
template_id_word = '95e_SbNmk945YHn2nFzk1qy3LsRVw_pmW7WtmPv7O_A'

# 恋爱纪念日
# start_date = os.environ['START_DATE']
# province = os.environ['PROVINCE']
# city = os.environ['CITY']

# 小宝的生日
# birthday = os.environ['BIRTHDAY']

# 测试号Token
# app_id = os.environ["APP_ID"]
# app_secret = os.environ["APP_SECRET"]

# 用户ID与消息模板，id1为早安提醒
# user_id1 = os.environ["USER_ID1"]
# user_id2 = os.environ["USER_ID2"]
# template_id1 = os.environ["TEMPLATE_ID1"]
# template_id_aq = os.environ["TEMPLATE_ID_aq"]
# template_id_pl = os.environ["TEMPLATE_ID_pl"]
# template_id_jq = os.environ["TEMPLATE_ID_jq"]


# FIRST_START,自记录起第一次姨妈来临时间
first_start = '2022-07-23'
FIRST_START = datetime.datetime.strptime(first_start, "%Y-%m-%d")

# FIRST_END,自记录起第一次姨妈结束时间
FIRST_END = FIRST_START + datetime.timedelta(days=JQ_LAST)
first_end = FIRST_END.strftime("%Y-%m-%d")

# NEXT_start,预计本次姨妈来临时间
NEXT_start = FIRST_START + datetime.timedelta(days=JQ_CYCLE)
next_start = NEXT_start.strftime("%Y-%m-%d")

NEXT_end = NEXT_start + datetime.timedelta(days=JQ_LAST)
next_end = NEXT_end.strftime("%Y-%m-%d")

# 本次姨妈日期（姨妈中）/上次姨妈日期/下次姨妈日期的判断与计算
def Date_JQ(NEXT_start, NEXT_end):
    if FIRST_END < today < NEXT_start:
        LAST_start = FIRST_START
        LAST_end = FIRST_END
        NEXT_start = LAST_start + datetime.timedelta(days=JQ_CYCLE)
        NEXT_end = NEXT_start + datetime.timedelta(days=JQ_LAST)
    if today > NEXT_start:
        LAST_start = NEXT_start
        LAST_end = NEXT_end
        NEXT_start = LAST_start+ datetime.timedelta(days=JQ_CYCLE)
        NEXT_end = NEXT_start + datetime.timedelta(days=JQ_LAST)
        while (today > NEXT_start):
            LAST_start = NEXT_start
            LAST_end = NEXT_end
            NEXT_start = LAST_start + datetime.timedelta(days=JQ_CYCLE)
            NEXT_end = NEXT_start + datetime.timedelta(days=JQ_LAST)
        NEXT_start = NEXT_start + datetime.timedelta(days=JQ_CYCLE_OMEGA)
        NEXT_end = NEXT_end + datetime.timedelta(days=JQ_LAST_OMEGA)
    return LAST_start, LAST_end, NEXT_start, NEXT_end

# ***************早安提醒*******************
def get_weather(city):
    conn = http.client.HTTPSConnection('api.tianapi.com')  #接口域名
    params = urllib.parse.urlencode({'key':'6a350d344f255cb49085462f2e173d19','city': city})
    headers = {'Content-type':'application/x-www-form-urlencoded'}
    conn.request('POST','/tianqi/index',params,headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    info = json.loads(data)
    week = info['newslist'][0]['week']
    nowtem = info['newslist'][0]['real']
    weather1 = info['newslist'][0]['weather']
    lowtem1 = info['newslist'][0]['lowest']
    hightem1 = info['newslist'][0]['highest']
    wind1 = info['newslist'][0]['windsc']
    rain1 = info['newslist'][0]['pop']
    weather2 = info['newslist'][1]['weather']
    lowtem2 = info['newslist'][1]['lowest']
    hightem2 = info['newslist'][1]['highest']
    wind2 = info['newslist'][1]['windsc']
    rain2 = info['newslist'][1]['pop']
    tips = info['newslist'][0]['tips']
    return week, tips, nowtem, weather1, weather2, lowtem1, lowtem2, hightem1, hightem2, wind1, wind2, rain1, rain2

def get_health():
    conn = http.client.HTTPSConnection('api.tianapi.com')  #接口域名
    params = urllib.parse.urlencode({'key':'6a350d344f255cb49085462f2e173d19'})
    headers = {'Content-type':'application/x-www-form-urlencoded'}
    conn.request('POST','/healthtip/index',params,headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    info = json.loads(data)
    health = info['newslist'][0]['content']
    return health

def get_air():
    conn = http.client.HTTPSConnection('api.tianapi.com')  #接口域名
    params = urllib.parse.urlencode({'key':'6a350d344f255cb49085462f2e173d19','area':city})
    headers = {'Content-type':'application/x-www-form-urlencoded'}
    conn.request('POST','/aqi/index',params,headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    info = json.loads(data)
    air = info['newslist'][0]['quality']
    return air

def get_wan():
    url = 'https://api.mcloc.cn/love?type=json'
    r = requests.get(url)
    response = r.json()
    word = response['data']
    return word

# 恋爱时长计算
def get_count():
  delta = today - datetime.datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday():
  next = datetime.datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days + 1

# 经期来临倒计时
def JQ_count(NEXT_start):
  # days_left，离经期还剩多少天
  Days_left = NEXT_start - today
  return Days_left.days + 1

# 经期结束倒计时
def End_count(NEXT_end):
    # 本次姨妈期结束倒计时，end_day为本次姨妈结束时间
    Days_left = NEXT_end - today
    return Days_left.days + 2

# 排卵期计算
def PL_count(LAST_end):
    # end_day为本次姨妈结束时间，days_left为本次姨妈期倒计时，days_left在这里无用处
    # 以本次姨妈结束日期和姨妈后排卵期来临时间来计算排卵期来临日期
    PL_start = LAST_end + datetime.timedelta(days=PL_PRE)
    # 排卵期来临日期加持续日期为排卵期结束日期
    PL_end = PL_start + datetime.timedelta(days=PL_LAST)
    return PL_start, PL_end

# 排卵期来临与结束倒计时
def PL_cng(LAST_end):
    PL_start, PL_end = PL_count(LAST_end)
    PL_come =  PL_start - today
    PL_go = PL_end -today
    return PL_come.days, PL_go.days

def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en

def case_shanbay():
    sb_url = "https://apiv3.shanbay.com/weapps/dailyquote/quote/?date=" + str(today)
    result = {}
    record = requests.get(sb_url).json()
    result['date'] = today
    word_ch = record["translation"]
    word_en = record["content"]
    return word_en, word_ch

# 经期状态判断
def get_status(NEXT_start, NEXT_end, LAST_end):
    PL_start, PL_end = PL_count(LAST_end)
    global THIS_START, THIS_END
    if NEXT_start <= today <= NEXT_end:
        THIS_START = NEXT_start
        THIS_END = NEXT_end
        JQstatus = "经期中"
        Corstatus = "#C70000"
    elif PL_start <= today <= PL_end:
        JQstatus = "排卵期"
        Corstatus = "#ECEC94"
    else:
        JQstatus = "安全期"
        Corstatus = "#66F970"
    return JQstatus, Corstatus

# ****************主程序-早安提醒******************
if __name__ == "__main__":

    now = str(today.hour)
    now = int(now)
    air = get_air()
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    week, tips, nowtem, weather1, weather2, lowtem1, lowtem2, hightem1, hightem2, wind1, wind2, rain1, rain2 = get_weather(city)
    note_ch, note_en = get_ciba()
    word_en, word_ch = case_shanbay()
    health = get_health()
    if now < 12:
        morning_data = {
                "date": {
                    "value": "{} {}".format(today.strftime('%Y-%m-%d'), week),
                    "color": "#00FFFF"
                    },
                "city": {
                    "value": city,
                    "color": "#808A87"
                    },
                "weather": {
                    "value": weather1,
                    "color": "#ED9121"
                    },
                "now_temperature": {
                    "value": nowtem,
                    "color": "#ED9121"
                    },    
                "min_temperature": {
                    "value": lowtem1,
                    "color": "#00FF00"
                    },
                "max_temperature": {
                    "value": hightem1,
                    "color": "#FF6100"
                },
                "wind": {
                    "value": wind1,
                    "color": "#4682B4"
                },
                "rain": {
                    "value": rain1,
                    "color": "#1E90FF"
                },
                "air": {
                    "value": air,
                    "color": "#00CED1"
                },
                "tips": {
                    "value": tips,
                    "color": "#F4A460"
                },
                "love_day": {
                    "value": get_count(),
                    "color": "#87CEEB"
                },
                "birthday": {
                    "value": get_birthday(),
                    "color": "#FF8000"
                },
                "note_en": {
                    "value": note_en,
                    "color": "#173177"
                },
                "note_ch": {
                    "value": note_ch,
                    "color": "#173177"
                },
            }
        if debug == True:
            res = wm.send_template(user_id1, template_id1, morning_data)
        else:
            res = wm.send_template(user_id1, template_id1, morning_data)
            res = wm.send_template(user_id2, template_id1, morning_data)
        print(res)

    # *******************经期提醒***********************
        LAST_start_now, LAST_end_now, NEXT_start_now, NEXT_end_now = Date_JQ(NEXT_start, NEXT_end)
        now_status, color_status = get_status(NEXT_start_now, NEXT_end_now, LAST_end_now)
        PL_come, PL_go = PL_cng(LAST_end_now)
        PL_start, PL_end = PL_count(LAST_end_now)
        Days_left = End_count(NEXT_end_now)
        if now_status == '安全期':
            template_id = template_id_aq
            JQ_data = {
                "Now_Status":{
                    "value": now_status,
                    "color": color_status
                    },
                "last_JQ":{
                    "value": "{}".format(LAST_start_now.strftime('%Y-%m-%d')),
                    "color": "#ED9121"
                    },
                "end_JQ":{
                    "value": "{}".format(LAST_end_now.strftime('%Y-%m-%d')),
                    "color": "#808A87"
                    },
                "next_JQ":{
                    "value": "{}".format(NEXT_start_now.strftime('%Y-%m-%d')),
                    "color": "#FF6100",
                    },
                "days_left":{
                    "value": JQ_count(NEXT_start_now),
                    "color": "#FF8000"
                    },
                "PL_start":{
                    "value": PL_come,
                    "color": "#FF8000"
                    },
                "health": {
                    "value": health,
                    "color": "#BC8F8F"
                },
                "word_en":{
                    "value": word_en,
                    "color": "#173177"
                    },
                "word_ch":{
                    "value": word_ch,
                    "color": "#173177"
                    }
            }
        if now_status == '排卵期':
            template_id = template_id_pl
            JQ_data = {
                "Now_Status":{
                    "value": now_status,
                    "color": color_status
                    },
                "last_JQ":{
                    "value": "{}".format(LAST_start_now.strftime('%Y-%m-%d')),
                    "color": "#ED9121"
                    },
                "end_JQ":{
                    "value": "{}".format(LAST_end_now.strftime('%Y-%m-%d')),
                    "color": "#808A87"
                    },
                "next_JQ":{
                    "value": "{}".format(NEXT_start_now.strftime('%Y-%m-%d')),
                    "color": "#FF6100",
                    },
                "days_left":{
                    "value": JQ_count(NEXT_start_now),
                    "color": "#FF8000"
                    },
                "PL_end":{
                    "value": PL_go,
                    "color": "#FF8000"
                    },
                "health": {
                    "value": health,
                    "color": "#BC8F8F"
                },
                "word_en":{
                    "value": word_en,
                    "color": "#173177"
                    },
                "word_ch":{
                    "value": word_ch,
                    "color": "#173177"
                    }
            }    
        if now_status == '经期中':
            template_id = template_id_jq
            JQ_data = {
                "Now_Status":{
                    "value": now_status,
                    "color": color_status
                    },
                "next_JQ":{
                    "value": "{}".format(NEXT_start_now.strftime('%Y-%m-%d')),
                    "color": "#ED9121"
                    },
                "nextend_JQ":{
                    "value": "{}".format(NEXT_end_now.strftime('%Y-%m-%d')),
                    "color": "#808A87"
                    },
                "days_left":{
                    "value": Days_left,
                    "color": "#FF8000"
                    },
                "health": {
                    "value": health,
                    "color": "#BC8F8F"
                },
                "word_en":{
                    "value": word_en,
                    "color": "#173177"
                    },
                "word_ch":{
                    "value": word_ch,
                    "color": "#173177"
                }
            }
        if debug == True:
            res = wm.send_template(user_id1, template_id, JQ_data)
        else:
            res = wm.send_template(user_id1, template_id, JQ_data)
            res = wm.send_template(user_id2, template_id, JQ_data)
        print(res)

    # ******************明日天气提醒***********
    if now > 13:
        word = get_wan()
        tommorow = today + datetime.timedelta(days=1)
        week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
        week = week_list[tommorow.isoweekday() % 7]
        wan_data = {
                "date": {
                    "value": "{} {}".format(tommorow.strftime('%Y-%m-%d'), week),
                    "color": "#00FFFF"
                    },
                "city": {
                    "value": city,
                    "color": "#808A87"
                    },
                "weather": {
                    "value": weather2,
                    "color": "#ED9121"
                    },
                "now_temperature": {
                    "value": nowtem,
                    "color": "#ED9121"
                    },    
                "min_temperature": {
                    "value": lowtem2,
                    "color": "#00FF00"
                    },
                "max_temperature": {
                    "value": hightem2,
                    "color": "#FF6100"
                },
                "wind": {
                    "value": wind2,
                    "color": "#4682B4"
                },
                "rain": {
                    "value": rain2,
                    "color": "#1E90FF"
                },
                "air": {
                    "value": air,
                    "color": "#00CED1"
                },
                "tips": {
                    "value": tips,
                    "color": "#F4A460"
                },
                "note_en": {
                    "value": note_en,
                    "color": "#173177"
                },
                "note_ch": {
                    "value": note_ch,
                    "color": "#173177"
                },
            }
        word_data = {
                "words": {
                    "value": word,
                    "color": "#000080"
                },
        }
        if debug == True:
            res = wm.send_template(user_id1, template_id_wan, wan_data)
            print(res)
            res = wm.send_template(user_id1, template_id_word, word_data)
            print(res)
        else:
            res = wm.send_template(user_id1, template_id_wan, wan_data)
            res = wm.send_template(user_id1, template_id_word, word_data)
            res = wm.send_template(user_id2, template_id_wan, wan_data)
            res = wm.send_template(user_id2, template_id_word, word_data)
        os.system("pause")

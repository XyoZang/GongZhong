import datetime
from datetime import date
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from time import time, localtime
import cityinfo
from requests import get, post
import sys
import os

# ************参数设置*************
debug = False
jq_last = 6
JQ_last = jq_last - 1
JQ_cycle = 30
PL_pre = 10
PL_last = 9

# ************变量定义*************

today = datetime.datetime.now()
start_date = os.environ['START_DATE']
province = os.environ['PROVINCE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id1 = os.environ["USER_ID1"]
user_id2 = os.environ["USER_ID2"]
template_id1 = os.environ["TEMPLATE_ID1"]
template_id_aq = os.environ["TEMPLATE_ID_aq"]
template_id_pl = os.environ["TEMPLATE_ID_pl"]
template_id_jq = os.environ["TEMPLATE_ID_jq"]

last_JQ = os.environ['LAST_JQ']
Last_JQ = datetime.datetime.strptime(last_JQ, "%Y-%m-%d")

End_JQ = Last_JQ + datetime.timedelta(days=JQ_last)
end_JQ = End_JQ.strftime("%Y-%m-%d")

Next_JQ = End_JQ + datetime.timedelta(days=JQ_cycle)
next_JQ = Next_JQ.strftime("%Y-%m-%d")

# ***************早安提醒*******************
def get_weather(province, city):
    # 城市id
    try:
        city_id = cityinfo.cityInfo[province][city]["AREAID"]
    except KeyError:
        print("推送消息失败，请检查省份或城市是否正确")
        os.system("pause")
        sys.exit(1)
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
      "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    # print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn

# 恋爱时长计算
def get_count():
  delta = today - datetime.datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday():
  next = datetime.datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

# 经期来临倒计时
def JQ_count():
  Days_left = Next_JQ - today
  return Days_left.days

# 经期结束倒计时
def End_count(Next_JQ):
    End_day = Next_JQ + datetime.timedelta(days=JQ_last)
    Days_left = End_day -today
    return End_day, Days_left

# 排卵期计算
def PL_count(Next_JQ):
    End_day, Days_left = End_count(Next_JQ)
    PL_start = End_day + datetime.timedelta(days=PL_pre)
    PL_end = PL_start + datetime.timedelta(days=PL_last)
    return PL_start, PL_end

# 排卵期来临倒计时
def PL_cng():
    PL_start, PL_end = PL_count(Next_JQ)
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
def get_status(Next_JQ):
    End_day, Days_left = End_count(Next_JQ)
    PL_start, PL_end = PL_count(Next_JQ)
    if Next_JQ <= today <= End_day:
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

    client = WeChatClient(app_id, app_secret)

    wm = WeChatMessage(client)
    wea, temp, tempn = get_weather(province, city)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    week = week_list[today.isoweekday() % 7]
    note_ch, note_en = get_ciba()
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
                    "value": wea,
                    "color": "#ED9121"
                },
            "min_temperature": {
                    "value": tempn,
                    "color": "#00FF00"
                },
            "max_temperature": {
                  "value": temp,
                  "color": "#FF6100"
                },
            "love_day": {
                  "value": get_count(),
                  "color": "#87CEEB"
                },
            "birthday": {
                  "value": get_birthday() + 1,
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

    word_en, word_ch = case_shanbay()
    now_status, color_status = get_status(Next_JQ)
    PL_come, PL_go = PL_cng()
    PL_start, PL_end = PL_count(Next_JQ)
    End_day, Days_left = End_count(Next_JQ)
    if now_status == '安全期':
        template_id = template_id_aq
        JQ_data = {
            "Now_Status":{
                "value": now_status,
                "color": color_status
                },
            "last_JQ":{
                "value": "{}".format(Last_JQ.strftime('%Y-%m-%d')),
                "color": "#ED9121"
                },
            "end_JQ":{
                "value": "{}".format(End_JQ.strftime('%Y-%m-%d')),
                "color": "#808A87"
                },
            "next_JQ":{
                "value": "{}".format(Next_JQ.strftime('%Y-%m-%d')),
                "color": "#FF6100",
                },
            "days_left":{
                "value": JQ_count(),
                "color": "#FF8000"
                },
            "PL_start":{
                "value": PL_come,
                "color": "#FF8000"
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
                "value": "{}".format(Last_JQ.strftime('%Y-%m-%d')),
                "color": "#ED9121"
                },
            "end_JQ":{
                "value": "{}".format(End_JQ.strftime('%Y-%m-%d')),
                "color": "#808A87"
                },
            "next_JQ":{
                "value": "{}".format(Next_JQ.strftime('%Y-%m-%d')),
                "color": "#FF6100",
                },
            "days_left":{
                "value": JQ_count(),
                "color": "#FF8000"
                },
            "PL_end":{
                "value": PL_go,
                "color": "#FF8000"
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
                "value": "{}".format(Next_JQ.strftime('%Y-%m-%d')),
                "color": "#ED9121"
                },
            "nextend_JQ":{
                "value": "{}".format(End_day.strftime('%Y-%m-%d')),
                "color": "#808A87"
                },
            "days_left":{
                "value": Days_left.days + 1,
                "color": "#FF8000"
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
    os.system("pause")

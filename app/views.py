from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import json
import requests
from pytz import timezone
import datetime
import os
import sys


import pya3rt


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
# talk_api = settings.TALK_API

# 天気予報 RakutenRapidApiのOpenWeatherMapを使う。
def getWeather():
    url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q":"Nishinomiya,jp","lat":"34.7489444","lon":"135.3417722", "units":"metric" ,"lang":"ja"}
    headers = {
        'x-rapidapi-key': "415427c189msh5c445f822aa1907p101ff9jsn869b4fac17ff",
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    forecastData = json.loads(response.text)

    if not ('list' in forecastData):
        print ('error')
        return

    words = '【今日の天気】\n'
    beforeDate = ''
    print(forecastData['list'][0])
    for item in forecastData['list']:
        forecastDatetime = timezone('Asia/Tokyo').localize(datetime.datetime.fromtimestamp(item['dt']))

        # 本日分のみ通知対象とする
        if beforeDate != '' and beforeDate != forecastDatetime.strftime('%Y-%m-%d'):
            break
        else:
            beforeDate = forecastDatetime.strftime('%Y-%m-%d')

        weatherDescription = item['weather'][0]['description']
        emoji = ''
        # 絵文字の分岐は適当
        if '曇' in weatherDescription:
            emoji = '\uDBC0\uDCAC'
        elif '雪' in weatherDescription:
            emoji = '\uDBC0\uDCAB'
        elif '雨' in weatherDescription:
            emoji = '\uDBC0\uDCAA'
        elif '晴' in weatherDescription:
            emoji = '\uDBC0\uDCA9'

        temperature_max = int(item['main']['temp_max'])
        temperature_min = int(item['main']['temp_min'])
        rainfall = 0
        if 'rain' in item and '3h' in item['rain']:
            rainfall = item['rain']['3h']
        words += '\n{0}\n天気:{1} {2}\n最高気温:{3}℃ 最低気温:{4}℃\n雨量(mm):{5}\n'.format(forecastDatetime.strftime('%Y-%m-%d %H:%M'), emoji, weatherDescription, temperature_max, temperature_min ,rainfall)

    return words



class CallbackView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')

    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            print(e)
            return HttpResponseServerError()

        return HttpResponse('OK')


    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    def message_event(event):
        reply = event.message.text 
        weatherText = getWeather()

        if reply == "天気":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=weatherText)
            )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )

        # client = pya3rt.TalkClient(talk_api)
        # response = client.talk(event.message.text)
        # reply = response['results'][0]['reply']

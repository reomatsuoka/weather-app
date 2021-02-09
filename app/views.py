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
API_KEY = "415427c189msh5c445f822aa1907p101ff9jsn869b4fac17ff"
ZIP = '663-8202,jp'
API_URL = 'http://api.openweathermap.org/data/2.5/forecast?zip={0}&units=metric&lang=ja&APPID={1}'
# talk_api = settings.TALK_API

# 天気予報 RakutenRapidApiのOpenWeatherMapを使う。
def getWeather():
    url = API_URL.format(ZIP, API_KEY)
    response = requests.get(url)
    forecastData = json.loads(response.text)

    if not ('list' in forecastData):
        pirnt (error)
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

        temperature = item['main']['temp']
        rainfall = 0
        if 'rain' in item and '3h' in item['rain']:
            rainfall = item['rain']['3h']
        words += '\n{0}\n天気:{1} {2}\n気温(℃):{3}\n雨量(mm):{4}\n'.format(forecastDatetime.strftime('%Y-%m-%d %H:%M'), emoji, weatherDescription, temperature, rainfall)

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

        return HttpsResponse('OK')


    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    def message_event(event):
        push_text = event.message.text 
        weatherText = getWeather()
        if push_text == "天気":
            line_bot_api.reply_message(
            event.push_text_token,
            TextSendMessage(text=weatherText)
            )
        else:
            line_bot_api.reply_message(
            event.push_text_token,
            TextSendMessage(text=push_text)
            )
        # client = pya3rt.TalkClient(talk_api)
        # response = client.talk(event.message.text)
        # reply = response['results'][0]['reply']

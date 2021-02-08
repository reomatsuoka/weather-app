from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from json
import requests

# import pya3rt


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
# talk_api = settings.TALK_API

# 天気予報 RakutenRapidApiのOpenWeatherMapを使う。
def get_weather():
    url = "https://community-open-weather-map.p.rapidapi.com/weather"
    querystring = {"q":"Kobe,jp","units":"metric","lang":"ja"}
    headers = {
    'x-rapidapi-key': "415427c189msh5c445f822aa1907p101ff9jsn869b4fac17ff" ,
    'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    forecastData = json.loads(response.text)

    if not ('list' in forecastData):
        pirnt (error)
        return



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
        reply = event.message.text 
        # client = pya3rt.TalkClient(talk_api)
        # response = client.talk(event.message.text)
        # reply = response['results'][0]['reply']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
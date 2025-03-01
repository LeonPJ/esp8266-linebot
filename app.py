from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
import requests
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
# openai.api_key = os.getenv('OPENAI_API_KEY')


# def GPT_response(text):
#     # 接收回應
#     response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
#     print(response)
#     # 重組回應
#     answer = response['choices'][0]['text'].replace('。','')
#     return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        # GPT_answer = GPT_response(msg)
        # print(GPT_answer)
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer)) 
        user_id = event.source.user_id
        if "TOKEN" in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(user_id))
        elif "OPEN" in msg:
            if(user_id == os.getenv('AUTHORIZE_USER_1') or user_id == os.getenv('AUTHORIZE_USER_2') or user_id == os.getenv('AUTHORIZE_USER_3')):

                #  open door
                url = os.getenv('BLYNK_URL')
                params = {
                    "token": os.getenv('BLYNK_TOKEN'),
                    "v0": os.getenv('BLYNK_STATUS')
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("開門 - 成功"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("開門 - 失敗"))

        # elif "CLOSE" in msg:
        #     if(user_id == os.getenv('AUTHORIZE_USER_1') or user_id == os.getenv('AUTHORIZE_USER_2') or user_id == os.getenv('AUTHORIZE_USER_3')):

        #         # enable close
        #         url = os.getenv('BLYNK_URL')
        #         params = {
        #             "token": os.getenv('BLYNK_TOKEN'),
        #             "v2": os.getenv('BLYNK_STATUS')
        #         }
        #         response = requests.get(url, params=params)
        #         if response.status_code == 200:
        #             # close door
        #             url = os.getenv('BLYNK_URL')
        #             params = {
        #                 "token": os.getenv('BLYNK_TOKEN'),
        #                 "v1": os.getenv('BLYNK_STATUS')
        #             }
        #             response = requests.get(url, params=params)
        #             if response.status_code == 200:
        #                 line_bot_api.reply_message(event.reply_token, TextSendMessage("關門 - 成功"))
        #             else:
        #                 line_bot_api.reply_message(event.reply_token, TextSendMessage("關門 - 失敗"))
        #         else:
        #             line_bot_api.reply_message(event.reply_token, TextSendMessage("授權 - 失敗"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("未授權"))

                        
    except:
        print(traceback.format_exc())
        # line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'))

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

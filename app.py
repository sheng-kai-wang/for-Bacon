import os

from config import *
from crawl import *
from kd2 import *

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)


app = Flask(__name__)


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text

    if "查詢股票" in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入 [股票代號] [日期] \n格式: 2330 2021-01-01"))

    elif event.message.text[:4].isdigit():
        input_word = event.message.text.replace(" ", "")  # 合併字串取消空白
        stock_name = input_word[0:4]  # 2330
        start_date = input_word[4:]  # 2020-01-01
        content = plot_stcok_k2_chart(IMGUR_CLIENT_ID, stock_name, start_date)
        message = ImageSendMessage(
            original_content_url=content, preview_image_url=content)
        line_bot_api.reply_message(event.reply_token, message)
        
    
    elif "即時新聞" in message:
        result = news_crawler()
        line_bot_api.reply_message(event.reply_token,
                                TextSendMessage(text=result))
    elif "產業資訊" in message:
        result1 = weekly_news()
        line_bot_api.reply_message(event.reply_token,
                                TextSendMessage(text=result1))

    else:
        line_bot_api.reply_message(event.reply_token, message)
        


if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

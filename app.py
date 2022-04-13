import os
import re

from config import *
from crawl import *



# basic
import numpy as np
import pandas as pd
import pyimgur

# get data
import pandas_datareader as pdr

# visual
import matplotlib.pyplot as plt
import mpl_finance as mpl
import mplfinance as mpf
import matplotlib.ticker as ticker
import matplotlib.ticker as FormatStrFormatter

#%matplotlib inline
import seaborn as sns

# import seaborn as sns 
from bs4 import BeautifulSoup

#time
import datetime as datetime

#talib
import talib
import pandas as pd
import requests,datetime
from matplotlib.font_manager import FontProperties # 設定字體

import yfinance as yf


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


#def plot_stcok_k_chart(IMGUR_CLIENT_ID, stock, start_date):

 #   stock = str(stock)+".tw"

    # yf.pdr_override()  # <== that's all it takes :-)
    # download dataframe
    # data = pdr.get_data_yahoo(stock, start_date)
    
  #  data = yf.download(stock, start_date)

   # mpf.plot(data, type='candle', mav=(5, 20,60,120), volume=True,style='yahoo',
    #         title=stock, savefig=PATH)

    # 上傳圖片
  #  im = pyimgur.Imgur(IMGUR_CLIENT_ID)
   # uploaded_image = im.upload_image(PATH, title=stock+" candlestick chart")
    # print(uploaded_image.link)

    # 顯示雲端圖床圖片
    #return uploaded_image.link


def plot_stcok_k2_chart(IMGUR_CLIENT_ID, stock, start_date):
    
    plt.rcParams['font.sans-serif']=['Microsoft JhengHei']
    plt.rcParams['font.family']=['Adobe Hebrew']
    plt.rcParams['axes.unicode_minus']=False

    stock = str(stock)+".tw"

    #start_date='2021-01-01'
    #stock = "3008.tw"


    yf.pdr_override()
    #end = datetime.datetime.now()
   # df = pdr.get_data_yahoo(stock, start_date)#end)

    df = yf.download(stock, start_date)
    df.index = df.index.format(formatter=lambda x: x.strftime('%Y-%m-%d')) 


    sma_5 = talib.SMA(np.array(df['Close']), 5)
    sma_10 = talib.SMA(np.array(df['Close']), 10)
    sma_30 = talib.SMA(np.array(df['Close']), 30)
    sma_60 = talib.SMA(np.array(df['Close']), 60)
    sma_120 = talib.SMA(np.array(df['Close']), 120)

    df['k'], df['d'] = talib.STOCH(df['High'], df['Low'], df['Close'])
    df['k'].fillna(value=0, inplace=True)
    df['d'].fillna(value=0, inplace=True)

    fig = plt.figure(figsize=(30, 35))
    # 設定標題
    plt.title(stock,x=1, y=1.1, color='darkblue',fontsize=150)


    ax  = fig.add_axes([0,0.4,2,0.5])  #左下座標(0,0.2)  寬高(1,0.5)




    for lobj in ax.get_yticklabels():

        lobj.set_size(65)
        lobj.set_color('black')

    plt.title("Open:"+str(round(df['Open'][-1], 2))+"  Close:"+str(round(df['Close'][-1], 2))+"\nHigh:"+str(round(df['High'][-1] ,2))+"    Low:"+str(round(df['Low'][-1], 2)),fontsize="65",fontweight='bold',bbox=dict(facecolor='yellow',edgecolor='red',alpha=0.65),loc='left')
    plt.title("Date:"+df.index[-1],fontsize="60",fontweight='bold',loc="right")
    plt.grid(True,linestyle="--",color='gray',linewidth='0.5',axis='both')

    ax2 = fig.add_axes([0,0.2,2,0.2])  #
    ax2.set_ylim([-10,110]) # >80股票強勢 <20弱勢
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.75) #>80賣出
    ax2.axhline(y=20, color='gray', linestyle='--', alpha=0.75)


    for lobj in ax2.get_yticklabels():

        lobj.set_size(60)
        lobj.set_color('black')


    ax3 = fig.add_axes([0,0,  2,0.2])  #


    #設定y軸值，名稱，字體大小
    ax.set_ylabel('Price', y=1.05,color='r',fontsize=80,rotation=0)#子軸名稱
    ax3.set_ylabel('Volume',color='r',fontsize=80)#子軸名稱


    for lobj in ax3.get_yticklabels():

        lobj.set_size(40)
        lobj.set_color('black')
        

    mpl.candlestick2_ochl(ax, df['Open'], df['Close'], df['High'],
                        df['Low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
 



    #圖例
    ax.plot(sma_5, label=' 5MA')
    ax.plot(sma_10, label='10MA')
    ax.plot(sma_30, label='30MA')
    ax.plot(sma_60, label='60MA')
    ax.plot(sma_120, label='12MA')

    ax2.plot(df['k'], label='K')
    ax2.plot(df['d'], label='D')

    # date_step 與 len(df.index) 成正比
    # 時間長，日期間距變大
    # 時間短，日期間距變小
    step_const = 25
    date_step = int(len(df.index)/step_const)
    if (date_step<1):
        date_step = 1
    print('date_step: ', date_step)

    mpl.volume_overlay(ax3, df['Open'], df['Close'], df['Volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
    ax3.set_xticks(range(0, len(df.index), date_step))

   # tick_spacing = df.index.size/10 # x軸密集度

    #ax3.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax3.set_xticklabels(df.index[::date_step],fontsize=60,rotation=35)


    ax.legend( fontsize=35);
    ax2.legend( fontsize=30);

   
    fig.savefig(PATH,bbox_inches='tight')


    # 上傳圖片
    im = pyimgur.Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=stock+" candlestick chart")
    print(uploaded_image.link)

    # 顯示雲端圖床圖片
    return uploaded_image.link



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    # if event.message.text[:2].upper() == "@K":
    #     input_word = event.message.text.replace(" ", "")  # 合併字串取消空白
    #     stock_name = input_word[2:6]  # 2330
    #     # start_date = datetime.datetime(2021,10,1)
    #     start_date = input_word[6:]  # 2020-01-01
    #     content = plot_stcok_k_chart(IMGUR_CLIENT_ID, stock_name, start_date)
    #     message = ImageSendMessage(
    #         original_content_url=content, preview_image_url=content)
    #     line_bot_api.reply_message(event.reply_token, message)

    if "查詢股票" in message:
        is_query_stock = True
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入 [股票代號] [日期] \n格式: 2330 2021-01-01"))

    elif event.message.text[:4].isdigit():
        is_query_stock = False
        input_word = event.message.text.replace(" ", "")  # 合併字串取消空白
        stock_name = input_word[0:4]  # 2330
       # start_date = datetime.datetime(2021,01,1)
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

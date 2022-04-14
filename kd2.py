from config import *
from crawl import *

# basic
import numpy as np
import pyimgur

# visual
import matplotlib.pyplot as plt
import mpl_finance as mpl

# talib
import talib

# data
import yfinance as yf

def plot_stcok_k2_chart(IMGUR_CLIENT_ID, stock, start_date):
    
    plt.rcParams['font.sans-serif']=['Microsoft JhengHei']
    plt.rcParams['font.family']=['Adobe Hebrew']
    plt.rcParams['axes.unicode_minus']=False

    stock = str(stock)+".tw"

    yf.pdr_override()

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


    ax3 = fig.add_axes([0,0,  2,0.2])


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


    parts = 8 # 切出八個日期
    date_step = 1 # 預設的日期間隔
    date_list = df.index # 預設的日期資料
    if (len(date_list) > parts): # 如果資料超過八筆，就切出八個日期
        date_step = int(len(date_list)/(parts-1)) # 日期間隔
        date_list = date_list[::date_step].values # 日期資料
        date_list[-1] = df.index[-1] # 最後一筆一定是今天日期


    mpl.volume_overlay(ax3, df['Open'], df['Close'], df['Volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
    ax3.set_xticks(range(0, len(df.index), date_step))
    ax3.set_xticklabels(date_list, fontsize=60, rotation=35)

    ax.legend( fontsize=35)
    ax2.legend( fontsize=30)

   
    fig.savefig(PATH,bbox_inches='tight')


    # 上傳圖片
    im = pyimgur.Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=stock+" candlestick chart")
    print(uploaded_image.link)

    # 顯示雲端圖床圖片
    return uploaded_image.link

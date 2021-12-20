#https://youngwonhan-family.tistory.com/32

import mplfinance as mpf
import pandas_datareader as web

df = web.naver.NaverDailyReader('005930', start='20201201' , end='20210619').read()
df = df.astype(int)

def plot1(df):
    #mpf.plot(df, type='candle')
    colorset = mpf.make_marketcolors(up='tab:red', down='tab:blue', volume='tab:blue')
    s = mpf.make_mpf_style(marketcolors=colorset)
    mpf.plot(df, type='candle', volume=True, style=s, block=False) # 최근 60 row data 출력


import plotly.graph_objects as go
import plotly.subplots as ms

df['MA5'] = df['Close'].rolling(5).mean()
df['MA20'] = df['Close'].rolling(20).mean()
df['MA60'] = df['Close'].rolling(60).mean()

ma5 = go.Scatter(x=df.index, y=df['MA5'], line=dict(color='black', width=0.8), name='ma5')
ma20 = go.Scatter(x=df.index, y=df['MA20'], line=dict(color='red', width=0.9), name='ma20')
ma60 = go.Scatter(x=df.index, y=df['MA60'], line=dict(color='green', width=1), name='ma60')

def plot2(df):
    candle = go.Candlestick(x=df.index)
    candle = go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='red', # 상승봉
	    decreasing_line_color='blue' # 하락봉
    )
    '''
    fig = go.Figure(data=[candle, ma5, ma20, ma60])
    #fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(title=dict(text="엔씨소프트 2020년 하반기 일 차트", x=0.5))
    '''
    volume_bar = go.Bar(x=df.index, y=df['Volume'])
    fig = ms.make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)    

    fig.add_trace(candle, row=1, col=1)
    fig.add_trace(ma5, row=1, col=1)
    fig.add_trace(ma20, row=1, col=1)
    fig.add_trace(ma60, row=1, col=1)
    fig.add_trace(volume_bar, row=2, col=1)
    fig.update_layout(
        title='Samsung stock price',
        yaxis1_title='Stock Price',
        yaxis2_title='Volume',
        xaxis2_title='periods',
        xaxis1_rangeslider_visible=False,
        xaxis2_rangeslider_visible=True,    
    )
    
    fig.show()

plot1(df)
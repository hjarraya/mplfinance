import pandas as pd
from datetime import timedelta
import datetime
import pytz
import numpy as np
import alpaca_trade_api as tradeapi
import mplfinance as mpf
import matplotlib.animation as animation

api = tradeapi.REST(API_KEY,
                    API_SECRET_ID,
                    'https://paper-api.alpaca.markets')
dbDateFormat = "%Y-%m-%d %H:%M:%S"
# pd.set_option('mode.chained_assignment', 'raise')
# pd.options.mode.chained_assignment = None  # default='warn'
def get_data(symbol, lookback):

    all_data = pd.DataFrame()
    # Current time in UTC
    now_est = datetime.datetime.now(pytz.timezone('EST'))

    # Dates between which we need historical data
    from_date = (now_est - timedelta(days=lookback)).strftime(dbDateFormat)
    to_date = now_est.strftime(dbDateFormat)

    # returns open, high, low, close, volume, vwap
    all_data = api.polygon.historic_agg_v2(symbol, 5, 'minute', _from=from_date, to=to_date).df
    all_data.drop(columns=['volume'], inplace=True)
    all_data.replace(0, method='bfill', inplace=True)
    all_data.index.name = "Date"
    all_data.index = pd.to_datetime(all_data.index)
    all_data['Date'] = all_data.index
    # all_data = all_data.reset_index(level=0, drop=True).reset_index()
    return all_data


data = get_data('CAT', 1)
data.to_csv('data.csv')
df = data
print(df)


pkwargs=dict(type='candle')

fig, axes = mpf.plot(data.iloc[0:20],returnfig=True,volume=False,
                     figsize=(11,8),
                     title='\n\nS&P 500 ETF',**pkwargs)
ax1 = axes[0]


def reg_calc(df):
    x = list(range(0, len(data.index.tolist())))
    y = data['close']
    fit = np.polyfit(x, y, 1)
    fit_fn = np.poly1d(fit)
    return fit_fn

print(reg_calc(df))



def animate(ival):

    if (20+ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return

    data = df.iloc[10:(20+ival)]
    data['Date']=data.index.astype(str)
    dates = data.Date.tolist()
    datepairs = [(d1, d2) for d1, d2 in zip(dates, dates[1:])]


    mpf.plot(data,ax=ax1, tlines=[dict(tlines=datepairs,tline_use='high',colors='g'),
                    dict(tlines=datepairs,tline_use='low',colors='b')], **pkwargs)
    ax1.clear()


ani = animation.FuncAnimation(fig, animate, interval=200)

mpf.show()
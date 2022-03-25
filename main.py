import json
import API
from KrownCrossBackTest import KrownCrossBackTest
from datetime import datetime, timedelta
import numpy as np
import sys
from DailyTrend import DailyTrend
from DataGrab import DataGrab
from Strategy import Strategy
import tkinter as tk
np.set_printoptions(threshold=sys.maxsize)

# nomics api key: m_419a355b4a2283777a4aa1a6590c43ffb409fe5a
if __name__ == '__main__':
    file_name = './test2'
    npy_file = './Data/npy/'+file_name+'.npy'
    json_file = './Data/json/'+file_name
    # window = tk.Tk(screenName="test")
    # label = tk.Label(window, text="helloworld")
    # label.pack()
    # window.mainloop()

    # Aquire the desired data
    # start = datetime(year=2021, month=1, day=1, hour=0, minute=0, second=0)
    # end = datetime(year=2021, month=12, day=31, hour=23, minute=0, second=0)
    # dg1 = DataGrab(exchange="gdax", tf="1h", market="BTC-USD", start=start, end=end,
    #                file=file_name)
    # dg1.export_data()
    # inception = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
    # endtime = datetime(year=2011, month=9, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
    # raw_list = API.KEY.Candles.get_candles(interval="1d", start=inception, end=endtime, currency="BTC")
    # print(raw_list[0])
    # dt1 = DailyTrend("BTC")
    # np_list = dt1.get_np_list()
    # print(len(dt1.check_data_set_times()), dt1.check_data_set_times())

    dt1 = DailyTrend("BTC")
    dt1.get_daily_data()
    dt1.set_np_data()

    # with open('./Data/json/BTCDailyTrend', 'r') as json_data:
    #     data = json.load(json_data)
    #     json_data.close()
    # dicttest = {}
    # for x in data:
    #     dicttest.






    #start2 = datetime.strptime(input("Start time as %Y-%m-%d %H:%M:%S| "), "%Y-%m-%d %H:%M:%S")
    #2022-01-01 00:00:00
    # strat = Strategy(int(input("Choose Trading Strategy - kc:1, other:2 | "))).stratInput()


    # Bring in crunched data and run against backtest .npy extension
    # npy_list = np.load(npy_file, allow_pickle=True)
    # with open(json_file) as json_file:
    #     json_data = json.load(json_file)
    #     json_file.close()
    # kc1 = KrownCrossBackTest(emaL=9, emaM=21, emaH=55, np_data=npy_list.item(), json_data=json_data)

    # kc1.krown_cross_json_export()
    #print(kc1)
    #bbwp = kc1.bbwp()
    # print(kc1.ema_crosses()['total_crosses'])

    # kc_ee = kc1.entry_exit()
    # average_roi_list = []
    # win_loss = []
    # win = 0
    # loss = 0
    # capital = 1000
    # for x in kc_ee:
    #     print(x)
    #     average_roi_list.append(((x[1]/x[0])-1)*100)
    # for y in kc_ee:
    #     if y[0] < y[1]:
    #         win_loss.append("W")
    #         win += 1
    #     else:
    #         win_loss.append("L")
    #         loss += 1
    # print(len(average_roi_list))
    # print(average_roi_list)
    # average_roi = sum(average_roi_list)/len(average_roi_list)
    # print(average_roi)
    # print(win/(win+loss))
    #
    # for z in average_roi_list:
    #     capital = capital * (1+(z/100))
    # print(capital)
    # kc1 = KrownCrossBackTest(emaL=9, emaM=21, emaH=55, start=start, end=end)
    #
    #kc1.ema_crosses()
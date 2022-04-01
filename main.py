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
    file_name = 'GDAX_ALL'
    npy_file = './Data/npy/'+file_name+'.npy'
    json_file = './Data/json/'+file_name
    # window = tk.Tk(screenName="test")
    # label = tk.Label(window, text="helloworld")
    # label.pack()
    # window.mainloop()

    # Aquire the desired data
    # start = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0)
    # end = datetime(year=2022, month=3, day=27, hour=0, minute=0, second=0)
    # dg1 = DataGrab(exchange="gdax", tf="1h", market="BTC-USD", start=start, end=end,
    #                file=file_name)
    # #dg1.export_data()
    # dg1.get_np_list()


    # inception = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
    # endtime = datetime(year=2022, month=3, day=28, hour=0, minute=0, second=0).isoformat() + "Z"
    # raw_list = API.KEY.Candles.get_candles(interval="1d", start=inception, end=endtime, currency="BTC")
    # dt1 = DailyTrend("BTC")
    # np_list = dt1.get_np_list()
    # #print(len(dt1.check_data_set_times()), dt1.check_data_set_times())
    #
    # dt1 = DailyTrend("BTC_GDAX")
    # dt1.get_daily_data_exchange("gdax", "BTC-USD")
    # dt1.set_np_data()
    # dt1.export_ema_data()

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


    # kc1.krown_cross_json_export()
    #print(kc1)
    #bbwp = kc1.bbwp()
    # print(kc1.ema_crosses()['total_crosses'])



    npy_list = np.load(npy_file, allow_pickle=True)
    with open(json_file) as json_file:
        json_data = json.load(json_file)
        json_file.close()
    kc_all = KrownCrossBackTest(emaL=9, emaM=21, emaH=55, np_data=npy_list.item(), json_data=json_data,
                                kc_file='gdax_all')
    #kc_all.krown_cross_json_export()
    kc_ee = kc_all.entry_exit()
    average_time = sum([x[2] for x in kc_ee])/len(kc_ee)
    print("Average_Time:", average_time)
    average_roi_list = []
    win_loss = []
    win = 0
    loss = 0
    capital = 1000
    for x in kc_ee:
        average_roi_list.append(round((((x[1][1]/x[0][1])-1)*100), 3))
    for y in kc_ee:
        if y[0][1] < y[1][1]:
            win_loss.append("W")
            win += 1
        else:
            win_loss.append("L")
            loss += 1
    print(len(average_roi_list))
    print(average_roi_list)
    b_w = max(average_roi_list)
    b_l = min(average_roi_list)
    print("Biggest Winner =", b_w, "| Biggest Loser =", b_l)
    average_roi = sum(average_roi_list)/len(average_roi_list)
    print("Trade Average: {}%".format("{:.2f}".format(average_roi)))
    print("Percentage Win: {}%".format(("{:.2f}".format(win/(win+loss)*100))))

    for z in average_roi_list:
        #print("trade:", capital)
        capital = capital * (1+(z/100))
    print(capital)





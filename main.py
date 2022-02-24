from KrownCrossBackTest import KrownCrossBackTest
from datetime import datetime, timedelta
import numpy as np
import sys
from DataGrab import DataGrab
from Strategy import Strategy
import tkinter as tk
np.set_printoptions(threshold=sys.maxsize)

# nomics api key: m_419a355b4a2283777a4aa1a6590c43ffb409fe5a
if __name__ == '__main__':
    # window = tk.Tk(screenName="test")
    # label = tk.Label(window, text="helloworld")
    # label.pack()
    # window.mainloop()

    # Aquire the desired data
    # start = datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0)
    # end = datetime(year=2022, month=2, day=11, hour=23, minute=0, second=0)
    #
    # dg1 = DataGrab(exchange="gdax", tf="1h", market="BTC-USD", start=start, end=end, file='./Data/npy/test1')
    # dg1.np_export_data()

    #start2 = datetime.strptime(input("Start time as %Y-%m-%d %H:%M:%S| "), "%Y-%m-%d %H:%M:%S")
    #2022-01-01 00:00:00
    # strat = Strategy(int(input("Choose Trading Strategy - kc:1, other:2 | "))).stratInput()


    # Bring in crunched data and run against backtest
    npy_list = np.load('./Data/npy/test1', allow_pickle=True)
    kc1 = KrownCrossBackTest(emaL=9, emaM=21, emaH=55, data=npy_list.item())
    print(kc1)


    # kc1 = KrownCrossBackTest(emaL=9, emaM=21, emaH=55, start=start, end=end)
    #
    # kc1.amountCrosses()
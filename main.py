import json
import API
from KrownCrossBackTest import KrownCrossBackTest
from datetime import datetime, timedelta
import numpy as np
import sys
import fnmatch
import os
from DailyTrend import DailyTrend
from DataGrab import DataGrab
from Strategy import Strategy
import tkinter as tk
np.set_printoptions(threshold=sys.maxsize)

def find(filename, directory):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return True
        else:
            return False

if __name__ == '__main__':
    # file_name = 'GDAX_ALL'
    # npy_file = './Data/npy/' + file_name + '.npy'
    # json_file = './Data/json/' + file_name
    #Select which strat to use:

    # strat_option = int(input("Please enter number number based on provided options: 1-KrownCross, 2-More to come!"))
    strat_option = 1
    if strat_option == 1:
        start = datetime(year=2021, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
        end = datetime(year=2022, month=3, day=31, hour=0, minute=0, second=0).isoformat() + "Z"
        exchange = "gdax"
        ema_l = 9
        ema_m = 21
        ema_h = 55
        print("Lets Back test the Krown Cross Strategy... \n"
              "But first I'm going to need a few things")
        ticker = str(input("Please enter the ticker of the coin you want to back test on - "))
        time_frame = str(input("Enter time frame based on the following options | 30m, 1h, 4h, 1d - "))
        print("Collecting Data from inception of the token... This shouldn't take any loner than a minute or so,")
        print("Lets gather some information on the krown cross back test to perform")
        # dt = DailyTrend("BTC")
        # dt.set_ema_data()
        ema_l = int(input("Enter the quickest moving ema - ") or ema_l)
        ema_m = int(input("Enter the second quickest moving ema - ") or ema_m)
        ema_h = int(input("Enter the third quickest moving ema - ") or ema_h)
        #file_data_names
        filename = ticker.upper() + time_frame
        market = ticker.upper() + "-USD"
        dg = DataGrab(exchange=exchange, tf=time_frame, market=market, start=start, end=end, file=filename)
        if not find(filename, "./Data/json/"):
            dg.set_export_data()
        #dg.set_export_data()
        kc = KrownCrossBackTest(ema_l, ema_m, ema_h, dg.load_np_list(), dg.load_json_data(), filename, ticker)
        if not find (filename, "./Data/kc"):
            kc.set_krown_cross_json_export()
        kc.rsi()

        #kc.entry_exit_analysis('bbwp')
        kc.get_roi()
        kc.entry_exit_analysis("any")
    else:
        print("more to come!")





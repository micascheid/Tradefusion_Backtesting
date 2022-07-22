import json
import API
import KCObj
from KrownCrossBackTest import KrownCrossBackTest
from datetime import datetime, timedelta
import numpy as np
import sys
import fnmatch
import os
from DailyTrend import DailyTrend
from DataGrab import DataGrab
from Strategy import Strategy
from DataGrab import candle_merge, load_np_data_static, load_json_data_static
np.set_printoptions(threshold=sys.maxsize)

def find(filename, directory):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return True
        else:
            return False


def bfi_kc_signal_find():
    """
    Uses BFI to loop through various inputs to gauge best set of inputs. All inputs use the following checklist to
    make a full trade as shown below.
    Checklist conditions:
        -Stop Loss
        -Entry conditions
        -Exit conditions
        -Invalidation
    """
    bbwp_entry = 0
    bbwp_exit = 0
    rsi_entry = 0
    rsi_exit = 0
    emaL_entry = 0
    emaL_exit = 0
    emaM_entry = 0
    emaM_exit = 0
    emaH_entry = 0
    emaH_exit = 0
    daily_ema_entry = 0
    daily_ema_exit = 0
    entry_exit_list = 0


if __name__ == '__main__':
    # file_name = 'GDAX_ALL'
    # npy_file = './Data/npy/' + file_name + '.npy'
    # json_file = './Data/json/' + file_name
    #Select which strat to use:

    # strat_option = int(input("Please enter number number based on provided options: 1-KrownCross, 2-More to come!"))
    strat_option = 1
    if strat_option == 1:
        start = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
        end = datetime(year=2022, month=4, day=30, hour=0, minute=0, second=0).isoformat() + "Z"
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

        # ema_l = int(input("Enter the quickest moving ema - ") or ema_l)
        # ema_m = int(input("Enter the second quickest moving ema - ") or ema_m)
        # ema_h = int(input("Enter the third quickest moving ema - ") or ema_h)

        #file_data_names
        filename = ticker.upper() + time_frame
        market = ticker.upper() + "-USD"
        dg = DataGrab(exchange=exchange, tf=time_frame, market=market, start=start, end=end, file=filename)
        # if not find(filename, "./Data/json/"):
        #     dg.set_export_data()
        #dg.set_export_data()

        # candle_merge("./Data/json/BTC1h", "2h")

        # kc = KrownCrossBackTest(ema_l, ema_m, ema_h, load_np_data_static("BTC2h"), load_json_data_static("BTC2h"),
        #                         filename,
        #                         ticker)
        kc = KrownCrossBackTest(ema_l, ema_m, ema_h, dg.load_np_list(), dg.load_json_data(), filename, ticker)
        # if not find (filename, "./Data/kc"):
        #     kc.set_krown_cross_json_export()
        #kc.set_krown_cross_json_export()
        #kc.rsi()

        #kc.entry_exit_analysis('bbwp')
        #kc.get_roi()
        bbwp_entry, bbwp_exit = 50, 90
        rsi_entry, rsi_exit = 0, 80
        emaL_entry, emaL_exit = 1, 3
        emaM_entry, emaM_exit = .5, 3
        emaH_entry, emaH_exit = 1, 3
        daily_ema_entry, daily_ema_exit = 0,0
        bmsb_entry, bmsb_exit = 0, 0 #not coded in function yet
        interests = [KCObj.BBWP, KCObj.EMA_MID]
        ee_dict = kc.entry_exit2(bbwp_entry, bbwp_exit, rsi_entry, rsi_exit, emaL_entry, emaL_exit, emaM_entry,
                                 emaM_exit, emaH_entry, emaH_exit, daily_ema_entry, daily_ema_exit, bmsb_entry,
                                 bmsb_exit, interests)
        print(ee_dict)
        print(len(ee_dict))
    else:
        print("more to come!")

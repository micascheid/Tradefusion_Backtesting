import json
import time

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
from matplotlib import pyplot as plt
from Strategy import Strategy
from DataGrab import candle_merge, load_np_data_static, load_json_data_static
np.set_printoptions(threshold=sys.maxsize)


def precision(num, prec):
    return "{:.{}f}".format(num, prec)


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
        -Stop Loss: Cross of 9 and 21
        -Entry conditions:
        -Exit conditions
        -Invalidation
    """
    bbwp_entry_l, bbwp_exit_l, bbwp_entry_s, bbwp_exit_s = 50, 85, 50, 80
    rsi_entry_l, rsi_exit_l, rsi_entry_s, rsi_exit_s = 0, 70, 80, 0
    emaL_entry_l, emaL_exit_l, emaL_entry_s, emaL_exit_s = 1, 3, 3, 1
    emaM_entry_l, emaM_exit_l, emaM_entry_s, emaM_exit_s = 1, 3, .5, 2.5
    emaH_entry_l, emaH_exit_l, emaH_entry_s, emaH_exit_s = 0, 3, 0, 3
    daily_ema_entry_l, daily_ema_exit_l, daily_ema_entry_s, daily_ema_exit_s = 0, 0, 0, 0
    bmsb_entry_l, bmsb_exit_l, bmsb_entry_s, bmsb_exit_s = 0, 0, 0, 0  # not coded in function yet

    #bbwp = [bbwp_entry_l, bbwp_exit_l, bbwp_entry_s, bbwp_exit_s]
    rsi = [rsi_entry_l, rsi_exit_l, rsi_entry_s, rsi_exit_s]
    emaL = [emaL_entry_l, emaL_exit_l, emaL_entry_s, emaL_exit_s]
    emaM = [emaM_entry_l, emaM_exit_l, emaM_entry_s, emaM_exit_s]
    emaH = [emaH_entry_l, emaH_exit_l, emaH_entry_s, emaH_exit_s]
    daily_ema = [daily_ema_entry_l, daily_ema_exit_l, daily_ema_entry_s, daily_ema_exit_s]
    bmsb = [bmsb_entry_l, bmsb_exit_l, bmsb_entry_s, bmsb_exit_s]
    interests = [KCObj.BBWP]

    #entry up to, exit starting at, step
    bbwp_range = [70, 50, 10] #last entry, start exit, step


    #Through each iteration I want the
    #Working bookmark. Working on an optimal bbwp by itself. Iterate through different entry types while exiting
    # between different exit ranges
    results_totals = []
    iterations = 0
    for x in range(bbwp_range[1], 110, bbwp_range[2]): #exit: exit start, exit last, step
        for y in range(0, bbwp_range[0], bbwp_range[2]): #entry: 0, last entry, step
            bbwp = [y, x, y, x]
            emaL = [.1, 1.5, .1, 1.5]
            emaM = [.5, 1.5, .5, 1.5]

            positions = kc.entry_exit2(bbwp, rsi, emaL, emaM, emaH, daily_ema, bmsb, interests)[4]
            meta = {
                "bbwp": "{}-{}".format(str(y), str(x)),
                "rsi": "NA",
                "emaL": "NA",
                "emaM": "NA",
                "emaH": "NA",
                "daily_ema": "NA",
                "bmsb": "NA",
            }
            results_totals.append((meta, positions))

    return results_totals


def bfi_kc_signal_find_bmsb_split():
    all_trades = bfi_kc_signal_find()
    above_bmsb_results = []
    below_bmsb_results = []

    for i in all_trades:
        above = []
        below = []
        for j in i[1]:
            if j.bmsb:
                above.append(j)
            else:
                below.append(j)
        above_bmsb_results.append((i[0], above))
        below_bmsb_results.append((i[0], below))

    return all_trades, above_bmsb_results, below_bmsb_results


def bfi_analysis_trade_results():
    total_results = bfi_kc_signal_find_bmsb_split()
    brokenup_by_bmsb = []
    all_results = []
    for i in total_results:
        for j in i:
            max_drawdown = 1000
            max_upside = -1000
            wins = 0
            losses = 0
            pnl_total = 0
            capital = 1000
            capital_list = []
            for y in range(1, len(j[1])):
                pnl = j[1][y].get_pnl()
                winorloss = j[1][y].get_winorloss()
                if pnl < max_drawdown:
                    max_drawdown = pnl
                if pnl > max_upside:
                    max_upside = pnl
                if winorloss == "w":
                    wins += 1
                else:
                    losses += 1
                capital = capital * (1+(pnl/100))
                capital_list.append(capital)
            win_ratio = (wins/(wins+losses))

            result = {
                "bbwp": j[0]["bbwp"],
                "rsi": j[0]["rsi"],
                "emaL": j[0]["emaL"],
                "emaM": j[0]["emaM"],
                "emaH": j[0]["emaH"],
                "daily_ema_pnl": j[0]["rsi"],
                "bmsb": "NA",  # Measure of performance difference above bmsb vs below. above_pnl/below_pnl
                "max_drawdown": precision(max_drawdown, 2),
                "max_upside": precision(max_upside, 2),
                "w_l": precision(win_ratio, 2),
                "capital": precision(capital, 2)
            }
            all_results.append((result, j[1]))
        brokenup_by_bmsb.append(all_results)
        all_results = []
    return brokenup_by_bmsb

def bfi_analysis():
    """
        This function returns the best result of the bfi_kc_signal_find()
    """
    #Grab get results of bfi test which has object = [({meta}, all trades),({meta}, all_trades)]
    total_trades_split_by_bmsb = bfi_analysis_trade_results()
    all_results = []

    for i in total_trades_split_by_bmsb:
        best_result = i[0]
        best_return = 0
        for j in i:
            if float(j[0]["capital"]) > best_return:
                best_return = float(j[0]["capital"])
                best_result = j
        all_results.append(best_result)
    return all_results


if __name__ == '__main__':
    # file_name = 'GDAX_ALL'
    # npy_file = './Data/npy/' + file_name + '.npy'
    # json_file = './Data/json/' + file_name
    #Select which strat to use:

    # strat_option = int(input("Please enter number number based on provided options: 1-KrownCross, 2-More to come!"))
    strat_option = 1
    if strat_option == 1:
        start = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
        end = datetime(year=2017, month=12, day=16, hour=0, minute=0, second=0).isoformat() + "Z"

        # start = datetime(year=2017, month=12, day=17, hour=0, minute=0, second=0).isoformat() + "Z"
        # end = datetime(year=2022, month=8, day=21, hour=0, minute=0, second=0).isoformat() + "Z"
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
        dg = DataGrab(exchange=exchange, tf=time_frame, market=market, start=start, end=end, file=filename,
                      in_sample_type=True)
        # if not find(filename, "./Data/json/"):
        #     dg.set_export_data()
        dg.set_export_data()

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
        total_time = time.time()
        analysis = bfi_analysis()
        for x in analysis:
            print(x[0])
        # for y in analysis[0][1]:
        #     print(y)
        total_time = time.time() - total_time
        print("Run Time: {}".format(total_time))
    else:
        print("more to come!")

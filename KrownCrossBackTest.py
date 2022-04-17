import matplotlib.pyplot
from talib import abstract
from datetime import datetime, timedelta
from DailyTrend import DailyTrend
import json
from KCObj import KCObj
from matplotlib import pyplot as plt

MA = 13
LOOKBACK = 252
EMA = abstract.Function('EMA')
PRECISION = 4


def precision(num, prec):
    return "{:.{}f}".format(num, prec)


def ema_dif(close, ema, trade_type):
    if trade_type == "long":
        return ((close/ema)-1)*100
    if trade_type == "short":
        return (1-(ema/close))*100


class KrownCrossBackTest:
    def __init__(self, emaL, emaM, emaH, np_data, json_data, kc_file, ticker):
        self.np_data = np_data
        self.emaL = emaL
        self.emaM = emaM
        self.emaH = emaH
        self.emaLL = [precision(x, 4) for x in EMA(self.np_data, self.emaL)]
        self.emaML = [precision(x, 4) for x in EMA(self.np_data, self.emaM)]
        self.emaHL = [precision(x, 4) for x in EMA(self.np_data, self.emaH)]
        self.start = datetime.strptime(np_data['meta'][0].strip("Z"), "%Y-%m-%dT%H:%M:%S")
        self.tf = np_data['meta'][1]
        self.json_data = json_data
        self.kc_file = kc_file
        self.ticker = ticker

    # def ema_crosses(self):
    #     # emaH has not been evaulated above 55h time period and may see invalid results above that
    #         # start crossing analysis at emaH*4
    #     # full_cross is when all moving averages are in aline above or below one another
    #     # watch_cross is when faster ema is crossing middle moving average
    #     # paramater to tune the dials
    #         # When to enter? at cross? how far form 9 to enter? How far is acceptable to enter off 55?
    #         # Take profit
    #         # When to exit? at cross back over?
    #             # Hard Exit
    #
    #     #Algo trade:
    #         #entry: After complete cross enter within 1% of 21 if oppurtunity occurs and risk to 55 ema is 2% or less
    #         #exit: bbwp > 80 first, 9 cross 21 for sure out
    #         #stop: close below emaH
    #
    #     cross_start = self.emaH*4
    #
    #     cross_occurence = {}
    #     cross_occurence_list = []
    #     cross_up = False
    #     cross_down = False
    #     new_cross = False
    #     total_crosses = 0
    #     bbwp_start_time = self.start + timedelta(hours=LOOKBACK+MA)
    #     if len(self.emaLL) == len(self.emaML) == len(self.emaHL):
    #         #Establish Baseline, where are the ema's current position at start of analysis?
    #         l_start, m_start, h_start = self.emaLL[cross_start], self.emaML[cross_start], self.emaHL[cross_start]
    #         if l_start > m_start > h_start:
    #             cross_up, cross_down = True, False
    #         elif l_start < m_start < h_start:
    #             cross_up, cross_down = False, True
    #         else:
    #             cross_up, cross_down = False, False
    #
    #         for i in range(cross_start, len(self.emaLL)):
    #             el, em, eh = self.emaLL[i], self.emaML[i], self.emaHL[i]
    #             if el > em > eh and cross_up == False:
    #                 cross_up, cross_down, new_cross = True, False, True
    #                 cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = "cross_up"
    #             if el < em < eh and cross_down == False:
    #                 cross_up, cross_down, new_cross = False, True, True
    #                 cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = "cross_down"
    #             if new_cross:
    #                 total_crosses += 1
    #             new_cross = False
    #     else:
    #         return -1
    #     return {"start": self.start,
    #             "timeframe": self.tf,
    #             "total_crosses": total_crosses,
    #             "cross_occurrences": cross_occurence}

    def ema_crosses_2(self):
        #bbwp start:
        #ema start: length is same as raw_json
        cross_start = self.emaH*4
        cross_occurence = {}
        cross_occurence_list = []
        CROSS_UP_S = "cross_up"
        CROSS_DOWN_S = "cross_down"
        CONT = "_cont"
        LIMBO = "_limbo"
        new_cross = False
        total_crosses = 0
        current_cross = 'none'
        bbwp_start_time = self.start + timedelta(hours=LOOKBACK+MA)
        if len(self.emaLL) == len(self.emaML) == len(self.emaHL):
            #Establish Baseline, where are the ema's current position at start of analysis?
            l_start, m_start, h_start = self.emaLL[cross_start], self.emaML[cross_start], self.emaHL[cross_start]
            if l_start > m_start > h_start:
                cross_up, cross_down = True, False
            elif l_start < m_start < h_start:
                cross_up, cross_down = False, True
            else:
                cross_up, cross_down = False, False

            for i in range(cross_start, len(self.emaLL)):
                el, em, eh = self.emaLL[i], self.emaML[i], self.emaHL[i]
                if el > em > eh and not cross_up:
                    cross_up, cross_down, new_cross = True, False, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = CROSS_UP_S
                    cross_occurence_list.append(((self.start+timedelta(hours=i)).isoformat()+"Z", CROSS_UP_S))
                    current_cross = "cross_up"
                if el < em < eh and not cross_down:
                    cross_up, cross_down, new_cross = False, True, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = CROSS_DOWN_S
                    cross_occurence_list.append(((self.start + timedelta(hours=i)).isoformat() + "Z", CROSS_DOWN_S))
                    current_cross = "cross_down"
                if new_cross:
                    total_crosses += 1
                #Check to see if a limbo occurence exists
                if CROSS_UP_S in current_cross and not new_cross and el < em:
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = CROSS_UP_S + LIMBO
                    cross_occurence_list.append(((self.start+timedelta(hours=i)).isoformat() + "Z", current_cross +
                                                 LIMBO))
                elif CROSS_DOWN_S in current_cross and not new_cross and el > em:
                    cross_occurence[(self.start + timedelta(hours=i)).isoformat() + "Z"] = CROSS_DOWN_S + LIMBO
                    cross_occurence_list.append(((self.start + timedelta(hours=i)).isoformat() + "Z", current_cross +
                                                 LIMBO))
                elif not new_cross:
                    cross_occurence[(self.start + timedelta(hours=i)).isoformat() + "Z"] = current_cross + CONT
                    cross_occurence_list.append(((self.start + timedelta(hours=i)).isoformat() + "Z", current_cross +
                                                 CONT))
                new_cross = False
        else:
            return -1
        return {"start": self.start,
                "timeframe": self.tf,
                "total_crosses": total_crosses,
                "cross_occurrences": cross_occurence,
                "cross_list": cross_occurence_list}

    def bbwp(self):
        STD = 2.0
        MATYPE=0 #0 Represents SMA look up docs for other options
        BBANDS = abstract.Function('BBANDS', MA, STD, STD, MATYPE)
        #talib.BBANDS(self.np_data['close'], timeperiod=13, matype=0)
        upper, middle, lower = BBANDS(self.np_data)
        bbw = []
        bbwp = []
        price = self.np_data['close']
        for i in range(len(price)):
            width = ((upper[i]-lower[i])/middle[i])
            bbw.append(width)
        for j in range((LOOKBACK+MA)-1, len(bbw)):
            count = 0
            current_bbw = bbw[j]
            for k in range(j-LOOKBACK, j):
                if bbw[k] < current_bbw:
                    count += 1
            bbwp.append((count/LOOKBACK)*100)
        print("len bbwp:", len(bbwp))
        return bbwp

    def rsi(self):
        RSI = abstract.Function('RSI')
        rsi = RSI(self.np_data)[MA+LOOKBACK:]
        return rsi

    def get_daily_trend(self):
        dt = DailyTrend(self.ticker)
        dt.set_np_data()
        dt.set_ema_data()

    def set_krown_cross_json_export(self):
        # Description: After the emaL, emaM, emaH, bbwap, daily_trend and cross arrays have been created
            # this function export that information in a list of json objects to a file
            # under Data/krowncross/ for easier analysis on determing entry, exit and W/L
        print("Exporting list of krown cross data to file")
        dt = DailyTrend(self.ticker)
        dt.set_daily_data()
        dt.set_np_data()
        dt.set_ema_data()
        daily_trend = dt.get_daily_trend()
        json_data = self.json_data
        # occurences = self.ema_crosses()['cross_occurrences']
        emaL = self.emaLL
        emaM = self.emaML
        emaH = self.emaHL
        cross_list = self.ema_crosses_2()['cross_list']

        # Deterine start point in which data is useful
            # which ever is greatest bbwp(Lookback + MA) or emaH*4
        ema_start = self.emaH*4
        start_time = ema_start if ema_start > LOOKBACK+MA else LOOKBACK+MA
        bbwp = self.bbwp()
        rsi = self.rsi()
        kc_list = []
        #start = datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0).isoformat()+"Z"

        for x in range(start_time, len(self.json_data)):
            time = (self.json_data[x]['timestamp'])
            date_only = datetime.strptime(time.strip("Z"), "%Y-%m-%dT%H:%M:%S").replace(hour=0, minute=0,
                                                                                        second=0).isoformat() + "Z"
            kc_dict = {
                "timestamp": str(self.json_data[x]['timestamp']),
                "close": str(precision(float(self.json_data[x]['close']), 4)),
                "cross_status": str(cross_list[x-ema_start][1]),
                "bbwp": str(precision((bbwp[(x-start_time)+1]), PRECISION)),
                "rsi": precision(rsi[x-start_time], PRECISION),
                "emaL": str(emaL[x]),
                "emaM": str(emaM[x]),
                "emaH": str(emaH[x]),
                "daily_ema": daily_trend[date_only]}
            kc_list.append(kc_dict)
            #start = (start + timedelta(hours=1)).isoformat()+"Z"
        file = open('./Data/kc/' + self.kc_file, "w")
        file.write(json.dumps(kc_list))
        file.close()

    def kc_load(self):
        file = open('./Data/kc/' + self.kc_file, "r")
        return json.load(file)

    def entry_exit(self):
        # Other thoughts: Checking which regime BTC is in regarding bull market support band
        self.set_krown_cross_json_export()
        kc_data = self.kc_load()
        positions = []
        positions_dict={}
        global entry
        global exit
        long_bias = False
        ema_mid_tolerance = .5
        ema_high_tolerance = 2
        last_entry = ""
        last_exit_time = datetime.strptime(kc_data[0]['timestamp'].strip('Z'), "%Y-%m-%dT%H:%M:%S")
        global in_trade
        in_trade = False
        LIMBO = "limbo"
        for x in kc_data:
            # convert json_obj variables back
            kc_obj = KCObj(x)

            timestamp, close, cross_status, bbwp, emaL, emaM, emaH, daily_ema = kc_obj.timestamp, kc_obj.close, \
                                                                      kc_obj.cross_status, kc_obj.bbwp, kc_obj.emaL,\
                                                                      kc_obj.emaM, kc_obj.emaH, kc_obj.daily_ema
            #looking for an entry
            if not in_trade:
                if "up" in cross_status and not (LIMBO in cross_status) and close >= daily_ema:
                    long_bias = True
                # if "down" in x["cross_status"]:
                #     long_bias = False

                if long_bias:
                    # open*x=exit
                    ema_low_dif = (emaL/close)-1
                    ema_mid_dif = (emaM/close)-1
                    ema_high_dif = (emaH/close)-1
                    if ema_mid_dif <= ema_mid_tolerance and not (LIMBO in cross_status):
                        entry = kc_obj
                        in_trade = True
                        continue
                # else:
                #     ema_low_dif = ((emaL-close)/emaL)*100
                #     ema_mid_dif = ((emaM-close)/emaM)*100
                #     ema_high_dif = ((emaH-close)/emaH)*100

                # if ema_high_dif > ema_high_tolerance:
                #     print("")


            #looking for an exit
            #TODO looking for an exit on long
            if in_trade:
                if not (LIMBO in cross_status) and (bbwp >= 90):# or close <= emaL):
                    # entry_time = datetime.strptime(entry.timestamp, "%Y-%m-%dT%H:%M:%S")
                    # exit_time = datetime.strptime(kc_obj.timestamp, "%Y-%m-%dT%H:%M:%S")
                    duration = (entry.timestamp - kc_obj.timestamp).seconds // 3600
                    pnl = ((kc_obj.close/entry.close)-1)*100
                    w_l = "w" if pnl > 0 else "l"
                    dict_obj = {
                        "timestamp_exit:": kc_obj.timestamp,
                        "duration": duration,
                        "pnl": pnl,
                        "w_l": w_l
                    }
                    positions_dict[entry.timestamp] = dict_obj
                    positions.append(((entry.timestamp, entry.close), (kc_obj.timestamp, kc_obj.close), duration))
                    long_bias = False
                    in_trade = False
                    continue
                # if emaL <= emaM: #GTFO scenario
                #     positions.append((entry.close, kc_obj.close))
                #     long_bias = False
                #     in_trade = False

            #TODO looking for an exit on short

        return positions_dict

    def entry_exit_basic(self):
        kc_data = self.kc_load()
        trade_long = False
        trade_short = False
        kc_obj_low = {"timestamp": "2011-01-01T00:00:00Z",
                      "close": "100000",
                      "cross_status": "NULL",
                      "bbwp": "0",
                      "rsi": "0",
                      "emaL": "1",
                      "emaM": "1",
                      "emaH": "1",
                      "daily_ema": "1"}
        kc_obj_high = {"timestamp": "2011-01-01T00:00:00Z",
                      "close": "1",
                      "cross_status": "NULL",
                      "bbwp": "0",
                      "rsi": "0",
                      "emaL": "1",
                      "emaM": "1",
                      "emaH": "1",
                      "daily_ema": "1"}
        ee = []
        best_ee_long = []
        best_ee_short = []
        current_high = kc_obj_high
        current_low = kc_obj_low
        UP = "cross_up"
        DOWN = "cross_down"
        entry_i = 0
        exit_i = 0

        for idx, x in enumerate(kc_data):
            if not trade_long and not trade_short:
                if x['cross_status'] == UP:
                    entry_i = idx
                    exit_i = idx
                    trade_long = True
                    kc_obj = x
                    current_high = x
                if x['cross_status'] == DOWN:
                    entry_i = idx
                    exit_i = idx
                    trade_short = True
                    kc_obj = x
                    current_low = x

            # First find the best exit candle
            if trade_long and float(x['close']) > float(current_high['close']):
                current_high = x
                exit_i = idx
            if trade_short and float(x['close']) < float(current_low['close']):
                current_low = x
                exit_i = idx

            if x['cross_status'] == DOWN and trade_long:
                ee.append((kc_obj, x, "long"))
                #once next cross is confirmed look for previous best entry before high and after entry
                current_low = kc_obj_low
                roi = 0
                for i in range(entry_i, exit_i):
                    if float(kc_data[i]['close']) < float(current_low['close']):
                        current_low = kc_data[i]
                if entry_i >= exit_i:
                    current_low = current_high
                #roi = ((float(current_low[1]['close']) / float(current_high[0]['close'])) - 1) * 100
                best_ee_long.append((current_low, current_high, "long", roi))
                current_high = x
                trade_long = False
                trade_short = True
                kc_obj = x
                entry_i = idx
            if x['cross_status'] == UP and trade_short:
                ee.append((kc_obj, x, "short"))
                current_high = kc_obj_high
                for i in range(entry_i, exit_i):
                    if float(kc_data[i]['close']) > float(current_high['close']):
                            current_high = kc_data[i]
                best_ee_short.append((current_low, current_high, "short"))
                current_low, current_high = x, x
                trade_long = True
                trade_short = False
                kc_obj = x
                entry_i = idx
        print("\n".join([str(long) for long in best_ee_long if long[2] == "long"]))
        return ee, best_ee_long, best_ee_short

    def entry_exit_analysis(self, roi):
        # What do I wanna know
            # How far from 9,21,55 ema was the e/e from?
            # Current bbwp
            # State of RSI
            # Current daily trend
        basic_ee, longs, shorts = self.entry_exit_basic()

        longs_analysis = []
        short_analysis = []
        long_bbwp = []
        long_rsi = []
        long_ema_l_spread = []
        long_ema_m_spread = []
        long_ema_h_spread = []
        long_daily_ema = []
        long_roi = []

        for long in longs:
            entry = KCObj(long[0])
            exit = KCObj(long[1])
            timestamp, close, cross_status, bbwp, emaL, emaM, emaH, daily_ema, rsi = entry.timestamp, entry.close, \
                                                                      entry.cross_status, entry.bbwp, entry.emaL,\
                                                                      entry.emaM, entry.emaH, entry.daily_ema, entry.rsi

            ema_l_dif = ema_dif(close, emaL, "long")
            ema_m_dif = ema_dif(close, emaM, "long")
            ema_h_dif = ema_dif(close, emaH, "long")
            roi = ema_dif(exit.close, close, "long")
            longs_analysis.append(
                {"ema_l_dif": ema_l_dif,
                 "ema_m_dif": ema_m_dif,
                 "ema_h_dif": ema_h_dif,
                 "rsi": rsi,
                 "bbwp": bbwp,
                 "roi": roi}
            )
            long_rsi.append(rsi)
            long_ema_l_spread.append(ema_l_dif)
            long_ema_m_spread.append(ema_m_dif)
            long_ema_h_spread.append(ema_h_dif)
            long_daily_ema.append(daily_ema)
            long_bbwp.append(bbwp)
            long_roi.append(roi)
        for short in shorts:
            entry = KCObj(short[1])
            exit = KCObj(short[0])
            timestamp, close, cross_status, bbwp, emaL, emaM, emaH, daily_ema, rsi = entry.timestamp, entry.close, \
                                                                      entry.cross_status, entry.bbwp, entry.emaL,\
                                                                      entry.emaM, entry.emaH, entry.daily_ema, entry.rsi

            ema_l_dif = ema_dif(close, emaL, "short")
            ema_m_dif = ema_dif(close, emaM, "short")
            ema_h_dif = ema_dif(close, emaH, "short")
            roi = ema_dif(close, exit.close, "short")

            short_analysis.append(
                {"ema_l_dif": ema_l_dif,
                 "ema_m_dif": ema_m_dif,
                 "ema_h_dif": ema_h_dif,
                 "rsi": rsi,
                 "bbwp": bbwp,
                 "roi": roi}
            )
        print(long_roi)
        #plot longs bbwap entry
        metrics = [("rsi", long_rsi), ("ema_l_spread",long_ema_l_spread), ("ema_m_spread", long_ema_m_spread),
                   ("ema_h_spread",long_ema_h_spread), ("daily_ema",long_daily_ema), ("bbwp", long_bbwp), ("roi", long_roi)]
        print(long_rsi)
        for metric in metrics:
            blue = []
            blue_idx = []
            red = []
            red_idx = []
            for idx in range(len(metric[1])):
                if long_roi[idx] < 8:
                    blue.append(metric[1][idx])
                    blue_idx.append(idx)
                else:
                    red.append(metric[1][idx])
                    red_idx.append(idx)
            plt.scatter(x=blue_idx, y=blue, c="#00BFFF")
            plt.scatter(x=red_idx, y=red, c="#FF0000")
            plt.ylabel(metric[0])
            plt.figure()

        plt.show()



    def get_roi(self):
        basic_ee, longs, shorts = self.entry_exit_basic()

        position_entry_exit = []
        # for entries in positions:
        #     position_entry_exit.append((entries[0][0].isoformat(), entries[1][0].isoformat()))
        # print(position_entry_exit)
        average_roi_list = []
        #print(longs)
        # sorted_positions = sorted(longs.items(), key=lambda kv: kv[1]['pnl'], reverse=True)

        for long in longs:
            average_roi_list.append(((float(long[1]['close'])/float(long[0]['close']))-1)*100)
        print(average_roi_list)


        win_loss = []
        win = 0
        loss = 0
        capital = 1000
        # for x in positions:
        #     average_roi_list.append(round((((x[1][1]/x[0][1])-1)*100), 3))
        # for y in positions:
        #     if y[0][1] < y[1][1]:
        #         win_loss.append("W")
        #         win += 1
        #     else:
        #         win_loss.append("L")
        #         loss += 1
        # print(len(average_roi_list))
        # print(average_roi_list)
        # b_w = max(average_roi_list)
        # b_l = min(average_roi_list)
        # print("Biggest Winner =", b_w, "| Biggest Loser =", b_l)
        # average_trade = sum(average_roi_list)/len(average_roi_list)
        # print("Trade Average: {}%".format("{:.2f}".format(average_trade)))
        # print("Percentage Win: {}%".format(("{:.2f}".format(win/(win+loss)*100))))
        # w_l = (win/(win+loss) * 100)

        for z in average_roi_list:
            #print("trade:", capital)
            capital = capital * (1+(z/100))
        print(capital)
        # return {
        #         "w_l": w_l,
        #         "average_trade": average_trade,
        #         "capitol_ending": capital,
        #         "total_trades": len(average_roi_list)
        #         }

    # def __str__(self):
    #     kc = self.ema_crosses()
    #     return "Start: %s\nTimeframe: %s\nTotal Crosses: %s\nTotal Occurrences: %s" % \
    #            (kc['start'],
    #             kc['timeframe'],
    #             kc['total_crosses'],
    #             kc['cross_occurrences'])

    # def entry_exit_basic_backup(self):
    #     kc_data = self.kc_load()
    #     trade_long = False
    #     trade_short = False
    #     kc_obj_low = {"timestamp": "2011-01-01T00:00:00Z",
    #                   "close": "100000",
    #                   "cross_status": "NULL",
    #                   "bbwp": "0",
    #                   "rsi": "0",
    #                   "emaL": "1",
    #                   "emaM": "1",
    #                   "emaH": "1",
    #                   "daily_ema": "1"}
    #     kc_obj_high = {"timestamp": "2011-01-01T00:00:00Z",
    #                    "close": "1",
    #                    "cross_status": "NULL",
    #                    "bbwp": "0",
    #                    "rsi": "0",
    #                    "emaL": "1",
    #                    "emaM": "1",
    #                    "emaH": "1",
    #                    "daily_ema": "1"}
    #     ee = []
    #     best_ee_long = []
    #     best_ee_short = []
    #     current_high = kc_obj_high
    #     current_low = kc_obj_low
    #     UP = "cross_up"
    #     DOWN = "cross_down"
    #     entry_i = 0
    #     found_i = 0
    #
    #     for idx, x in enumerate(kc_data):
    #         if not trade_long and not trade_short:
    #             if x['cross_status'] == UP:
    #                 entry_i = idx
    #                 found_i = idx
    #                 trade_long = True
    #                 kc_obj = x
    #                 current_high = x
    #             if x['cross_status'] == DOWN:
    #                 entry_i = idx
    #                 found_i = idx
    #                 trade_short = True
    #                 kc_obj = x
    #                 current_low = x
    #
    #         # First find the best exit candle
    #         if trade_long and float(x['close']) > float(current_high['close']):
    #             current_high = x
    #             found_i = idx
    #         if trade_short and float(x['close']) < float(current_low['close']):
    #             current_low = x
    #             found_i = idx
    #
    #         if x['cross_status'] == DOWN and trade_long:
    #             ee.append((kc_obj, x, "long"))
    #             # once next cross is confirmed look for previous best entry before high and after entry
    #             current_low = kc_obj_low
    #             for i in range(entry_i, found_i):
    #                 if float(kc_data[i]['close']) < float(current_low['close']):
    #                     current_low = kc_data[i]
    #             best_ee_long.append((current_low, current_high))
    #             current_high = x
    #             trade_long = False
    #             trade_short = True
    #             kc_obj = x
    #             entry_i = idx
    #         if x['cross_status'] == UP and trade_short:
    #             ee.append((kc_obj, x, "short"))
    #             current_high = kc_obj_high
    #             for i in range(entry_i, found_i):
    #                 if float(kc_data[i]['close']) > float(current_high['close']):
    #                     current_high = kc_data[i]
    #             best_ee_short.append((current_low, current_high))
    #             current_low, current_high = x, x
    #             trade_long = True
    #             trade_short = False
    #             kc_obj = x
    #             entry_i = idx
    #     [print(long) for long in best_ee_long]
    #     return ee, best_ee_long, best_ee_short


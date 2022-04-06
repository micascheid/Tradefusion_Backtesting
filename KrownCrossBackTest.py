from talib import abstract
from datetime import datetime, timedelta
from DailyTrend import DailyTrend
import json
from KCObj import KCObj

MA = 13
LOOKBACK = 252
EMA = abstract.Function('EMA')

class KrownCrossBackTest:
    def __init__(self, emaL, emaM, emaH, np_data, json_data, kc_file, ticker):
        self.np_data = np_data
        self.emaL = emaL
        self.emaM = emaM
        self.emaH = emaH
        self.emaLL = EMA(self.np_data, self.emaL)
        self.emaML = EMA(self.np_data, self.emaM)
        self.emaHL = EMA(self.np_data, self.emaH)
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
    #         #exit: bbwap > 80 first, 9 cross 21 for sure out
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
        #bbwap start:
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
            bbwp.append("{:.3f}".format((count/LOOKBACK)*100))
        return bbwp

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
        bbwap = self.bbwp()
        emaL = self.emaLL
        emaM = self.emaML
        emaH = self.emaHL
        cross_list = self.ema_crosses_2()['cross_list']

        # Deterine start point in which data is useful
            # which ever is greatest bbwap(Lookback + MA) or emaH*4
        ema_start = self.emaH*4
        start_time = ema_start if ema_start > LOOKBACK+MA else LOOKBACK+MA
        bbwp = self.bbwp()
        kc_list = []
        #start = datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0).isoformat()+"Z"

        for x in range(start_time, len(self.json_data)):
            time = (self.json_data[x]['timestamp'])
            date_only = datetime.strptime(time.strip("Z"), "%Y-%m-%dT%H:%M:%S").replace(hour=0, minute=0,
                                                                                        second=0).isoformat() + "Z"
            kc_dict = {"timestamp": str(self.json_data[x]['timestamp']),
                    "close": str(self.json_data[x]['close']),
                    "cross_status": str(cross_list[x-ema_start][1]),
                    "bbwap": str(bbwp[(x-start_time)+1]),
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
        # Returns a list of tuples(entry, exit)
        # Algo trade:
        #Risk Management: GTFO
            # stop 1: close above or below 55e
            # Expidited: above or below previous swing high/low - Note: bring in later as pivots are not calculated rn
        #Entry:
            # a.)
            # b.) Can start an entry with a close around 21 if more aggressive 55 if more conservative : Roger
            # c.) confirmation of rsi divergence : Negative
            # d.) low or downtrending bbwp : Roger
        #Exit: Which ever of the following comes first
            # a.) RSI divergence : Negative
            # b.) BBWP > 80 or 90 : Positive
            # c.) 9e crossing 21e
        # Invalidation:
            # hourly trend is against daily trend or suggests caution
            #
        # Other thoughts: Checking which regime BTC is in regarding bull market support band
        self.set_krown_cross_json_export()
        kc_data = self.kc_load()
        positions = []
        global entry
        global exit
        long_bias = False
        ema_mid_tolerance = 1
        ema_high_tolerance = 2
        last_entry = ""
        last_exit_time = datetime.strptime(kc_data[0]['timestamp'].strip('Z'), "%Y-%m-%dT%H:%M:%S")
        global in_trade
        in_trade = False
        LIMBO = "limbo"
        for x in kc_data:
            # convert json_obj variables back
            kc_obj = KCObj(x)

            timestamp, close, cross_status, bbwap, emaL, emaM, emaH, daily_ema = kc_obj.timestamp, kc_obj.close, \
                                                                      kc_obj.cross_status, kc_obj.bbwap, kc_obj.emaL,\
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
                    if ema_mid_dif <= ema_mid_tolerance and not (LIMBO in cross_status) and bbwap <= 20:
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
                if not (LIMBO in cross_status) and (bbwap >= 100 or close <= emaL):
                    # entry_time = datetime.strptime(entry.timestamp, "%Y-%m-%dT%H:%M:%S")
                    # exit_time = datetime.strptime(kc_obj.timestamp, "%Y-%m-%dT%H:%M:%S")
                    duration = (entry.timestamp - kc_obj.timestamp).seconds // 3600
                    positions.append(((entry.timestamp, entry.close), (kc_obj.timestamp, kc_obj.close), duration))
                    long_bias = False
                    in_trade = False
                    continue
                # if emaL <= emaM: #GTFO scenario
                #     positions.append((entry.close, kc_obj.close))
                #     long_bias = False
                #     in_trade = False

            #TODO looking for an exit on short

        return positions

    def get_roi(self):
        positions = self.entry_exit()
        average_roi_list = []
        win_loss = []
        win = 0
        loss = 0
        capital = 1000
        for x in positions:
            average_roi_list.append(round((((x[1][1]/x[0][1])-1)*100), 3))
        for y in positions:
            if y[0][1] < y[1][1]:
                win_loss.append("W")
                win += 1
            else:
                win_loss.append("L")
                loss += 1
        # print(len(average_roi_list))
        # print(average_roi_list)
        b_w = max(average_roi_list)
        b_l = min(average_roi_list)
        # print("Biggest Winner =", b_w, "| Biggest Loser =", b_l)
        average_trade = sum(average_roi_list)/len(average_roi_list)
        # print("Trade Average: {}%".format("{:.2f}".format(average_trade)))
        # print("Percentage Win: {}%".format(("{:.2f}".format(win/(win+loss)*100))))
        w_l = (win/(win+loss) * 100)

        for z in average_roi_list:
            #print("trade:", capital)
            capital = capital * (1+(z/100))
        return {
                "w_l": w_l,
                "average_trade": average_trade,
                "capitol_ending": capital
                }

    # def __str__(self):
    #     kc = self.ema_crosses()
    #     return "Start: %s\nTimeframe: %s\nTotal Crosses: %s\nTotal Occurrences: %s" % \
    #            (kc['start'],
    #             kc['timeframe'],
    #             kc['total_crosses'],
    #             kc['cross_occurrences'])

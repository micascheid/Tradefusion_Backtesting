import talib
from talib import abstract
from datetime import datetime, timedelta
import json

MA = 13
LOOKBACK = 252
EMA = abstract.Function('EMA')


class KrownCrossBackTest:
    def __init__(self, emaL, emaM, emaH, np_data, json_data):
        self.np_data = np_data
        self.emaL = emaL
        self.emaM = emaM
        self.emaH = emaH
        self.emaLL = EMA(self.np_data, self.emaL)
        self.emaML = EMA(self.np_data, self.emaM)
        self.emaHL = EMA(self.np_data, self.emaH)
        self.start = np_data['meta'][0]
        self.tf = np_data['meta'][1]
        self.json_data = json_data

    def ema_crosses(self):
        # emaH has not been evaulated above 55h time period and may see invalid results above that
            # start crossing analysis at emaH*4
        # full_cross is when all moving averages are in aline above or below one another
        # watch_cross is when faster ema is crossing middle moving average
        # paramater to tune the dials
            # When to enter? at cross? how far form 9 to enter? How far is acceptable to enter off 55?
            # Take profit
            # When to exit? at cross back over?
                # Hard Exit

        #Algo trade:
            #entry: After complete cross enter within 1% of 21 if oppurtunity occurs and risk to 55 ema is 2% or less
            #exit: bbwap > 80 first, 9 cross 21 for sure out
            #stop: close below emaH

        cross_start = self.emaH*4

        cross_occurence = {}
        cross_occurence_list = []
        cross_up = False
        cross_down = False
        new_cross = False
        total_crosses = 0
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
                if el > em > eh and cross_up == False:
                    cross_up, cross_down, new_cross = True, False, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = "cross_up"
                if el < em < eh and cross_down == False:
                    cross_up, cross_down, new_cross = False, True, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()+"Z"] = "cross_down"
                if new_cross:
                    total_crosses += 1
                new_cross = False
        else:
            return -1
        return {"start": self.start,
                "timeframe": self.tf,
                "total_crosses": total_crosses,
                "cross_occurrences": cross_occurence}

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
        print("length bbw:", len(bbw))
        for j in range((LOOKBACK+MA)-1, len(bbw)):
            count = 0
            current_bbw = bbw[j]
            for k in range(j-LOOKBACK, j):
                if bbw[k] < current_bbw:
                    count += 1
            bbwp.append("{:.3f}".format((count/LOOKBACK)*100))
        print("length bbwp:", len(bbwp))
        return bbwp

    def krown_cross_json_export(self):
        # Description: After the emaL, emaM, emaH, bbwap, and cross arrays have been created
            # this function export that information in a list of json objects to a file
            # under Data/krowncross/ for easier analysis on determing entry, exit and W/L
        print("Exporting list of krown cross data to file")
        json_data = self.json_data
        occurences = self.ema_crosses()['cross_occurrences']
        bbwap = self.bbwp()
        emaL = self.emaLL
        emaM = self.emaML
        emaH = self.emaHL


    def entry(self):
        #start off w basic entry where cross occurs
        bbwap_start = LOOKBACK+MA
        ema_crosses = self.ema_crosses()["cross_occurrences"]
        entry_price = 0
        for entry in ema_crosses:
            if ema_crosses[entry] == 'cross_up':
                for x in self.json_data:
                    if x['timestamp'] == entry:
                        entry_price = x['close']
            if ema_crosses[entry] == 'cross_down':
                for x in self.json_data:
                    if x['timestamp'] == entry:
                        entry_price = x['close']


    def exit(self):
        return print("exit")

    def roi(self, entry, exit):
        return print("roi")

    def __str__(self):
        kc = self.ema_crosses()
        return "Start: %s\nTimeframe: %s\nTotal Crosses: %s\nTotal Occurrences: %s" % \
               (kc['start'],
                kc['timeframe'],
                kc['total_crosses'],
                kc['cross_occurrences'])

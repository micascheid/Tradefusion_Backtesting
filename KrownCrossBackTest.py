import talib
from talib import abstract
from datetime import datetime, timedelta
import json

MA = 13
LOOKBACK = 252
class KrownCrossBackTest:
    def __init__(self, emaL, emaM, emaH, data):
        self.emaL = emaL
        self.emaM = emaM
        self.emaH = emaH
        self.data = data
        self.start = data['meta'][0]
        self.tf = data['meta'][1]
    def ema_crosses(self):
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

        EMA = abstract.Function('EMA')
        #print(self.data)
        emaL = EMA(self.data, self.emaL)
        emaM = EMA(self.data, self.emaM)
        emaH = EMA(self.data, self.emaH)
        cross_occurence = {}
        cross_occurence_list = []
        cross_up = False
        cross_down = False
        new_cross = False
        total_crosses = 0
        bbwp_start_time = self.start + timedelta(hours=LOOKBACK+MA)
        if len(emaL) == len(emaM) == len(emaH):
            #Establish Baseline, where are the ema's current position at start of analysis?
            l_start, m_start, h_start = emaL[self.emaH], emaM[self.emaH], emaH[self.emaH]
            if l_start > m_start > h_start:
                cross_up, cross_down = True, False
            elif l_start < m_start < h_start:
                cross_up, cross_down = False, True
            else:
                cross_up, cross_down = False, False

            for i in range(self.emaH, len(emaL)):
                el, em, eh = emaL[i], emaM[i], emaH[i]
                if el > em > eh and cross_up == False:
                    cross_up, cross_down, new_cross = True, False, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()] = "cross_up"
                if el < em < eh and cross_down == False:
                    cross_up, cross_down, new_cross = False, True, True
                    cross_occurence[(self.start+timedelta(hours=i)).isoformat()] = "cross_down"
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
        #talib.BBANDS(self.data['close'], timeperiod=13, matype=0)
        upper, middle, lower = BBANDS(self.data)
        bbw = []
        bbwp = []
        price = self.data['close']
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

    def entry(self):
        bbwap_start = LOOKBACK+MA
        ema_crosses = self.ema_crosses()
        entry_price = 0
        for entry in ema_crosses:
            if ema_crosses[entry] == 'cross_up':
                print("something for now")
        return print("entry")

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

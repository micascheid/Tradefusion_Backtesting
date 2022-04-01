import json
import API
from nomics import Nomics
import numpy as np
from datetime import datetime, timedelta


class DataGrab:
    start = 0
    def __init__(self, exchange, tf, market, start, end, file):
        self.exchange = exchange
        self.tf = tf
        self.market = market
        self.start = start
        self.end = end
        self.file = file
        self.nomics = API.KEY

    def apiCall(self, start, end):
        return self.nomics.Candles.get_candles(exchange=self.exchange, interval=self.tf, market=self.market,
                                               start=start, end=end)

    def get_data_np(self):
        raw_list = self.data_conglomeration(self.start, self.end)
        # print("List", raw_np_list)
        #timestampBuilder = []
        openArrayBuilder = []
        highBuilder = []
        lowBuilder = []
        closeBuilder = []
        volumeBuilder = []

        for i in raw_list:
            #timestampBuilder.append(i['timestamp'])
            openArrayBuilder.append(float(i['open']))
            highBuilder.append(float(i['high']))
            lowBuilder.append(float(i['low']))
            closeBuilder.append(float(i['close']))
            volumeBuilder.append(float(i['volume']))

        #timestamp = np.ndarray(timestampBuilder)
        meta = np.array([self.start, 1])

        openArray = np.array(openArrayBuilder)
        high = np.array(highBuilder)
        low = np.array(lowBuilder)
        close = np.array(closeBuilder)
        volume = np.array(volumeBuilder)

        return {
            'meta': meta,
            'open': openArray,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, raw_list



    #TODO
    def get_data_csv(self):
        # jsonObj = json.dumps(dictTest)
        # fileExport = open('exportADA.json', "w")
        # fileExport.write(jsonObj)

        # pdObj = pd.read_json('Results.py', orient='index')
        # csvData = pdObj.to_csv('BinanceUSDT.csv', index=False)
        # #
        # df = pd.read_csv('BinanceUSDT.csv')
        # df = dropna(df)
        # indicatorEMA = ema_indicator(close=df["close"], window=9)
        # #indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        # print(indicatorEMA.to_json())
        #print((indicator_bb.bollinger_lband())[21])
        print("csv data")

    def data_conglomeration(self, start, end):
        mainList = []
        DELTA = timedelta(hours=719)
        DELTANEXT = timedelta(hours=1)
        timeDiff = end-start
        totalHours = (timeDiff.days * 24) + timeDiff.seconds // 3600
        print('total hours:', totalHours)
        iteration = totalHours // 719
        lastHours = totalHours % 719
        print(lastHours)
        startNew = start
        if totalHours >= 719:
            for i in range(iteration):
                time1 = startNew
                time2 = startNew + DELTA
                json_obj = self.apiCall(start=time1.isoformat()+"Z", end=time2.isoformat()+"Z")
                for j in json_obj:
                    mainList.append(j)
                print(i,"|", time1, time2)
                startNew = time2 + DELTANEXT
        if lastHours != 0:
            json_obj = self.apiCall(start=startNew.isoformat()+"Z", end=end.isoformat()+"Z")
            for k in json_obj:
                mainList.append(k)
            print(iteration, "|", startNew, end)

        return mainList

    def export_data(self):
        np_list, raw_list = self.get_data_np()
        np.save('./Data/npy/'+self.file+".npy", np_list, allow_pickle=True)

        json_string = json.dumps(raw_list)
        file = open('./Data/json/'+self.file, 'w')
        file.write(json_string)
        file.close()

    def get_np_list(self):
        npy_lists = np.load('./Data/npy/' + self.file + '.npy', allow_pickle=True)
        return npy_lists.item()

    def check_data_set_times(self, results):
        HOUR_ADD = timedelta(hours=1)
        time_compare = results[0]['timestamp']
        missing_time = []

        for x in range(len(results)):
            while time_compare != results[x]['timestamp']:
                missing_time.append(time_compare)
                timeNext = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
                time_compare = (timeNext + HOUR_ADD).isoformat()+"Z"
            if time_compare == results[x]['timestamp']:
                timeNext = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
                time_compare = (timeNext + HOUR_ADD).isoformat()+"Z"
        return missing_time

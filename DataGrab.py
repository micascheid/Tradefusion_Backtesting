import json
import API
from nomics import Nomics
import numpy as np
from datetime import datetime, timedelta
from talib import abstract

def set_data_np_static(json_file_name, tf):
    with open("./Data/json/" + json_file_name, "r") as json_file:
        json_data = json.load(json_file)
        json_file.close()
    raw_list = json_data
    # print("List", raw_np_list)
    # timestampBuilder = []
    openArrayBuilder = []
    highBuilder = []
    lowBuilder = []
    closeBuilder = []
    volumeBuilder = []

    for i in raw_list:
        # timestampBuilder.append(i['timestamp'])
        openArrayBuilder.append(float(i['open']))
        highBuilder.append(float(i['high']))
        lowBuilder.append(float(i['low']))
        closeBuilder.append(float(i['close']))
        volumeBuilder.append(float(i['volume']))

    # timestamp = np.ndarray(timestampBuilder)
    meta = np.array([json_data[0]['timestamp'], tf])

    openArray = np.array(openArrayBuilder)
    high = np.array(highBuilder)
    low = np.array(lowBuilder)
    close = np.array(closeBuilder)
    volume = np.array(volumeBuilder)

    np_obj = {
               'meta': meta,
               'open': openArray,
               'high': high,
               'low': low,
               'close': close,
               'volume': volume
           }
    np.save('./Data/npy/' + json_file_name + ".npy", np_obj, allow_pickle=True)


def load_np_data_static(npy_file_name):
    npy_lists = np.load('./Data/npy/' + npy_file_name + '.npy', allow_pickle=True)
    return npy_lists.item()


def load_json_data_static(json_file_name):
    with open("./Data/json/" + json_file_name) as json_file:
        json_data = json.load(json_file)
        json_file.close()
    return json_data


def json_cleanup(json_obj, missing):
    if missing:
        return {
            "timestamp": json_obj["timestamp"],
            "open": json_obj["close"],
            "high": json_obj["close"],
            "low": json_obj["close"],
            "close": json_obj["close"],
            "volume": json_obj["volume"]
        }
    else:
        return {
            "timestamp": json_obj["timestamp"],
            "open": json_obj["open"],
            "high": json_obj["high"],
            "low": json_obj["low"],
            "close": json_obj["close"],
            "volume": json_obj["volume"]
        }


def get_missing_data_set_times(json_data_list):
    results = json_data_list
    HOUR_ADD = timedelta(hours=1)
    time_compare = results[0]['timestamp']
    missing_times = []
    for x in range(len(results)):
        while not time_compare == results[x]['timestamp']:
            missing_times.append(time_compare)
            time_next = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
            time_compare = (time_next + HOUR_ADD).isoformat() + "Z"
        if time_compare == results[x]['timestamp']:
            time_next = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
            time_compare = (time_next + HOUR_ADD).isoformat() + "Z"
    return missing_times


def add_missing_times(json_data_list):

    data = json_data_list
    missing_times = get_missing_data_set_times(data)
    final_json_list = []

    for x in range(len(data)):
        if len(missing_times) > 0:
            missing_time_convert = datetime.strptime(missing_times[0].strip("Z"), "%Y-%m-%dT%H:%M:%S")
            current_time_convert = datetime.strptime(data[x]['timestamp'].strip("Z"), "%Y-%m-%dT%H:%M:%S")
            current_time_convert2 = datetime.strptime(data[x-1]['timestamp'].strip("Z"), "%Y-%m-%dT%H:%M:%S")
            if x > 0:
                add_obj = data[x - 1]
            while current_time_convert > missing_time_convert > current_time_convert2 \
                    and len(missing_times) > 0:
                add_obj_2 = add_obj
                add_obj_2['timestamp'] = missing_time_convert.isoformat()+"Z"
                missing_times.pop(0)
                final_json_list.append(json_cleanup(add_obj_2, True))
                if len(missing_times) > 0:
                    missing_time_convert = datetime.strptime(missing_times[0].strip("Z"), "%Y-%m-%dT%H:%M:%S")

        final_json_list.append(json_cleanup(data[x], False))

    with open("./Data/json/BTC1d", 'w') as json_file:
        json_string = json.dumps(final_json_list)
        json_file.write(json_string)
        json_file.close()


def dup_check(json_data_list):
    og_len = len(json_data_list)
    dup_check_list = len({each['timestamp']: each for each in json_data_list}.values())
    if og_len != dup_check_list:
        print("your shit is wack")
        return True
    else:
        print("not dupes!")
        return False

def candle_merge_weekly(json_file_name, tf_wanted):
    SMA = abstract.Function("SMA")
    WEEKLY_SMA = 20
    #hard coded for now
    conversion = int(tf_wanted[:-1])

    with open("./Data/json/"+json_file_name, "r") as json_file:
        json_data = json.load(json_file)
        json_file.close()
    merged_candles = []
    start = 0
    #first find the first candle with 00:00:00 UTC time and build from there
    for idx, x in enumerate(json_data):
        time = datetime.strptime(x['timestamp'].strip("Z"), "%Y-%m-%dT%H:%M:%S")
        if time.hour == 0 and time.weekday() == 0:
            start = idx
            break
    print("start:", start)
    for x in range(start, len(json_data)-6, 7):
        timestamp = json_data[x]['timestamp']
        open_val = float(json_data[x]['open'])
        volume = 0
        high = float(json_data[x]['high'])
        low = float(json_data[x]['low'])
        for i in range(7):
            high = high if high > float(json_data[x+i]['high']) else float(json_data[x+i]['high'])
            low = low if low < float(json_data[x+i]['low']) else float(json_data[x+i]['low'])
            volume = volume + float(json_data[x+i]['volume'])
        close = float(json_data[x + 6]['close'])
        new_json = {
            "timestamp": timestamp,
            "open": open_val,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        }
        merged_candles.append(new_json)

    with open("./Data/json/BTC"+tf_wanted, "w") as new_data_file:
        data = json.dumps(merged_candles)
        new_data_file.write(data)
        new_data_file.close()

    set_data_np_static("BTC"+tf_wanted, 2)

    #write ema data
    ema_data = load_np_data_static("BTC1w")
    weekly_np = SMA(ema_data, WEEKLY_SMA)
    btc_ema_data = {}

    for x in range(len(merged_candles)):
        btc_ema_data[merged_candles[x]['timestamp']] = weekly_np[x]
    with open("./Data/ema/BTCWeeklyEMA", "w") as btc_ema_file:
        json_string = json.dumps(btc_ema_data)
        btc_ema_file.write(json_string)
        btc_ema_file.close()
    return merged_candles

def candle_merge(json_file_name, tf_wanted):

    #hard coded for now
    conversion = int(tf_wanted[:-1])

    with open("./Data/json/"+json_file_name, "r") as json_file:
        json_data = json.load(json_file)
        json_file.close()
    merged_candles = []
    start = 0
    #first find the first candle with 00:00:00 UTC time and build from there
    for idx, x in enumerate(json_data):
        time = datetime.strptime(x['timestamp'].strip("Z"), "%Y-%m-%dT%H:%M:%S")
        if time.hour == 0:
            start = idx
            break
    print("start:", start)
    for x in range(start, len(json_data)-1, conversion):
        timestamp = json_data[x]['timestamp']
        open_val = float(json_data[x]['open'])
        high = float(json_data[x]['high']) if float(json_data[x]['high']) > float(json_data[x+1]['high']) else \
            float(json_data[x+1]['high'])
        low = float(json_data[x]['low']) if float(json_data[x]['low']) < float(json_data[x+1]['low']) else \
            float(json_data[x+1]['low'])
        close = float(json_data[x+1]['close'])
        volume = float(json_data[x]['volume']) + float(json_data[x+1]['volume'])
        new_json = {
            "timestamp": timestamp,
            "open": open_val,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        }
        merged_candles.append(new_json)

    with open("./Data/json/BTC"+tf_wanted, "w") as new_data_file:
        data = json.dumps(merged_candles)
        new_data_file.write(data)
        new_data_file.close()

    set_data_np_static("BTC"+tf_wanted, 2)
    return merged_candles

def check_data_set_times(results):
    HOUR_ADD = timedelta(hours=1)
    time_compare = results[0]['timestamp']
    missing_time = []
    print(len(results))
    for x in range(len(results)):
        while time_compare != results[x]['timestamp']:
            missing_time.append(time_compare)
            timeNext = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
            time_compare = (timeNext + HOUR_ADD).isoformat()+"Z"
        if time_compare == results[x]['timestamp']:
            timeNext = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
            time_compare = (timeNext + HOUR_ADD).isoformat()+"Z"

    return missing_time

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

    def api_call(self, start, end, aggregate):
        if aggregate:
            if self.tf != "1h" or self.tf != "1d":
                print("Can only perfom aggregate candles on 1h and 1d timeframes")
            else:
                return self.nomics.Candles.get_candles(interval="1d", start=self.start, end=self.end, currency=self.market)
        else:
            print("exchange:", self.exchange, "tf:", self.tf, "market:", self.market)
            return self.nomics.Candles.get_candles(exchange=self.exchange, interval=self.tf, market=self.market,
                                                   start=start, end=end)

    def get_data_np(self):
        raw_list = self.data_conglomeration(self.start, self.end)
        add_missing_times(raw_list)
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
        start = datetime.strptime(start.strip("Z"), "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(end.strip("Z"), "%Y-%m-%dT%H:%M:%S")
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
                json_obj = self.api_call(start=time1.isoformat()+"Z", end=time2.isoformat()+"Z", aggregate=False)
                for j in json_obj:
                    mainList.append(j)
                print(i,"|", time1, time2)
                startNew = time2 + DELTANEXT
        if lastHours != 0:
            json_obj = self.api_call(start=startNew.isoformat()+"Z", end=end.isoformat()+"Z", aggregate=False)
            for k in json_obj:
                mainList.append(k)
            print(iteration, "|", startNew, end)

        return mainList

    def set_export_data(self):
        np_list, raw_list = self.get_data_np()
        np.save('./Data/npy/'+self.file+".npy", np_list, allow_pickle=True)

        json_string = json.dumps(raw_list)
        file = open('./Data/json/'+self.file, 'w')
        file.write(json_string)
        file.close()

    def load_np_list(self):
        npy_lists = np.load('./Data/npy/' + self.file + '.npy', allow_pickle=True)
        return npy_lists.item()



    def load_json_data(self):
        with open("./Data/json/"+self.file) as json_file:
            json_data = json.load(json_file)
            json_file.close()
        return json_data





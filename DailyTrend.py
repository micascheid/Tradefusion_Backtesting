import json
import API
import numpy as np
from datetime import datetime, timedelta
from talib import abstract

EMA = abstract.Function("EMA")
ema_daily = 21


class DailyTrend:
    def __init__(self, base):
        self.nomics = API.KEY
        self.base = base
        self.np_file = "./Data/dailytrend/" + self.base + ".npy"
        self.raw_json_file = "./Data/json/" + self.base + "DailyTrend"
        self.json_final_file = "./Data/dailytrend/" + self.base + "JSONFinal"
        self.ema_data_file = "./Data/dailytrend/" + self.base + "EMA"

    def get_daily_data(self):

        inception = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
        endtime = datetime.now().isoformat() + "Z"
        raw_list = self.nomics.Candles.get_candles(interval="1d", start=inception, end=endtime, currency=self.base)
        json_string = json.dumps(raw_list)
        file = open(self.raw_json_file, 'w')
        file.write(json_string)
        file.close()
        self.add_missing_times()

    def get_daily_data_exchange(self, exchange, market):
        inception = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0).isoformat() + "Z"
        endtime = datetime.now().isoformat() + "Z"
        raw_list = self.nomics.Candles.get_candles(exchange=exchange, interval="1d", market=market, start=inception,
                                                   end=endtime)
        json_string = json.dumps(raw_list)
        file = open(self.raw_json_file, 'w')
        file.write(json_string)
        file.close()
        self.add_missing_times()

    def set_np_data(self):
        with open(self.json_final_file) as json_file:
            raw_list = json.load(json_file)
            json_file.close()
        timestampBuilder = []
        openArrayBuilder = []
        highBuilder = []
        lowBuilder = []
        closeBuilder = []
        volumeBuilder = []
        cleaned_json = {}

        for i in raw_list:
            openArrayBuilder.append(float(i['open']))
            highBuilder.append(float(i['high']))
            lowBuilder.append(float(i['low']))
            closeBuilder.append(float(i['close']))
            volumeBuilder.append(float(i['volume']))

        openArray = np.array(openArrayBuilder)
        high = np.array(highBuilder)
        low = np.array(lowBuilder)
        close = np.array(closeBuilder)
        volume = np.array(volumeBuilder)

        np_list_built = {
                            'open': openArray,
                            'high': high,
                            'low': low,
                            'close': close,
                            'volume': volume
                        }

        np_list = np_list_built
        np.save(self.np_file, np_list, allow_pickle=True)

    def get_np_list(self):
        npy_lists = np.load(self.np_file, allow_pickle=True)
        return npy_lists.item()

    def get_ema_results(self):
        ema_list = self.get_np_list()
        return EMA(ema_list, ema_daily)

    def get_missing_data_set_times(self):
        with open(self.raw_json_file) as json_file:
            results = json.load(json_file)
            json_file.close()
        DAY_ADD = timedelta(days=1)
        time_compare = results[0]['timestamp']
        missing_time = []
        for x in range(len(results)):
            while not time_compare == results[x]['timestamp']:
                missing_time.append(time_compare)
                time_next = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
                time_compare = (time_next + DAY_ADD).isoformat() + "Z"
            if time_compare == results[x]['timestamp']:
                time_next = datetime.strptime(time_compare.strip('Z'), "%Y-%m-%dT%H:%M:%S")
                time_compare = (time_next + DAY_ADD).isoformat() + "Z"
        return missing_time

    def add_missing_times(self):
        with open(self.raw_json_file) as json_file:
            data = json.load(json_file)
            json_file.close()

        missing_times = self.get_missing_data_set_times()
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

        with open(self.json_final_file, 'w') as json_file:
            json_string = json.dumps(final_json_list)
            json_file.write(json_string)
            json_file.close()

    def export_ema_data(self):
        ema_list = self.get_ema_results()
        ema_export_dict = {}
        TIME_NEXT = timedelta(days=1)
        with open(self.raw_json_file, 'r') as raw_json:
            start_date_str = json.load(raw_json)[0]['timestamp']
            raw_json.close()
        time = start_date_str
        for x in ema_list:
            ema_export_dict[time] = x
            grab_time = datetime.strptime(time.strip("Z"), "%Y-%m-%dT%H:%M:%S")
            time = (grab_time + TIME_NEXT).isoformat() + "Z"
        with open(self.ema_data_file, 'w') as ema_data_file:
            ema_data_file.write(json.dumps(ema_export_dict))
            ema_data_file.close()


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

from datetime import datetime

CLOSE = "close"
BBWP = "bbwp"
EMA_LOW = "ema_low"
EMA_MID = "ema_mid"
EMA_HIGH = "ema_high"
DAILY_EMA = "daily_ema"
RSI = "rsi"
BMSB = "bmsb"


class KCObj:
    def __init__(self, kc_json_obj):
        self.timestamp = datetime.strptime(kc_json_obj['timestamp'].strip('Z'), "%Y-%m-%dT%H:%M:%S")
        self.close = float(kc_json_obj['close'])
        self.cross_status = kc_json_obj['cross_status']
        self.bbwp = float(kc_json_obj['bbwp'])
        self.emaL = float(kc_json_obj['emaL'])
        self.emaM = float(kc_json_obj['emaM'])
        self.emaH = float(kc_json_obj['emaH'])
        self.daily_ema = float(kc_json_obj['daily_ema'])
        self.rsi = float(kc_json_obj['rsi'])
        self.bmsb = bool(kc_json_obj['bmsb'])


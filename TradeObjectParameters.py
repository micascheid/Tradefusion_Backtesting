

class BestParameter:
    def __init__(self, result):
        self.result = result["bb"]

    def get_bbwp(self):
        return self.result["bbwp"]

    def get_rsi(self):
        return self.result["rsi"]

    def get_emaL(self):
        return self.result["emaL"]

    def get_emaM(self):
        return self.result["emaM"]

    def get_emaH(self):
        return self.result["emaH"]

    def get_daily_ema_pnl(self):
        return self.result["daily_ema_pnl"]

    def get_bmsb(self):
        return self.result["bmsb"]

    def get_max_drawdown(self):
        return self.result["max_drawdown"]

    def get_max_upside(self):
        return self.result["max_upside"]

    def get_w_l(self):
        return self.result["w_l"]

    def get_pnl(self):
        return self.result["pnl"]
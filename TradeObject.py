

class TradeObject:
    def __init__(self, time_entry, time_exit, duration, pnl, winorloss, type, bbwp_entry):
        self.time_entry = time_entry
        self.time_exit = time_exit
        self.duration = duration
        self.pnl = pnl
        self.winorloss = winorloss
        self.type = type
        self.bbwp_entry = bbwp_entry

    def get_json(self):
        return \
            {"time_entry": self.time_entry,
             "time_exit": self.time_exit,
             "duration": self.duration,
             "pnl": self.pnl,
             "winorloss": self.winorloss,
             "type": self.type
            }

    def get_time_entry(self):
        return self.time_entry

    def get_time_exit(self):
        return self.time_exit

    def get_duration(self):
        return self.duration

    def get_pnl(self):
        return self.pnl

    def get_winorloss(self):
        return self.winorloss

    def get_type(self):
        return self.type

    def __str__(self):
        return "{}, {}, type: {}, duration: {}, pnl: {}, bbwp_entry: {}".format(self.time_entry, self.time_exit,
                                                                              self.type,
                                                               self.duration, self.pnl, self.bbwp_entry)


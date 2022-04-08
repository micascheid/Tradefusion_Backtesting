import json
from datetime import datetime
import API
from nomics import Nomics
import urllib.request


class Usage():
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY

    def get_total_usage(self):
        print("Grabbing usage starting from the first of the month...")
        month = datetime.now().month
        year = datetime.now().year
        start = datetime(year=year, month=month, day=1).isoformat()+"Z"

        url = "https://api.nomics.com/v1/meta/usage?key="+self.API_KEY+"&start="+start
        usage = urllib.request.urlopen(url).read()
        json_list = json.loads(usage)
        total = sum([request['requests'] for request in json_list])
        print("Total request starting from:", start, "is", total)


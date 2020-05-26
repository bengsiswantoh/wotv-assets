from urllib.request import urlopen, Request
import xmltodict
from collections import OrderedDict
import json

host = "https://cache-na-wotvffbe-com.sqex-edge.jp/"
req = Request(url = host, method = "GET", headers={"MaxKeys":500})
ret = urlopen(req).read()
data = xmltodict.parse(xml)

def od2d(data):
    ret = {}
    for key,value in data.items():
        if isinstance(value, list) and isinstance(value[0], OrderedDict):
            ret[key] = [
                od2d(val)
                for val in value
            ]
        elif isinstance(value, OrderedDict):
            ret[key] = od2d(value)
        else:
            ret[key] = value
    return ret
data = od2d(data)
print()
contents = data["contents"]
print()

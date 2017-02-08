import requests
import time
import json

def query_server(**kwargs):

    data = {}
    data['arduino_id'] = json.dumps(kwargs["arduino_ids"])
    data['channel_name'] = json.dumps(kwargs["channel_names"])
    data['value_to_set'] = json.dumps(kwargs["precisions"])

    print data
    url = "http://127.0.0.1:5000/arduino/query"
    try:

        
        # start = time.time()
        # r = requests.post(url, data=data)
        r = requests.get(r"http://127.0.0.1:5000/arduino/query?arduino_id=['95432313837351E00271']&channel_names=[['i1','i2']]&precisions=[['2','2']]")
        response_code = r.status_code

        print response_code

        if response_code == 200:
            print r.text
        

    except Exception as e:
        print e


if __name__ == "__main__":

    for i in range(1):
        query_server(arduino_ids=["95432313837351E00271"], channel_names=[["i1","i2"]], precisions=[[1, 2]])
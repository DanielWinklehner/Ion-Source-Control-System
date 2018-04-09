import json
import requests

if __name__ == '__main__':
    url_str = 'http://10.77.0.4:5000/'

    r = requests.get(url_str + 'initialize/')

    # do a query test
    device_dict_list = [{
        'device_driver': 'Arduino',
        'device_id': '95433343933351B012C2',
        'locked_by_server': False,
        'channel_ids': ['v1', 'v2', 'i1', 'i2'],
        'precisions': [2, 2, 2, 2],
        'values': [None, None, None, None],
        'data_types': ['float', 'float', 'float', 'float']
    }]
    data = {'data': json.dumps(device_dict_list)}
    r = requests.post(url_str + 'device/query', data=data)

    print(r.text)

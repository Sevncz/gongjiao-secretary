#!/usr/bin/python
# coding: utf-8
# __author__ = 'SevnCZ'
# __email__ = "wecz0321@gmail.com"
# __copyright__ = "Copyright 2019, SevnCZ"
import requests
import json
import sendmsg

line_detail_url = 'http://www.bjbus.com/api/api_line_detail.php'
line_rttime_url = 'http://www.bjbus.com/api/api_line_rtime.php'

line_data_id = 5144892607000260306
headers = {
'Host':'www.bjbus.com',
'Accept':'application/json, text/plain, */*',
'Connection':'keep-alive',
'Proxy-Connection':'keep-alive',
'Cookie':'SERVERID=564a72c0a566803360ad8bcb09158728|1575454990|1575454978; PHPSESSID=2f40359a2c2a37de3a424d83c29d67db; acw_tc=3ccdc14515754549784621091e2e3e25b7043c70630c6f462271bdc9a01dc8',
'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.8(0x17000820) NetType/WIFI Language/zh_CN',
'Accept-Language':'zh-cn',
'Referer':'http://www.bjbus.com/api/index.php',
'Accept-Encoding':'gzip, deflate'
}


def get_line_detail(line_name, station_name):
    payload = {
        'linename': line_name,
        'dataid': line_data_id
    }
    response = requests.get(line_detail_url, payload, headers=headers)
    if response.status_code == 200:
        result_entity = response.json()
        status = result_entity['status']
        if 'ok' != status:
            print(result_entity)
            raise RuntimeError("请求失败")
        data = result_entity['data']
        if data:
            line_entity = data['line']
            if line_entity:
                v_stat_list = line_entity['v_stat_list']
                v_line_uuid = line_entity['v_line_uuid']
                for station in v_stat_list:
                    if station_name == station['v_stat_name']:
                        print('v_stat_seq ->', station['v_stat_seq'])
                        print('v_stat_name ->', station['v_stat_name'])
                        return station['v_stat_seq'], v_line_uuid


def get_rtime(station_seq, uuid):
    payload = {
        'uuid': uuid,
        'station': station_seq
    }
    response = requests.get(line_rttime_url, payload, headers=headers)
    if response.status_code == 200:
        result_entity = response.json()
        status = result_entity['status']
        if 'ok' != status:
            return None
        data = result_entity['data']
        if data:
            rtime = data['rTime']
            if rtime:
                return rtime


if __name__ == "__main__":
    linename = '110(天桥-地铁柳芳站)'
    stationname = '左家庄中街'
    station_seq, uuid = get_line_detail(linename, stationname)
    rtime_entity = get_rtime(station_seq, uuid)
    if rtime_entity:
        print(rtime_entity)
        if 'busTime' in rtime_entity:
            bus_time = rtime_entity['busTime']
            bus_time_type = rtime_entity['busTimeType']

            if '秒' == bus_time_type or bus_time <= 10:
                sendmsg.send_email(json.dumps(rtime_entity))
        elif 'rTips' in rtime_entity:
            sendmsg.send_email('已进站')

#!/usr/bin/python
# coding: utf-8
# __author__ = 'SevnCZ'
# __email__ = "wecz0321@gmail.com"
# __copyright__ = "Copyright 2019, SevnCZ"
import requests
import re
from ast import literal_eval
import sendmsg
from html.parser import HTMLParser

bjbus_url = "http://www.bjbus.com/home/ajax_rtbus_data.php"

def strip_tags(html):
    """
    Python中过滤HTML标签的函数
    >>> str_text=strip_tags("<font color=red>hello</font>")
    >>> print str_text
    hello
    """
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()
    return ''.join(result)

def get_line_dir(line_name, session):
    # 构建请求链接
    selbline = requests.utils.quote(line_name)
    url = bjbus_url + '?act=getLineDirOption&selBLine={}'.format(selbline)
    r = session.get(url, verify=False)
    r.encoding = r.apparent_encoding  # 处理编码
    rt = r.text
    # 匹配信息
    uuid_list = re.findall('(?<=value=")\d+', rt)
    busdir_list = re.findall('\((.*?)\)', rt)
    return dict(zip(busdir_list, uuid_list))


def get_station_dir(line_name, uuid, session):
    # 构建请求链接
    selbline = requests.utils.quote(line_name)
    url = '{}?act=getDirStationOption&selBLine={}&selBDir={}'.format(bjbus_url, selbline, uuid)
    r = session.get(url, verify=False)
    r.encoding = r.apparent_encoding  # 处理编码
    rt = r.text
    # 匹配信息
    seq_list = re.findall('(?<=value=")\d+', rt)
    station_list = re.findall('>(.*?)<', rt)
    station_list_clear = []
    for station_name in station_list:
        if station_name != '请选择上车站' and station_name != '':
            station_list_clear.append(station_name)
    return dict(zip(station_list_clear, seq_list))


def get_bus_station_info(line_name, uuid, station_seq, session):
    url = '{}?act=busTime&selBLine={}&selBDir={}&selBStop={}'.format(bjbus_url, line_name, uuid, station_seq)
    r = session.get(url, verify=False)
    html = literal_eval(r.text)['html']
    bus_info = re.findall('<\\\/p><p>(.*?)<\\\/p><\\\/article>', html)
    for info in bus_info:
        # 替换反斜杠
        return info.replace('\\', '')


def rec_str(mystr):
    # 输入't19'或者'T19'都能自动转换为'特19'
    return re.sub('t', '特', mystr, flags=re.I)


def main(line_name, direction, station_name):
    # 创建session，自动处理cookies，添加头信息
    request_session = requests.Session()
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    header = {'User-Agent': UA}
    request_session.headers.update(header)

    # 输入车次信息，获取班车的特征码uuid以及始末站
    line_name_tr = rec_str(line_name)
    line_info = get_line_dir(line_name_tr, request_session)
    if direction in line_info:
        uuid = line_info[direction]
        station_info = get_station_dir(line_name_tr, uuid, request_session)
        station_seq = station_info[station_name]
        time_info_html = get_bus_station_info(line_name_tr, uuid, station_seq, request_session)
        if time_info_html == '车辆均已过站' or time_info_html == '此方向上无车辆运行':
            print(time_info_html)
            return
        time_info = re.findall('<span>(.*?)</span>', time_info_html)
        print(time_info_html)
        time = time_info[1]
        if int(time) <= 20:
            time_info_str = strip_tags(time_info_html)
            print(time_info_str)
            sendmsg.send_sms_myself(time_info_str.replace('此', ' {} '.format(station_name)))


if __name__ == '__main__':
    linename = '110'
    direction = "天桥-地铁柳芳站"
    stationname = '左家庄中街'
    # linename = '122'
    # direction = "北京西站南广场-北京站东"
    # stationname = '光明桥'
    main(linename, direction, stationname)

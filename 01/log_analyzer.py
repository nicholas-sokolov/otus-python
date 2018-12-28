#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
from datetime import datetime
import json
import os
import re
import argparse

#
# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}
log_name_pattern = re.compile(r'([a-zA-Z0-9\-]+).\S+(\d{8}).(\S+)')
log_pattern = r"""(?P<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s+](?P<remote_user>\w+)?[\s\-](?P<http_x_real_ip>.+?)\[(?P<time_local>\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2} [\+|\-]\d{4})\]\s+\"(?P<method>\S{3,10}) (?P<request>\S+) HTTP\/1\.\d\" (?P<status>\d{3}) (?P<body_bytes_sent>\d+) \"(?P<http_referer>[\-|\S+]+)?\" \"(?P<http_user_agent>.+)\" \"(?P<http_x_forwarded_for>.+)\" \"(?P<http_X_REQUEST_ID>.+)\" \"(?P<http_X_RB_USER>.+)\" (?P<request_time>\d+\.\d+)"""


def main():
    log_name = 'nginx-access-ui'

    parser = argparse.ArgumentParser(usage='%(prog)s --config configfile.json',
                                     description='Log parser', formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('--config', type=str,
                        help='Path to external config file (default: local config will be used)')
    args = parser.parse_args()
    # Config
    settings = get_settings(args.config)
    log_dir = settings['LOG_DIR']
    log_path = find_log(log_dir, log_name)
    if not log_path:
        exit(1)
    log_data = parse_log(log_path)

    print(log_path)

    # get data and analyze

    # render html


def get_settings(configfile):
    """ Получить настройки из файла если он есть, затем обновить локальные настройки
    :param str configfile: Путь до json файла с настройками
    :return: Dictionary с настройками
    """
    settings = {}
    if configfile is None:
        return config
    elif os.path.exists(configfile) and os.path.getsize(configfile):
        with open(configfile) as file:
            settings = json.load(file)

    return config.update(settings)


def find_log(log_dir, name):
    """ Найти последний лог с требуемым названием в директории с логами
    :param str log_dir: Путь к директории с логами
    :param str name: Название лога
    :return: str|None, путь к логу если он найден иначе None
    """
    try:
        logs_list = os.listdir(log_dir)
    except FileNotFoundError as err:
        print(err)
        exit(1)

    result_list = []
    for log_item in logs_list:
        if not log_name_pattern.findall(log_item):
            continue
        log_name, date, ext = log_name_pattern.findall(log_item)[0]
        item_date = datetime.strptime(date, '%Y%m%d')

        if log_name == name:
            if not result_list:
                result_list.append(log_item)
                continue
            _log_name, _date, _ext = log_name_pattern.findall(result_list[0])[0]
            _item_date = datetime.strptime(date, '%Y%m%d')
            if item_date > _item_date:
                result_list = [log_item]

    # возможно нужно здесь выйти если логов нет
    if not result_list:
        return None
    return os.path.join(log_dir, result_list[0])


def parse_log(path):
    if os.path.splitext(path)[-1] == '.gz':
        with gzip.open(path) as f:
            file_content = f.readlines()
    else:
        with open(path) as f:
            file_content = f.readlines()
    pattern = re.compile(log_pattern)
    result = {}
    for item in file_content:
        if not pattern.search(item.decode()):
            # TODO: сделать подсчет доли нераспаршеных записей
            continue
        log_line = pattern.search(item.decode())
        key = log_line.group('request')
        time = float(log_line.group('request_time'))

        try:
            count = result.get(key).get('count') + 1
            time_sum = round(result.get(key).get('time_sum') + time, 3)
        except AttributeError as err:
            count = 1
            time_sum = time
        result.update({key: {'count': count, 'time_sum': time_sum}})

    print(result)


if __name__ == "__main__":
    main()

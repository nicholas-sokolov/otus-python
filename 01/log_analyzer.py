#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
log_pattern = re.compile(r'([a-zA-Z0-9\-]+).\S+(\d{8}).(\S+)')


def main():
    log_name = 'nginx-access-ui'

    parser = argparse.ArgumentParser(usage='%(prog)s --config configfile.json',
                                     description='Log parser', formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('--config', type=str,
                        help='Path to external config file (default: local config will be used)')
    parser.print_help()
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
    # try:
    logs_list = os.listdir(log_dir)
    # except Exception as err:
    result_list = []
    for log_item in logs_list:
        if not log_pattern.findall(log_item):
            continue
        log_name, date, ext = log_pattern.findall(log_item)[0]
        item_date = datetime.strptime(date, '%Y%m%d')

        if log_name == name:
            if not result_list:
                result_list.append(log_item)
                continue

            _log_name, _date, _ext = log_pattern.findall(result_list[0])[0]
            _item_date = datetime.strptime(date, '%Y%m%d')
            if item_date > _item_date:
                result_list = [log_item]

    if not result_list:
        return None
    return os.path.join(log_dir, result_list[0])


def parse_log(path):
    pass


if __name__ == "__main__":
    main()

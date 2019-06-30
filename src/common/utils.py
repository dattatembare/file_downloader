"""
    utils.py
    Utils class provided the utility functions for string, date and other common operations
    DownloadUrl class is named tuple, it has file_url, out_dir and search_data variables
"""
from src.common.download_exceptions import DownloadException

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import bs4
import datetime
from dateutil.relativedelta import relativedelta
import ntpath
import pathlib
import requests
import os
import logging
from collections import namedtuple
# from common.download_exceptions import *
import re

DownloadUrl = namedtuple('DownloadUrl', ['file_url', 'out_file', 'search_data', 'report_group', 'params', 'method'])
DownloadUrl.__new__.__defaults__ = (None,) * len(DownloadUrl._fields)

DealInfo = namedtuple('DealInfo', ['deal_id', 'deal_name', 'link', 'f_html'])


class Utils:
    """
    Utils class has utility methods used in downloader modules and classes
    """
    STR_XML_ = '.xml'

    def format_html(self, html_str):
        """
        format html page source, BeautifulSoup makes sure formatted output source is valid for parsing
        :param html_str: html page source string
        :return: formatted html
        """
        soup = bs4.BeautifulSoup(html_str, 'html5lib')
        f_html = soup.prettify()
        logging.debug(f'Formatted html::: {f_html}')
        return f_html

    def date_range(self, time_span):
        """
        prepare the list of date object/s for provided time span,
            if mm/yyyy then date one object of 01/mm/yyyy
            if mm/yyyy-mm/yyyy then list date objects for given time span
        :param time_span: mm/yyyy or mm/yyyy-mm/yyyy
        :return: list of dates
        """
        result = []
        dur = ['01/' + dt.strip() for dt in time_span.split('-')]
        start = self.get_datetime(dur[0])
        end = self.get_datetime(dur[1] if len(dur) > 1 else dur[0])
        while start <= end:
            result.append(start)
            start += relativedelta(months=1)
        return result

    def get_datetime(self, date_str, date_format='%d/%m/%Y'):
        """
        return datetime object for give date string
        :param date_str: date string
        :param date_format: date format string
        :return: datetime
        """
        return datetime.datetime.strptime(date_str, date_format)

    def latest_url(self, a_url, out_dir, provider, latest=datetime.datetime.now()):
        """
        This method is used only for FM
        :param a_url: access url
        :param out_dir: output directory
        :param latest: current timestamp
        :return: latest available url on fm portal
        """
        f_url = a_url + latest.strftime("%b") + str(latest.year) + self.STR_XML_
        if self.is_url_exist(f_url):
            out_dir += '/' + str(latest.year) + '-' + str(latest.month) + '/' + provider
            o_file = self.out_file(f_url, out_dir)
            return DownloadUrl(f_url, o_file, '', str(latest.year) + '-' + latest.strftime("%b"))
        return self.latest_url(a_url, out_dir, provider, latest + relativedelta(months=-1))

    def out_file(self, url, o_dir, p_type=None):
        """
        appends extension from file url if not exist in filepath
        create directory to download the file
        :param url: url to download the file
        :param o_dir: output directory
        :param p_type: extra parameter to append to directory path
        :return: absolute file path
        """
        if p_type:
            o_dir += '/' + p_type
        o_file = o_dir + '/' + self._path_leaf(url) if not o_dir.__contains__('.') else o_dir
        try:
            # Create {o_dir} if not exist
            pathlib.Path(os.path.dirname(o_file)).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DownloadException('9000_UNEXPECTED_ERROR', e) from None
        return o_file

    def get_formatted_message(self, message, log_data_dict: dict) -> str:
        """
        Create enhanced log format line
        :param message: The original log message
        :param log_data_dict: One level dictionary of key/values to log
        :return: The formatted message
        """
        kv_list = [f'message={message}']
        kv_list += [f'{tup[0]}={tup[1]}' for tup in log_data_dict.items()]
        return ','.join(kv_list)

    def _path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def is_url_exist(self, url):
        """
        check if file exist on portal
        :param url: url to verify
        :return: boolean
        """
        request = requests.get(url)
        if request.status_code == 200:
            return True
        return False

    def validate_date(self, dt, date_format='%Y-%m-%d %H:%M:%S.%f'):
        """
        validate date and return boolean and datetime object
        :param dt: date string
        :param date_format: date format to verfy
        :return: datetime
        """
        try:
            return True, datetime.datetime.strptime(dt, date_format)
        except ValueError:
            return False, None

    def is_valid_time_span(self, time_span):
        """
        verify time span input
        :param time_span:
        :return:
        """
        if len(time_span) > 0:
            if time_span == 'latest':
                return True
            elif len(time_span) > 5 and len(time_span) < 8:
                # RegEx for mm/yyyy
                pattern1 = re.compile(b'^(0?[1-9]|1[012])(\/)\d{4}$')
                if pattern1.match(time_span):
                    return True
            elif len(time_span) > 11 and len(time_span) < 15:
                # RegEx for mm/yyyy-mm/yyyy
                pattern2 = re.compile(b'^(0?[1-9]|1[012])[\/]\d{4}[\-](0?[1-9]|1[012])[\/]\d{4}$')
                if pattern2.match(time_span):
                    return True
        return False

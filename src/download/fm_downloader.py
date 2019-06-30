"""
    fm_downloader.py
    module contains FMDownloader class to provide provider specific functionality
"""
__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import logging

from common.utils import DownloadUrl
from download.file_downloader import FileDownloader


class FMDownloader(FileDownloader):
    """
    FMDownloader class provided the functions for parsing page source code
        parse()  : implementation for fm provider
    """
    STR_XML_ = '.xml'

    def parse(self, **opts):
        """
        method parses the FM specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.debug('FMDownloader:parse')
        time_span = opts['tspan']
        out_dir = opts['output']
        access_urls = opts['access_urls']
        download_urls = list()
        for a_url in access_urls:
            if time_span == 'latest':
                download_urls.append(self.utils.latest_url(a_url['url'], out_dir, opts['provider']))
            else:
                for d in self.utils.date_range(time_span):
                    f_url = a_url['url'] + d.strftime("%b") + str(d.year) + self.STR_XML_
                    if self.utils.is_url_exist(f_url):
                        o_dir = out_dir + '/' + str(d.year) + '-' + str(d.month) + '/' + opts['provider']
                        o_file = self.utils.out_file(f_url, o_dir)
                        download_urls.append(DownloadUrl(f_url, o_file, '', str(d.year) + '-' + d.strftime("%b")))
        a_url['download_urls'] = download_urls

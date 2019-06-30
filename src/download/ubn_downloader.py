"""
    ubn_downloader.py
    module contains UbnDownloader class to provide provider specific functionality
"""
__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import logging

import lxml.html

from common.download_exceptions import DownloadException
from common.utils import DownloadUrl
from download.file_downloader import FileDownloader


class UbnDownloader(FileDownloader):
    """
    UbnDownloader class has functions for parsing page source code
        parse()  : implementation for 'ubn' provider
    """

    def _login_failed(self, provider, response):
        if 'Your user ID or password was invalid' in response.text:
            return True
        else:
            return False

    def parse(self, **opts):
        """
        method parses the 'ubn' specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.debug('UbnDownloader:parse')
        provider = opts['provider']
        out_dir = opts['output']
        access_config = self.configs.access_config[provider]
        site_url = access_config['site-url']
        for a_url in opts['access_urls']:
            download_urls = list()
            for xpath in a_url['xpath']:
                for deal_info_dict in a_url['deal_info_dict_list']:
                    if 'f_html' in deal_info_dict:
                        tree = lxml.html.fromstring(deal_info_dict['f_html'])
                        try:
                            tr = tree.xpath(xpath)
                        except Exception as e:
                            raise DownloadException('4000_PARSING_FAILED', e)
                        search_data = ''
                        yyyy_mon = ''
                        for td in tr:
                            td_txt = td.text.strip()
                            if td_txt:
                                if 'Investor Report' in td_txt:
                                    search_data = ''
                                    search_data += td_txt + '||'
                                else:
                                    dt = self.utils.validate_date(td_txt)
                                    if dt[0]:
                                        yyyy_mon = str(dt[1].year) + '-' + str(dt[1].month)
                                        search_data += dt[1].strftime("%b") + ' ' + str(dt[1].year) + '||'
                                    else:
                                        search_data += td_txt + '||'
                            w_td = td.xpath('a/@href | a/text()')
                            for href, a_text in zip(*[iter(w_td)] * 2):
                                logging.debug(f'href:: {href} a_text:: {a_text}')
                                f_url = site_url + href.strip()
                                o_file = out_dir + '/' + yyyy_mon + '/' + provider + '/' + deal_info_dict['dealName']
                                o_file += '/' + deal_info_dict['dealName'] + '-Investor-Report-' + yyyy_mon
                                o_file += '.' + a_text.strip()
                                download_urls.append(
                                    DownloadUrl(f_url, o_file, search_data, deal_info_dict['dealName']))
                # del a_url['f_html']
                a_url['download_urls'] = download_urls

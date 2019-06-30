"""
    wf_downloader.py
    module contains WellsFargoDownloader class to provide provider specific functionality
"""
import logging

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import lxml.html

from common.download_exceptions import DownloadException
from common.utils import DownloadUrl
from download.file_downloader import FileDownloader


class WFDownloader(FileDownloader):
    """
    WellsFargoDownloader class has functions for parsing page source code
        parse()  : implementation for 'ubn' provider
    """

    def _login_failed(self, provider, response):
        """
        Verify login
        Message from site:
        '{"messageCode":null,"message":"There was an error processing your request. Please try again. WCA1163",
         "status":"ERROR","currentAction":null,"nextAction":"login","targetUrl":"","id":null}'
         TODO raise exception from here
        :param provider:
        :param response:
        :return:
        """
        if 'There was an error processing your request. Please try again. WCA1163' in response.text:
            return True
        else:
            return False

    def parse(self, **opts):
        """
        method parses the 'WF' specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.debug('WellsFargoDownloader:parse')
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
                            trs = tree.xpath(xpath)
                        except Exception as e:
                            raise DownloadException('4000_PARSING_FAILED', e)
                        # to avoid the dates confusion, using first 3 items and 5th item from tr
                        # search_data will have only 'Current Cycle' date
                        for tr in trs:
                            # print(f'table.text :: {etree.tostring(tr)}')
                            td = tr.xpath('td')
                            if len(td) > 5:
                                w_td = td[1].xpath('a/@href | a/img/@alt')
                                for href, doc in zip(*[iter(w_td)] * 2):
                                    f_url = site_url + href.strip()
                                    search_data = doc.strip() + ' || '
                                if f_url:
                                    search_data += td[0].text.strip() + ' || '
                                    dt = self.utils.validate_date(td[2].text.strip(), '%m/%d/%Y')
                                    if dt[0]:
                                        yyyy_mon = str(dt[1].year) + '-' + str(dt[1].month)
                                        search_data += dt[1].strftime("%b") + ' ' + str(dt[1].year) + '||'
                                    if 'series_name' in deal_info_dict:
                                        deal_name = deal_info_dict['series_name']
                                        file_ext = '.csv'
                                    elif 'shelf_name' in deal_info_dict:
                                        deal_name = deal_info_dict['shelf_name']
                                        file_ext = '.zip'
                                    for hist_ele in td[5].xpath('a/@href'):
                                        hist_ele = hist_ele.strip()
                                        file_name = hist_ele[hist_ele.index('doc=') + 4:] + file_ext
                                        o_file = out_dir + '/' + yyyy_mon + '/' + provider + '/'
                                        o_file += deal_name + '/' + file_name
                                        download_urls.append(
                                            DownloadUrl(f_url, o_file, search_data, deal_name))
                        # del a_url['f_html']
                        a_url['download_urls'] = download_urls

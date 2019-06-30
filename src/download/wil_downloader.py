"""
    wil_downloader.py
    module contains WilmingtonDownloader class to provide provider specific functionality
"""
import logging
import re

import lxml.html

from common.utils import DownloadUrl
from download.file_downloader import FileDownloader


class WilDownloader(FileDownloader):
    """
    WilmingtonDownloader class has functions for parsing page source code
        parse()  : implementation for 'wil' provider
    """

    def parse(self, **opts):
        """
        method parses the 'wil' specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.info('WilmingtonDownloader:parse')
        # RegEx for dd-mon-YYYY
        pattern = re.compile('^(\d{1,2})(\/|-)([a-zA-Z]{3})(\/|-)(\d{2})$')
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
                        tr = tree.xpath(xpath)
                        s_data = ''
                        f_url = ''
                        o_dir = ''
                        dt_str = ''
                        for td in tr:
                            td_txt = td.text.strip()
                            if td_txt:
                                # This Date conversion is for Search criteria
                                if pattern.match(td_txt):
                                    m = pattern.search(td_txt)
                                    # receiving year as YY, 20 Hard coded to make YYYY, assuming data is 2000 onwards
                                    s_data += m.group(3) + ' 20' + m.group(5) + '||'
                                    dt_str = m.group(3) + m.group(5)
                                else:
                                    s_data += td_txt + '||'
                            w_td = td.xpath('a/@href | a/text()')
                            for href, a_text in zip(*[iter(w_td)] * 2):
                                logging.debug(f'href:: {href} a_text:: {a_text}')
                                f_url = site_url + href.strip().replace('Snapshot', 'ExportSnapshotData')
                                o_dir = out_dir + '/' + provider + '/' + a_text.strip()
                        download_urls.append(DownloadUrl(f_url, o_dir + '/' + dt_str + '.xlsx', s_data, ''))
                # del a_url['f_html']
                a_url['download_urls'] = download_urls

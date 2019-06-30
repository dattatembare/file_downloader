"""
    ct_downloader.py
    module contains CTDownloader class to provide provider specific functionality
"""
import logging

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import lxml.html

from common.download_exceptions import DownloadException
from download.file_downloader import FileDownloader


class CTDownloader(FileDownloader):
    """
    CTDownloader class has functions for parsing page source code
        parse()  : implementation for 'ct' provider
    """

    def _login_failed(self, provider, response):
        if "Login failed" in response.text:
            return True
        else:
            return False

    def parse(self, **opts):
        """
        method parses the 'ct' specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.debug('CTDownloader:parse')
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
                        # xpath = "body/div/div/div/table/tbody/tr/td/form/table[3]/tbody/tr/td"
                        # table[3] or table[@class='tableBorder'] gives same result
                        try:
                            tr = tree.xpath(xpath)
                        except Exception as e:
                            raise DownloadException('4000_PARSING_FAILED', e)
                        for td in tr:
                            if td.text.strip():
                                stmt_grp = td.text.strip()
                            mbs_tds = td.xpath("a/@href | a/text() | span/text()")
                            for href, a_text, s_text in zip(*[iter(mbs_tds)] * 3):
                                logging.debug(f'href:{href}, report_name:{a_text}, payment_date:{s_text}')
                                stm_date = self._get_statement_date(s_text.strip())
                                f_url = site_url + href.strip()
                                o_dir = out_dir + '/' + str(stm_date.year) + '-' + str(stm_date.month)
                                o_dir += '/' + provider + '/' + stmt_grp
                                s_data = a_text.strip() + ' || ' + s_text.strip() + ' || ' + stmt_grp
                                download_urls.append(DownloadUrl(f_url, o_dir, s_data, stmt_grp))
            # del a_url['f_html']
            a_url['download_urls'] = download_urls

    def _get_statement_date(self, stm_date_str):
        dt_list = stm_date_str.split()
        if len(dt_list) > 2:
            dd_mon_yyyy = '01-' + dt_list[2] + '-' + dt_list[-1].replace(')', '')
            return self.utils.get_datetime(dd_mon_yyyy, "%d-%b-%Y")
        else:
            # When date is not available then return old date
            return self.utils.get_datetime('01-Jan-1900', "%d-%b-%Y")

"""
    bony_downloader.py
    module contains BonyDownloader class to provide provider specific functionality
"""

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import datetime
import itertools

import lxml.html
import requests

from common.download_exceptions import DownloadException
from download.file_downloader import FileDownloader


class BonyDownloader(FileDownloader):
    """
    BonyDownloader class has functions for parsing page source code
        parse()  : implementation for 'BONY' provider
    """

    def authenticate(self, provider):
        """
        Step 1:: Authenticate and login to provider's portal
        :param provider: provider
        :return: requests session
        """
        logging.debug('BonyDownloader:authenticate')
        auth_config = self.configs.auth_config[provider]
        access_config = self.configs.access_config[provider]
        session = requests.Session()
        logging.debug(f':::1 Connect to {access_config["login-url"]} and get cookies')
        session.get(access_config['login-url'])
        logging.debug(f':::2 Call {access_config["auth-url"]} page')
        # requests will use the available cookies from session
        try:
            res1 = session.post(access_config["auth-url"], data=auth_config)
            if self._login_failed(provider, res1):
                raise DownloadException('2000_AUTHENTICATION_FAILED',
                                        custom_message=f"Authentication failed for {provider}")
            logging.debug(f'Login status :: {res1.status_code}')
            # BONY request need certificate key for each request
            f_html = self.utils.format_html(res1.text)
            tree = lxml.html.fromstring(f_html)
            csrf_key = tree.xpath('//form[@name="NavForm"]/input[@name="csrfKey"]/@value')[0]
        except Exception as e:
            raise DownloadException('2000_AUTHENTICATION_FAILED', e) from None
        return session, {'for_next_params': True, 'csrfKey': csrf_key}

    def _login_failed(self, provider, response):
        if 'Invalid Login' in response.text:
            return True
        else:
            return False

    def access(self, session, **opts):
        """
        Step 2:: Pull access URL/s from configs file and use it to pull page source which has URLs for file download
            after method execution a_url['deal_info_dict_list'] appended to opts dictionary
        TODO Use namedtuple DealInfo to make current dictionary generic to all providers
        :param session: session with site cookies
        :param opts: user/commandline inputs
        :return: None
        """
        logging.debug('FileDownloader:access')
        provider = opts['provider']
        previous_url_results = list()
        for a_url in opts['access_urls']:
            logging.debug(f':::3 Send request to {a_url} page')
            # Pull input parameters to append as a query string
            user_config = opts['user_input_config'] if 'user_input_config' in opts else None
            user_inputs = user_config['input'] if user_config else self.configs.user_input_config[provider][
                'input']
            deal_info_list = self._prepare_params(a_url, user_inputs)
            # Update URL with values pulled from previous page response
            deal_info_list = self._use_previous_url_result(deal_info_list, previous_url_results)
            # After use clean the previous_url_results
            previous_url_results = []
            for deal_info in deal_info_list:
                params = deal_info['params']
                from_opts = opts['response_dict'] if 'response_dict' in opts else {}
                params = {**params, **from_opts}
                opts['response_dict'] = {}
                try:
                    if a_url['method'] == 'POST':
                        res = session.post(deal_info['link'], data=params)
                    elif a_url['method'] == 'GET':
                        res = session.get(deal_info['link'], params=params)
                except Exception as e:
                    raise DownloadException('3000_ACCESS_FAILED', e)
                logging.debug(f'status code :: {res.status_code} history :: {res.history} response URL :: {res.url}')
                f_html = self.utils.format_html(res.text)
                tree = lxml.html.fromstring(f_html)
                for ele_name, ele_value in a_url['result-dict'].items():
                    if 'for_next_params' in ele_name:
                        _result = self._dict_for_next_url(ele_value, tree)
                        _result['for_next_params'] = True
                        previous_url_results.append(_result)
                        deal_info['for_next_params'] = _result
                        opts['response_dict'] = {'csrfKey': _result['csrfKey']}
                    elif 'for_next_url' in ele_name:
                        _result = self._dict_for_next_url(ele_value, tree)
                        _result['for_next_url'] = True
                        previous_url_results.append(_result)
                    elif 'deal_info' in ele_name:
                        deal_info['deal_info'] = self._dict_for_next_url(ele_value, tree)
                    elif 'for_parsing' in ele_name:
                        f_html_trees = list()
                        for xp in ele_value:
                            f_html_trees.append(tree.xpath(xp))
                        deal_info['f_html'] = f_html_trees
            a_url['deal_info_dict_list'] = deal_info_list

    def _prepare_params(self, a_url, user_inputs):
        # pull mandatory input parameters from access-config
        input_param_dict = a_url['input-param']
        # prepare links for next request/s
        links_with_params = list()
        for attr_name, attr_values in user_inputs.items():
            for attr_value in attr_values:
                req_body = input_param_dict.copy()
                req_body[attr_name] = attr_value
                links_with_params.append({'link': a_url['url'], 'params': req_body})
        return links_with_params

    def _use_previous_url_result(self, links, previous_url_results):
        if len(links) == len(previous_url_results):
            for link, previous_url_result in zip(links, previous_url_results):
                if 'hd_deal_number' in previous_url_result:
                    deal_num = previous_url_result['hd_deal_number']
                    deal_num = deal_num[:deal_num.index('~')] if deal_num else deal_num
                    previous_url_result['hd_deal_number'] = deal_num
                if 'for_next_params' in previous_url_result:
                    link['params'] = {**link['params'], **previous_url_result}
        else:
            for link, previous_url_result in itertools.product(links, previous_url_results):
                if 'for_next_params' in previous_url_result:
                    link['params'] = {**link['params'], **previous_url_result}
        return links

    def _dict_for_next_url(self, input_dict, tree):
        # print(f'table.text :: {etree.tostring(tree)}')
        result_dict = dict()
        for k, xp in input_dict.items():
            try:
                xp_result = tree.xpath(xp)
                result_dict[k] = ''.join(xp_result).strip()
            except Exception as e:
                raise DownloadException('3000_ACCESS_FAILED', e)
        return result_dict

    def parse(self, **opts):
        """
        method parses the 'BONY' specific page source using xpath from access-configs, after method execution
            a_url['download_urls'] appended to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        logging.debug('BonyDownloader:parse')
        out_dir = opts['output']
        provider = opts['provider']
        for a_url in opts['access_urls']:
            download_urls = list()
            for deal_info_dict in a_url['deal_info_dict_list']:
                if 'f_html' in deal_info_dict:
                    f_url = a_url['for_download_urls']['download_url']
                    input_dict = a_url['for_download_urls']['request_body'].copy()
                    for k, v in deal_info_dict['for_next_params'].items():
                        if 'for_next_params' not in k:
                            input_dict[k] = v
                    deal_name = deal_info_dict['deal_info']['deal_name']
                    for trs in deal_info_dict['f_html']:
                        for tr in trs:
                            # print(f'table.text :: {etree.tostring(tr)}')
                            report_id = tr.xpath('td/input[@name="cb_rpt_id"]/@value')
                            report_name = ''.join(tr.xpath('td[2]/a/text()')).strip()
                            if len(report_id) > 0:
                                report_id = report_id[0][:report_id[0].index('~')]
                            payment_date = tr.xpath('td[6]/text()')
                            if len(payment_date) > 0:
                                payment_date = payment_date[0].strip()
                                dt = datetime.datetime.strptime(payment_date, "%d-%b-%Y")
                            for span in tr.xpath('td/span[@class="RecordNormalText"]/input'):
                                report_ext_key = span.xpath('@name')[0]
                                report_ext_value = span.xpath('@value')[0]
                                file_extension = report_ext_value[report_ext_value.index('~') + 1:]
                                input_dict_copy = dict(input_dict)
                                input_dict_copy['hd_avl_rpt_id'] = report_id
                                input_dict_copy[report_ext_key] = report_ext_value
                                input_dict_copy['lb_reportdate'] = dt.strftime("%B") + '++' + str(dt.year)
                                input_dict_copy['hd_extension'] = file_extension
                                o_file = out_dir + '/' + str(dt.year) + '-' + str(dt.month) + '/' + provider + '/'
                                o_file += (deal_name + ' pay ' + payment_date + ' ' + report_name).replace(' ', '_')
                                o_file += '.' + file_extension
                                search_data = report_id + ' || ' + report_name + ' || ' + dt.strftime("%b") + ' '
                                search_data += str(dt.year) + ' || ' + deal_name
                                download_urls.append(
                                    DownloadUrl(f_url, o_file, search_data, deal_name, input_dict_copy, 'POST'))
                    # del a_url['f_html']
                    a_url['download_urls'] = download_urls

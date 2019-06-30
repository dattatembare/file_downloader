"""
    file_downloader.py
    module contains FileDownloader for whole file downloading functionality,
"""

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import abc
import datetime
import logging

import lxml.html
import requests
from dateutil.relativedelta import relativedelta

from common.download_exceptions import DownloadException
from common.utils import Utils
from configs.config import Config


class FileDownloader(metaclass=abc.ABCMeta):
    """
    class provides the functions for whole file downloading functionality, file downloader has -
        authentication() : checks authentication details in auth_config and authenticates using provided user details,
                           returns session object after successful login
        access() : navigates through the portal, pulls page source code and generates formatted page source,
                   formatted html appended to opts dictionary (a_url['f_html'] = f_html_list)
        parse()  : abstract function, each provider has to implementation their own parsing functionality,
                   parser generates list of download url dictionaries, appends a_url['download_urls'] to opts
        filter() : filters the URLs dictionary using user inputs (provided in user-input-configs)
                   and updates download url dictionaries
        download_files() : Downloads files to output directory using details provided in download url dictionary
        file_transfer()  : Transfers the files to desired path (configured in file-transfer-configs)
    """

    def __init__(self):
        self._configs = Config()
        self._utils = Utils()
        self.format_log_msg = self._utils.get_formatted_message

    @property
    def configs(self):
        return self._configs

    @property
    def utils(self):
        return self._utils

    def authenticate(self, provider):
        """
        Step 1:: Authenticate and login to provider's portal
        :param provider: provider
        :return: requests session
        """
        logging.debug('FileDownloader:authenticate')
        auth_config = self.configs.auth_config[provider]
        access_config = self.configs.access_config[provider]
        session = requests.Session()
        logging.debug(f':::1 Connect to {access_config["login-url"]} and get cookies')
        session.get(access_config['login-url'])
        # logging.info(f'Session cookies {s.cookies.get_dict()}')
        logging.debug(f':::2 Call {access_config["auth-url"]} page')
        # requests will use the available cookies from session
        try:
            res1 = session.post(access_config["auth-url"], data=auth_config)
            if self._login_failed(provider, res1):
                raise DownloadException('2000_AUTHENTICATION_FAILED',
                                        custom_message=f"Authentication failed for {provider}")
            logging.debug(f'Login status :: {res1.status_code}')
            # logging.info(f'Page Details:::: {res1.status_code}, {res1.cookies.get_dict()}, res1.headers, {res1.text}')
        except Exception as e:
            raise DownloadException('2000_AUTHENTICATION_FAILED', e) from None
        return session, None

    def _login_failed(self, provider, response):
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
            deal_info_list = list()
            # Pull input parameters to append as a query string
            if len(a_url['input-param']) > 0:
                user_config = opts['user_input_config'] if 'user_input_config' in opts else None
                user_inputs = user_config['input'] if user_config else self.configs.user_input_config[provider]['input']
                deal_info_list = self._append_query_str_to_url(a_url, user_inputs)
            else:
                deal_info_list.append(a_url['url'])
            # Update URL with value pulled from previous page
            deal_info_list = self._urls_with_previous_result(a_url, deal_info_list, previous_url_results)
            for deal_info in deal_info_list:
                link = deal_info['link']
                params = deal_info['params'] if 'params' in deal_info else {}
                try:
                    if a_url['method'] == 'POST':
                        res = session.post(link, data=params)
                    elif a_url['method'] == 'GET':
                        res = session.get(link, params=params)
                except Exception as e:
                    raise DownloadException('3000_ACCESS_FAILED', e, f'Access failed for {a_url["method"]} - {link}')
                logging.debug(f'status code :: {res.status_code} history :: {res.history} response URL :: {res.url}')
                if len(a_url['xpath']) > 0:
                    f_html = self.utils.format_html(res.text)
                    if 'for_next_url' in a_url['result-url-dict'] or 'for_next_params' in a_url['result-url-dict']:
                        previous_url_results.append(self._values_for_next_url(a_url, f_html))
                    else:
                        deal_info['f_html'] = f_html
            a_url['deal_info_dict_list'] = deal_info_list

    def _urls_with_previous_result(self, a_url, links, previous_url_results):
        if 'for_next_url' in a_url['result-url-dict']:
            return links
        elif 'for_next_params' in a_url['result-url-dict']:
            return links
        elif 'for_download' in a_url['result-url-dict']:
            return links
        elif len(previous_url_results) > 0 and 'for_next_url' not in a_url['result-url-dict']:
            for link in links:
                for result, index in zip(previous_url_results, range(len(previous_url_results))):
                    if 'for_next_url' in result:
                        attr_name = link[link.index('{') + 1:link.index('}')]
                        result['link'] = link.replace('{' + attr_name + '}', previous_url_results[index][attr_name])
        else:
            return list(map(lambda l: {'link': l}, links))
        return previous_url_results

    def _values_for_next_url(self, a_url, f_html, input_dict=None):
        result_dict = input_dict if input_dict else dict(a_url['result-url-dict'])
        tree = lxml.html.fromstring(f_html)
        key_list = list(a_url['result-url-dict'].keys())[1:]  # Excluding first element, Ex. 'for_next_url'
        for k, xp in zip(key_list, a_url['xpath']):
            try:
                result_dict[k] = tree.xpath(xp)[0].strip()
            except Exception as e:
                raise DownloadException('3000_ACCESS_FAILED', e, f'Access failed for xpath: {xp} and source {f_html}')
        return result_dict

    def _append_query_str_to_url(self, a_url, user_inputs):
        input_param_dict = a_url['input-param']
        links_with_params = list()
        for attr_name, attr_values in user_inputs.items():
            for attr_value in attr_values:
                req_body = input_param_dict.copy()
                req_body[attr_name] = attr_value
                links_with_params.append({'link': a_url['url'], 'params': req_body})
        return links_with_params

    @abc.abstractmethod
    def parse(self, **opts):
        """
        Step 3:: abstract method, provider specific parsing done in provider downloader class.
            Use xpath from access-configs to parse the page source, after method execution a_url['download_urls'] appended
            to opts dictionary
        :param opts: user/commandline inputs + a_url['deal_info_dict_list']
        :return:
        """
        pass

    def filter(self, **opts):
        """
        Step 4:: Use filter/s from user-input-configs and/or from commandline/scheduler and list URLs for file download
            Using user-input-config download URLs (a_url['download_urls']) filtered and updated
        :param opts: user/commandline inputs + a_url['deal_info_dict_list'] + a_url['download_urls']
        :return: None
        """
        provider = opts['provider']
        time_span = opts['tspan']
        for a_url in opts['access_urls']:
            filtered_urls = list()
            if 'download_urls' in a_url and len(a_url['download_urls']) > 0:
                download_urls = a_url['download_urls']
                if time_span == 'latest':
                    latest = datetime.datetime.now()
                    while len(filtered_urls) == 0:
                        time_span = str(latest.month) + '/' + str(latest.year)
                        filtered_urls = self._filter_urls(provider, download_urls, time_span)
                        latest = latest + relativedelta(months=-1)
                else:
                    filtered_urls = self._filter_urls(provider, download_urls, time_span)
            a_url['download_urls'] = filtered_urls

    def _filter_urls(self, provider, url_dicts, time_span):
        """
        Get provider specific file url for given filter configs and time span
        :param provider: provider
        :param url_dicts: having url related information
        :param time_span: time span
        :return: filtered urls dictionary list
        """
        t_span = self.utils.date_range(time_span)
        dates = list(map(lambda dt: dt.strftime("%b") + ' ' + str(dt.year), t_span))
        filters = self.configs.user_input_config[provider]['filters']
        urls = list()
        for url_dict in url_dicts:
            s_data = url_dict.search_data
            if len(filters) > 0 and len(dates) > 0 \
                    and len(list(filter(lambda f: s_data.__contains__(f), filters))) == len(filters) \
                    and len(list(filter(lambda d: s_data.__contains__(d), dates))) > 0:
                urls.append(url_dict)
            elif len(filters) == 0 and len(dates) > 0 \
                    and len(list(filter(lambda d: s_data.__contains__(d), dates))) > 0:
                urls.append(url_dict)
        return urls

    def download_files(self, session, **opts):
        """
        # Step 5::Download files to output directory, using urls and output directory in 'download_url' dictionary
        :param session: session object site cookies
        :param opts: user/commandline inputs + a_url['deal_info_dict_list'] + a_url['download_urls']
        :return: None
        """
        logging.debug('FileDownloader:Download files')
        download_count = 0
        for a_url in opts['access_urls']:
            if 'download_urls' in a_url:
                download_urls = a_url['download_urls']
                for download_url in download_urls:
                    d_url = download_url.file_url
                    o_file = download_url.out_file
                    o_file = self.utils.out_file(d_url, o_file)
                    if session:
                        if download_url.method and 'POST' in download_url.method:
                            response = session.post(d_url, data=download_url.params)
                        else:
                            response = session.get(d_url)
                    else:
                        response = requests.get(download_url.file_url, stream=True)
                    self._download(o_file, response)
                    logging.info(f"[Report: {download_url.report_group}] [{o_file}] downloaded")
                    download_count += 1
        if download_count == 0:
            raise DownloadException('6001_FILE_DOWNLOAD_NO_FILE')

    def _download(self, o_file, response):
        """
        Download file to output directory, raise exception of login session has expired
        :param o_file: output file path
        :param response: response
        :return: None
        """
        try:
            if response.status_code == 200:
                with open(o_file, 'wb') as output:
                    output.write(response.content)
            else:
                raise DownloadException('6000_FILE_DOWNLOAD_FAILED',
                                        custom_message=f'File not available {response.status_code}')
        except Exception as e:
            raise DownloadException('6000_FILE_DOWNLOAD_FAILED', e) from None

    def file_transfer(self, **opts):
        """
        Step 6:: Transfer files to destination path using file-transfer-configs
        TODO implementation for file transfer
        :param opts: user/commandline inputs + a_url['deal_info_dict_list'] + a_url['download_urls']
        :return:
        """
        logging.debug('FileDownloader:File Transfer')

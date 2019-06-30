"""
    processor.py
    Executes whole process for provided provider and inputs
    Processor steps ::
        authentication : checks authentication details in auth_config and authenticate using provided user details
        access : navigates through the portal, pulls page source code and returns formatted page source
        parse  : pull the desired data with help of formatted page source and xpaths (provided in access-configs)
                 and returns URL's dictionary
        filter : filters the URLs dictionary using user inputs (provided in user-input-configs)
                 and returns desired URL's dictionary
        download files : Downloads files to output directory using details provided in URL's dictionary
        transfer files : Transfers the files to desired path (configured in file-transfer-configs)
"""
__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'
import logging

from common.download_exceptions import DownloadException
from common.utils import Utils
from configs.config import Config
from download.bony_downloader import BonyDownloader
from download.ct_downloader import CTDownloader
from download.fm_downloader import FMDownloader
from download.ubn_downloader import UbnDownloader
from download.wf_downloader import WFDownloader
from download.wil_downloader import WilDownloader

error_logger = logging.getLogger("error_logger")


def _get_downloader_obj(provider):
    """
    downloader factory - generates provider specific downloader object
    :param provider: provider
    :return: provider specific downloader object
    """
    if provider == 'fm':
        downloader = FMDownloader()
    elif provider == 'ct':
        downloader = CTDownloader()
    elif provider == 'wil':
        downloader = WilDownloader()
    elif provider == 'ubn':
        downloader = UbnDownloader()
    elif provider == 'wf-wffm':
        downloader = WFDownloader()
    elif provider == 'wf-ry':
        downloader = WFDownloader()
    elif provider == 'wf-wfeu':
        downloader = WFDownloader()
    elif provider == 'bony':
        downloader = BonyDownloader()
    else:
        logging.info(f'No support for provider :: {provider}')
    return downloader


def validate_n_format(configs, **opts):
    """
    This method validate and format the commandline parameters provided by user
    Converting provider string to lowercase to match with configuration keys
    :param configs: reference to Config class object, which has all config details
    :param opts: commandline input parameters
    :return: None
    """
    opts['provider'] = opts['provider'].lower()
    opts['tspan'] = opts['tspan'].lower() if opts['tspan'] else 'latest'
    # Validations for provider, tspan and other input variables
    utils = Utils()
    if opts['provider'] not in configs.auth_config.keys():
        raise DownloadException('1001_INVALID_PROVIDER')
    elif not utils.is_valid_time_span(opts['tspan']):
        raise DownloadException('1002_INVALID_TIME_SPAN_FORMAT')


def process_profile(**opts):
    """
    process_profile method executes one or more providers listed for desired profile
    :param opts:
    :return:
    """
    configs = Config()
    profile = opts['profile'].lower()
    opts['output'] += '/' + profile
    profile_dict = configs.get_config(configs.profile_config[profile]['user-input-config'])
    for provider, user_input_config in profile_dict.items():
        logging.info(f'START processing :: profile {profile} for provider {provider}')
        opts['provider'] = provider
        opts['user_input_config'] = user_input_config
        process(**opts)
        logging.info(f'END processing :: process profile {profile} for provider {provider}')


def process(**opts):
    """
    process method validates inputs and executes all workflow methods for one provider
    :param opts: user/commandline inputs
    :return: None
    """
    session = None
    try:
        configs = Config()
        validate_n_format(configs, **opts)
        opts['provider'] = opts['provider'].lower()
        provider = opts['provider'].lower()
        # Start file download processing
        downloader = _get_downloader_obj(provider)
        auth_config = configs.auth_config[provider]
        access_config = configs.access_config[provider]
        opts['access_urls'] = access_config['access-url'].copy()
        logging.info(f"Retrieval initiated for {provider}")
        if auth_config:
            # Authenticate and login
            session, response_dict = downloader.authenticate(provider)
            opts['response_dict'] = response_dict
            # Access
            downloader.access(session, **opts)
            # Parse
            downloader.parse(**opts)
            # Filter files for download
            downloader.filter(**opts)
            # Download files
            downloader.download_files(session, **opts)
        else:
            logging.debug(f'Authentication not required for provider :: {provider}')
            # For 'FM' provider, access, parse and filter covered in parse method
            downloader.parse(**opts)
            # Download files
            downloader.download_files(session, **opts)
        # Transfer files to desired path
        downloader.file_transfer(**opts)
        logging.info(f"Storage complete for {provider}")
    except DownloadException as u:
        u.log_message()
        raise u
    except Exception as e:
        error_logger.exception(f'0000: ERROR - Unknown exception :: {e}')
        raise e
    finally:
        # Close session after file download
        if session:
            session.close()
    return opts

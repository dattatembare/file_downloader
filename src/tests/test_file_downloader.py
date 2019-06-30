import datetime
import os
import unittest
from collections import namedtuple

from dateutil.relativedelta import relativedelta

from common.download_exceptions import DownloadException
from common.utils import DownloadUrl
from download.ct_downloader import CTDownloader
from download.fm_downloader import FMDownloader
from download.ubn_downloader import UbnDownloader


class TestFileDownloader(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self._out_dir = os.getcwd()

    def tearDown(self):
        """tear down"""

    def test_login_failed_ct(self):
        print('Test: CT - Testing login failure check')
        Response = namedtuple('Response', 'text')
        downloader = CTDownloader()
        self.assertFalse(downloader._login_failed("ct", Response('bla')))
        self.assertTrue(downloader._login_failed("ct", Response('<html>Login failed</html>')))

    def test_login_failed_ubn(self):
        print('Test: UBN - Testing login failure check')
        Response = namedtuple('Response', 'text')
        downloader = UbnDownloader()
        self.assertFalse(downloader._login_failed("ct", Response('bla')))
        self.assertTrue(
            downloader._login_failed("ct", Response('<html>Your user ID or password was invalid</html>')))

    def test_download_files_success(self):
        print('Test: FM - Testing download success')
        o_file = self._out_dir + '/fm/2018-May/LoanLevel01May2018.xml'
        access_urls = [
            {'url': 'https://www.fm.com/wp-content/uploads/Pool01', 'method': 'GET', 'input-param': [],
             'xpath': [], 'result-url-dict': [],
             'download_urls': [DownloadUrl('https://www.fm.com/wp-content/uploads/LoanLevel01May2018.xml',
                                           o_file, '', '2018-May')]}]
        opts = dict()
        opts['access_urls'] = access_urls
        session = None
        downloader = FMDownloader()
        downloader.download_files(session, **opts)
        self.assertTrue(os.path.isfile(o_file))

    def test_download_files_no_file_available_404(self):
        print('Test: FM - Testing download fail because of file not available (404) on site')
        current_date = datetime.datetime.now()
        next_month = current_date + relativedelta(months=+1)
        o_file = self._out_dir + '/fm/2018-May/LoanLevel01' + next_month.strftime("%b") + str(
            next_month.year) + '.xml'
        access_urls = [
            {'url': 'https://www.fm.com/wp-content/uploads/Pool01', 'method': 'GET', 'input-param': [],
             'xpath': [], 'result-url-dict': [],
             'download_urls': [DownloadUrl(
                 'https://www.fm.com/wp-content/uploads/LoanLevel01' + next_month.strftime("%b") + str(
                     next_month.year) + '.xml',
                 o_file, '', str(next_month.year) + '-' + next_month.strftime("%b"))]}]
        opts = dict()
        opts['access_urls'] = access_urls
        session = None
        downloader = FMDownloader()
        try:
            downloader.download_files(session, **opts)
        except DownloadException as d:
            self.assertEqual('6000_FILE_DOWNLOAD_FAILED', d.cause.exception_code, 'Test failed!')
            self.assertEqual('File not available 404', d.cause.custom_message, 'Test failed!')

    def test_download_files_no_file_for_download(self):
        access_urls = [
            {'url': 'https://www.fm.com/wp-content/uploads/Pool01', 'method': 'GET', 'input-param': [],
             'xpath': [], 'result-url-dict': [],
             'download_urls': []}]
        opts = dict()
        opts['access_urls'] = access_urls
        session = None
        downloader = FMDownloader()
        try:
            downloader.download_files(session, **opts)
        except DownloadException as d:
            self.assertEqual('6001_FILE_DOWNLOAD_NO_FILE', d.exception_code, 'Test failed!')


if __name__ == "__main__":
    unittest.main()  # run all tests

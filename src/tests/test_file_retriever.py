import os
import unittest

from common.utils import Utils
from file_retriever import FileRetriever


class TestFileRetriever(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.ret = FileRetriever()
        self.utils = Utils()
        self._out_dir = os.getcwd() + '/tests-downloads'
        self.arg_dict = {"profile": "", "provider": "fm", "output": self._out_dir, "tspan": "latest"}
        try:
            os.lstat(self._out_dir)
        except FileNotFoundError:
            os.mkdir(self._out_dir)
        print(f'Test files download dir : {self._out_dir}')

    def tearDown(self):
        print('::::::::::: Deleting all downloaded files :::::::::::')
        # shutil.rmtree(self._out_dir)

    def test_download_latest_file_for_FM(self):
        print('Test 1: Download latest file for FM')
        opts = self.ret.retrieve(**self.arg_dict)
        self._verify_result(opts)

    def test_download_may_2018_file_for_FM(self):
        print('Test 2: Download May 2018 file for FM')
        self.arg_dict['tspan'] = '5/2018'
        opts = self.ret.retrieve(**self.arg_dict)
        self._verify_result(opts)

    def test_download_files_in_date_range(self):
        print('Test 3: Download all files in date range - June 2018 to Nov 2018 for FM')
        self.arg_dict['tspan'] = '6/2018-10/2018'
        opts = self.ret.retrieve(**self.arg_dict)
        self._verify_result(opts)

    def test_download_latest_file_for_CT(self):
        print('Test 4: Download latest file for CT')
        self.arg_dict['provider'] = 'ct'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_aug_2018_file_for_CT(self):
        print('Test 5: Download Aug 2018 file for CT')
        self.arg_dict['provider'] = 'ct'
        self.arg_dict['tspan'] = '8/2018'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_file_in_date_range_for_CT(self):
        print('Test 6: Download files from Sep 2018 to Nov 2018 for CT')
        self.arg_dict['provider'] = 'ct'
        self.arg_dict['tspan'] = '9/2018-11/2018'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    @unittest.skip("skip until fully implemented")
    def test_download_nov_2018_file_for_Wilmingtont(self):
        print('Test 7: Download Nov 2018 file for Wilmington')
        self.arg_dict['provider'] = 'wil'
        self.arg_dict['tspan'] = '11/2018'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_latest_file_for_ubn(self):
        print('Test 8: Download latest file for UBN')
        self.arg_dict['provider'] = 'ubn'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_april_2018_file_for_ubn(self):
        print('Test 9: Download April 2018 file for UBN')
        self.arg_dict['provider'] = 'ubn'
        self.arg_dict['tspan'] = '4/2018'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_files_from_may2018_to_oct2018_for_ubn(self):
        print('Test 10: Download files May 2018 to Oct 2018 files for UBN')
        self.arg_dict['provider'] = 'ubn'
        self.arg_dict['tspan'] = '5/2018-10/2018'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_latest_file_for_wf(self):
        print('Test 11: Download latest file for Wells Fargo')
        self.arg_dict['provider'] = 'wf-WFFM'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_latest_file_for_wf_shelf(self):
        print('Test 12: Download latest file for Wells Fargo shelf (Other Reports and Files)')
        self.arg_dict['provider'] = 'wf-RY'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_latest_file_for_wf_eu(self):
        print('Test 11: Download latest file for Wells Fargo')
        self.arg_dict['provider'] = 'wf-WFEU'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            self.fail(f'Test failed because of {e}')

    def test_download_latest_file_for_bony(self):
        print('Test 13: Download latest file for BONY')
        self.arg_dict['provider'] = 'bony'
        try:
            opts = self.ret.retrieve(**self.arg_dict)
            self._verify_result(opts)
        except Exception as e:
            if '6001_FILE_DOWNLOAD_NO_FILE' not in e.exception_code:
                self.fail(f'Test failed because of {e}')
            else:
                print(e.exception_code)

    def _verify_result(self, opts):
        for a_url in opts['access_urls']:
            if 'download_urls' in a_url:
                download_urls = a_url['download_urls']
                for download_url in download_urls:
                    o_file = self.utils.out_file(download_url.file_url, download_url.out_file)
                    self.assertTrue(os.path.isfile(o_file))


if __name__ == "__main__":
    unittest.main()  # run all tests

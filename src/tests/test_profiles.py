import os
import unittest

from file_retriever import FileRetriever


class TestFileRetriever(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.ret = FileRetriever()
        self._out_dir = os.getcwd() + '/tests-profiles'
        self.arg_dict = {'profile': 'jim', 'provider': None, 'output': self._out_dir, 'tspan': 'latest'}
        try:
            os.lstat(self._out_dir)
        except FileNotFoundError:
            os.mkdir(self._out_dir)
        print(f'Test files download dir : {self._out_dir}')

    def tearDown(self):
        print('::::::::::: Deleting all downloaded files :::::::::::')
        # shutil.rmtree(self._out_dir)

    def test_profile_jim(self):
        print('Test 1: Download latest file for profile "jim"')
        self.ret.retrieve(**self.arg_dict)

    def test_profile_mark(self):
        print('Test 1: Download latest file for profile "mark"')
        opts = self.arg_dict
        opts['profile'] = 'mark'
        self.ret.retrieve(**opts)

    def test_profile_wf(self):
        print('Test 1: Download latest file for profile "mark"')
        opts = self.arg_dict
        opts['profile'] = 'wf'
        self.ret.retrieve(**opts)


if __name__ == "__main__":
    unittest.main()  # run all tests

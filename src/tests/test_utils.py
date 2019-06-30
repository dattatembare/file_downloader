import datetime
import os
import shutil
import unittest

from common.utils import Utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.utils = Utils()
        self._out_dir = os.getcwd() + '/temp/'
        self._teardown_flag = False

    def tearDown(self):
        if self._teardown_flag:
            print('::::::::::: Deleting all test files :::::::::::')
            shutil.rmtree(self._out_dir)

    def test_format_html_for_broken_source(self):
        input_html = '<html><body><table><tr><td>test</td><td></tr></table></body></html>'
        expected_html = '<html>\n <head>\n </head>\n <body>\n  <table>\n   <tbody>\n    <tr>\n     <td>\n      test\n     </td>\n     <td>\n     </td>\n    </tr>\n   </tbody>\n  </table>\n </body>\n</html>'
        actual_html = self.utils.format_html(input_html)
        self.assertEqual(expected_html, actual_html, 'Actual html source did not match with expected html source')

    def test_format_html_for_good_source(self):
        input_html = '<html><body><table><tr><td>test</td></tr></table></body></html>'
        expected_html = '<html>\n <head>\n </head>\n <body>\n  <table>\n   <tbody>\n    <tr>\n     <td>\n      test\n     </td>\n    </tr>\n   </tbody>\n  </table>\n </body>\n</html>'
        actual_html = self.utils.format_html(input_html)
        self.assertEqual(expected_html, actual_html, 'Actual html source did not match with expected html source')

    def test_format_html_for_plain_text(self):
        input_html = 'Checking plain text'
        expected_html = '<html>\n <head>\n </head>\n <body>\n  Checking plain text\n </body>\n</html>'
        actual_html = self.utils.format_html(input_html)
        self.assertEqual(expected_html, actual_html, 'Actual html source did not match with expected html source')

    def test_date_range_one_month(self):
        in_date = '11/2018'
        expected_result = [datetime.datetime.strptime('01/11/2018', "%d/%m/%Y")]
        actual_result = self.utils.date_range(in_date)
        self.assertEqual(expected_result, actual_result, 'Dates are not matching')

    def test_date_range_multi_month(self):
        in_date = '9/2018-11/2018'
        expected_result = [datetime.datetime.strptime('01/9/2018', "%d/%m/%Y"),
                           datetime.datetime.strptime('01/10/2018', "%d/%m/%Y"),
                           datetime.datetime.strptime('01/11/2018', "%d/%m/%Y")]
        actual_result = self.utils.date_range(in_date)
        self.assertEqual(expected_result, actual_result, 'Dates are not matching')

    def test_date_range_invalid_input(self):
        in_date = '9/2018-11/2018-12/2018'
        expected_result = [datetime.datetime.strptime('01/9/2018', "%d/%m/%Y"),
                           datetime.datetime.strptime('01/10/2018', "%d/%m/%Y"),
                           datetime.datetime.strptime('01/11/2018', "%d/%m/%Y")]
        actual_result = self.utils.date_range(in_date)
        self.assertEqual(expected_result, actual_result, 'Dates are not matching')

    def test_out_file_success(self):
        self._teardown_flag = True
        in_url = 'http://lseg.com/test.pdf'
        in_dir = self._out_dir + 'out'
        expected_dir = self._out_dir + 'out/test.pdf'
        actual_dir = self.utils.out_file(in_url, in_dir)
        self.assertEqual(expected_dir, actual_dir, 'Generated directory is not correct')

    def test_out_file_success_with_partition(self):
        self._teardown_flag = True
        in_url = 'http://lseg.com/test.pdf'
        in_dir = self._out_dir + 'out'
        in_partition = 'level1'
        expected_dir = self._out_dir + 'out/level1/test.pdf'
        actual_dir = self.utils.out_file(in_url, in_dir, in_partition)
        self.assertEqual(expected_dir, actual_dir, 'Generated directory is not correct')

    def test_is_url_exist_success(self):
        in_url = 'https://www.fm.com/wp-content/uploads/LoanLevel01Oct2018.xml'
        actual_status = self.utils.is_url_exist(in_url)
        self.assertTrue(actual_status, 'URl is not exist')

    def test_is_url_exist_failure(self):
        in_url = 'https://www.fm.com/wp-content/uploads/LoanLevel01102018.xml'
        actual_status = self.utils.is_url_exist(in_url)
        self.assertFalse(actual_status, 'URl is exist')

    def test_validate_date_true(self):
        actual_date = self.utils.validate_date('1/1/2018', '%m/%d/%Y')
        self.assertTrue(actual_date[0], 'Date format not matching for input date')
        self.assertEqual(2018, actual_date[1].year, 'Year is not valid')
        self.assertEqual(1, actual_date[1].month, 'Month is not valid')
        self.assertEqual(1, actual_date[1].day, 'Day is not valid')

    def test_validate_date_false(self):
        actual_date = self.utils.validate_date('1-1-2018', '%m/%d/%Y')
        self.assertFalse(actual_date, 'Date format is matching for input date')

    def test_is_valid_time_span_latest(self):
        self.assertTrue(self.utils.is_valid_time_span('latest'), 'Invalid time span')

    def test_is_valid_time_span_jan_2018(self):
        self.assertTrue(self.utils.is_valid_time_span('1/2018'), 'Invalid time span')

    def test_is_valid_time_span_nov_2018(self):
        self.assertTrue(self.utils.is_valid_time_span('11/2018'), 'Invalid time span')

    def test_is_valid_time_span_range(self):
        self.assertTrue(self.utils.is_valid_time_span('1/2018-11/2018'), 'Invalid time span')

    def test_is_valid_time_span_false_current(self):
        self.assertFalse(self.utils.is_valid_time_span('current'), 'Valid time span')

    def test_is_valid_time_span_wrong_format_1(self):
        self.assertFalse(self.utils.is_valid_time_span('11-2018'), 'Valid time span')

    def test_is_valid_time_span_wrong_format_2(self):
        self.assertFalse(self.utils.is_valid_time_span('112018'), 'Valid time span')

    def test_is_valid_time_span_wrong_format_3(self):
        self.assertFalse(self.utils.is_valid_time_span('112018'), 'Valid time span')

    def test_is_valid_time_span_wrong_format_4(self):
        self.assertFalse(self.utils.is_valid_time_span('2018/10'), 'Valid time span')

    def test_is_valid_time_span_wrong_format_5(self):
        self.assertFalse(self.utils.is_valid_time_span('2018/10-2018/12'), 'Valid time span')


if __name__ == "__main__":
    unittest.main()  # run all tests

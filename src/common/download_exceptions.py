"""
    download_exceptions.py
    module contains DownloadException class to handle user exceptions
"""

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import logging


class DownloadException(Exception):
    """
    class is responsible to handle user and python built-in exceptions through this class
        exception_messages - Dictionary has errors/warnings from all the areas of application, more messages could be
            added by incrementing the number in particular area.
        log_message - Prints the error code, error message stored in exception_messages dictionary, original
            message from raised exception and custom message if provided
    """

    def __init__(self, exception_code, cause=None, custom_message=None):
        self.exception_code = str(exception_code)
        self.custom_message = custom_message
        self.cause = cause
        self.error_logger = logging.getLogger("error_logger")

    def log_message(self):
        """
        log the message using exception_code, custom_message and cause
        TODO use get_formatted_message
        :return: None
        """
        msg = self.custom_message if self.custom_message else exception_messages[self.exception_code]
        if self.cause:
            self.error_logger.error(f'{self.exception_code}: {msg} :: {self.cause} ')
        else:
            self.error_logger.error(f'{self.exception_code}: {msg}')


"""
exception_messages stored as exception_code and exception_message
"""
exception_messages = {
    '1000_VALIDATION_FAILED': 'Validation failed',
    '1001_INVALID_PROVIDER': 'Provider name is invalid or no support for this provider',
    '1002_INVALID_TIME_SPAN_FORMAT': 'Time span format is not correct, it should be either latest(text), mm/yyyy or mm/yyyy-mm/yyyy',
    '2000_AUTHENTICATION_FAILED': 'Authentication failed',
    '3000_ACCESS_FAILED': 'Access failed',
    '4000_PARSING_FAILED': 'Parsing failed',
    '5000_FILTER_FAILED': 'Filter failed',
    '6000_FILE_DOWNLOAD_FAILED': 'File Download failed',
    '6001_FILE_DOWNLOAD_NO_FILE': 'Files are not available for download',
    '7000_FILE_TRANSFER_FAILED': 'File Transfer failed',
    '8000_UTIL_METHOD_FAILED': 'Utils method call failed',
    '9000_UNEXPECTED_ERROR': 'Something went wrong'
}

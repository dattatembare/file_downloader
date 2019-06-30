"""
    file_retriver.py
    This is entry point for the application, the application could be called from command line, scheduler
    or any other application

"""

__author__ = 'Dattatraya Tembare<tembare.datta@gmail.com>'

import logging
from optparse import OptionParser

from download.processor import process
from download.processor import process_profile


class FileRetriever:
    """
    FileRetriever class processes profiles and specific providers
    """

    def retrieve(self, **opts):
        """
        retriever() checks the basic parameters availability and gives call to processor or process_profile
        Basic requirement is input combination of 'provider' and 'output' OR 'profile' and 'output'
            If all 4 input parameters provided then 'process_profile' execution starts
        :param opts: dictionary with 4 elements (output, provider, profile and tspan)
        :return: None
        """
        if opts['profile'] and opts['output']:
            process_profile(**opts)
        elif opts['provider'] and opts['output']:
            return process(**opts)
        else:
            print("Provide required parameter combination 'provider' and 'output' OR 'profile' and 'output'")


# Input variables from commandline/scheduler/Unit Tests
def main() -> object:
    """
    main method is entry point for commandline
    Application support 4 input parameters -
        output   : Desired output directory for files download (Required)
        provider : provider is vendor or data source name, required if profile is not provided
        profile  : profile is user who is responsible to download the files for multiple providers,
                    required if provider is not provided
        tspan    : Time span, it can be 'latest'(default) or 'mm/yyyy' or 'mm/yyyy-mm/yyyy'

    :return:
    """
    parser = OptionParser(usage="%prog [options] <url>")
    parser.add_option("-o", "--output", default=False, dest="output", help="Download File PATH", metavar="OUTPUT")
    parser.add_option("-s", "--provider", default=None, dest="provider", help="Provider provider", metavar="PROVIDER")
    parser.add_option("-p", "--profile", default=None, dest="profile", help="Profile name", metavar="PROFILE")
    parser.add_option("-t", "--tspan", default='latest', dest="tspan", help="Time span in mm/yyyy", metavar="DURATION")

    opts, args = parser.parse_args()
    logging.debug(f'opts: {opts} args: {args}')
    opts_dict = vars(opts)
    # Download Files
    d = FileRetriever()
    d.retrieve(**opts_dict)


if __name__ == '__main__':
    main()

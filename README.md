# FILE DOWNLOADER: 

**Application processing steps ::**

1. authentication : checks authentication details in auth_config and authenticate using provided user details

2. access : navigates through the portal, pulls page source code and returns formatted page source

3. parse  : pull the desired data with help of formatted page source and xpaths (provided in access-configs)
         and returns URL's dictionary

4. filter : filters the URLs dictionary using user inputs (provided in user-input-configs)
         and returns desired URL's dictionary

5. download files : Downloads files to output directory using details provided in URL's dictionary

6. transfer files : Transfers the files to desired path (configured in file-transfer-configs)

**Assumptions:**

1. All the keys used in config files (*-config.json) are lowercase with - or _



**To Download provider specific files use below commands ::**

1: Download provider specific latest file

    >python file_retriver.py --provider <provider name> --output <output directory>

2: Download profile specific latest files

    >python file_retriver.py --profile <profile name> --output <output directory>


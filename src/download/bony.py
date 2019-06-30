import datetime

import lxml.html
import requests

from common.utils import Utils
from configs.config import Config

# Get access URLs from config file
configs = Config()
utils = Utils()
a_config = configs.access_config['bony']
a_urls = a_config['access-url']
in_p_val = '04542BHM7'

# Session will be closed at the end of 'with' block
with requests.Session() as s:
    print(f':::1 Connect to {a_config["login-url"]} and get cookies')
    s.get(a_config["login-url"])
    # print(f"Session cookies {s.cookies.get_dict()}")
    print(f':::2 Call {a_config["auth-url"]} page, requests will use the available cookies from first request')
    res1 = s.post(a_config["auth-url"], data=configs.auth_config['bony'])
    # print(f'Page Details:::: {res1.status_code}, {res1.cookies.get_dict()}, res1.headers, {res1.text}')
    f_html = utils.format_html(res1.text)
    tree = lxml.html.fromstring(f_html)
    csrf_key = tree.xpath('//form[@name="NavForm"]/input[@name="csrfKey"]/@value')[0]
    # print(csrf_key)
    print(':::3 Pull access URL/s from config file and pull file download URL/s')
    download_urls = list()
    search_input = {"_Event": "Search.SearchDeal", "hd_page_number": "1", "hd_search_method": "BEGINS",
                    "hd_product_type": "ALL", "hd_display_by": "CUSIP", "hd_search_by": "CUSIP",
                    "hd_sort_by": "CUSIP_ASC", "hd_linkclicked": "", "hd_eventState": "HOMEPAGE",
                    "lb_product_type": "ALL", "lb_search_by": "CUSIP", "hd_records_per_page": "50",
                    "lb_quick_lookup": "Select", "rb_search_method": "BEGINS"}
    search_input['csrfKey'] = csrf_key
    # search_input['tb_search_for'] = in_p_val
    search_input['hd_search_for'] = in_p_val
    res2 = s.post('https://bony.com/GCTIRServices/SFRWServlet', data=search_input)
    f_html = utils.format_html(res2.text)
    # print(f_html)
    tree = lxml.html.fromstring(f_html)
    csrf_key = tree.xpath('//form[@name="NavForm"]/input[@name="csrfKey"]/@value')[0]
    deal_number = tree.xpath('//table[@id="FirstLevelDataTable"]/tbody/tr/td/input[@name="cb_cls_id"]/@value')[0]
    deal_number = deal_number[:deal_number.index('~')]
    print('Parse the CUSIP search result and find deal report')
    deal_report_input = {
        "_ReturnToEvent": "_Event%7ESEARCH.SEARCHDEAL%26_NavigationState%7EDEFAULT%26TB_SEARCH_FOR%7E04542BHM7%26HD_PAGE_NUMBER%7E1%26LB_SEARCH_BY%7ECUSIP%26LB_PRODUCT_TYPE%7EALL%26HD_EVENTSTATE%7EHOMEPAGE%26LB_QUICK_LOOKUP%7ESelect%26HD_PRODUCT_TYPE%7EALL%26HD_DISPLAY_BY%7ECUSIP%26HD_SEARCH_FOR%7E04542BHM7%26RB_SEARCH_METHOD%7EBEGINS%26HD_SEARCH_METHOD%7EBEGINS%26CSRFKEY%7Ep6mjWo9DDSwk8jm8lJO70Fxk0qZmigBI%26HD_LINKCLICKED%7E%26HD_SORT_BY%7ECUSIP_ASC%26HD_RECORDS_PER_PAGE%7E50%26HD_SEARCH_BY%7ECUSIP",
        "_Event": "DEAL.DealReports", "_NavigationState": "DEFAULT", "BreadCrumbOldEventState": "SEARCHDEAL",
    }
    deal_report_input['csrfKey'] = csrf_key
    deal_report_input['hd_deal_number'] = deal_number
    res3 = s.post('https://bony.com/GCTIRServices/SFRWServlet', data=deal_report_input)
    f_html_deal = utils.format_html(res3.text)
    # print(f_html_deal)
    tree = lxml.html.fromstring(f_html_deal)
    extract_file_input = {
        "_ReturnToEvent": "_Event%7EDEAL.DEALREPORTS%26_NavigationState%7EDEFAULT%26CSRFKEY%7Ep6mjWo9DDSx20qtuDA%2Bvl87uABCc2Tgz%26BREADCRUMBOLDEVENTSTATE%7ESEARCHDEAL%26HD_DEAL_NUMBER%7E28756",
        "hd_rpt_type": "R", "hd_action": "D", "BreadCrumbOldEventState": "SEARCHDEAL", "lb_portfolio": "0"
    }
    csrf_key = tree.xpath('//form[@name="NavForm"]/input[@name="csrfKey"]/@value')[0]
    # print(csrf_key)
    trs = tree.xpath('//table[@id="FirstLevelDataTable"]/tbody/tr')
    for tr in trs:
        # print(f'table.text :: {etree.tostring(tr)}')
        report_name = ''.join(tr.xpath('td[2]/a/text()')).strip()
        input_dict = extract_file_input.copy()
        report_id = tr.xpath('td/input[@name="cb_rpt_id"]/@value')
        if len(report_id) > 0:
            report_id = report_id[0][:report_id[0].index('~')]
        payment_date = tr.xpath('td[6]/text()')
        if len(payment_date) > 0:
            payment_date = payment_date[0].strip()
            dt = datetime.datetime.strptime(payment_date, "%d-%b-%Y")
            report_date = dt.strftime("%B") + '++' + str(dt.year)
        for span in tr.xpath('td/span[@class="RecordNormalText"]/input'):
            report_ext_key = span.xpath('@name')[0]
            report_ext_value = span.xpath('@value')[0]
            file_extension = report_ext_value[report_ext_value.index('~') + 1:]
            # print(report_id, report_ext_key, report_ext_value, report_date, file_extension)
            input_dict['csrfKey'] = csrf_key
            input_dict['hd_avl_rpt_id'] = report_id
            input_dict[report_ext_key] = report_ext_value
            input_dict['lb_reportdate'] = report_date
            input_dict['hd_extension'] = file_extension
            print(input_dict)
            response = s.post('https://bony.com/GCTIRServices/SFRWReportDownloadServlet',
                              data=input_dict)
            # f_html_download = utils.format_html(res4.text)
            # print(f_html_download)
            if response.status_code == 200:
                # ABFC_Asset-Backed_Certificates,_Series_2004-FF1_pay_26_nov_2018_Investor_Report_-_Detail.XLS
                with open('C:/POC/1/' + report_ext_value.replace('~', '.'),
                          'wb') as output:
                    output.write(response.content)

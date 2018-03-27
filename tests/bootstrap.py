import json
import os
import logging
import sys
from TwitterAPI import TwitterAPI
from lib.data_writer import DataWriter as DW


def init_logger(log_file):
    # initialize logger
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s: %(levelname)s: %(filename)s: %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        filemode='a')
    # print log messages to stdout too
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    # ignore logs from some modules, unless their level is warning or higher
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("oauthlib").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def boot():
    """
    initialize the root logger
    make connection to twitter and create TwitterAPI object
    createa new DataWriter object
    :return: (api, writer)
    """
    conf_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '../server.conf')  # so we can run this
    # from any directory
    with open(conf_file) as f:
        values = json.load(f)
        data_dir = values['data_dir']
        consumer_key = values['consumer_key']
        consumer_secret = values['consumer_secret']
        log_file = values['log_file']
        log_file = log_file if log_file != '' else 'server.log'
    init_logger(log_file)
    api = TwitterAPI(consumer_key, consumer_secret, auth_type='oAuth2')
    writer = DW(data_dir)
    return api, writer

import json
import os
from TwitterAPI import TwitterAPI
from lib.data_writer import DataWriter as DW


def get_config():
    """
    :return: the dictionary with the different configurations
    """
    conf_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '../server.conf')  # so we can run this
    # from any directory
    with open(conf_file) as f:
        values = json.load(f)
    return values


def get_api():
    config = get_config()
    api = TwitterAPI(config['consumer_key'], config['consumer_secret'], auth_type='oAuth2')
    return api


def get_writer():
    config = get_config()
    data_dir = config['data_dir']
    writer = DW(data_dir)
    return writer

from TwitterAPI import TwitterAPI
from TwitterMine.data_writer import DataWriter as DW
from tests import CONFIG
from TwitterMine.miner import Miner


def get_config():
    """
    :return: the dictionary with the different configurations
    """
    return CONFIG


def get_api():
    config = get_config()
    api = TwitterAPI(config['consumer_key'], config['consumer_secret'], auth_type='oAuth2')
    return api


def get_writer():
    config = get_config()
    data_dir = config['data_dir']
    writer = DW(data_dir)
    return writer


def get_miner():
    return Miner(CONFIG['consumer_key'], CONFIG['consumer_secret'], CONFIG['data_dir'])

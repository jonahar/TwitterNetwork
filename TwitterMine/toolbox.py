import json
import logging
import sys

from TwitterAPI.TwitterAPI import TwitterAPI
from TwitterMine.data_writer import DataWriter as DW
from TwitterMine.miner import Miner
from TwitterMine.server import Server

logging.basicConfig(filename='server_dev.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filemode='a')
# print log messages to stdout too
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# ignore logs from some modules, unless their level is warning or higher
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('oauthlib').setLevel(logging.WARNING)
logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

SERVER_CONF_FILE = None


def init(server_conf: str):
    """
    :param server_conf: server config file.
    :return:
    """
    global SERVER_CONF_FILE
    SERVER_CONF_FILE = server_conf


def get_config():
    """
    :return: the dictionary with the different configurations
    """
    if SERVER_CONF_FILE is None:
        raise ValueError('Must call toolbox.init before using the toolbox')
    with open(SERVER_CONF_FILE) as f:
        config = json.load(f)
    return config


def get_user_api():
    config = get_config()
    return TwitterAPI(config['consumer_key'],
                      config['consumer_secret'],
                      config['access_token_key'],
                      config['access_token_secret'])


def get_app_api():
    config = get_config()
    return TwitterAPI(config['consumer_key'], config['consumer_secret'], auth_type='oAuth2')


def get_writer():
    config = get_config()
    return DW(config['data_dir'])


def get_miner():
    config = get_config()
    return Miner(config['consumer_key'], config['consumer_secret'],
                 config['access_token_key'], config['access_token_secret'], config['data_dir'])


def get_server():
    config = get_config()
    return Server(config['consumer_key'], config['consumer_secret'],
                  config['access_token_key'], config['access_token_secret'],
                  config['data_dir'], config['port'])

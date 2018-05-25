import sys
import os
import logging
import json
from TwitterMine.server import Server
from TwitterAPI.TwitterAPI import TwitterAPI
from TwitterMine.data_writer import DataWriter as DW
from TwitterMine.miner import Miner

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

# TODO change this variable to point to your config file
SERVER_CONF_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '../my_config/server.conf')
CLIENT_CONF_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '../my_config/client.conf')


def get_config():
    """
    :return: the dictionary with the different configurations
    """
    with open(SERVER_CONF_FILE) as f:
        config = json.load(f)
    return config


def get_api():
    config = get_config()
    return TwitterAPI(config['consumer_key'],
                      config['consumer_secret'],
                      config['access_token_key'],
                      config['access_token_secret'])


def get_writer():
    config = get_config()
    data_dir = config['data_dir']
    return DW(data_dir)


def get_miner():
    config = get_config()
    return Miner(config['consumer_key'], config['consumer_secret'],
                 config['access_token_key'], config['access_token_secret'], config['data_dir'])


def get_server():
    config = get_config()
    return Server(config['consumer_key'], config['consumer_secret'],
                  config['access_token_key'], config['access_token_secret'],
                  config['data_dir'], config['port'])

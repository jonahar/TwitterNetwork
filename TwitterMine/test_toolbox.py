import json
import logging
import os
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

# TODO change this variable to point to your config file
SERVER_CONF_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '../my_config/server.conf')
CLIENT_CONF_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '../my_config/client.conf')

with open(SERVER_CONF_FILE) as f:
    config = json.load(f)

api = TwitterAPI(config['consumer_key'],
                 config['consumer_secret'],
                 config['access_token_key'],
                 config['access_token_secret'])

writer = DW(config['data_dir'])

miner = Miner(config['consumer_key'], config['consumer_secret'],
              config['access_token_key'], config['access_token_secret'], config['data_dir'])

server = Server(config['consumer_key'], config['consumer_secret'],
                config['access_token_key'], config['access_token_secret'],
                config['data_dir'], config['port'])


def get_config():
    """
    :return: the dictionary with the different configurations
    """
    return config


def get_api():
    return api


def get_writer():
    return writer


def get_miner():
    return miner


def get_server():
    return server

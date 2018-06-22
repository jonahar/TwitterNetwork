import argparse
import json
import logging
import sys

from TwitterMine.server import Server


def init_logger(log_file):
    """
    initialize the logger
    :param log_file: path to log file
    """
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
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


def parse_args():
    """
    parse and return the program arguments
    """
    parser = argparse.ArgumentParser(prog='TwitterMiner Server',
                                     usage='daemon [OPTIONS]',
                                     description='Twitter data extraction service')
    parser.add_argument('-c', '--conf', metavar='config-file',
                        help='configurations file for the server (default \'server.conf\')',
                        required=False, type=str, default='server.conf')
    parser.add_argument('-a', '--auth-type', metavar='auth_type', required=False, type=str,
                        choices=['app', 'user'], default='app',
                        help='authentication type for twitter api ("app" or "user")')
    return parser.parse_args()


def start(server_conf_file, auth_type):
    """
    read the configurations for the server and start it.
    :param server_conf_file: path to config file
    :param auth_type: Twitter auth type: 'app' or 'user'
    :return:
    """
    with open(server_conf_file) as f:
        config = json.load(f)
    init_logger(config['log_file'])
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']
    access_token_key = None
    access_token_secret = None
    data_dir = config['data_dir']
    port = config['port']

    if auth_type == 'user':
        access_token_key = config['access_token_key']
        access_token_secret = config['access_token_secret']
    server = Server(consumer_key, consumer_secret, access_token_key, access_token_secret, data_dir,
                    port)
    logging.getLogger().info('Running REST server')
    try:
        server.run()
    except Exception as e:
        logging.critical(str(e))


if __name__ == '__main__':
    args = parse_args()
    start(args.conf, args.auth_type)

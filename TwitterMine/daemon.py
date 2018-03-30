import argparse
import json
import logging
import sys
from TwitterMine.rest_server import RESTServer


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
    parser.add_argument('-c', '--conf',
                        help='configurations file for the server (default \'server.conf\')',
                        required=False, type=str, default='server.conf')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server_conf_file = args.conf
    with open(server_conf_file) as f:
        config = json.load(f)
    init_logger(config['log_file'])
    server = RESTServer(config['consumer_key'], config['consumer_secret'],
                        config['data_dir'], config['port'])
    logging.info('Running REST server')
    server.run()

import requests
import json
import re
import argparse
from sys import stdin

interactive_prompt = """
Enter a command to execute. Command structure is one of:
    mine <resource> of <screen_name> [limit]
    listen to user [screen_name]
    listen to keywords [comma,separated,keywords]

where resource is one of: 'details', 'friends', 'followers', 'tweets', 'likes'
Enter 'exit' to quit
"""

server_host_port = ''
headers = {'content-type': 'application/json'}


def parse_args():
    """
    parse and return the program arguments
    """
    parser = argparse.ArgumentParser(prog='TwitterMiner Client',
                                     usage='client [OPTIONS]',
                                     description='Twitter data extraction service (client)')
    parser.add_argument('-c', '--conf',
                        help='configurations file for the client (default \'client.conf\')',
                        required=False, type=str, default='client.conf')

    # exactly one of -s and -i is allowed
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', help='script file with list of commands')
    group.add_argument('-i', help='start the client in interactive mode', action='store_true')
    return parser.parse_args()


def check_connection():
    """
    Test the connection to the daemon
    :return: True if a request and a response were successfully transmitted to and from the daemon
    """
    r = requests.get(server_host_port)
    return r.ok


def send_request(resource, data):
    """
    :param resource: string, server resource path
    :param data: dictionary
    """
    url = server_host_port + resource
    data = json.dumps(data)
    r = requests.post(url, data=data, headers=headers)
    if not r.ok:
        print('request to {0} failed. error code {1}'.format(resource, r.status_code))


def request_user_details(screen_name):
    data = {'screen_name': screen_name}
    send_request('/mine/user_details', data)


def request_friends_ids(screen_name, limit=0):
    data = {'screen_name': screen_name, 'limit': limit}
    send_request('/mine/friends_ids', data)


def request_followers_ids(screen_name, limit=0):
    data = {'screen_name': screen_name, 'limit': limit}
    send_request('/mine/followers_ids', data)


def request_tweets(screen_name, limit=0):
    data = {'screen_name': screen_name, 'limit': limit}
    send_request('/mine/tweets', data)


def request_likes(screen_name, limit=0):
    data = {'screen_name': screen_name, 'limit': limit}
    send_request('/mine/likes', data)


RESOURCE_IDX = 1
SCR_NAME_IDX = 3
LIMIT_IDX = 4
LISTEN_TYPE_IDX = 2
LISTEN_PARAM_IDX = 3


class Client:
    def __init__(self, script=None):
        self.script = script
        self.mine_command_regex = re.compile(
            '\s*mine\s+(details|friends|followers|tweets|likes)\s+of\s+\w+(\s+\d*)?\s*')
        self.listen_command_regex = re.compile(
            '\s*listen\s+to\s+(user\s+\w+)|(keywords?\s+\w+(,\w+)*)\s*')

    def execute_single_command(self, command):
        """
        :param command: string. the command to execute
        """
        if self.mine_command_regex.fullmatch(command):
            tokens = command.split()
            resource = tokens[RESOURCE_IDX]
            screen_name = tokens[SCR_NAME_IDX]
            if len(tokens) > LIMIT_IDX:
                limit = int(tokens[LIMIT_IDX])
            else:
                limit = 0
            if resource == 'details':
                request_user_details(screen_name)
            elif resource == 'friends':
                request_friends_ids(screen_name, limit)
            elif resource == 'followers':
                request_followers_ids(screen_name, limit)
            elif resource == 'tweets':
                request_tweets(screen_name, limit)
            elif resource == 'likes':
                request_likes(screen_name, limit)

        elif self.listen_command_regex.fullmatch(command):
            tokens = command.split()
            listen_type = tokens[LISTEN_TYPE_IDX]
            param = tokens[LISTEN_PARAM_IDX]
            if listen_type == 'user':
                raise NotImplemented('listen to user not implemented')
            elif listen_type in ['keyword', 'keywords']:
                raise NotImplemented('listen to keywords not implemented')
        else:
            print('Invalid command:', command)

    def execute_commands(self, stream):
        """
        :param stream: file-like stream  of commands, separated with newlines
        """
        for line in stream:
            line = line[:-1]  # remove newline character
            if line == '':
                continue
            elif line == 'exit':
                break
            else:
                self.execute_single_command(line)

    def interactive_mode(self):
        stream = stdin
        self.execute_commands(stream)

    def script_mode(self):
        stream = open(self.script)
        self.execute_commands(stream)
        stream.close()


if __name__ == '__main__':
    args = parse_args()
    client_conf_file = args.conf
    with open(client_conf_file) as f:
        config = json.load(f)
    server_host_port = 'http://' + config['host'] + ':' + str(config['port'])
    if not check_connection():
        print('Connection to the daemon could not be established. '
              'Please check that the daemon is running and the host:port are correct')
        exit(1)
    if args.i:
        Client().interactive_mode()
    else:  # script mode
        Client(args.s).script_mode()

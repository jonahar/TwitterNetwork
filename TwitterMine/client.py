import requests
import json
import re
import argparse
from sys import stdin

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


def execute_command(command):
    """
    :param command: string. the command to execute
    """


interactive_prompt = """Enter a command to execute. command structure is one of:
mine [resource] of [screen_name]
listen to user [screen_name]
listen to keywords [comma,seperated,keywords]

where resource is one of: 'details', 'friends', 'followers', 'tweets', 'likes'\n"""


def interactive_mode():
    print(interactive_prompt)


def script_mode(script):
    pass


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
        print('interactive move')
    else:  # script mode
        script = args.s
        print('script mode')





# command = stdin.readline()
# command_regex = re.compile('\s*mine\s+(friends|followers|details|tweets|likes)\s+of\s+\w+\s*')
# command_regex.match(command)

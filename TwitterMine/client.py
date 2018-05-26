import requests
from requests.exceptions import ConnectionError
import json
import re
import argparse
from sys import stdin

# description and help
interactive_prompt = """\
--TwitterMine Client--
Enter a command to execute. To quit enter 'exit'.
"""
commands_help = """\
A valid command should be in one of the following formats:
    - mine <resource> of <screen_name> [limit]
    - listen to user <comma,separated,ids> [stop]
    - listen to keywords <comma,separated,keywords> [stop]
    - server shutdown

* <resource> is one of: 'details', 'friends', 'followers', 'tweets', 'likes', 'neighbors'
* the 'stop' word at the end of a listen command indicates that the list of values are values to stop listening to
"""

server_host_port = ''  # to be initialized according to config
headers = {'content-type': 'application/json'}

# valid commands regex
mine_command_regex = re.compile(
    '\s*mine\s+(details|friends|followers|tweets|likes|neighbors)\s+of\s+\w+(\s+\d*)?\s*')
listen_command_regex = re.compile(
    '\s*listen\s+to\s+((user\s+\d+(,\d+)*)|(keywords?\s+\w+(,\w+)*))(\s+stop)?\s*')
server_shutdown_command = re.compile('\s*server\s+shutdown\s*')


def parse_args():
    """
    parse and return the program arguments
    """
    parser = argparse.ArgumentParser(description='TwitterMine client',
                                     epilog=commands_help,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--conf', metavar='config-file',
                        help='configurations file for the client (default \'client.conf\')',
                        required=False, type=str, default='client.conf')

    # exactly one of -s and -i is allowed
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', help='script file with list of commands', metavar='script')
    group.add_argument('-i', help='start the client in interactive mode', action='store_true')
    return parser.parse_args()


def check_connection():
    """
    Test the connection to the daemon. Trying to access the server index.
    :return: True if a request and a response were successfully transmitted to and from the daemon
    """
    try:
        r = requests.get(server_host_port)
        return r.ok
    except ConnectionError as e:
        return False


def send_request(resource, data=None, quiet=False):
    """
    :param resource: string, server resource path
    :param data: dictionary
    :param quiet: if True, doesn't print errors
    :return: True on a successful response
    """
    assert server_host_port != ''
    url = server_host_port + resource
    data = json.dumps(data)
    try:
        r = requests.post(url, data=data, headers=headers, timeout=10)
        return r.ok
    except requests.exceptions.RequestException as e:
        if not quiet:
            print(e)
            return False


def request_user_details(screen_name):
    """
    :param screen_name:
    :return: True on a successful response
    """
    data = {'screen_name': screen_name}
    return send_request('/mine/user_details', data)


def request_friends_ids(screen_name, limit=0):
    """
    :param screen_name:
    :param limit:
    :return: True on a successful response
    """
    data = {'screen_name': screen_name, 'limit': limit}
    return send_request('/mine/friends_ids', data)


def request_followers_ids(screen_name, limit=0):
    """
    :param screen_name:
    :param limit:
    :return: True on a successful response
    """
    data = {'screen_name': screen_name, 'limit': limit}
    return send_request('/mine/followers_ids', data)


def request_tweets(screen_name, limit=0):
    """
    :param screen_name:
    :param limit:
    :return: True on a successful response
    """
    data = {'screen_name': screen_name, 'limit': limit}
    return send_request('/mine/tweets', data)


def request_likes(screen_name, limit=0):
    """
    :param screen_name:
    :param limit:
    :return: True on a successful response
    """
    data = {'screen_name': screen_name, 'limit': limit}
    return send_request('/mine/likes', data)


def request_neighbors(screen_name, limit=0):
    """
    :param screen_name:
    :param limit:
    :return: True on a successful response
    """
    print('sending neighbors req')
    data = {'screen_name': screen_name, 'limit': limit}
    return send_request('/mine/neighbors', data)


def request_listen(mode, track, follow):
    """
    :param mode: 'add' or 'remove'
    :param track: list of words to track
    :param follow: list of user ids to follow
    :return: True on a successful response
    """
    data = {'mode': mode, 'track': track, 'follow': follow}
    return send_request('/listen', data)


def request_server_shutdown():
    """
    send a shutdown request to the server
    """
    return send_request('/shutdown', quiet=True)


RESOURCE_IDX = 1
SCR_NAME_IDX = 3
LIMIT_IDX = 4
LISTEN_TYPE_IDX = 2
LISTEN_PARAM_IDX = 3
STOP_KEYWORD_IDX = 4


def execute_single_command(command):
    """
    :param command: string. the command to execute
    """
    ok = False
    if mine_command_regex.fullmatch(command):
        print('sending request "{0}"... '.format(command), end='')
        tokens = command.split()
        resource = tokens[RESOURCE_IDX]
        screen_name = tokens[SCR_NAME_IDX]
        if len(tokens) > LIMIT_IDX:
            limit = int(tokens[LIMIT_IDX])
        else:
            limit = 0
        if resource == 'details':
            ok = request_user_details(screen_name)
        elif resource == 'friends':
            ok = request_friends_ids(screen_name, limit)
        elif resource == 'followers':
            ok = request_followers_ids(screen_name, limit)
        elif resource == 'tweets':
            ok = request_tweets(screen_name, limit)
        elif resource == 'likes':
            ok = request_likes(screen_name, limit)
        elif resource == 'neighbors':
            ok = request_neighbors(screen_name, limit)

    elif listen_command_regex.fullmatch(command):
        print('sending request "{0}"... '.format(command), end='')
        tokens = command.split()
        listen_type = tokens[LISTEN_TYPE_IDX]  # distinguish between track/follow
        params = tokens[LISTEN_PARAM_IDX]
        params = params.split(',')
        if STOP_KEYWORD_IDX < len(tokens):
            mode = 'remove'
        else:
            mode = 'add'
        if listen_type == 'user':
            ok = request_listen(mode, follow=params)
        elif listen_type in ['keyword', 'keywords']:
            ok = request_listen(mode, track=params)
        else:
            raise ValueError('unsupported listen type')
    elif server_shutdown_command.fullmatch(command):
        print('sending request "{0}"... '.format(command), end='')
        request_server_shutdown()
        print('server shutdown request sent. Client exiting...')
        exit(0)
    else:
        print('Invalid command:', command)
        return
    if ok:
        print('Done')
    else:
        print('Failed. Check server log for more details')


def execute_commands(stream):
    """
    :param stream: file-like stream of commands, separated with newlines
    """
    for line in stream:
        line = line[:-1]  # remove newline character
        if line == '':
            continue
        elif line == 'exit':
            break
        else:
            execute_single_command(line)


def interactive_mode():
    """
    run the client in interactive mode
    """
    print(interactive_prompt)
    print(commands_help)
    stream = stdin
    execute_commands(stream)


def script_mode(script):
    """
    run the client in script mode
    :param script: path to commands file
    """
    stream = open(script)
    execute_commands(stream)
    stream.close()


def init_host_port(client_conf_file):
    global server_host_port
    with open(client_conf_file) as f:
        config = json.load(f)
    server_host_port = 'http://' + config['host'] + ':' + str(config['port'])


if __name__ == '__main__':
    args = parse_args()
    client_conf_file = args.conf
    init_host_port(client_conf_file)
    if not check_connection():
        print('Connection to the daemon could not be established. '
              'Please check that the daemon is running and the host:port are correct')
        exit(1)
    if args.i:
        interactive_mode()
    else:  # script mode
        script_mode(args.s)

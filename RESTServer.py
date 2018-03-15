from flask import Flask, jsonify, abort, request
from Miner import Miner
import json
import logging
import sys


def init_logger():
    # initialize logger
    logging.basicConfig(filename='server.log', level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                        filemode='a')
    # print log messages to stdout too
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class RESTServer:
    def __init__(self, conf_file):
        """
        creating a REST server instance. server is established according to the given
        config file

        :param conf_file: string, path to config file
        """
        with open(conf_file) as f:
            values = json.load(f)
            database_file = values['database']
            keys = dict()
            keys['consumer_token'] = values['consumer_token']
            keys['consumer_secret'] = values['consumer_secret']
            keys['access_token'] = values['access_token']
            keys['access_token_secret'] = values['access_token_secret']

            self.miner = Miner(keys, database_file)
            self.app = Flask(__name__)
            self.counter = 0

        @self.app.route('/')
        def index():
            logging.info('server index was accessed')
            self.counter += 1
            return "Welcome to TwitterMine REST server!\nFor your convenience a counter is " \
                   "increased each time this index page is accessed.\n" \
                   "Current counter value: {}\n".format(self.counter)

        @self.app.route('/mine/friends_ids', methods=['POST'])
        def mine_friends_ids():
            logging.info('Got request to mine friends ids')
            user, limit = self.parse_params(request.json)
            self.miner.mine_friends_ids(user, limit)
            return jsonify({'success': True}), 201

        @self.app.route('/mine/followers_ids', methods=['POST'])
        def mine_followers_ids():
            logging.info('Got request to mine followers ids')
            user, limit = self.parse_params(request.json)
            self.miner.mine_followers_ids(user, limit)
            return jsonify({'success': True}), 201

        @self.app.route('/mine/user', methods=['POST'])
        def mine_user():
            logging.info('Got request to mine user')
            user, _ = self.parse_params(request.json)
            self.miner.mine_user(user)
            return jsonify({'success': True}), 201

    def parse_params(self, json_params):
        """
        parsing the parameters of the mining requests

        :param json_params: a dictionary with key 'user' and an optional key 'limit'
        :return: a tuple (user, limit)
        """
        if not json_params or 'user' not in json_params:
            abort(400)
        user = json_params['user']
        limit = json_params['limit'] if 'limit' in json_params else 0
        return user, limit

    def run(self, debug=True, port=5000):
        self.app.run(debug=debug, port=port, threaded=True)


if __name__ == '__main__':
    init_logger()
    server_conf_file = '/cs/usr/jonahar/PythonProjects/TwitterMine/server.conf'
    server = RESTServer(server_conf_file)
    server.run()












    # @app.route('/todo/api/v1.0/tasks', methods=['GET'])
    # def get_tasks():
    #     return jsonify({'tasks': tasks})
    #
    #
    # @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
    # def get_task(task_id):
    #     task = [task for task in tasks if task['id'] == task_id]
    #     if len(task) == 0:
    #         abort(404)
    #     return jsonify({'task': task[0]})
    #
    #
    # @app.route('/todo/api/v1.0/tasks', methods=['POST'])
    # def create_task():
    #     # request.json is the dictionary sent by the user who made the request
    #     print("request.json: ", request.json)
    #     if not request.json or not 'title' in request.json:
    #         abort(400)
    #     task = {
    #         'id': tasks[-1]['id'] + 1,
    #         'title': request.json['title'],
    #         # if description was not provided assign default value (empty string)
    #         'description': request.json.get('description', ""),
    #         'done': False
    #     }
    #     tasks.append(task)
    #     return jsonify({'task': task}), 201

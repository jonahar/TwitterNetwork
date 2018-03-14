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



class RESTserver:
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

        @self.app.route('/')
        def index():
            logging.info('server index was accessed')
            return "Welcome to TwitterMine REST server!"

        @self.app.route('/mine/following_ids/<string:user>', methods=['POST'])
        def mine_following_ids(user):
            logging.info('got request to mine following ids')
            self.miner.mine_following_ids(user)
            return jsonify({'success': True}), 201

        @self.app.route('/mine/followers_ids/<string:user>', methods=['POST'])
        def mine_followers_ids(user):
            logging.info('got request to mine followers ids')
            self.miner.mine_followers_ids(user)
            return jsonify({'success': True}), 201

    def run(self, debug=True, port=5000):
        self.app.run(debug=debug, port=port, threaded=True)


if __name__ == '__main__':
    init_logger()
    server_conf_file = '/cs/usr/jonahar/PythonProjects/TwitterMine/server.conf'
    server = RESTserver(server_conf_file)
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

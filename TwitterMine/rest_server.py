import logging
from flask import Flask, jsonify, request
from TwitterMine.miner import Miner

HTTP_SUCCESS_CODE = 200
HTTP_ERROR_CODE = 400


class RESTServer:
    """
    TwitterMine REST server. Listens for requests from clients and executes them.

    A success message returned from the server means that a valid request was received and
    successfully inserted to the queue of requests (and does NOT mean that the request processing
    is finished)
    """

    def __init__(self, consumer_key, consumer_secret, data_dir, port):
        """
        :param consumer_key: Twitter API key
        :param consumer_secret: Twitter API secret key
        :param data_dir: directory for storing the extracted information
        :param port: the port to listen for incoming requests
        """
        self.miner = Miner(consumer_key, consumer_secret, data_dir)
        self.port = port
        self.app = Flask(__name__)
        self.counter = 0

        # define all endpoints in the REST server
        @self.app.route('/')
        def index():
            logging.info('server index was accessed')
            self.counter += 1
            return "Welcome to TwitterMine REST server!\nFor your convenience a counter is " \
                   "increased each time this index page is accessed.\n" \
                   "Current counter value: {}\n".format(self.counter)

        @self.app.route('/mine/user_details', methods=['POST'])
        def mine_user_details():
            logging.info('user_details request received')
            args = request.json
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            self.miner.produce_job('user_details', args)
            return self.success_response()

        @self.app.route('/mine/friends_ids', methods=['POST'])
        def mine_friends_ids():
            logging.info('friends ids request received')
            args = request.json
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('friends_ids', args)
            return self.success_response()

        @self.app.route('/mine/followers_ids', methods=['POST'])
        def mine_followers_ids():
            logging.info('followers ids request received')
            args = request.json
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('followers_ids', args)
            return self.success_response()

        @self.app.route('/mine/tweets', methods=['POST'])
        def mine_tweets():
            logging.info('tweets request received')
            args = request.json
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('tweets', args)
            return self.success_response()

        @self.app.route('/mine/likes', methods=['POST'])
        def mine_likes():
            logging.info('likes request received')
            args = request.json
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('likes', args)
            return self.success_response()

    def check_screen_name(self, args):
        """
        :return: True iff args is a dictionary with key 'screen_name'
        """
        return args is not None and 'screen_name' in args

    def success_response(self):
        """
        returns a success response
        """
        r = jsonify({'success': True})
        r.status_code = HTTP_SUCCESS_CODE
        return r

    def miss_arg_response(self):
        """
        returns a missing argument response
        """
        r = jsonify({'error': {'message': 'required argument is missing'}})
        r.status_code = HTTP_ERROR_CODE
        return r

    def run(self, debug=False):
        self.app.run(debug=debug, port=self.port, threaded=True)

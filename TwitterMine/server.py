import logging
from flask import Flask, jsonify, request
from TwitterMine.miner import Miner

HTTP_SUCCESS_CODE = 200
HTTP_ERROR_CODE = 400


class Server:
    """
    TwitterMine REST server. Listens for requests from clients and executes them.

    A success message returned from the server means that a valid request was received and
    successfully inserted to the queue of requests (and does NOT mean that the request processing
    is finished)
    """

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret,
                 data_dir, port):
        """
        :param consumer_key:
        :param consumer_secret:
        :param access_token_key:
        :param access_token_secret:
        :param data_dir: directory for storing the extracted information
        :param port: the port to listen for incoming requests
        """
        self.miner = Miner(consumer_key, consumer_secret, access_token_key, access_token_secret,
                           data_dir)
        self.port = port
        self.app = Flask(__name__)
        self.dummy_counter = 0
        self.logger = logging.getLogger()

        # define all endpoints in the REST server
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            self.logger.info('server index was accessed')
            self.dummy_counter += 1
            return "Welcome to TwitterMine REST server!\nFor your convenience a counter is " \
                   "increased each time this index page is accessed.\n" \
                   "Current counter value: {}\n".format(self.dummy_counter)

        # todo test this endpoint
        @self.app.route('/shutdown', methods=['GET', 'POST'])
        def shutdown():
            self.logger.info('shutdown request received')
            self.logger.info('stopping miner...')
            self.miner.stop()
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                self.logger.error('Server couldn\'t terminate properly' +
                                  '(not running with the Werkzeug Server). ' +
                                  'Terminating entire program')
                exit(1)
            func()
            self.logger.info('Server shutting down...')
            return self.success_response()

        @self.app.route('/mine/user_details', methods=['POST'])
        def mine_user_details():
            self.logger.info('user_details request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            self.miner.produce_job('user_details', args)
            return self.success_response()

        @self.app.route('/mine/friends_ids', methods=['POST'])
        def mine_friends_ids():
            self.logger.info('friends ids request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('friends_ids', args)
            return self.success_response()

        @self.app.route('/mine/followers_ids', methods=['POST'])
        def mine_followers_ids():
            self.logger.info('followers ids request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('followers_ids', args)
            return self.success_response()

        @self.app.route('/mine/tweets', methods=['POST'])
        def mine_tweets():
            self.logger.info('tweets request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('tweets', args)
            return self.success_response()

        @self.app.route('/mine/likes', methods=['POST'])
        def mine_likes():
            self.logger.info('likes request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('likes', args)
            return self.success_response()

        @self.app.route('/mine/neighbors', methods=['POST'])
        def mine_neighbors():
            self.logger.info('neighbors request received')
            args = request.get_json()
            if not self.check_screen_name(args):
                return self.miss_arg_response()
            if 'limit' not in args:
                # limit was not specified. use default
                args['limit'] = 0
            self.miner.produce_job('neighbors', args)
            return self.success_response()

        @self.app.route('/listen', methods=['POST'])
        def listen():
            self.logger.info('listen request received')
            args = request.get_json()
            if 'mode' not in args or ('track' not in args and 'follow' not in args):
                return self.miss_arg_response()
            self.miner.produce_job('listen', args)
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
        self.miner.run()
        self.app.run(host='0.0.0.0', debug=debug, port=self.port, threaded=True)

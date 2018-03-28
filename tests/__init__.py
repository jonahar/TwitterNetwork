import logging
import sys
import os
import json

conf_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../server.conf')  # so we
# can run this from any directory
with open(conf_file) as f:
    values = json.load(f)

CONFIG = values

# initialize logger
logging.basicConfig(filename=CONFIG['log_file'], level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filemode='a')
# print log messages to stdout too
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# ignore logs from some modules, unless their level is warning or higher
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("oauthlib").setLevel(logging.WARNING)
logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

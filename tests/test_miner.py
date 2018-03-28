import tests.bootstrap as boot
import time
import logging
from lib.miner import Miner

config = boot.get_config()
miner = Miner(config['consumer_key'], config['consumer_secret'], config['data_dir'])
miner.run()

screen_names = ['realDonaldTrump', 'Google', 'DisneyPixar']
FOLLOWERS_LIMIT = 4000
for scr_name in screen_names:
    args = {'screen_name': scr_name, 'limit': 0}
    miner.produce_job('user_details', args)

    args = {'screen_name': scr_name, 'limit': 0}
    miner.produce_job('friends_ids', args)

    args = {'screen_name': scr_name, 'limit': FOLLOWERS_LIMIT}
    miner.produce_job('followers_ids', args)

logging.getLogger().info('Main produced all jobs. Going to sleep for 30 seconds')
time.sleep(30)
logging.getLogger().info('Main terminating')
exit(0)

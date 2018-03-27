import tests.bootstrap as boot
from lib.miner import Miner

config = boot.get_config()
miner = Miner(config['consumer_key'], config['consumer_secret'], config['data_dir'])

screen_names = ['realDonaldTrump', 'Google', 'DisneyPixar']
FOLLOWERS_LIMIT = 30000
for scr_name in screen_names:
    miner.mine_user(scr_name)
    miner.mine_followers_ids(scr_name, FOLLOWERS_LIMIT)
    miner.mine_friends_ids(scr_name)

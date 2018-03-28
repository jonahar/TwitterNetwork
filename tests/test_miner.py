from random import shuffle, random
import logging
import time
import tests.bootstrap as boot
from lib.miner import Miner

config = boot.get_config()
miner = Miner(config['consumer_key'], config['consumer_secret'], config['data_dir'])
miner.run()

screen_names = ['realDonaldTrump', 'Google', 'DisneyPixar', 'NASA', 'HebrewU']
FOLLOWERS_LIMIT = 20000
TWEETS_LIMIT = 80000

jobs = []
# creating a list of jobs
for scr_name in screen_names:
    jobs.append(('screen_name', {'screen_name': scr_name}))
    jobs.append(('friends_ids', {'screen_name': scr_name, 'limit': 0}))
    jobs.append(('followers_ids', {'screen_name': scr_name, 'limit': FOLLOWERS_LIMIT}))
    jobs.append(('tweets', {'screen_name': scr_name, 'limit': TWEETS_LIMIT}))
    jobs.append(('likes', {'screen_name': scr_name, 'limit': 0}))

# randomize the jobs order
shuffle(jobs)
for job_type, args in jobs:
    if random() < 0.5:
        time.sleep(3)
    miner.produce_job(job_type, args)

logging.getLogger().info('Main produced all jobs. waiting indefinitely')
while True:
    pass

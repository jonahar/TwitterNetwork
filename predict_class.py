import json
import os
from collections import Counter

from TwitterMine import test_toolbox

modularity_classes_file = '/cs/usr/jonahar/modularity_classes.json'
network_users_filename = '/cs/usr/jonahar/israel_palestine_network_users.json'

with open(network_users_filename) as f:
    id_to_name = json.load(f)['id_to_name']

with open(modularity_classes_file) as f:
    name_to_class = json.load(f)


def prediction_data_mine(screen_name, timeline_limit=100000, friends_limit=500000,
                         followers_limit=500000):
    """
    mine relevant information to predict the class of the given user
    :return:
    """
    miner = test_toolbox.get_miner()
    miner.run()
    miner.produce_job('neighbors', {'screen_name': screen_name, 'limit': timeline_limit})
    miner.produce_job('friends', {'screen_name': screen_name, 'limit': friends_limit})
    miner.produce_job('followers', {'screen_name': screen_name, 'limit': followers_limit})
    miner.stop()


def get_predictions_from_file(counter, file, line_type='id'):
    """
    count class relations from the given file
    :param counter:
    :param file:
    :param line_type: the type of information stored in the file. one of 'id' or 'name', specifying
                      whether the lines in the file represents ids of users of names of users
    :return: updated counter
    """
    if os.path.exists(file):
        with open(file) as f:
            for line in f:
                if type == 'id':
                    name = id_to_name[int(line[:-1])]
                    if name in name_to_class:
                        counter[name_to_class[name]] += 1
                elif type == 'name':
                    name = line[:-1]
                    if name in name_to_class:
                        counter[name_to_class[name]] += 1


def predict_class(screen_name):
    """
    compute probabilities of being in each of the modularity classes for the user with the given
    screen name
    :param screen_name: screen name of the user
    :return:
    """
    counter = Counter()
    data_dir = test_toolbox.get_config()['data_dir']
    friends_file = os.path.join(data_dir, screen_name, 'friends')
    followers_file = os.path.join(data_dir, screen_name, 'followers')
    neighbors_file = os.path.join(data_dir, screen_name, 'neighbors')

    # counter = get_predictions_from_file(counter, friends_file, 'id')
    # counter = get_predictions_from_file(counter, followers_file, 'id')
    # counter = get_predictions_from_file(counter, neighbors_file, 'name')

    total_weight = sum(counter.values())
    probabilities = {k: v / total_weight for k, v in counter.items()}
    return probabilities


scr_name = 'realDonaldTrump'
prediction_data_mine(scr_name)
prob = predict_class(scr_name)
print(json.dumps(prob, indent=4))

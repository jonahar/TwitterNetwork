import json
import os
import sys
from collections import Counter

from TwitterMine import test_toolbox

modularity_classes_file = '/cs/usr/jonahar/modularity_classes.json'
network_users_filename = '/cs/usr/jonahar/israel_palestine_network_users.json'

with open(network_users_filename) as f:
    id_to_name = json.load(f)['id_to_name']

with open(modularity_classes_file) as f:
    o = json.load(f)
    name_to_class = o['name_to_class']
    class_label = o['class_label']


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
                if line_type == 'id':
                    id = int(line[:-1])
                    if id in id_to_name:
                        name = id_to_name[id]
                        counter[name_to_class[name]] += 1
                elif line_type == 'name':
                    name = line[:-1]
                    if name in name_to_class:
                        counter[name_to_class[name]] += 1
    return counter


timeline_limit = 100000
friends_limit = 25000
followers_limit = 25000


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

    # mine relevant information
    miner = test_toolbox.get_miner()
    miner.run()
    if not os.path.exists(friends_file):
        miner.produce_job('friends_ids', {'screen_name': screen_name, 'limit': friends_limit})
    if not os.path.exists(followers_file):
        miner.produce_job('followers_ids', {'screen_name': screen_name, 'limit': followers_limit})
    if not os.path.exists(neighbors_file):
        miner.produce_job('neighbors', {'screen_name': screen_name, 'limit': timeline_limit})
    miner.stop()

    counter = get_predictions_from_file(counter, friends_file, 'id')
    counter = get_predictions_from_file(counter, followers_file, 'id')
    counter = get_predictions_from_file(counter, neighbors_file, 'name')

    total_weight = sum(counter.values())
    probabilities = {k: v / total_weight for k, v in counter.items()}
    return probabilities


if __name__ == '__main__':
    scr_name = sys.argv[1]
    prob = predict_class(scr_name)
    for c in prob:
        if c in class_label:
            prob[c] = '{0} ({1})'.format(prob[c], class_label[c])
    print(json.dumps(prob, indent=4))

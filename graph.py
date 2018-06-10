import json
import os
from collections import Counter
from math import log

from TwitterMine.utils import RETWEET, QUOTE, REPLY


def name_serial_map(data_dir, necessary_files):
    """
    find all users in the data_dir that have all the necessary files in their directory. Each such
    user is given a unique identifier (serial)

    :param data_dir:
    :param necessary_files: list of filenames
    :return: mapping dictionary from screen name to serial
    """
    serial = 0
    name_to_serial = dict()
    for scr_name in os.listdir(data_dir):
        user_dir = os.path.join(data_dir, scr_name)
        if os.path.isdir(user_dir):
            valid_user = True
            for file in necessary_files:
                filepath = os.path.join(user_dir, file)
                if not os.path.isfile(filepath):
                    valid_user = False
                    break
            if valid_user:
                name_to_serial[scr_name] = serial
                serial += 1
    return name_to_serial


LIKE = 4
assert LIKE not in [RETWEET, QUOTE, REPLY]


def graph_info(data_dir):
    """
    creates a graph-info object, which is a dictionary with keys 'neighborship' and 'followers_count'
    :param data_dir:
    """
    neighborship = dict()
    followers_count = dict()

    for user_scr_name in name_to_serial:
        details_file = os.path.join(data_dir, user_scr_name, 'user_details')
        neighbors_file = os.path.join(data_dir, user_scr_name, 'neighbors')
        likes_file = os.path.join(data_dir, user_scr_name, 'likes')

        with open(details_file) as df:
            followers_count[user_scr_name] = json.load(df)['followers_count']

        neighborship[user_scr_name][RETWEET] = Counter()
        neighborship[user_scr_name][QUOTE] = Counter()
        neighborship[user_scr_name][REPLY] = Counter()
        neighborship[user_scr_name][LIKE] = Counter()

        with open(neighbors_file) as nf:
            for line in nf:
                tokens = line[:-1].split(';')
                neighbor_scr_name = tokens[0]
                neighborship_type = tokens[2]
                if neighbor_scr_name in name_to_serial:
                    # the neighbor belongs to our network
                    neighborship[user_scr_name][neighborship_type][neighbor_scr_name] += 1

        with open(likes_file) as lf:
            for line in lf:
                tweet = json.loads(line)
                neighbor_scr_name = tweet['user']['screen_name']
                if neighbor_scr_name in name_to_serial:
                    # the neighbor belongs to our network
                    neighborship[user_scr_name][LIKE][neighbor_scr_name] += 1

    return {'neighborship': neighborship, 'followers_count': followers_count}


def write_gexf_format(graph_file, neighborship, name_to_serial, node_size=lambda x: 1,
                      label_size_threshold=-1):
    """
    writes a graph file in gexf format

    :param graph_file: output file
    :param neighborship: dictionary. neighborship[i] has multiples dictionaries, one for each
                         neighborship type. neighborship[i][type] is a dictionary whose keys are
                         screen names of neighbors (of that type) and the value is the weight
                         of the neighborship
    :param name_to_serial: dictionary, mapping screen names to serial numbers
    :param node_size: function that takes a screen name and returns the size of this user's node.
    :param label_size_threshold: write label only to nodes whose size is at least this threshold
    """
    graph = open(graph_file, mode='w')
    graph.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2" xmlns:viz="http://www.gexf.net/1.3/viz">
<graph mode="static" defaultedgetype="directed">
""")
    graph.write('<nodes>\n')
    for user_scr_name in neighborship:
        id = name_to_serial[user_scr_name]
        size = node_size(user_scr_name)
        label = '' if size < label_size_threshold else user_scr_name
        graph.write('<node id="{0}" label="{1}">\n'.format(id, label))
        graph.write('<viz:size value="{0}"></viz:size>\n'.format(size))
        graph.write('</node>\n')

    graph.write('</nodes>\n')

    graph.write('<edges>\n')
    for user_scr_name in neighborship:
        user_id = name_to_serial[user_scr_name]
        for neighbor_scr_name, weight in neighborship[user_scr_name].items():
            neighbor_id = name_to_serial[neighbor_scr_name]
            graph.write('<edge source="{0}" target="{1}" weight="{2}"/>\n'.format(user_id,
                                                                                  neighbor_id,
                                                                                  weight))
    graph.write('</edges>\n')
    graph.write('</graph>\n')
    graph.write('</gexf>\n')
    graph.close()


if __name__ == '__main__':
    data_dir = '/cs/labs/avivz/jonahar/Twitter/cryptocurrency_data_dir'
    network_filename = '/cs/usr/jonahar/network_users.json'
    necessary_files = ['user_details', 'neighbors', 'likes']
    graph_info_file = '/cs/usr/jonahar/graph_info.json'
    graph_file = '/cs/usr/jonahar/graph.gexf'

    # create name -> serial map
    name_to_serial = name_serial_map(data_dir, necessary_files)

    # save mapping to file
    with open(network_filename, mode='w') as net:
        json.dump(name_to_serial, net, indent=4)

    # create graph-info object
    graph_info = graph_info(data_dir)

    # write graph-info object
    with open(graph_info_file, mode='w') as gii:
        json.dump(graph_info, gii, indent=4)

    # create graph file
    node_size_func = lambda screen_name: log(graph_info['followers_count'][screen_name] + 1)
    write_gexf_format(graph_file, graph_info['neighborship'], name_to_serial, node_size_func, 0)

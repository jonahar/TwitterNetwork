import json
import os
import sys
from functools import reduce
from math import log

import numpy as np
from scipy.sparse import lil_matrix

from TwitterMine.utils import RETWEET, QUOTE, REPLY

SERIAL_IDX = 0
FOLLOWERS_COUNT_IDX = 1

LIKE = 4
ALL = 5
adjacency_types = [RETWEET, QUOTE, REPLY, LIKE, ALL]
assert len(adjacency_types) == len(set(adjacency_types))  # unique value for each
graphs_names = ['retweet.gexf', 'quote.gexf', 'reply.gexf', 'like.gexf', 'all.gexf']

MAX_NODE_SIZE = 100


def def_node_size(screen_name):
    return 1


def def_node_color():
    return "000000"


def network_users(data_dir, necessary_files, network_file):
    """
    find all users in the data_dir that have all the necessary files in their directory. Each such
    user is given a unique identifier (serial)

    if network file exists, read users map from file and return it.

    :param data_dir:
    :param necessary_files: list of filenames
    :param network_file:
    :return: a dictionary mapping  screen name to tuple (serial, followers_count)
    """
    if os.path.isfile(network_filename):
        with open(network_filename) as nf:
            map = json.load(nf)
        return map
    serial = 0
    map = dict()
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
                details_file = os.path.join(user_dir, 'user_details')
                with open(details_file) as df:
                    followers_count = json.load(df)['followers_count']
                map[scr_name] = (serial, followers_count)
                serial += 1
    with open(network_file, mode='w') as net:
        json.dump(map, net, indent=4)
    return map


def adjacencies_matrices(users_map, data_dir, matrices_file):
    """
    Build all kinds of neighborship matrices (a total of 5).
    For any matrix A, A[i,j] is the directed edge from i to j.

    If matrices_file exists, read matrices from file and return them

    :param users_map:
    :param data_dir:
    :return: dictionary with keys RETWEET, QUOTE, REPLY, LIKE, ALL. Values are sparse matrices that
             correspond to the relevant neighborship type
    """
    if os.path.isfile(matrices_file):
        data = np.load(matrices_file)
        matrices = {RETWEET: data['retweet'],
                    QUOTE: data['quote'],
                    REPLY: data['reply'],
                    LIKE: data['like'],
                    ALL: data['all']}
        return matrices
    N = len(users_map)
    if log(N, 2) < 8:
        dtype = np.uint8
    elif log(N, 2) < 16:
        dtype = np.uint16
    else:
        dtype = np.uint32
    print('initializing matrices. dtype=', dtype, sep='')
    matrices = {RETWEET: lil_matrix((N, N), dtype=dtype),
                QUOTE: lil_matrix((N, N), dtype=dtype),
                REPLY: lil_matrix((N, N), dtype=dtype),
                LIKE: lil_matrix((N, N), dtype=dtype)}
    for user_name in users_map:
        neighbors_file = os.path.join(data_dir, user_name, 'neighbors')
        likes_file = os.path.join(data_dir, user_name, 'likes')
        i = users_map[user_name][SERIAL_IDX]
        # RETWEET, QUOTE and REPLY matrices
        if os.path.isfile(neighbors_file):
            with open(neighbors_file) as nf:
                for line in nf:
                    tokens = line[:-1].split(';')
                    neighbor_name = tokens[0]
                    neighborship_type = int(tokens[2])
                    if neighbor_name in users_map:
                        # the neighbor belongs to our network
                        j = users_map[neighbor_name][SERIAL_IDX]
                        matrices[neighborship_type][i, j] += 1
        # LIKE matrix
        if os.path.isfile(likes_file):
            with open(likes_file) as lf:
                for line in lf:
                    tweet = json.loads(line)
                    neighbor_name = tweet['user']['screen_name']
                    if neighbor_name in users_map:
                        # the neighbor belongs to our network
                        j = users_map[neighbor_name][SERIAL_IDX]
                        matrices[LIKE][i, j] += 1
    # add all matrices
    all = reduce(lil_matrix.__add__, matrices.values())
    matrices[ALL] = all
    np.savez(matrices_file, retweet=matrices[RETWEET], quote=matrices[QUOTE], reply=matrices[REPLY],
             like=matrices[LIKE], all=matrices[ALL])
    return matrices


def write_gexf_format(graph_file, adjacency, users_map, node_size=def_node_size,
                      node_color=def_node_color, label_size_threshold=-1):
    """
    writes a graph file in gexf format

    :param graph_file: output file
    :param adjacency: sparse numpy matrix
    :param users_map: dictionary, mapping screen_name to (serial, followers_count)
    :param node_size: function that takes a screen name and returns the size of this user's node.
    :param node_color: function that takes a screen name and returns the color of this user's node
    :param label_size_threshold: write label only to nodes whose size is at least this threshold
    :return:
    """
    graph = open(graph_file, mode='w')
    graph.write("""<?xml version="1.0" encoding="UTF-8"?>
    <gexf xmlns="http://www.gexf.net/1.2draft" version="1.2" xmlns:viz="http://www.gexf.net/1.3/viz">
    <graph mode="static" defaultedgetype="directed">
    """)
    graph.write('<nodes>\n')
    for user_name in users_map:
        id = users_map[user_name][SERIAL_IDX]
        size = node_size(user_name)
        color = node_color(user_name)
        label = '' if size < label_size_threshold else user_name
        graph.write('<node id="{0}" label="{1}">\n'.format(id, label))
        graph.write('<viz:size value="{0}"></viz:size>\n'.format(size))
        graph.write('<viz:color hex="{0}" a="1"/>'.format(color))
        graph.write('</node>\n')
    graph.write('</nodes>\n')
    graph.write('<edges>\n')
    # iterate over all non-zero elements in the adjacency matrix
    for i, j in zip(*adjacency.nonzero()):
        graph.write('<edge source="{0}" target="{1}" weight="{2}"/>\n'.format(i, j,
                                                                              adjacency[i, j]))
    graph.write('</edges>\n')
    graph.write('</graph>\n')
    graph.write('</gexf>\n')
    graph.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: graph <graph_properties>')

    graph_properties = sys.argv[1]
    with open(graph_properties) as f:
        d = json.load(f)
        data_dir = d['data_dir']
        network_filename = d['network_filename']
        necessary_files = d['necessary_files']
        matrices_file = d['matrices_file']
        graph_dir = d['graph_dir']

    print('creating users map')
    users_map = network_users(data_dir, necessary_files, network_filename)
    most_followed = max(users_map, key=lambda k: users_map[k][FOLLOWERS_COUNT_IDX])
    max_followers_count = users_map[most_followed][FOLLOWERS_COUNT_IDX]

    print('creating adjacencies matrices')
    matrices = adjacencies_matrices(users_map, data_dir, matrices_file)

    # create graph file
    base = max_followers_count ** (1 / MAX_NODE_SIZE)
    node_size_func = lambda screen_name: log(users_map[screen_name][FOLLOWERS_COUNT_IDX] + 1, base)

    print('writing graph files')
    for key, name in zip(adjacency_types, graphs_names):
        graph_file = os.path.join(graph_dir, name)
        write_gexf_format(graph_file, matrices[key], users_map, node_size_func, 0)

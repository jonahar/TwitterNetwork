import json
import os

import numpy as np

from TwitterGraph import graph
from clustering import utils

######################################
'write a gexf file of the like relation according to MCL'
######################################
expansion = 2
inflation = 1.7

if __name__ == '__main__':
    graph_properties = '/path/to/graph_properties.json'
    mcl_clusters_file = '/path/to/like-mcl-cluster.json'  # it not exist, will be created below
    gexf_filename = '/path/to/like-mcl.gexf'

    with open(graph_properties) as f:
        d = json.load(f)
        network_filename = d['network_filename']
        matrices_file = d['matrices_file']

    # load the like matrix
    like = np.load(matrices_file)['like'][()]
    # turn to undirected
    like = like + like.T

    if os.path.isfile(mcl_clusters_file):
        with open(mcl_clusters_file) as cf:
            clusters = json.load(cf)
    else:
        clusters = utils.mcl_cluster(like, expansion, inflation)
        with open(mcl_clusters_file, mode='w') as cf:
            json.dump(clusters, cf, indent=4)

    with open(network_filename) as nf:
        users_map = json.load(nf)

    node_color_func = utils.get_node_color_func(clusters, users_map)
    graph.write_gexf_format(gexf_filename, like, users_map, node_color=node_color_func)

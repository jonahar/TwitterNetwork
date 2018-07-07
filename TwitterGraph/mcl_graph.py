import json
import os
import sys

import numpy as np

from TwitterGraph import utils

######################################
'write a gexf file of the like relation according to MCL'
'print modularity and sizes of the biggest clusters'
######################################


usage = 'Usage: mcl-graph <graph-properties-file> <cluster-file.json> <gexf-file> <expansion> <inflation>'
help = 'This script reads a clustering of the network (or makes it using MCL if not exist) and ' \
       'writes a gexf file of the network according to the clustering (nodes colored by cluster)\n' \
       'network_file and matrices_file specified in the graph-properties must exist'

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(usage)
        print()
        print(help)
        exit()
    graph_properties = sys.argv[1]
    mcl_clusters_file = sys.argv[2]
    gexf_filename = sys.argv[3]
    expansion = int(sys.argv[4])
    inflation = float(sys.argv[5])

    with open(graph_properties) as f:
        d = json.load(f)
        network_file = d['network_file']
        matrices_file = d['matrices_file']

    # load the like matrix
    like = np.load(matrices_file)['like'][()]
    # turn to undirected to find clusters
    like_undirected = like + like.T

    if os.path.isfile(mcl_clusters_file):
        with open(mcl_clusters_file) as cf:
            clusters = json.load(cf)
    else:
        clusters = utils.mcl_cluster(like_undirected, expansion, inflation)
        with open(mcl_clusters_file, mode='w') as cf:
            json.dump(clusters, cf, indent=4)

    with open(network_file) as nf:
        users_map = json.load(nf)

    # write gexf file
    node_color_func = utils.get_node_color_func(clusters, users_map)
    utils.write_gexf_format(gexf_filename, like, users_map, node_color=node_color_func)

    modularity = utils.get_modularity(like_undirected, clusters)
    clusters.sort(key=lambda t: len(t), reverse=True)
    print('===============================\n'
          'e={0}, i={1}, modularity={2}, biggest-clusters-size: {3},{4},{5},{6}\n'
          '==============================='.format(expansion, inflation, modularity,
                                                   len(clusters[0]), len(clusters[1]),
                                                   len(clusters[2]), len(clusters[3])))

    sys.stdout.flush()

import json

import numpy as np

from TwitterGraph import utils

'''
Some code snippets that read and manipulate the data that was produced by TwitterGraph.

This demo is relevant after creating the different adjacencies matrices using TwitterGraph.graph
and after creating the mcl clustering file using clustering.mcl-graph
'''

mcl_clusters_file = 'mcl-cluster.json'
graph_properties = 'my-conf/graph_properties.json'

# read all properties
with open(graph_properties) as f:
    d = json.load(f)
    data_dir = d['data_dir']
    results_file = d['results_file']
    commands_file = d['commands_file']
    matrices_file = d['matrices_file']
    network_file = d['network_file']
    necessary_files = d['necessary_files']
    graph_dir = d['graph_dir']

# read all adjacencies matrices (sparse matrices)
matrices = np.load(matrices_file)
like = matrices['like'][()]  # this weird indexing is due to sparse matrices loading bug
reply = matrices['reply'][()]
quote = matrices['quote'][()]
retweet = matrices['retweet'][()]
all = matrices['all'][()]

# read the pre-computed clustering (computed by MCL on the like matrix)
with open(mcl_clusters_file) as f:
    mcl_clusters = json.load(f)  # list of lists

# turn the like matrix to undirected
undirected_like = like + like.T
# compute modularity
print('MCL clustering modularity:', utils.get_modularity(undirected_like, mcl_clusters))

# create adjacency matrix between clusters and display results of top 5 clusters:
clusters_like_adjacency = utils.get_clusters_adjacencies(like, mcl_clusters)
print(clusters_like_adjacency[:5, :5])

clusters_reply_adjacency = utils.get_clusters_adjacencies(reply, mcl_clusters)
print(clusters_reply_adjacency[:5, :5])

clusters_quote_adjacency = utils.get_clusters_adjacencies(quote, mcl_clusters)
print(clusters_quote_adjacency[:5, :5])

clusters_retweet_adjacency = utils.get_clusters_adjacencies(retweet, mcl_clusters)
print(clusters_retweet_adjacency[:5, :5])

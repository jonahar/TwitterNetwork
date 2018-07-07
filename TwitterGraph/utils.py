import numpy as np

from markov_clustering import mcl

# RGB tuples
COLORS = [(60, 180, 75),  # Green
          (145, 30, 180),  # Purple
          (0, 130, 200),  # Blue
          (230, 25, 75),  # Red
          (70, 240, 240),  # Cyan
          (255, 225, 25),  # Yellow
          (170, 110, 40),  # Brown
          (250, 190, 190),  # Pink
          (245, 130, 48),  # Orange
          (240, 50, 230),  # Magenta
          (210, 245, 60),  # Lime
          (0, 128, 128),  # Teal
          (230, 190, 255),  # Lavender
          (255, 250, 200),  # Beige
          (128, 0, 0),  # Maroon
          (170, 255, 195),  # Mint
          (128, 128, 0),  # Olive
          (255, 215, 180),  # Coral
          (0, 0, 128),  # Navy
          (255, 20, 147)  # deep pink
          ]
DEF_COLOR = (128, 128, 128)  # gray


def mcl_cluster(matrix, expansion, inflation):
    """
    :param matrix: adjacency matrix
    :return: list of tuples. each tuple are ids of nodes in the same cluster
    """
    result = mcl.run_mcl(matrix, expansion=expansion, inflation=inflation, iterations=600,
                         verbose=True)
    clusters = mcl.get_clusters(result)
    return clusters


def complete_clusters(clusters, num_nodes):
    """
    modify the argument 'clusters' such that every node id in the range [0, num_nodes-1] has
    a cluster (filling with new clusters for missing ids)

    :param clusters:
    :param num_nodes:
    :return: the modified clusters
    """
    done = set([id for c in clusters for id in c])  # all nodes that appear in some cluster
    # make sure every node is in a cluster. if not, put it in a new cluster by itself
    for id in range(num_nodes):
        if id not in done:
            clusters.append((id,))
    return clusters


def get_id_to_cluster(clusters, num_ids):
    """
    :param clusters: list of tuples. each tuples contains ids in the same cluster
    :param num_ids: total number of ids. the ids are all integers in [0, num_ids-1]
    :return: a dictionary, mapping id to cluster id.
    """
    clusters = complete_clusters(clusters, num_ids)
    id_to_cluster = dict()
    for i in range(len(clusters)):
        for id in clusters[i]:
            id_to_cluster[id] = i
    return id_to_cluster


def get_clusters_adjacencies(adjacency, clusters: list):
    """
    Create an adjacency matrix of the clusters

    :param adjacency: adjacency matrix of the network
    :param clusters: list of tuples. each tuples contains ids in the same cluster
    :return: matrix with shape (num_clusters, num_clusters)
    """
    clusters.sort(key=lambda t: len(t), reverse=True)
    id_to_cluster = get_id_to_cluster(clusters, adjacency.shape[0])
    num_clusters = len(clusters)
    mat = np.zeros((num_clusters, num_clusters))
    rows, cols = adjacency.nonzero()
    for i, j in zip(rows, cols):
        weight = adjacency[i, j]
        src_cluster = id_to_cluster[i]
        dest_cluster = id_to_cluster[j]
        mat[src_cluster, dest_cluster] += weight
    return mat


SERIAL_IDX = 0


def get_node_color_func(clusters, users_map):
    """
    :param id_to_color: dictionary, mapping
    :param users_map: users map dictionary
    :return: a node color function (compatible to the write_gexf_format function)
    """
    clusters.sort(key=lambda t: len(t), reverse=True)
    id_to_cluster = get_id_to_cluster(clusters, len(users_map))

    def node_color(screen_name):
        id = users_map[screen_name][SERIAL_IDX]
        cluster_id = id_to_cluster[id]
        if cluster_id < len(COLORS):
            return COLORS[cluster_id]
        return DEF_COLOR

    return node_color


def get_modularity(adjacency, clusters):
    """
    Computes the modularity of a network.

    :param adjacency: adjacency matrix. treated as undirected!
    :param clusters: list of tuples. each tuples contains ids in the same cluster
    :return: float. the modularity of the network
    """
    total_weight = np.sum(adjacency)
    e = get_clusters_adjacencies(adjacency, clusters)
    e = e / total_weight
    a = np.sum(e, axis=1)
    return np.sum(e.diagonal() - np.power(a, 2))


def get_modularity2(adjacency, clusters):
    """
    Another way of computing modularity. VERY memory consuming.
    Don't use for large networks. only for sanity check
    """
    num_ids = adjacency.shape[0]
    id_to_cluster = get_id_to_cluster(clusters, num_ids)
    S = np.zeros(shape=(adjacency.shape[0], len(clusters)))  # S[v,c]=1 iff v is in cluster c
    for id in range(adjacency.shape[0]):
        cluster_id = id_to_cluster[id]
        S[id, cluster_id] = 1
    total_weight = np.sum(adjacency)
    degrees = np.sum(adjacency, axis=1)

    C = np.outer(degrees, degrees)
    C = C / total_weight  # C[v,w] = deg(v)*deg(w) / 2m
    B = adjacency - C
    M = np.dot(np.dot(S.T, B), S)
    return np.trace(M) / total_weight


def get_modularity3(adjacency, clusters):
    """
    yet another way of computing modularity (INEFFICIENT for large networks).
    """

    rows, cols = adjacency.shape
    num_ids = adjacency.shape[0]
    id_to_cluster = get_id_to_cluster(clusters, num_ids)
    degrees = np.sum(adjacency, axis=1)
    total_weight = np.sum(adjacency)
    sum = 0
    for i in range(rows):
        for j in range(cols):
            if id_to_cluster[i] == id_to_cluster[j]:
                sum += adjacency[i, j] - (degrees[i] * degrees[j]) / total_weight
    sum = sum / total_weight
    return sum


def def_node_size(screen_name):
    return 1


def def_node_color(screen_name):
    return 0, 0, 0


def def_node_label(screen_name):
    return screen_name


def write_gexf_format(graph_file, adjacency, users_map, node_size=def_node_size,
                      node_color=def_node_color, node_label=def_node_label,
                      label_size_threshold=-1):
    """
    writes a graph file in gexf format
    :param graph_file: output file
    :param adjacency: sparse numpy matrix
    :param users_map: dictionary, mapping screen_name to (serial, followers_count)
    :param node_size: function that takes a screen name and returns the size of this user's node.
    :param node_color: function that takes a screen name and returns the color of this user's node.
                       color is a string with 6 letters, representing RGB color in hex format
    :param node_label: function that takes a screen name and returns the label for this node
    :param label_size_threshold: write label only to nodes whose size is at least this threshold
    :return:
    """
    graph = open(graph_file, mode='w')
    graph.write("""<?xml version="1.0" encoding="UTF-8"?>
    <gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.1draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
    <graph mode="static" defaultedgetype="directed">
    """)
    graph.write('<nodes>\n')
    for user_name in users_map:
        id = users_map[user_name][SERIAL_IDX]
        size = node_size(user_name)
        r, g, b = node_color(user_name)
        label = '' if size < label_size_threshold else node_label(user_name)
        graph.write('<node id="{0}" label="{1}">\n'.format(id, label))
        graph.write('<viz:size value="{0}"></viz:size>\n'.format(size))
        graph.write('<viz:color r="{0}" g="{1}" b="{2}" a="1"/>'.format(r, g, b))
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

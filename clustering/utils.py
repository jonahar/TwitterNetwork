import markov_clustering as mc
import numpy as np

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
          (0, 0, 128)]  # Navy
DEF_COLOR = (128, 128, 128)  # gray


def mcl_cluster(matrix, expansion, inflation):
    """
    :param matrix: adjacency matrix
    :return: list of tuples. each tuple are ids of nodes in the same cluster
    """
    result = mc.run_mcl(matrix, expansion=expansion, inflation=inflation, iterations=600,
                        verbose=True)
    clusters = mc.get_clusters(result)
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
    yet another, INEFFICIENT for large networks, way of computing modularity.
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

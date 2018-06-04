import json
import os
from collections import Counter

data_dir = '/cs/labs/avivz/jonahar/Twitter/israel_palestine_data_dir'
network_filename = '/cs/usr/jonahar/network_users.json'
graph_file = '/cs/usr/jonahar/graph_description.gexf'

graph_info_file = '/cs/usr/jonahar/graph_info.json'

with open(network_filename) as f:
    o = json.load(f)
    name_to_serial = o['name_to_serial']
    serial_to_name = o['serial_to_name']

print('reading graph info file')
if os.path.isfile(graph_info_file):
    with open(graph_info_file) as gif:
        graph_info = json.load(gif)
        adjacencies = graph_info['adjacencies']
        followers_count = graph_info['followers_count']
else:
    adjacencies = dict()
    followers_count = dict()
# adjacencies[i][j] = number of times that user i interacted with user j (commented/retweeted)


print('filling missing parts in graph info (from data dir)')
for user_scr_name in name_to_serial:
    if user_scr_name in adjacencies:
        continue  # information about this user already exist

    neighbors_file = os.path.join(data_dir, user_scr_name, 'neighbors')
    details_file = os.path.join(data_dir, user_scr_name, 'user_details')
    with open(details_file) as df:
        followers_count[user_scr_name] = json.load(df)['followers_count']

    adjacencies[user_scr_name] = Counter()
    with open(neighbors_file) as nf:
        for line in nf:
            neighbor_scr_name = line[:-1]
            if neighbor_scr_name == user_scr_name or neighbor_scr_name not in name_to_serial:
                # neighbor is the user itself, or neighbor is not in our network
                continue
            adjacencies[user_scr_name][neighbor_scr_name] += 1

print('writing updated graph info file')
with open(graph_info_file, mode='w') as gif:
    graph_info = {'adjacencies': adjacencies, 'followers_count': followers_count}
    json.dump(graph_info, gif, indent=4)

max_followers_count = max(followers_count.values())
max_node_size = 100


def write_dot_format():
    graph = open(graph_file, mode='w')
    graph.write('digraph G {\n')

    for user_scr_name in adjacencies:
        user_id = name_to_serial[user_scr_name]
        graph.write('{0} [label="{1}"]\n'.format(user_id, user_scr_name))
        for neighbor_scr_name, weight in adjacencies[user_scr_name].items():
            neighbor_id = name_to_serial[neighbor_scr_name]
            graph.write('{0} -> {1} [weight="{2}"];\n'.format(user_id, neighbor_id, weight))
    graph.write('}')
    graph.close()


def node_size(num_followers):
    """
    :return: the size of a node with the given followers count
    """
    if num_followers == 0:
        return 0
    return num_followers ** 0.261  # found by curve fitting. 0->0, 500k->50, 50M->100


label_size_threshold = 15  # minimum node size to display label


def write_gexf_format():
    graph = open(graph_file, mode='w')

    graph.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2" xmlns:viz="http://www.gexf.net/1.3/viz">
<graph mode="static" defaultedgetype="directed">
""")
    graph.write('<nodes>\n')
    for user_scr_name in adjacencies:
        id = name_to_serial[user_scr_name]
        size = node_size(followers_count[user_scr_name])
        label = '' if size < label_size_threshold else user_scr_name
        graph.write(
            '<node id="{0}" label="{1}">\n'.format(id, label))
        graph.write('<viz:size value="{0}"></viz:size>\n'.format(size))
        graph.write('</node>\n')

    graph.write('</nodes>\n')

    graph.write('<edges>\n')
    for user_scr_name in adjacencies:
        user_id = name_to_serial[user_scr_name]
        for neighbor_scr_name, weight in adjacencies[user_scr_name].items():
            neighbor_id = name_to_serial[neighbor_scr_name]
            graph.write('<edge source="{0}" target="{1}" weight="{2}"/>\n'.format(user_id,
                                                                                  neighbor_id,
                                                                                  weight))
    graph.write('</edges>\n')
    graph.write('</graph>\n')
    graph.write('</gexf>\n')
    graph.close()


print('Writing graph file')
write_gexf_format()

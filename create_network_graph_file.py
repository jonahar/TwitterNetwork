import os
import json

data_dir = '/cs/labs/avivz/jonahar/Twitter/data_dir_netanyahu_nuclear_iran'
network_file = '/cs/labs/avivz/jonahar/Twitter/iran_network_users.json'
graph_file = '/cs/labs/avivz/jonahar/Twitter/iran_network.gv'

graph = open(graph_file, mode='w')
graph.write('digraph G {\n')

with open(network_file) as n:
    network = json.load(n)

for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        friends_file = os.path.join(sub_dir, 'friends')
        if os.path.isfile(friends_file):
            user = scr_name
            user_friends = []
            with open(friends_file) as f:
                for line in f:
                    friend_id = line[:-1]  # remove newline
                    if friend_id in network:
                        user_friends.append(network[friend_id])
            graph.write(user)
            graph.write(' -> {')
            for friend in user_friends:
                graph.write(' ')
                graph.write(friend)

            graph.write('} ;\n')

graph.close()

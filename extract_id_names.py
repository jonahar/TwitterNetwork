import os
import json

data_dir = '/home/jona/Downloads'
network_users = dict()
for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        details_file = os.path.join(sub_dir, 'user_details')
        friends_file = os.path.join(sub_dir, 'friends')
        if os.path.isfile(details_file):
            f = open(details_file)
            details = json.load(f)
            network_users[details['id']] = details['name']
            f.close()
        else:
            print('Missing details for user', scr_name)
        if not os.path.isfile(friends_file):
            print('Missing friends of user', scr_name)

network_file = open('network_users.json')
json.dump(network_users, network_file)
network_file.close()

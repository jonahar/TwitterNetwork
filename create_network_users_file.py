import os
import json

# creates a dictionary of identifier:name and name:identifier for every user in the data
# dir (unique identifier for each user)

data_dir = '/cs/labs/avivz/jonahar/Twitter/israel_gaza_data_dir'
network_filename = '/cs/labs/avivz/jonahar/Twitter/israel_gaza_network_users.json'

identifier = 0
user_to_identifier = dict()
identifier_to_user = dict()

for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        details_file = os.path.join(sub_dir, 'user_details')
        neighbors_file = os.path.join(sub_dir, 'neighbors')
        if os.path.isfile(neighbors_file):
            user_to_identifier[scr_name] = identifier
            identifier_to_user[identifier] = scr_name
            identifier += 1

network_file = open(network_filename, mode='w')
json.dump({'user_to_identifier': user_to_identifier, 'identifier_to_user': identifier_to_user},
          network_file, indent=4, sort_keys=True)
network_file.close()

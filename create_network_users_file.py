import json
import os

# creates the following dictionaries
# name -> serial
# serial -> name
# serial -> id (twitter id)
# id -> serial
#
# only users with details file and neighbors file are counted. each user is given a unique serial
# serial numbers take less space than twitter ids

data_dir = '/cs/labs/avivz/jonahar/Twitter/israel_palestine_data_dir'
network_filename = '/cs/usr/jonahar/israel_palestine_network_users.json'

serial = 0
user_to_serial = dict()
serial_to_user = dict()
name_to_id = dict()

for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        details_file = os.path.join(sub_dir, 'user_details')
        neighbors_file = os.path.join(sub_dir, 'neighbors')
        if os.path.isfile(neighbors_file) and os.path.isfile(details_file):
            with open(details_file) as f:
                id = json.load(f)['id']
            user_to_serial[scr_name] = serial
            serial_to_user[serial] = scr_name
            name_to_id[scr_name] = id
            serial += 1

with open(network_filename, mode='w') as out_file:
    json.dump({'user_to_serial': user_to_serial,
               'serial_to_user': serial_to_user,
               'name_to_id': name_to_id},
              out_file)

import json
import os

# creates the following dictionaries
# name -> serial
# serial -> name
# name -> id (twitter id)
# id -> name
#
# only users with details file and neighbors file are counted. each user is given a unique serial
# serial numbers take less space than twitter ids and are used in graph representation file

data_dir = '/cs/labs/avivz/jonahar/Twitter/israel_palestine_data_dir'
network_filename = '/cs/usr/jonahar/network_users.json'

serial = 0
name_to_serial = dict()
serial_to_name = dict()
name_to_id = dict()
id_to_name = dict()

for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        details_file = os.path.join(sub_dir, 'user_details')
        neighbors_file = os.path.join(sub_dir, 'neighbors')
        if os.path.isfile(neighbors_file) and os.path.isfile(details_file):
            with open(details_file) as f:
                id = json.load(f)['id']
            name_to_serial[scr_name] = serial
            serial_to_name[serial] = scr_name
            name_to_id[scr_name] = id
            id_to_name[id] = scr_name
            serial += 1

with open(network_filename, mode='w') as out_file:
    json.dump({'name_to_serial': name_to_serial,
               'serial_to_name': serial_to_name,
               'name_to_id': name_to_id,
               'id_to_name': id_to_name},
              out_file)

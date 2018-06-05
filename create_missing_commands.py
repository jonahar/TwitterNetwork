import os

data_dir = '/cs/labs/avivz/jonahar/Twitter/cryptocurrency_data_dir'
in_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/cryptocurrency-search-results'
commands_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/cryptocurrency-missing-commands'

neighbors_commands = 0
details_commands = 0

users = set()
with open(in_file) as ifs:
    for line in ifs:
        tokens = line[:-1].split(';')
        scr_name = tokens[1]
        users.add(scr_name)
        original_scr_name = tokens[2]
        if original_scr_name:
            users.add(original_scr_name)



with  open(commands_file, mode='w') as c:
    for scr_name in users:
        user_dir = os.path.join(data_dir, scr_name)
        if not os.path.isdir(user_dir):
            c.write('mine neighbors of {0} 2500\n'.format(scr_name))
            neighbors_commands += 1
            details_commands += 1
        else:
            neighbors_file = os.path.join(user_dir, 'neighbors')
            details_file = os.path.join(user_dir, 'user_details')
            if not os.path.isfile(neighbors_file):
                c.write('mine neighbors of {0} 2000\n'.format(scr_name))
                neighbors_commands += 1
                details_commands += 1
            elif not os.path.isfile(details_file):
                c.write('mine details of {0}\n'.format(scr_name))
                details_commands += 1

print('neighbors_commands', neighbors_commands)
print('details_commands', details_commands)

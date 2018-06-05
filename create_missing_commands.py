import os


data_dir = '/cs/labs/avivz/jonahar/Twitter/israel_gaza_data_dir'
in_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-palestine-search-results'
commands_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-palestine-missing-commands'

neighbors_commands = 0
details_commands = 0

with open(in_file) as ifs, open(commands_file, mode='w') as c:
    for line in ifs:
        scr_name = line[:-1].split(';')[1]
        user_dir = os.path.join(data_dir, scr_name)
        if not os.path.isdir(user_dir):
            c.write('mine neighbors of {0} 2000\n'.format(scr_name))
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

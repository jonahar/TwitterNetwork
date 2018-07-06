import json
import sys

NUM_NEIGHBORS = 2500
NUM_LIKES = 200


def get_unique_users(results_file: str):
    users = set()
    with open(results_file) as ifs:
        for line in ifs:
            tokens = line[:-1].split(';')
            scr_name = tokens[1]
            users.add(scr_name)
            original_scr_name = tokens[2]
            if original_scr_name:
                users.add(original_scr_name)
    return users


def write_commands(users: set, commands_file: str):
    with open(commands_file, mode='w') as c:
        for scr_name in users:
            c.write('mine details of {0}\n'.format(scr_name))
            c.write('mine likes of {0} {1}\n'.format(scr_name, NUM_LIKES))
            c.write('mine neighbors of {0} {1}\n'.format(scr_name, NUM_NEIGHBORS))

        c.write('exit\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: create_commands_file <graph-properties-file>')
        exit()
    graph_properties = sys.argv[1]
    with open(graph_properties) as f:
        d = json.load(f)
        results_file = d['results_file']
        commands_file = d['commands_file']

    users = get_unique_users(results_file)
    write_commands(users, commands_file)

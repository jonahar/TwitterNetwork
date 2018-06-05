results_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/cryptocurrency-search-results'
commands_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/cryptocurrency-client-commands'


def calc_neighbors_mining_time(num_users, neighbors_per_user, neighbors_per_request,
                               neighbors_requests_per_minute=1500 / 15,
                               details_requests_per_minute=900 / 15):
    """
    returns time in minutes for the mining process
    """
    details = num_users / details_requests_per_minute
    neighbors = ((
                     num_users * neighbors_per_user) / neighbors_per_request) / neighbors_requests_per_minute
    return max(details, neighbors)


commands = set()
with open(results_file) as r:
    for line in r:
        tokens = line[:-1].split(';')
        scr_name = tokens[1]
        commands.add('mine neighbors of {0} 2500\n'.format(scr_name))
        original_scr_name = tokens[2]
        if original_scr_name:
            commands.add('mine neighbors of {0} 2500\n'.format(original_scr_name))

with open(commands_file, mode='w') as c:
    for line in commands:
        c.write(line)

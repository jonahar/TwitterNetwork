from TwitterAnalysis import properties

results_file = properties.results_file
commands_file = properties.commands_file


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


users = set()
with open(results_file) as ifs:
    for line in ifs:
        tokens = line[:-1].split(';')
        scr_name = tokens[1]
        users.add(scr_name)
        original_scr_name = tokens[2]
        if original_scr_name:
            users.add(original_scr_name)
with open(commands_file, mode='w') as c:
    for scr_name in users:
        c.write('mine likes of {0} 200\n'.format(scr_name))
        c.write('mine neighbors of {0} 2500\n'.format(scr_name))

    c.write('exit\n')

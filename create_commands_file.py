results_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-palestine-search-results'
commands_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-palestine-client-commands'

with open(results_file, encoding='utf-8') as r, open(commands_file, mode='w', encoding='utf-8') as c:
    for line in r:
        screen_name = line[:-1].split(';')[1]
        c.write('mine neighbors of {0} 2000\n'.format(screen_name))

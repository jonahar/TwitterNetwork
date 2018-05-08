NEWLINE = '\n'

results_file = 'netanyahu-nuclear-iran.results.sorted'
commands_file = 'client-commands'

with open(results_file) as r, open(commands_file, mode='w') as c:
    for line in r:
        screen_name = line.split(';')[1]
        c.write('mine details of {0}'.format(screen_name))
        c.write(NEWLINE)
        c.write('mine friends of {0} 5000'.format(screen_name))
        c.write(NEWLINE)

NEWLINE = '\n'

results_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-gaza.results.sorted'
commands_file = '/cs/usr/jonahar/PycharmProjects/TwitterMine/israel-gaza-client-commands'

with open(results_file) as r, open(commands_file, mode='w') as c:
    for line in r:
        screen_name = line.split(';')[1]
        c.write('mine details of {0}'.format(screen_name))
        c.write(NEWLINE)

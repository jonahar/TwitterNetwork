#!/usr/bin/python3
import random

N = 500  # group size
B = 50  # neutral group size
num_top_stars = 2
num_mid_stars = 20
num_low_stars = 100
top_star_prob = .8
mid_star_prob = .6
low_star_prob = .4
same_group_prob = .2
neutral_prob = .1
rival_group_prob = .01

group1 = range(N)
group2 = range(N, 2 * N)
NEUTRAL_GROUP = range(2 * N, 2 * N + B)

# average number of friends for each person
average_num_friends = num_top_stars * top_star_prob + \
                      num_mid_stars * mid_star_prob + \
                      num_low_stars * low_star_prob + \
                      (N - num_top_stars - num_mid_stars - num_low_stars) * same_group_prob + \
                      N * rival_group_prob + \
                      len(NEUTRAL_GROUP) * neutral_prob

# print('Expected number of friends for each user:', average_num_friends)

lines = []
lines.append('digraph G {')

group = group1
for group in [group1, group2]:
    stars = random.sample(group, num_top_stars + num_mid_stars + num_low_stars)
    top_stars = stars[:num_top_stars]
    mid_stars = stars[num_top_stars:num_top_stars + num_mid_stars]
    low_stars = stars[-num_low_stars:]
    for i in group:
        i_friends = []
        for j in group:
            # does i follows j
            if j in top_stars:
                if random.random() < top_star_prob:
                    i_friends.append(j)
            elif j in mid_stars:
                if random.random() < mid_star_prob:
                    i_friends.append(j)
            elif j in low_stars:
                if random.random() < mid_star_prob:
                    i_friends.append(j)
            else:
                if random.random() < same_group_prob:
                    i_friends.append(j)

        for j in NEUTRAL_GROUP:
            if random.random() < neutral_prob:
                i_friends.append(j)

        i_friends = [str(j) for j in i_friends]

        lines.append(str(i) + ' -> {' + ' '.join(i_friends) + '} ;')

for X, Y in [(group1, group2), (group2, group1)]:
    for i in X:
        for j in Y:
            if random.random() < rival_group_prob:
                lines.append(str(i) + ' -> ' + str(j) + ';')

lines.append('}')
for l in lines: print(l)

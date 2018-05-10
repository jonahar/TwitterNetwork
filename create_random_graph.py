from random import random

N = 1000
SAME_GROUP_PERCENT = .8
NEUTRAL_GROUP_PERCENT = .15
RIVAL_GROUP_PERCENT = .05
friends_per_user = 100

print('digraph G {')

for i in range(N):
    i_friends = []

    if i > 2 * N / 5 and i < 3 * N / 5:
        # i is a neutral user
        i_friends = [str(j) for j in range(N) if random() < friends_per_user / N]
    else:
        for j in range(N):
            if (i < 2 * N / 5 and j < 2 * N / 5) or (i > 3 * N / 5 and j > 3 * N / 5):
                # same group
                if random() < (friends_per_user / N) * SAME_GROUP_PERCENT:
                    i_friends.append(str(j))
            elif (i < 2 * N / 5 and j > 3 * N / 5) or (i > 3 * N / 5 and j < 2 * N / 5):
                # rival group
                if random() < (friends_per_user / N) * RIVAL_GROUP_PERCENT:
                    i_friends.append(str(j))
            else:
                # j is neutral
                if random() < (friends_per_user / N) * NEUTRAL_GROUP_PERCENT:
                    i_friends.append(str(j))
    try:
        i_friends.remove(str(i))
    except ValueError:
        pass

    print(str(i), ' -> {', ' '.join(i_friends), '} ;')

print('}')

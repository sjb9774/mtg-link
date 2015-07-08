from itertools import combinations
COLORS = ['b', 'g', 'r', 'u', 'w']
ALL_COLOR_COMBINATIONS = []
for i in xrange(1, len(COLORS) + 1):
    combinations_of_size_i = combinations(COLORS, i)
    for combination in combinations_of_size_i:
        ALL_COLOR_COMBINATIONS.append(combination)

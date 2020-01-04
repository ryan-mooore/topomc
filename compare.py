def compare(map1, map2):
    map3 = map1
    for y, row in enumerate(map1):
        for x, element in enumerate(row):
            map3[y][x] = element - map2[y][x]
    return map3

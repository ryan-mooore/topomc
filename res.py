#dependencies
try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")



def yaml_open(object):
    try:
        with open("settings.yaml", "r") as settings:
            settings = yaml.full_load(settings)
            return settings[object]
    except:
        raise Exception("settings.yaml is incorrectly formatted or missing")



"""
https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
"""

from time import perf_counter
start = 0

def print_progressbar(iteration, total, prefix = "", suffix = ""):

    decimals = 1
    length = 30
    fill = '■'
    empty = '□'
    print_end = "\r"

    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + empty * (length - filled_length)
    print(
        f'{print_end}{prefix} {bar} {percent}% {iteration}/{total} {suffix}',
        end = print_end
    )

    if iteration == 1:
        global start
        start = perf_counter()
    # Print New Line on Complete
    if iteration == total:
        end = perf_counter()
        exec_time = round(end - start, 2)
        print()
        print('%s %s in %ss' % (total, suffix, exec_time))
        print()



"""
This file is a pythonic adaptation of Reddit user bxny5's unstream
function for decoding minecraft chunkheightmap data, written in perl.
https://www.reddit.com/r/Minecraft/comments/bxny75/fun_with_chunk_data_heightmap_edition/
"""



def unstream(data, bits_per_value, int_size):

    bl = 0
    result = []
    value = 0

    for byte in data:
        for num in range(int_size):
            bit = (byte >> num) & 0x01
            value = (bit << bl) | value
            bl += 1
            if bl >= bits_per_value:
                result.append(value)
                value = 0
                bl = 0
    return result

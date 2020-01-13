# coding=UTF-8

"""
This function is taken from this stackoverflow question but adapted for the use
case of this application
https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
"""


from time import perf_counter
start = 0

def _print(iteration, total, prefix = "", suffix = ""):

    decimals = 1
    length = 30
    fill = '■'
    empty = '□'
    print_end = "\r"

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + empty * (length - filled_length)
    print(f"{print_end}{prefix} {bar} {percent}% {iteration}/{total} {suffix}", end = print_end)

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

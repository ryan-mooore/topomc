# coding=UTF-8

from time import perf_counter
start = 0


def _print(iteration, total, prefix="", suffix=""):
    """This function is taken from this stackoverflow question but adapted for
    the use case of this application
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """

    decimals = 1
    length = 30
    fill = "\u25A0"
    empty = "\u25A1"
    print_end = "\r"

    percent = ("{0:." + str(decimals) + "f}")\
        .format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + empty * (length - filled_length)
    
    print(
        f"{print_end}{prefix} {bar} {percent}% {iteration}/{total} {suffix}",
        end=print_end
        )

    if iteration == 1:
        global start
        start = perf_counter()

    # print new line on complete
    if iteration == total:
        end = perf_counter()
        exec_time = round(end - start, 2)
        print()
        print(f"{total} {suffix} in {exec_time}s")
        print()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import argparse

# config variables
MAX = 100
MIN = 0
SIZE = 100

MINIMUM_SIZE_GRAPH = 12
# DEFAULT_STRFTIME = "%Y-%j-%H:%M:%S:%L"
DEFAULT_STRFTIME = "%H:%M:%S"

COLORS = {
    "red": '\033[91m',
    "end": '\033[0m'
}
SYMBOL_TABLE = {
    "progress": ['\u258F', '\u258E', '\u258D', '\u258C', '\u258B', '\u258A', '\u2589', '\u2588'],
    "side": '\u2551',
    "horizontal": '\u2550',
    "corners": ['\u2554', '\u2557', '\u255A', '\u255D'],
    "ts": ['\u2566', '\u2569'],
    "empty": ' '
}

FLOAT_REGEX = "^[-+]?((\d*(\.|\,)\d+)|(\d+))\n$"


class TextGraph:

    def __init__(self, in_size, in_min, in_max, in_strftime):
        self.size = in_size
        self.min = in_min
        self.max = in_max
        self.strftime = in_strftime

        self.lenfloat = (8, 2)
        self.lenmin = len("%.2f" % self.min)
        self.lenmax = len("%.2f" % self.max)
        self.lenstrftime = len(time.strftime(self.strftime))

    def extremities(self, top=True):
        print(
            SYMBOL_TABLE["corners"][0 if top else 2],
            SYMBOL_TABLE["horizontal"] * (1 + self.lenstrftime + 1),
            SYMBOL_TABLE["ts"][0 if top else 1],
            SYMBOL_TABLE["horizontal"] * (1 + self.size + 1),
            SYMBOL_TABLE["ts"][0 if top else 1],
            SYMBOL_TABLE["horizontal"] * (1 + self.lenmin + 1),
            SYMBOL_TABLE["ts"][0 if top else 1],
            SYMBOL_TABLE["horizontal"] * (1 + self.lenfloat[0] + 1),
            SYMBOL_TABLE["ts"][0 if top else 1],
            SYMBOL_TABLE["horizontal"] * (1 + self.lenmax + 1),
            SYMBOL_TABLE["corners"][1 if top else 3],
            sep=""
        )

    def update(self, number):
        # print time
        print(
            SYMBOL_TABLE["side"],
            SYMBOL_TABLE["empty"],
            time.strftime(self.strftime),
            SYMBOL_TABLE["empty"],
            SYMBOL_TABLE["side"],
            SYMBOL_TABLE["empty"],
            sep="",
            end=""
        )

        # flag for extrapolation
        out_of_bounds = False

        # normalize number
        if number > self.max:
            out_of_bounds = True
            number = self.max
        elif number < self.min:
            out_of_bounds = True
            number = self.min

        # transform number to be workable
        number -= self.min

        # subblocks created with different chars
        sub_blocks_length = len(SYMBOL_TABLE["progress"])

        # relation between the values and
        relation = (self.size * sub_blocks_length) / (self.max - self.min)

        # offset in blocks related to graph zero
        offset = int(relation * number)

        # the individual offset of the block inside the char
        modulo = (offset - 1) % sub_blocks_length

        # offset in whole blocks excluding inside chars
        block_offset = int((offset - modulo) / sub_blocks_length)

        if not out_of_bounds:
            # print the graph
            print("%s%s%s" % (
                SYMBOL_TABLE["progress"][-1] * block_offset,
                SYMBOL_TABLE["progress"][modulo] if offset > 0 else SYMBOL_TABLE["empty"],
                ' ' * (self.size - block_offset - 1)
            ), end="")
        else:
            middle = int(self.size / 2)
            print("%s%s%s" % (
                SYMBOL_TABLE["empty"] * (middle - 1),
                "%s?%s" % (COLORS["red"], COLORS["end"]),
                SYMBOL_TABLE["empty"] * (self.size - middle)
            ), end="")

        # print the end
        print(
            SYMBOL_TABLE["empty"],
            SYMBOL_TABLE["side"],
            SYMBOL_TABLE["empty"],
            "%.2f" % self.min,
            SYMBOL_TABLE["empty"],
            SYMBOL_TABLE["side"],
            SYMBOL_TABLE["empty"],
            ("%%%d.%df" % (self.lenfloat[0], self.lenfloat[1])) % number,
            SYMBOL_TABLE["empty"],
            SYMBOL_TABLE["side"],
            SYMBOL_TABLE["empty"],
            "%.2f" % self.max,
            SYMBOL_TABLE["empty"],
            SYMBOL_TABLE["side"],
            sep=""
        )

def main():

    argument_parser = argparse.ArgumentParser(
        description="Plots realtime graphs based on a single number coming from stdin separated by newline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # add the needed arguments
    argument_parser.add_argument("-M", "--max", type=float, default=MAX, help="graph ceiling")
    argument_parser.add_argument("-m", "--min", type=float, default=MIN, help="graph zero")
    argument_parser.add_argument("-s", "--size", type=int, default=SIZE, help="graph length size in chars")
    argument_parser.add_argument("-t", "--strftime", type=str, default=DEFAULT_STRFTIME, help="graph strftime")

    # parse the args
    arguments = argument_parser.parse_args()

    # simple check on graph length
    if arguments.size < MINIMUM_SIZE_GRAPH:
        print("The size of the graph cannot be smaller than %d" % MINIMUM_SIZE_GRAPH)
        exit(1)

    # check simple logic
    if arguments.min >= arguments.max:
        print("There must be some interval between min and max")
        exit(1)

    # create text graph object
    tg = TextGraph(
        arguments.size,
        arguments.min,
        arguments.max,
        arguments.strftime
    )
    tg.extremities(top=True)

    # main stdin loop
    try:
        for line in sys.stdin:
            match = re.fullmatch(FLOAT_REGEX, line)
            if match is not None:
                number = float(match.groups()[0])
                tg.update(number)
    except KeyboardInterrupt:
        pass

    # tg.extremities(top=False)


if __name__ == "__main__":
    main()

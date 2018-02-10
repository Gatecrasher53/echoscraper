"""echoscraper scrapes and downloads lectures from Echo360 into organised folder structure."""

import re
import sys

from . import scraper
from . import download
from . import register

# Prints current Python interpreter version
# print("___ Python " + str(sys.version[:5]) + " ___\n")

# Outputs how many arguments program was run with
# print("Program '" + sys.argv[0] + "' run with " + str(len(sys.argv)-1) + " arguments.")

# GLOBALS
# Command List
COMMANDS = {
    "scrape": {
        "doc": scraper.__doc__,
        "func": scraper.start,
        "numargs": 1
    },
    "download": {
        "doc": download.__doc__,
        "func": download.start,
        "numargs": 1,
        "ops": ["c", "y"]
    },
    "register": {
        "doc": register.__doc__,
        "func": register.start,
        "numargs": 1,
        "ops": ["d", "f", "m"]
    }
}

# Function Definitions

def usage():
    """Prints usage information to user."""
    def indent(multiline, prefix, skip=[0]):
        lines = multiline.split('\n')
        lines = [line if i in skip else prefix + line for i, line in enumerate(lines)]
        return '\n'.join(lines)

    print(__doc__ + "\n")
    # TODO: Update usage message to match python package bs
    print("Usage:\n    python -m echoscraper <command> [options] <argument>")
    print("\tOR\n    python echoscraper-runner.py <command> [options] <argument>\n")

    print("Commands:")
    for key, value in COMMANDS.items():
        value["doc"].split('\n')
        print("    {:<10}  {:<}\n".format(key, indent(value["doc"], 16*' ')))
    
    print("Arguments:\n    All commands require the register filename\n")
    print("Example:\n    python -m echoscraper register -d register.json")
    print("        - prints the metadata for courses contained in './register.json'")

def options(start):
    """Get options for a given argument."""
    ops = []
    for arg in sys.argv[start+2:]:
        if re.match(r'-[a-z]', arg):
            ops.append(re.sub('-', '', arg))
        else:
            break

    return ops

def parse():
    """Get any arguments and options that were passed with the function call."""
    arguments = []
    for i, arg in enumerate(sys.argv[1:]):
        if not re.match(r'-[a-z]', arg):
            arguments.append([arg, *options(i)])

    return arguments


# Main code
def main():
    if len(sys.argv) < 2:
        # No arguments given, print usage message
        usage()

    else:
        arguments = parse()

        arg1 = arguments[0]
        if arg1[0] in COMMANDS:
            start = COMMANDS[arg1[0]]["func"]
            if len(arguments)-1 != COMMANDS[arg1[0]]["numargs"]:
                print("Wrong number of arguments to method '{}'.".format(arg1[0]))
            else:
                start(*arguments[1:], arg1[1:])
        else:
            print("Unknown command '{}'.".format(arguments[0][0]))

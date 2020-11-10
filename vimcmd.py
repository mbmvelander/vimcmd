#!/usr/bin/env python
 
import csv
import sys
import copy
import os.path
import random
import textwrap
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
 
 
CACHE_FILE = os.path.expanduser("~") + "/.vimcmd_cache"
 
SOURCES = {
    "basic": "/Users/malin/src/github.com/mbmvelander/vimcmd/data/vim-basic.csv"
}
 
 
def select_source(source):
    if source not in SOURCES.keys():
        if source in SOURCES.values():
            print("SOURCES: {}".format(SOURCES))
            return source
        if os.path.isfile(source):
            SOURCES[source] = source
        else:
            raise Exception("Source {} not recognised".format(source))
    return SOURCES.get(source, "")
 
 
def read_source(source):
    data = {}
    with open(source, mode="r") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Will overwrite if same keys are on several rows
            data[keys_to_id(row["keys"])] = copy.deepcopy(row)
    return data
 
 
def keys_to_id(keys):
    # Make alphanumeric (non-alnum translated to order number), lowercase, whitespace=underscore
    return "_".join("".join(c if c.isalnum() else str(ord(c)) for c in word)
                    for word in keys.lower().split())
 
 
def write_command_to_cache(command_id, source):
    today = datetime.today().strftime("%Y%m%d")
    with open(CACHE_FILE, "a+") as f:
        f.write("{};{};{}".format(command_id, today, source) + "\n")
 
 
def read_cached_commands():
    if not os.path.isfile(CACHE_FILE):
        return {}
    data = {}
    with open(CACHE_FILE, "r") as f:
        reader = csv.DictReader(f, delimiter=";", fieldnames=[
                                "id", "date", "source"])
        for row in reader:
            if not data.get(row["source"], {}):
                data[row["source"]] = {}
            # Will overwrite if same keys are on several rows
            data[row["source"]][row["date"]] = row["id"]
    return data
 
 
def clear_cache():
    # Truncate the cache file by simply opening it with w
    # This will create the file if it doesn't exist
    with open(CACHE_FILE, "w"):
        pass
 
 
def filter_already_used(commands, source):
    already_used = list(read_cached_commands().get(source, {}).values())
    return {k: commands[k] for k in commands.keys() if k not in already_used}
 
 
def get_todays_command(commands, source):
    cached_commands = read_cached_commands()
    todays_command_id = cached_commands.get(source, {}).get(
        datetime.today().strftime("%Y%m%d"), "")
    if not todays_command_id:
        (todays_command_id, todays_command) = pick_random_command(commands, source)
        write_command_to_cache(todays_command_id, source)
        return todays_command
    return commands[todays_command_id]
 
 
def pick_random_command(commands, source, exclude_used=True):
    if exclude_used is True:
        filtered_commands = filter_already_used(commands, source)
    else:
        filtered_commands = commands
    if not filtered_commands:
        print("Finished all Vim commands in current source! Select a new source of Vim commands for Command OTD, or clear cache to start over")
        sys.exit(0)
    random_id = random.choice(list(filtered_commands))
    return (random_id, filtered_commands[random_id])
 
 
def pretty_print(command_data):
    header = "VIM COMMAND OF THE DAY: {} ({})".format(
        command_data["keys"], command_data["short"])
    print(header)
    print("=" * len(header))
    print(textwrap.fill(command_data["long"], len(header)))
    print("-" * len(header))
 
 
def main(args):
    try:
        if args.clear_cache:
            clear_cache()
            return 0
        source = select_source(args.source)
        commands = read_source(source)
        pretty_print(get_todays_command(commands, source))
    except Exception as e:
        print("Failed: " + str(e))
        return 1
    return 0
 
 
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script for displaying a random Vim command")
    parser.add_argument("--source", dest="source",
                        default="basic", help="Location of csv file")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Clear the cache and exit")
    args = parser.parse_args()
    sys.exit(main(args))
 

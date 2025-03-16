#! /usr/bin/env python3
#
# Play with talking to MySQL
#
# Mar-2025, Pat Welch, pat@mousebrains.com

from argparse import ArgumentParser
import json
import os.path
import mysql.connector as mysql
import logging
from TPWUtils import Logger

class DB:
    def __init__(self, args:ArgumentParser):
        self.__args = args
        self.__db = None

    @staticmethod
    def addArgs(parser:ArgumentParser):
        grp = parser.add_argument_group(description="DB related options")
        grp.add_argument("--credentials", type=str, default="~/.config/levels", 
                         help="Database name to access")
        grp.add_argument("--dbname", type=str, default="levels", help="Database name to access")

def main():
    parser = ArgumentParser()
    Logger.addArgs(parser)
    DB.addArgs(parser)
    args = parser.parse_args()
    print(parser)
    print(args)

    Logger.mkLogger(args, fmt="%(asctime)s %(levelname)s: %(message)s")

    logging.info("Boris %s", args)

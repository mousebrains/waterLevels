#! /usr/bin/env python3
#
# Read in URL YAML files and fetch them, then store in a database
#
# Mar-2025, Pat Welch, pat@mousebrains.com

from argparse import ArgumentParser
from TPWUtils import Logger
import yaml
import os.path
import glob

parser = ArgumentParser(description='Fetch URLs from YAML files and store them in a database.')
parser.add_argument("--urls", type=str, default="urls.d",
                    help="Directory containing YAML files with URLs to fetch.")
parser.add_argument("--pages", type=str, default="pages", 
                    help="Directory to store fetched pages.")
Logger.addArgs(parser)
args = parser.parse_args()

Logger.mkLogger(args, fmt="%(asctime)s %(levelname)s %(message)s", level="INFO")
if not os.path.isdir(args.urls):
    raise FileNotFoundError(f"{args.urls} not found")

for fn in glob.glob(os.path.join(args.urls, "*.yaml")):
    logging.info("fn %s", fn)
    with open(fn, 'r') as f:
        items = yaml.safe_load(f)



#! /usr/bin/env python3
#
# Read in URL YAML files and fetch them, then store in a database
#
# Mar-2025, Pat Welch, pat@mousebrains.com

from argparse import ArgumentParser
from TPWUtils import Logger
import logging
import yaml
import os.path
import os
import glob
from urllib.parse import urlparse
import requests

class USGS_rdb:
    # Handle parsing of USGS RDB format files
    def __init__(self, body:byte, args:ArgumentParser) -> None:
        " Parse the USGS RDB data and store it in a database"
        logging.info("Parsing USGS RDB data of length %d", len(body))
        self.__names = None
        self.__formats = None
        for line in body.split(b"\n"):
            fields = line.strip().split(b"#", 1)
            if not fields: continue
            fields[0] = fields[0].strip()
            if len(fields[0]) == 0: continue
            fields = fields[0].split(b"\t")
            if len(fields) < 2: continue
            if "agency_cd" in fields:
                self.__parseNames(fields)
            elif "5s" in fields: 
                self.parseFormats(fields)
            else:
                self.__parseLine(fields)

    def __parseNames(self, fields:list) -> None:
        " Parse the header line to get names of columns"
        self.__names = [field.decode('utf-8') for field in fields]
        logging.info("Parsed names: %s", self.__names)

    def __parseFormats(self, fields:list) -> None:
        " Parse the format line to get data types of columns"
        self.__formats = [field[-1:].decode('utf-8') for field in fields]
        if not self.__names or (len(self.__formats) != len(self.__names)):
            logging.warning("Mismatch in number of formats and names, %s, %s", 
                            self.__names, self.__formats))
            self.__formats = None
            return
        logging.info("Parsed formats: %s", self.__formats)

    def __parseLine(self, fields:list) -> None:
        " Parse a data line and store it in a database"
        if self.__names is None:
            logging.warning("Skipping line, names not set, %s", b"\t".join(fields))
            return
        if self.__formats is None:
            logging.warning("Skipping line, formats not set, %s", b"\t".join(fields))
            return
        if len(fields) != len(self.__names):
            logging.warning("Skipping line, field count, %s, != %s", len(field), len(self.__names))
            return
        data = {name: field.decode('utf-8') for name, field in zip(self.__names, fields[1:])}
        # Here you would typically insert the data into a database
        logging.info("Parsed data: %s", data)

def parseContent(parser:str, body:bytes, args:ArgumentParser) -> None:
    " Parse the content of the fetched URL and store it in a database"

    logging.info("Parsing content for parser %s", parser)

    match parser.lower():
        case "usgs.rdb":
            parseUSGS_rdb(body, args)
        case "_":
            raise NotImplementedError(f"Parser {parser} not implemented")


def fetchURLs(parser:str, urls:list, args:ArgumentParser) -> None:
    " Fetch a list of URLs and store them in a database"
    if not os.path.isdir(args.pages):
        logging.info("Creating directory %s", args.pages)
        os.mkdir(args.pages)

    with requests.Session() as session:
        for url in urls:
            logging.info("Fetching %s", url)
            try:
                response = session.get(url)
                response.raise_for_status()  # Raise an error for bad responses
                filename = os.path.join(args.pages, f"{parser}_{os.path.basename(url)}")
                body = response.content
                with open(filename, 'wb') as fp:
                    fp.write(body)
                logging.info("Stored %s bytes in %s", len(body), filename)
                parseContent(parser, body, args)
            except requests.RequestException as e:
                logging.error("Error fetching %s: %s", url, str(e))
            except:
                logging.exception("Unexpected error while processing %s", url)

def procParser(parserName:str, urls:list, args:ArgumentParser) -> None:
    commonURL = mkCommonURL(urls)
    for key in sorted(commonURL):
        logging.info("Working on parser %s with n %s URLs", key, len(commonURL[key]))
        fetchURLs(parserName, commonURL[key], args)

def mkCommonURL(urls:list) -> dict:
    " Common groupings of URLs for common connection to a host"
    items = {}
    for url in urls:
        parsed = urlparse(url)
        if parsed.netloc not in items:
            items[parsed.netloc] = []
        items[parsed.netloc].append(url)

    return items

parser = ArgumentParser(description='Fetch URLs from YAML files and store them in a database.')
grp = parser.add_mutually_exclusive_group(required=False)
grp.add_argument("--urls", type=str, default="url.d",
                 help="Directory containing YAML files with URLs to fetch.")
grp.add_argument("--url", type=str, help="url YAML filename to work with")
grp.add_argument("--src", type=str,
                 help="Already retrieved page to parse, must also specify --parser")
grp.add_argument("--hyperlink", type=str,
                 help="URL to fetch, must also specify --parser")


parser.add_argument("--parser", type=str, help="Name of parser to use with --src or --hyperlink")

parser.add_argument("--pages", type=str, default="pages", 
                    help="Directory to store fetched pages.")
Logger.addArgs(parser)
args = parser.parse_args()

Logger.mkLogger(args, fmt="%(asctime)s %(levelname)s %(message)s")

if args.src:
    if not args.parser:
        raise parser.error("Must specify --parser with --src")
    if not os.path.isfile(args.src):
        raise FileNotFoundError(f"{args.src} not found")
    with open(args.src, "rb") as fp:
        body = fp.read()
        parseContent(args.parser, body, args)
    items = {}
elif args.hyperlink:
    if not args.parser:
        raise parser.error("Must specify --parser with --hyperlink")
    items = {ars.parser: [args.hyperlink]}
elif args.url:
    args.url = os.path.abspath(os.path.expanduser(args.url))
    if not os.path.isfile(args.url):
        raise FileNotFoundError(f"{args.url} not found")
    with open(args.url, 'r') as fp:
        items = yaml.safe_load(fp)
else: # args.urls
    args.urls = os.path.abspath(os.path.expanduser(args.urls))
    if not os.path.isdir(args.urls):
        raise FileNotFoundError(f"{args.urls} is not a directory")
    items = {}
    for fn in glob.glob(os.path.join(args.urls, "*.yaml")):
        with open(fn, 'r') as fp:
            info = yaml.safe_load(fp)
            for key in info:
                if key not in items:
                    items[key] = []
                items[key].extend(info[key])

for name in items:
    procParser(name, items[name], args)

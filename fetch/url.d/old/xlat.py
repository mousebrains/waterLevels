#! /usr/bin/env python3
#
# Translate original URL files into YAML files
#
# Mar-2025, Pat Welch, pat@mousebrains.com

from argparse import ArgumentParser
import yaml
import os.path

parser = ArgumentParser()
parser.add_argument("fn", nargs="+", type=str, help="Old URL files")
parser.add_argument("--outdir", type=str, default=".", help="Where to write output files")
args = parser.parse_args()

items = {}
for fn in args.fn:
    with open(fn, "r") as ifp:
        for line in ifp:
            line = line.strip()
            if not line: continue
            fields = line.split("#", 1)
            fields[0] = fields[0].strip()
            if not fields[0]: continue
            parts = fields[0].split(" ", 1)
            if len(parts) == 2:
                if parts[0] not in items: 
                    items[parts[0]] = []
                items[parts[0]].append(parts[1])
            else:
                print(f"Bad line '{line}'")
if items: 
    for key in items:
        ofn = os.path.join(args.outdir, key + ".yaml")
        with open(ofn, "w") as ofp:
            a = {key: items[key]}
            yaml.dump(a, ofp, default_flow_style=False, sort_keys=True)

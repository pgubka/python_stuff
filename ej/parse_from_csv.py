#!/usr/bin/python

"""
This is to parse and save eurojackpot numbers in json.
Csv is downloaded from
wget www.tipos.sk/Documents/Csv/eurojackpot.csv
"""
import argparse
import json

def parse_csv_file(filename):
    result = {}
    with open(filename,'rt') as fd:
        lines = fd.readlines()

    # ignore the 1st line with column names
    for line in lines[1:]:
        splited_line = line.split(';')
        print splited_line
        iso_date = splited_line[0]
        balls = [int(num) for num in splited_line[5:10]]
        euro = [int(num) for num in splited_line[10:12]]
        balls.sort()
        euro.sort()
        result[iso_date] = [balls, euro]

    return result

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Csv file name")
    parser.add_argument("--outfile", help="Json file with parsed results", default="results.json")
    args = parser.parse_args()

    results = parse_csv_file(args.filename)
    print json.dumps(results, sort_keys=True)

    with open(args.outfile,"wt") as fd:
        fd.write(json.dumps(results, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()

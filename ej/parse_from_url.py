#!/usr/bin/python

"""
This is to parse and save eurojackpot numbers in json.
Results must be downloaded from
https://www.euro-jackpot.net/en/results-archive-2018 (or another 201X)
and manually modified to the state

<a>
                <tr>
                    <td><a href="/en/results/06-04-2012">Friday 6<sup>th</sup> April 2012</a></td>
                    <td>
                        <ul class="balls small">
                                <li class="ball"><span>7</span></li>
                                <li class="ball"><span>8</span></li>
                                <li class="ball"><span>34</span></li>
                                <li class="ball"><span>36</span></li>
                                <li class="ball"><span>38</span></li>
                                <li class="euro"><span>4</span></li>
                                <li class="euro"><span>5</span></li>
                        </ul>
                    </td>
                </tr>
...
...
...
</a>
"""
import argparse
import json
import xml.etree.ElementTree as ET

def parse_xml_file(filename):
    result = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    for week in root:
        date = week[0][0].attrib['href'][12:]
        iso_date = date[-4:]+date[2:6]+date[:2]
        balls = [ int(week[1][0][i][0].text) for i in range(5)]
        euro = [ int(week[1][0][i][0].text) for i in range(5,7)]
        result[iso_date] = [balls, euro]

    return result

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Result file name")
    parser.add_argument("--outfile", help="Json file with parsed results", default="results.json")
    args = parser.parse_args()

    results = parse_xml_file(args.filename)
    print json.dumps(results, sort_keys=True)

    with open(args.outfile,"wt") as fd:
        fd.write(json.dumps(results, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()

import argparse
import csv
import urllib.request
import zlib

import fileifc


def run(args: argparse.Namespace):
    """
    Requests all the articles names in a given csv file from the origin server and writes the compressed article
    bodies to a JSON
    """
    with open(args.i, 'r') as fp:
        wrtr = fileifc.Writer(args.o)

        rdr = csv.reader(fp)

        for row in rdr:
            for article in row:
                response = urllib.request.urlopen('http://{}:8080/wiki/{}'.format(args.n, article))
                content = response.read()

                # compress content here so cache doesn't have to
                wrtr.write(article, zlib.compress(content))

        fp.close()
        wrtr.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Requests all the articles names in the given csv file from the origin'
                                                 'server and writes the compressed article bodies to a JSON')
    parser.add_argument('-i', required=True, help='input file name')
    parser.add_argument('-o', required=True, help='output file name')
    parser.add_argument('-n', required=False, default='ec2-18-207-254-152.compute-1.amazonaws.com',
                        help='origin server address')
    args = parser.parse_args()

    run(args)

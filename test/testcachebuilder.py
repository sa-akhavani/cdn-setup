import argparse

import fileifc
import requestcache


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tests requestcache')
    parser.add_argument('-i', required=True, help='input file name')
    parser.add_argument('-o', required=True, help='output file name')
    parser.add_argument('-n', required=False, default='ec2-18-207-254-152.compute-1.amazonaws.com',
                        help='origin server address')
    parser.add_argument('-skip', required=False, type=bool, default=True, help='skip requesting files')
    args = parser.parse_args()

    if not args.skip:
        requestcache.run(args)

    rdr = fileifc.Reader(args.o)
    objlist = rdr.read()

    sz = 0
    for obj in objlist:
        sz += len(obj['body'])

    print(sz)
    print(sz < 10485760)

import argparse

replicalist = ['ec2-34-238-192-84.compute-1.amazonaws.com',
               'ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com',
               'ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com',
               'ec2-34-248-209-79.eu-west-1.compute.amazonaws.com',
               'ec2-18-231-122-62.sa-east-1.compute.amazonaws.com',
               'ec2-3-101-37-125.us-west-1.compute.amazonaws.com']

PIDFILE = 'pid.txt'


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', required=True, type=int, help='port')
    parser.add_argument('-o', required=True, help='origin')
    parser.add_argument('-n', required=True, help='name')
    parser.add_argument('-u', required=True, help='username')
    parser.add_argument('-i', required=True, help='keyfile')
    return parser.parse_args(argv[1:])

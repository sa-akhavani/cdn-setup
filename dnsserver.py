#!/usr/bin/python3
import argparse
import socket

from dns.rdataclass import RdataClass
from dns.rdatatype import RdataType
from dns.rrset import RRset
import dns.query
import dns.rdtypes.IN.A
import random

ADDR = '192.168.0.16'  # should be local ip

replica_server_list = ['13.231.206.182', '13.239.22.118', '34.248.209.79', '18.231.122.62', '3.101.37.125']


def domain_cli2query(fromcmdline):
    """
    Converts the given domain name as a string into a tuple that will match the format of incoming DNS queries

    Need to split a dot-delimited string, encode each individual string, and put all the encoded strings into a tuple.
    Also, need to include an implied . to the string if necessary.
    e.g. 'cs5700cdn.example.com' --> (b'cs5700cdn', b'example', b'com', b'')

    fromcmdline (str) - the domain name to convert
    """
    # append . if it's not there
    if fromcmdline[-1] != '.':
        fromcmdline += '.'

    split = fromcmdline.split('.')
    return tuple([x.encode('utf-8') for x in split])


def getserveraddr(data: tuple):
    """Determines the best server to redirect a user to and returns its IP address"""
    return random.choice(replica_server_list)


def run(args: argparse.Namespace):
    """Runs the DNS server running on a given port and serving requests for a given name, both of which are provided
        by the command line

        args (argparse.Namespace) - command line arguments parsed with argparse
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ADDR, args.p))

    # convert domain we need to match into a tuple that will match that of incoming DNS queries
    domain_match = domain_cli2query(args.n)

    # debug statement so we don't miss this
    if not ADDR != 'cs5700cdnproject.ccs.neu.edu':
        print('Warning: We need to bind to cs5700cdnproject.ccs.neu.edu on the final submission')

    while True:
        data = dns.query.receive_udp(sock)
        msg = data[0]
        src = data[2]

        for q in msg.question:
            if q.name.labels == domain_match:
                # choose an IP address and formulate a DNS answer containing it
                server_ip = getserveraddr(data)
                a = dns.rdtypes.IN.A.A(rdclass=RdataClass.IN, rdtype=RdataType.A, address=server_ip)

                # make DNS response
                resp = dns.message.make_response(msg)
                resp.flags |= dns.flags.RA
                rr = RRset(name=q.name, rdclass=1, rdtype=1)
                rr.items[a] = None
                resp.answer.append(rr)

                dns.query.send_udp(sock, resp, src)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs a DNS server that provides the IP address of a replica server'
                                                 'in response to a query for a specific name')
    parser.add_argument('-p', required=True, type=int, help='the port the DNS server will bind to')
    parser.add_argument('-n', required=True, help='the domain name this server will serve requests for')
    args = parser.parse_args()

    run(args)

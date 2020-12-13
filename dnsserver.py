#!/usr/bin/python3
import argparse
import logging
import socket
import urllib.request
import urllib.error

from dns.rdataclass import RdataClass
from dns.rdatatype import RdataType
from dns.rrset import RRset
import dns.query
import dns.rdtypes.IN.A

ADDR = '192.168.198.131'
replica_server_list = ['34.238.192.84', '13.231.206.182', '13.239.22.118', '34.248.209.79', '18.231.122.62', '3.101.37.125']
latency_map = dict()

logging.basicConfig(level=logging.DEBUG)


def domain_cli2query(fromcmdline: str):
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


def getserveraddr(src_ip: str):
    """Determines the best server to redirect a user to and returns its IP address"""
    if src_ip not in latency_map:
        # initialize all latencies to -1 so that we can send the client to all of them and get measurements
        latency_map[src_ip] = [-1] * len(replica_server_list)

    latencies = latency_map[src_ip]
    minlat = min(latencies)
    server_ip = replica_server_list[latencies.index(minlat)]

    logging.debug('Redirecting client to server {} which has RTT {}'.format(server_ip, minlat))
    return server_ip


def request_msmt(server_ip, server_port, client_ip):
    """Requests measurment data from the HTTP server and stores it if it receives any"""
    logging.debug('Requesting measurement data from {} for {}'.format(server_ip, client_ip))
    serveridx = replica_server_list.index(server_ip)  # only 6 elements. fine to do linear scan if it reduces code

    try:
        response = urllib.request.urlopen('http://{}:{}/msmt/{}'.format(server_ip, server_port, client_ip))
        content = response.read()
        logging.debug('Received message from HTTP server: {}'.format(content))
    except urllib.error.URLError:
        logging.debug('URLError when requesting measurement'.format(server_ip))
        content = b''

    if content == b'':
        rtt = latency_map[client_ip][serveridx]
    else:
        rtt = float(content)

    logging.debug('Obtained rtt value {}'.format(rtt))
    latency_map[client_ip][serveridx] = rtt
    logging.debug('New latency set: {}'.format(latency_map[client_ip][serveridx]))


def run(args: argparse.Namespace):
    """Runs the DNS server running on a given port and serving requests for a given name, both of which are provided
        by the command line

        args (argparse.Namespace) - command line arguments parsed with argparse
    """
    logging.debug('DNS Server init')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ADDR, args.p))

    # convert domain we need to match into a tuple that will match that of incoming DNS queries
    domain_match = domain_cli2query(args.n)

    # debug statement so we don't miss this
    if ADDR != 'cs5700cdnproject.ccs.neu.edu':
        print('Warning: We need to bind to cs5700cdnproject.ccs.neu.edu on the final submission')

    logging.debug('DNS Server accepting requests')
    while True:
        data = dns.query.receive_udp(sock)
        msg = data[0]
        src_ipport = data[2]
        logging.debug('Incoming request from {}'.format(src_ipport))

        for q in msg.question:
            if q.name.labels == domain_match:
                logging.debug('Valid request for {}'.format(args.n))

                # choose an IP address and formulate a DNS answer containing it
                server_ip = getserveraddr(src_ipport[0])
                a = dns.rdtypes.IN.A.A(rdclass=RdataClass.IN, rdtype=RdataType.A, address=server_ip)

                # make DNS response
                resp = dns.message.make_response(msg)
                resp.flags |= dns.flags.RA
                rr = RRset(name=q.name, rdclass=1, rdtype=1)
                rr.items[a] = None
                resp.answer.append(rr)

                logging.debug('Redirecting client to {}'.format(server_ip))
                dns.query.send_udp(sock, resp, src_ipport)

                request_msmt(server_ip, args.p, src_ipport[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs a DNS server that provides the IP address of a replica server'
                                                 'in response to a query for a specific name')
    parser.add_argument('-p', required=True, type=int, help='the port the DNS server will bind to')
    parser.add_argument('-n', required=True, help='the domain name this server will serve requests for')
    args = parser.parse_args()

    run(args)

#!/usr/bin/python3
import argparse
import subprocess
import urllib.request
import logging

from flask import Flask, request
import cache
import fileifc

# ec2-18-207-254-152.compute-1.amazonaws.com will be provided from the command line
# should resolve to '18.207.254.152'
origin_server_ip = None
origin_server_port = 8080
local_port = None
cache_memory_limit = 10485760

logging.basicConfig(level=logging.DEBUG)

CACHEFN = 'requested.json'

app = Flask(__name__)
cache = cache.Cache(cache_memory_limit)


def fillcache():
    """Fills the cache with the most popular pages by reading that data from a config file on the system"""
    rdr = fileifc.Reader(CACHEFN)
    objlist = rdr.read()

    for obj in objlist:
        cache.put(obj['article'], obj['body'], alreadycompressed=True)


def extractrtt(ssval: str):
    """
    Extracts the RTT from the given string, which should be the output of running ss -it

    ssval (str) the captured output of ss -it
    return (str) the extracted rtt value from ssval
    """
    split = ssval.split()
    rttstr = split[15]  # constant time lookup. should give us something like rtt:0.015/0.007
    return rttstr.split(':')[1].split('/')[0]


@app.route('/wiki/<name>')
def servearticle(name: str):
    """Serves requests for Wikipedia articles

    name (str) the article title being requested
    """
    # get the output of doing one of these commands and use the rtt field to store measurement data for this client
    dstout = subprocess.check_output(['ss', '-it', 'dport = :{}'.format(local_port)]).decode('utf-8')
    srcout = subprocess.check_output(['ss', '-it', 'sport = :{}'.format(local_port)]).decode('utf-8')

    print('talking to', request.remote_addr)
    print('forwarded for', request.headers.get('X-Forwarded-For', request.remote_addr))
    print('dst', extractrtt(dstout))
    print('src', extractrtt(srcout))

    content = cache.get(name)
    if content != -1:
        print('cache hit!')
        return content
    else:
        print('cache miss')
        response = urllib.request.urlopen('http://{}:{}/wiki/{}'.format(origin_server_ip, origin_server_port, name))
        page_content = response.read()
        return page_content


@app.route('/msmt/<name>')
def servemeasurement(name: str):
    """Serves requests for TCP RTTs of a given client

    name (str) the IP address of the client whose RTT with this server is being requested
    """
    pass  # TODO


@app.route('/<path:path>')
def catch_all(path):
    logging.debug('Request for unknown path {}'.format(path))
    page_content = urllib.request.urlopen('http://{}:{}/{}'.format(origin_server_ip, origin_server_port, path)).read()
    return page_content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs an HTTP server on a given port that serves a stub of Wikipedia')
    parser.add_argument('-p', required=True, type=int, help='the port the HTTP server will bind to')
    parser.add_argument('-o', required=True, help='the name of the origin server for the CDN')
    args = parser.parse_args()

    origin_server_ip = args.o
    local_port = args.p
    fillcache()
    app.run(host='0.0.0.0', port=args.p)

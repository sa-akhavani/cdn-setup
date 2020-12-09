#!/usr/bin/python3
import argparse
import subprocess

from flask import Flask
import requests
import cache

# ec2-18-207-254-152.compute-1.amazonaws.com will be provided from the command line
# should resolve to '18.207.254.152'
import fileifc

local_port = None
origin_server_ip = None
origin_server_port = 8080
cache_memory_limit = 10485760

CACHEFN = 'requested.json'

app = Flask(__name__)
cache = cache.Cache(cache_memory_limit)


def fillcache():
    """Fills the cache with the most popular pages by reading that data from a config file on the system"""
    rdr = fileifc.Reader(CACHEFN)
    objlist = rdr.read()

    for obj in objlist:
        cache.put(obj['article'], obj['body'], alreadycompressed=True)


@app.route('/wiki/<name>')
def servearticle(name: str):
    """Serves requests for Wikipedia articles

    name (str) the article title being requested
    """
    # get the output of doing one of these commands and use the rtt field to store measurement data for this client
    print(subprocess.check_output(['ss', '-it']).decode('utf-8'))
    strout = subprocess.check_output(['ss', '-it', 'dport = :{}'.format(local_port)]).decode('utf-8')
    strout.split()
    print(subprocess.check_output(['ss', '-it', 'sport = :{}'.format(local_port)]).decode('utf-8'))

    content = cache.get(name)
    if content != -1:
        print('cache hit!')
        return content
    else:
        print('cache miss')
        page_content = requests.get('http://{}:{}/wiki/{}'.format(origin_server_ip, origin_server_port, name)).content
        return page_content


@app.route('/msmt/<name>')
def servemeasurement(name: str):
    """Serves requests for TCP RTTs of a given client

    name (str) the IP address of the client whose RTT with this server is being requested
    """
    pass  # TODO


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs an HTTP server on a given port that serves a stub of Wikipedia')
    parser.add_argument('-p', required=True, type=int, help='the port the HTTP server will bind to')
    parser.add_argument('-o', required=True, help='the name of the origin server for the CDN')
    args = parser.parse_args()

    origin_server_ip = args.o
    local_port = args.p
    app.run(host='0.0.0.0', port=args.p)

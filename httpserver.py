#!/usr/bin/python3
import argparse
from flask import Flask
import requests
import cache

origin_server_ip = '18.207.254.152'
origin_server_port = 8080
cache_memory_limit = 10485760

app = Flask(__name__)
cache = cache.Cache(cache_memory_limit)


@app.route('/wiki/<name>')
def test(name):
    content = cache.get(name)
    if content != -1:
        print('cache hit!')
        return content
    else:
        print('cache miss')
        page_content = requests.get('http://{}:{}/wiki/{}'.format(origin_server_ip, origin_server_port, name)).content
        cache.put(name, page_content)
        return page_content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs an HTTP server on a given port that serves a stub of Wikipedia')
    parser.add_argument('-p', required=True, type=int, help='the port the HTTP server will bind to')
    parser.add_argument('-o', required=True, help='the name of the origin server for the CDN')
    args = parser.parse_args()

    origin_server_ip = args.o  # TODO test that this works
    app.run(host='0.0.0.0', port=args.p)

from flask import Flask
import requests
import cache
import sys

origin_server_ip = '18.207.254.152'
origin_server_port = 8080
cache_memory_limit = 10485760

app = Flask(__name__)
cache = cache.LRUCache(cache_memory_limit)

@app.route('/wiki/<name>')
def test(name):
    content = cache.get(name)
    if  content != -1:
        print('cache hit!')
        return content
    else:
        print('cache miss')
        page_content = requests.get('http://{}:{}/wiki/{}'.format(origin_server_ip, origin_server_port, name)).content
        cache.put(name, page_content)
        return page_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000)

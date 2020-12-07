import requests

from fileifc import Writer, Reader
import zlib


def e2everify():
    w = Writer('test.json')
    content = requests.get('http://ec2-18-207-254-152.compute-1.amazonaws.com:8080/wiki/Main_Page').content
    w.write('Main_Page', zlib.compress(content))
    w.close()

    r = Reader('test.json')
    obj = r.read()

    extracted = zlib.decompress(obj[0]['body'])

    print(content == extracted)


if __name__ == '__main__':
    e2everify()

from fileifc import Writer, Reader
import zlib


def write():
    w = Writer('test.json')
    content = open('wikipediajapanese.html', 'r').read()
    w.write('Main_Page', zlib.compress(content.encode('utf-8')))
    w.write('Page_2', b'\xff\xaa\nfdsa')
    w.close()


def read():
    r = Reader('test.json')
    obj = r.read()

    print(obj[0]['article'])
    print(zlib.decompress(obj[0]['body']))


def e2everify():
    w = Writer('test.json')
    content = open('Main_Page.html', 'r').read()
    encoded = content.encode('utf-8')
    w.write('Main_Page', zlib.compress(encoded))
    w.close()

    r = Reader('test.json')
    obj = r.read()

    extracted = zlib.decompress(obj[0]['body'])
    decoded = extracted.decode('utf-8')

    print(encoded == extracted)
    print(content == decoded)


if __name__ == '__main__':
    e2everify()

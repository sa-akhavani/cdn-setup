import json
import base64


class Writer:
    """
    Writes article names and their zlib-compressed bodies to a json file

    Using files like this allows us to fetch articles from the server only once, then deploy this file to each replica
    server so that every caching http server can quickly fill their cache.
    """
    def __init__(self, fn):
        self.fp = open(fn, 'w')
        self.output = []

    def write(self, article: str, body: bytes):
        """
        Stores the given article name and its body to be written later. The body is converted to a base64 string so that
        JSON can serialize it
        """
        jsonobj = dict()
        jsonobj['article'] = article
        jsonobj['body'] = base64.b64encode(body).decode('utf-8')
        self.output.append(jsonobj)

    def close(self):
        """Writes all the article/body pairs to the file and closes the file"""
        json.dump(self.output, self.fp)
        self.fp.close()


class Reader:
    """
    Reads article names and their zlib-compressed bodies from a json file
    """
    def __init__(self, fn):
        self.fp = open(fn, 'rb')

    def read(self):
        """Reads the json file to a list of dicts. All the base64 encoded bodies are decoded and the final list of dicts
        is returned
        """
        objlist = json.load(self.fp)
        for obj in objlist:
            obj['body'] = base64.b64decode(obj['body'])

        return objlist

    def close(self):
        self.fp.close()

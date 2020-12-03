import sys
import unittest

sys.path.append('..')
import dnsserver


class TestDNS(unittest.TestCase):
    def testconvertdomain(self):
        fromquery = (b'cs5700cdn', b'example', b'com', b'')
        self.assertEqual(dnsserver.domain_cli2query('cs5700cdn.example.com'), fromquery)
        self.assertEqual(dnsserver.domain_cli2query('cs5700cdn.example.com.'), fromquery)


if __name__ == '__main__':
    unittest.main()

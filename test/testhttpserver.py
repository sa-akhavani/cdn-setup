import unittest
import httpserver


class HTTPServerTest(unittest.TestCase):
    def test_parseSsCommand(self):
        ssval = """State   Recv-Q    Send-Q        Local Address:Port        Peer Address:Port     
ESTAB   0         0                 127.0.0.1:40000          127.0.0.1:44010    
	 cubic wscale:7,7 rto:204 rtt:0.015/0.007 ato:40 mss:32768 pmtu:65535 rcvmss:536 advmss:65483 cwnd:10 bytes_received:348 segs_out:1 segs_in:3 data_segs_in:1 send 174762.7Mbps lastsnd:4668 lastrcv:36 lastack:36 pacing_rate 349525.3Mbps rcv_space:65483 rcv_ssthresh:65483 minrtt:0.015
"""

        self.assertEqual('0.015', httpserver.extractrtt(ssval))


if __name__ == '__main__':
    unittest.main()

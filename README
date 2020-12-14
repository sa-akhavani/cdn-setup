# README

### High-level approach
DNS server maintains one measurement value for every replica server per client. All values are initialized to -1.
The first six times a client connects the DNS server, they will be sent to each replica server in order. Each time, the HTTP server
will measure the RTT between them and the client and make it available to the DNS server at a unique path. Then, when the DNS server has
measurements between that client and all replicas, it directs the client to the replica with the lowest measured latency.

The HTTP server maintains a cache (implemented as a hash table) of approximately 10MB of the most popular pages stored at the origin 
server. These pages are compressed with zlib to fit more data into the cache. If a client requests a path that is in the cache, the 
replica server uncompresses it and returns it. Otherwise, it requests the page from the origin server and returns it to the client.

### Performance-enhancing technqiues
1) Passively measure RTTs from 3-way handshake on the HTTP server. DNS server requests these to find best mappings for each new client  
2) Maintain a hashmap of the most popular article titles to the associated article bodies  
3) Compress the article bodies to fit more data into the cache  

### We faced three main problems in this assignment
1) How to efficiently create our cache at each replica? We could have had each replica send requests to the server, but then there would
be a long delay between the replica going up and when it could start responding to clients. In addition, this would put significant 
strain on the origin server. We decided instead that we would build a file containing the cache contents and deploy it with each replica.

2) How to store the cache contents in a file? A trivial approach would have been to use a format like JSON and store each article's
title and the entire article body together. But this would result in an enormous file that could not fit on the replica. We could
store the compressed article bodies in the file instead, but the compressed bodies are not human readable and thus unusable by JSON.
We could have designed our own file structure to handle this, but it felt like an unnecessary amount of work for a minor increase
in cache size. Our solution was to base64 encode the compressed article bodies, creating strings that can be encoded in JSON while 
still being smaller than the original articles. Thus, our cache is slightly less than 10MB once loaded into the replica, but we felt
comfortable taking that performance hit since the most popular articles were already in it.

3) How to passively measure RTT at the replicas? Ideally, we could measure the RTTs during the file transfer itself and report those, 
since that's the best indicator of performance, but the only tool we could find that does that is "ip tcp-metrics" which requires
sudo. Thus, we use the socket statistics tool, which will only give us the RTTs from the 3-way handshake, but which ultimately gives us 
a better metric of performance than active measurement or geographic mapping.

# Report

We started by developing our DNS server, which would initially just return the IP address of the origin server. To
minimize the amount of code we needed to write and test, we opted not to write our own DNS response parser and instead
leveraged dnspython's internal types. The initial DNS server was trivial to write once we understood dnspython's types
and the full server was only around 50 lines of code. We tested our DNS server by sending dig requests to it and seeing
that the IP address of the origin server was returned in the response. We (Ali and Anthony) pair-programmed to write the
DNS server.

For our HTTP server, we used the Flask library, since we had read about how easy it was to use; and it was easy! Our
initial HTTP server, which simply received requests for /wiki/<name> and fetched the article from the origin server, was
written in under 20 lines of code. We tested our HTTP server by sending it requests via wget. We pair-programmed to write
the HTTP server.

We then added a cache to our server. Our cache is simply a map that rejects additional put() operations once the total
size of all the values stored in it exceeds a given value (in this case, the  value is 10MB). Since the request
frequency for each piece of content follows a Zipf distribution, we decided not to implement any sort of cache
replacement, but rather to store the top most popular articles at each replica statically. We pair-programmed to write
this part.

In addition, our cache compresses all the data it stores using zlib. This increases the amount of data we can store
at each replica server without going over the 10MB quota. Integrating our cache into the HTTP server was trivial. Ali
wrote this part of the code.

To avoid having every replica server start with an empty cache and send requests for each article to the replica server, we
decided we would request all the articles once in our deploy script, store the data in a file, and deploy that to each replica
server. When the servers start up, they will read from that file to build their caches. 

We then decided on a format for this file and created an interface for reading and writing it. Our file format is a list of 
JSON objects, with each object containing a wikipedia article title and the zlib-compressed article body encoded in base64. 
The base64 encoding was necessary to stop JSON from encoding the article in unicode, which completely mangled the data upon 
recovery from the file. The data in the actual runtime cache is NOT encoded in base64, and this technique was only used to 
allow us to use JSON (a simple and familiar format).

This approach worked well enough, but the base64 encoding and aditional JSON brackets bloated the file. Thus, though we can store
around 135 compressed articles in our cache without going over the quota, 135 articles encoded in this file format will result in
an approximately 14MB file, which will not fit on the replicas. Thus, to use this file format, we take a minor hit to our cache
hit ratio. However, the resulting cache still holds more articles than it would if we had not compressed them (26 vs 95)

Another approach would have been to create our own binary file format, which stores the article title followed by its zlib
compressed article body. This would have required quite a bit more code and testing to ensure its correctness, but it would
have allowed us to store more data in our deployment file. 

Anthony wrote the file reader and writer, and we tested it by requesting /wiki/Main_Page from the origin server, encoding it 
in the JSON file, then reading it back from the file and ensuring that the retrieved message is the same as it was when it 
arrived from the origin server. 

After implementing these parts, we implemented a system that maps IPs to nearby replica servers. We discussed the method
and implementation together and Anthony wrote the code. The DNS server maintains one measurement value for every replica server 
per client. All values are initialized to -1. The first six times a client connects the DNS server, they will be sent to each 
replica server in order. Each time, the HTTP server will passively measure the RTT between them and the client using the 
socket-statistics command and make it available to the DNS server at a unique path /msmt/<client_ip>. 

Once the DNS server has the measured RTTs between one client and all replicas, it directs the client to the replica with the lowest 
measured latency. Even after the DNS server has these measurements, the HTTP servers still record new measurements and the DNS server
requests them to ensure that the latency data is as up-to-date as possible.

We decided to build our mapping using passive RTT measurement over active measurement or geolocation because passive 
measurement gives the best indication of end-to-end performance. Active measurement is limited in that a client may not respond to 
pings, so the only data available is the latency between the last responding host in a traceroute. Geolocation is susceptible to 
errors, for one thing, and communication in the Internet does not always take the shortest physical path anyway.

A better approach to passive RTT measurement would have been to use the ip tcp-metrics command, which records and caches RTTs. We could
have used this to obtain the RTTs during the data transfer, rather than just the 3-way handshake, which is all socket-statistics is able
to get. This would give us a much better latency metric and would allow us to send the article body right away instead of taking 
a little extra time to record the RTTs. However, ip tcp-metrics requires elevated privileges, and in our testing, the RTTs we obtained
were more than sufficient to direct us to the fastest replica server.

The final part was the deploy scripts, deployCDN copies httpserver, cache, and prefetched cache data to all http servers. It
also copies dnsserver to the DNS server. runCDN runs the http server in all replicas and also runs the DNS server. All the servers are run
in the background, and their PIDs are stored in a file called pid.txt stopCDN stops all http servers and the dns server by killing the process
ID stored in pid.txt

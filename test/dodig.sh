#!/bin/bash

NS=192.168.198.131
port=40000
NAME=cs5700cdn.example.com
dig +short +time=2 +tries=1 -p $port @$NS $NAME | head -1

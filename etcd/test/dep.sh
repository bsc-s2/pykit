#!/bin/sh

yum install -y \
    docker \
    docker-python

# pip install docker-py

service docker start

docker pull quay.io/coreos/etcd:v2.3.7
# docker pull mysql:5.7.13

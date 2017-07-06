#!/bin/sh

yum install -y \
    docker-1.12.6 \
    python-docker-py-1.10.6 \

# pip install docker-py

service docker start

docker pull quay.io/coreos/etcd:v2.3.7
# docker pull mysql:5.7.13

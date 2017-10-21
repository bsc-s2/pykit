#!/bin/sh

yum install -y \
    docker-1.12.6 \

service docker start

docker pull quay.io/coreos/etcd:v2.3.7
# docker pull mysql:5.7.13

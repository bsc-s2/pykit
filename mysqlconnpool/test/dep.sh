#!/bin/sh

yum install -y \
    docker \
    docker-python

# pip install docker-py

service docker start

docker pull daocloud.io/mysql:5.7.13
# docker pull mysql:5.7.13

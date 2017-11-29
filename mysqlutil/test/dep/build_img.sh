#!/bin/sh

yum install -y docker

service docker start

docker pull daocloud.io/mysql:5.7.13

docker build --no-cache -t test-mysql:0.0.1 .

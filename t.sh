#!/bin/sh

# dependency:
#     yum install -y docker
#     yum install -y docker-python
#     # pip install docker-py
#     # service docker start
#
#     docker pull daocloud.io/mysql:5.7.13
#     # docker pull mysql:5.7.13

python2 -m unittest discover -v --failfast

# python2 -m test.test_jobq -v
# python2 -m test.test_jobq.TestProbe -v

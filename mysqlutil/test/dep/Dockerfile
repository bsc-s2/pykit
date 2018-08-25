FROM daocloud.io/mysql:5.7.13

COPY ./install_data.sh /docker-entrypoint-initdb.d/

RUN chmod a+x /docker-entrypoint-initdb.d/install_data.sh

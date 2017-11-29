
FROM daocloud.io/mysql:5.7.13

ENV WORK_PATH /usr/local/work

ENV AUTO_RUN_DIR /docker-entrypoint-initdb.d

ENV INIT_SQL init.sql

ENV INSTALL_DATA_SHELL install_data.sh

RUN mkdir -p $WORK_PATH

COPY ./$INIT_SQL $WORK_PATH/

COPY ./$INSTALL_DATA_SHELL $AUTO_RUN_DIR/

RUN chmod a+x $AUTO_RUN_DIR/$INSTALL_DATA_SHELL

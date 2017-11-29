#!/bin/bash
mysql -uroot -p$MYSQL_ROOT_PASSWORD <<EOF
source $WORK_PATH/$INIT_SQL;
EOF

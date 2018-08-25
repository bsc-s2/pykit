#!/bin/bash
mysql -uroot -p$MYSQL_ROOT_PASSWORD <<'EOF'
CREATE DATABASE IF NOT EXISTS `test`;

USE `test`;

CREATE TABLE IF NOT EXISTS `errlog` (

    `_id`     int(11)       NOT NULL  AUTO_INCREMENT,
    `autolvl` varchar(16)   NOT NULL,
    `service` varchar(32)   NOT NULL,
    `ip`      varchar(16)   NOT NULL,
    `level`   varchar(16)   NOT NULL,
    `time`    bigint        NOT NULL,
    `content` varchar(4096) NOT NULL,

    PRIMARY KEY  (`_id`),

    UNIQUE KEY `idx_service_ip__id` (`service`,`ip`, `_id`),
    UNIQUE KEY `idx_autolvl_service_ip__id` (`autolvl`,`service`,`ip`, `_id`),
    UNIQUE KEY `idx_time__id` (`time`, `_id`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

INSERT INTO `errlog` VALUES
    (1,  'stable', 'common0', '127.0.0.1', 'info',  '201706060600', 'bad request'),
    (2,  'stable', 'common0', '127.0.0.2', 'warn',  '201706060601', 'bad request'),
    (3,  'alpha',  'common0', '127.0.0.2', 'info',  '201706060602', 'bad request'),
    (4,  'alpha',  'common1', '127.0.0.3', 'info',  '201706060603', 'bad request'),
    (5,  'beta',   'common1', '127.0.0.4', 'error', '201706060604', 'bad request'),
    (6,  'stable', 'common2', '127.0.0.3', 'info',  '201706060605', 'bad request'),
    (7,  'stable', 'common4', '127.0.0.1', 'error', '201706060606', 'bad request'),
    (8,  'beta',   'common0', '127.0.0.1', 'info',  '201706060607', 'bad request'),
    (9,  'alpha',  'common2', '127.0.0.1', 'info',  '201706060608', 'bad request'),
    (10, 'alpha',  'common3', '127.0.0.3', 'warn',  '201706060609', 'bad request'),
    (11, 'beta',   'common1', '127.0.0.1', 'info',  '201706060610', 'bad request'),
    (12, 'stable', 'common0', '127.0.0.1', 'error', '201706060611', 'bad request'),
    (13, 'stable', 'common0', '127.0.0.2', 'info',  '201706060612', 'bad request'),
    (14, 'alpha',  'common1', '127.0.0.2', 'info',  '201706060613', 'bad request'),
    (15, 'stable', 'common2', '127.0.0.3', 'error', '201706060614', 'bad request'),
    (16, 'beta',   'common3', '127.0.0.4', 'error', '201706060615', 'bad request'),
    (17, 'alpha',  'common4', '127.0.0.1', 'info',  '201706060616', 'bad request'),
    (18, 'beta',   'common0', '127.0.0.1', 'info',  '201706060617', 'bad request'),
    (19, 'stable', 'common0', '127.0.0.2', 'warn',  '201706060618', 'bad request'),
    (20, 'beta',   'common0', '127.0.0.1', 'info',  '201706060619', 'bad request'),
    (21, 'stable', 'common2', '127.0.0.4', 'warn',  '201706060620', 'bad request'),
    (22, 'stable', 'common1', '127.0.0.1', 'info',  '201706060621', 'bad request'),
    (23, 'alpha',  'common3', '127.0.0.2', 'error', '201706060622', 'bad request'),
    (24, 'alpha',  'common2', '127.0.0.2', 'info',  '201706060623', 'bad request'),
    (25, 'beta',   'common3', '127.0.0.2', 'error', '201706060624', 'bad request'),
    (26, 'beta',   'common3', '127.0.0.2', 'info',  '201706060625', 'bad request'),
    (27, 'alpha',  'common0', '127.0.0.3', 'warn',  '201706060626', 'bad request'),
    (28, 'stable', 'common1', '127.0.0.2', 'warn',  '201706060627', 'bad request'),
    (29, 'beta',   'common1', '127.0.0.1', 'info',  '201706060628', 'bad request'),
    (30, 'stable', 'common0', '127.0.0.3', 'info',  '201706060629', 'bad request'),
    (31, 'alpha',  'common1', '127.0.0.1', 'error', '201706060630', 'bad request'),
    (32, 'stable', 'common0', '127.0.0.1', 'info',  '201706060631', 'bad request');
EOF

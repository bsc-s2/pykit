#!/usr/bin/env python
# coding: utf-8

# https://dev.mysql.com/doc/refman/5.7/en/privileges-provided.html

# ALL [PRIVILEGES]                Synonym for “all privileges”    Server administration
# ALTER                           Alter_priv                      Tables
# ALTER ROUTINE                   Alter_routine_priv              Stored routines
# CREATE                          Create_priv                     Databases, tables, or indexes
# CREATE ROUTINE                  Create_routine_priv             Stored routines
# CREATE TABLESPACE               Create_tablespace_priv          Server administration
# CREATE TEMPORARY TABLES         Create_tmp_table_priv           Tables
# CREATE USER                     Create_user_priv                Server administration
# CREATE VIEW                     Create_view_priv                Views
# DELETE                          Delete_priv                     Tables
# DROP                            Drop_priv                       Databases, tables, or views
# EVENT                           Event_priv                      Databases
# EXECUTE                         Execute_priv                    Stored routines
# FILE                            File_priv                       File access on server host
# GRANT OPTION                    Grant_priv                      Databases, tables, or stored routines
# INDEX                           Index_priv                      Tables
# INSERT                          Insert_priv                     Tables or columns
# LOCK TABLES                     Lock_tables_priv                Databases
# PROCESS                         Process_priv                    Server administration
# PROXY                           See proxies_priv table          Server administration
# REFERENCES                      References_priv                 Databases or tables
# RELOAD                          Reload_priv                     Server administration
# REPLICATION CLIENT              Repl_client_priv                Server administration
# REPLICATION SLAVE               Repl_slave_priv                 Server administration
# SELECT                          Select_priv                     Tables or columns
# SHOW DATABASES                  Show_db_priv                    Server administration
# SHOW VIEW                       Show_view_priv                  Views
# SHUTDOWN                        Shutdown_priv                   Server administration
# SUPER                           Super_priv                      Server administration
# TRIGGER                         Trigger_priv                    Tables
# UPDATE                          Update_priv                     Tables or columns
# USAGE                           Synonym for “no privileges”     Server administration

privileges = {
        'ALL':                      ('ALL',                     ),
        'ALTER':                    ('ALTER',                   ),
        'ALTER_ROUTINE':            ('ALTER ROUTINE',           ),
        'CREATE':                   ('CREATE',                  ),
        'CREATE_ROUTINE':           ('CREATE ROUTINE',          ),
        'CREATE_TABLESPACE':        ('CREATE TABLESPACE',       ),
        'CREATE_TEMPORARY_TABLES':  ('CREATE TEMPORARY TABLES', ),
        'CREATE_USER':              ('CREATE USER',             ),
        'CREATE_VIEW':              ('CREATE VIEW',             ),
        'DELETE':                   ('DELETE',                  ),
        'DROP':                     ('DROP',                    ),
        'EVENT':                    ('EVENT',                   ),
        'EXECUTE':                  ('EXECUTE',                 ),
        'FILE':                     ('FILE',                    ),
        'GRANT_OPTION':             ('GRANT OPTION',            ),
        'INDEX':                    ('INDEX',                   ),
        'INSERT':                   ('INSERT',                  ),
        'LOCK_TABLES':              ('LOCK TABLES',             ),
        'PROCESS':                  ('PROCESS',                 ),
        'PROXY':                    ('PROXY',                   ),
        'REFERENCES':               ('REFERENCES',              ),
        'RELOAD':                   ('RELOAD',                  ),
        'REPLICATION_CLIENT':       ('REPLICATION CLIENT',      ),
        'REPLICATION_SLAVE':        ('REPLICATION SLAVE',       ),
        'SELECT':                   ('SELECT',                  ),
        'SHOW_DATABASES':           ('SHOW DATABASES',          ),
        'SHOW_VIEW':                ('SHOW VIEW',               ),
        'SHUTDOWN':                 ('SHUTDOWN',                ),
        'SUPER':                    ('SUPER',                   ),
        'TRIGGER':                  ('TRIGGER',                 ),
        'UPDATE':                   ('UPDATE',                  ),
        'USAGE':                    ('USAGE',                   ),
}

# set direct map

for k, v in privileges.items():
    privileges[v[0]] = v

# predefined shortcuts

privileges.update({
        'replicator': (  privileges["REPLICATION_CLIENT"]
                       + privileges["REPLICATION_SLAVE"]
                       + privileges["SELECT"]
        ),
        'monitor':    (  privileges["SELECT"]
        ),
        'business':   (  privileges["CREATE"]
                       + privileges["DROP"]
                       + privileges["REFERENCES"]
                       + privileges["ALTER"]
                       + privileges["DELETE"]
                       + privileges["INDEX"]
                       + privileges["INSERT"]
                       + privileges["SELECT"]
                       + privileges["UPDATE"]
        ),
        'readwrite':  (  privileges["DELETE"]
                       + privileges["INSERT"]
                       + privileges["SELECT"]
                       + privileges["UPDATE"]
        ),
})

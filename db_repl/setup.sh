#!/bin/bash

pg_ctl stop -D /var/lib/postgresql/data
rm -rf /var/lib/postgresql/data/*
sleep 30
pg_basebackup -R -h $DB_HOST -U $DB_REPL_USER -D /var/lib/postgresql/data -P
sleep 5
pg_ctl start -D /var/lib/postgresql/data

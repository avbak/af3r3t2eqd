#!/bin/bash
echo "host replication $DB_REPL_USER 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
psql -c "CREATE DATABASE $DB_DATABASE OWNER $DB_USER;"
psql -d $DB_DATABASE -a -f /docker-entrypoint-initdb.d/00_init.sql
psql -c "CREATE USER $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';"
psql -d $DB_DATABASE -c "ALTER TABLE phones OWNER TO $DB_USER;"
psql -c $DB_DATABASE -c "ALTER TABLE emails OWNER TO $DB_USER;"
psql -c "SELECT pg_reload_conf();"

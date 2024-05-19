#!/bin/bash

echo "host replication $DB_REPL_USER 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
psql -c "ALTER SYSTEM SET log_replication_commands TO 'on';"
psql -c "ALTER SYSTEM SET archive_mode TO 'on';"
psql -c "ALTER SYSTEM SET archive_command TO 'cp %p /postgres_archive/%f';"
psql -c "ALTER SYSTEM SET max_wal_senders TO 10;"
psql -c "ALTER SYSTEM SET wal_level TO 'replica';"
psql -c "ALTER SYSTEM SET wal_log_hints TO 'on';"
psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
psql -c "CREATE DATABASE $DB_DATABASE OWNER $DB_USER;"
sleep 5
psql -d $DB_DATABASE -a -f /var/lib/postgresql/00_init.sql
sleep 5
psql -c "CREATE USER $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';"
psql -d $DB_DATABASE -c "ALTER TABLE phones OWNER TO $DB_USER;"
psql -d $DB_DATABASE -c "ALTER TABLE emails OWNER TO $DB_USER;"
psql -c "SELECT pg_reload_conf();"

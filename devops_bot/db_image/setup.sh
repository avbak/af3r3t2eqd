#!/bin/bash
mkdir /var/lib/postgresql/data/archive
chown postgres:postgres /var/lib/postgresql/data/archive/
echo "host replication $DB_REPL_USER 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
psql -c "CREATE DATABASE $DB_DATABASE;"
psql -d $DB_DATABASE -a -f /docker-entrypoint-initdb.d/00_init.sql
psql -c "CREATE USER $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';"
psql -c "ALTER SYSTEM SET log_replication_commands TO 'on';"
psql -c "ALTER SYSTEM SET archive_mode TO 'on';"
psql -c "ALTER SYSTEM SET archive_command TO 'cp %p /var/lib/postgresql/data/archive/%f';"
psql -c "ALTER SYSTEM SET max_wal_senders TO 10;"
psql -c "ALTER SYSTEM SET wal_level TO 'replica';"
psql -c "ALTER SYSTEM SET wal_log_hints TO 'on';"
psql -c "SELECT pg_reload_conf();"

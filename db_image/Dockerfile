FROM postgres:16-bookworm
COPY ./setup.sh /docker-entrypoint-initdb.d/setup.sh
RUN chmod +x /docker-entrypoint-initdb.d/setup.sh
COPY ./00_init.sql /docker-entrypoint-initdb.d/00_init.sql

FROM postgres:16-bookworm
RUN mkdir /postgres_archive && chown postgres:postgres /postgres_archive
COPY ./setup.sh /docker-entrypoint-initdb.d/setup.sh
RUN chmod +x /docker-entrypoint-initdb.d/setup.sh
COPY ./00_init.sql /var/lib/postgresql/00_init.sql

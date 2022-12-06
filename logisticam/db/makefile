# Change these values only if you are having problems
#SHELL=/bin/bash
PP=cpp
PPFLAGS=-E -C -P

MERGE_TOOL=${shell git config --get merge.tool || echo meld}

# These values must match those in schema_common.sql
MYSQL=mysql
SQLITE=sqlite


# Default rule
.PHONY: all
all: mysql sqlite

# Schema rules
mariadb: mysql

mysql: schema_mysql.sql
schema_mysql.sql: DB = ${MYSQL}
schema_mysql.sql: .gen-schema

sqlite: schema_sqlite.sql
schema_sqlite.sql: DB = ${SQLITE}
schema_sqlite.sql: .gen-schema

.gen-schema: DB_PREFIX ?= schema_${DB}
.gen-schema: schema_common.sql
	${PP} ${PPFLAGS} -D ${call toupper,${DB}} -o ${DB_PREFIX}_auto.sql schema_common.sql
	@cp -i ${DB_PREFIX}_auto.sql ${DB_PREFIX}_merge.sql
	${MERGE_TOOL} --auto-merge ${DB_PREFIX}.sql ${DB_PREFIX}_merge.sql ${DB_PREFIX}_auto.sql
	@mv -i ${DB_PREFIX}_merge.sql ${DB_PREFIX}.sql
	@rm ${DB_PREFIX}_auto.sql

clean-schema:
	@rm -f schema_${MYSQL}_*.sql
	@rm -f schema_${SQLITE}_*.sql

.PHONY: mariadb mysql sqlite .gen-schema clean-schema


# Creation rules
create: create-mysql dista.sqlite

create-mariadb: create-mysql

create-mysql: NAME ?= dista
create-mysql: schema_mysql.sql
	echo "CREATE DATABASE ${NAME}; USE ${NAME};" \
	| cat - schema_${MYSQL}.sql statistics.sql \
	| mysql -u root -p

clean-mysql: NAME ?= dista
clean-mysql:
	mysql -u root -p -e "DROP DATABASE ${NAME};"

%.sqlite: schema_sqlite.sql
	sqlite3 $@ < schema_${SQLITE}.sql
	sqlite3 $@ < statistics.sql

clean-sqlite:
	@if [ -e *.sqlite ] ; then rm -i *.sqlite ; fi

.PHONY: create create-mariadb create-mysql clean-mysql clean-sqlite clean

# Clean everything
.PHONY: clean
clean: clean-schema clean-sqlite


# Custom utility functions
tolower = $(shell echo ${1} | tr '[:upper:]' '[:lower:]')
toupper = $(shell echo ${1} | tr '[:lower:]' '[:upper:]')


#!/usr/bin/env bash

/code/scripts/wait-for-it.sh $POSTGRES_HOST_DB:5432
PGPASSWORD=qwe123 psql -h $POSTGRES_HOST_DB -U emirnavruzov -d tp_aiomicro < /code/scripts/setup.sql

python -m async_orm.main
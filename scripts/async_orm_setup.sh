#!/usr/bin/env bash

/code/scripts/wait-for-it.sh db:5432
PGPASSWORD=qwe123 psql -h db -U emirnavruzov -d tp_aiomicro < /code/scripts/setup.sql

python -m async_orm.main
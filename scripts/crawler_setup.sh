#!/usr/bin/env bash

/code/scripts/wait-for-it.sh $POSTGRES_HOST_DB:5432
/code/scripts/wait-for-it.sh --timeout=0 $HOST_RABBITMQ:5672
/code/scripts/wait-for-it.sh --timeout=0 $HOST_ES:9200

python -m crawler.main
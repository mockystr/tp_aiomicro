#!/usr/bin/env bash

/code/scripts/wait-for-it.sh db:5432
/code/scripts/wait-for-it.sh rabbitmq:5672

python -m aioserver.server
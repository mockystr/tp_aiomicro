#!/usr/bin/env bash

/code/scripts/wait-for-it.sh db:5432
/code/scripts/wait-for-it.sh --timeout=0 rmq:5672
/code/scripts/wait-for-it.sh --timeout=0 es:9200

python -m crawler.main
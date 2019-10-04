#!/usr/bin/env bash

/code/scripts/wait-for-it.sh db:5432
/code/scripts/wait-for-it.sh rmq:5672
/code/scripts/wait-for-it.sh es:9200

python -m crawler.main
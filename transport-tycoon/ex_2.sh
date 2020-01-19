#!/bin/bash
set -euxo pipefail
ROUTE=$1
python3 ex_2.py $ROUTE | tee $ROUTE.2.log
python3 trace.py $ROUTE.2.log > $ROUTE.2.trace

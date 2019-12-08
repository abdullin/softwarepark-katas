#!/bin/bash
set -euxo pipefail
ROUTE=$1
python3 ex_2.py $ROUTE > $ROUTE.log
python trace.py $ROUTE.log > $ROUTE.trace

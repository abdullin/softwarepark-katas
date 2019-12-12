#!/bin/bash
set -euxo pipefail
ROUTE=$1
python3 ex_2.py $ROUTE > $ROUTE.2.log
python trace.py $ROUTE.2.log > $ROUTE.2.trace

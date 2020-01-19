#!/bin/bash
set -euxo pipefail
ROUTE=$1
go run ex_3.go $ROUTE | tee  $ROUTE.3.log
python3 trace.py $ROUTE.3.log > $ROUTE.3.trace

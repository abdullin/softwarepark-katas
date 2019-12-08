#!/bin/bash
set -euxo pipefail
ROUTE=$1
go run ex_3.go $ROUTE > $ROUTE.log
python trace.py $ROUTE.log > $ROUTE.trace

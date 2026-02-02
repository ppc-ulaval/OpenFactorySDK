#!/usr/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# api
docker build -t ofa-api $SCRIPT_DIR/api
#monitoring
docker build -t ivac-tool-monitoring-app $SCRIPT_DIR/monitoring/ivac
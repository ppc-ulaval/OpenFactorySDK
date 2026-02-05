#!/usr/bin/bash
docker compose -f openfactory/virtual/ivac/docker-compose.yml down
ofa device down openfactory/devices/ivac.yml

dashboard/down_dashboard.sh
openfactory/apps/down-apps.sh

/usr/local/bin/teardown.sh

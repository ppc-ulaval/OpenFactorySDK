#!/usr/bin/bash

/usr/local/bin/spinup.sh

#setup virtual devices
ofa device up openfactory/devices/ivac.yml
docker compose -f openfactory/virtual/ivac/docker-compose.yml up -d


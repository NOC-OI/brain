#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..
if [ "$EUID" -ne 0 ]
    then echo "This script must be run as root, exiting"
    exit
fi
source .env
export INTERNAL_SERVICE_SECRET
curl -H "Authorization: Bearer $INTERNAL_SERVICE_SECRET" -X GET http://localhost:8082/destroy > /dev/null 2>&1
docker compose down

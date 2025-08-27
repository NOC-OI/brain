#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..
if [ "$EUID" -ne 0 ]
    then echo "This script must be run as root, exiting"
    exit
fi
docker compose up

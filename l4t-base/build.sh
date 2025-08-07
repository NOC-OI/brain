#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
./download-libs.sh
docker buildx build -t brain/l4t-base:j62-r36.4-0 ./

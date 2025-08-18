#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
if [ -z "$(docker images -q docker-repo.bodc.me/oceaninfo/l4t-base:j62-r36.4-1 2> /dev/null)" ]; then
    if [ -d "l4t-base-j62-r36.4-1" ]; then
        ./l4t-base-j62-r36.4-1/build.sh
    else
        wget https://github.com/NOC-OI/l4t-base/archive/refs/tags/j62-r36.4-1.zip
        unzip j62-r36.4-1.zip
        rm j62-r36.4-1.zip
        ./l4t-base-j62-r36.4-1/build.sh
    fi
else
    echo "docker-repo.bodc.me/oceaninfo/l4t-base:j62-r36.4-1 available locally, skipping build of base container."
fi
./vision/build.sh
./asea2-camera-if/build.sh
./dashboard/build.sh

#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
mkdir -p libs
cd libs

SHAOUT=($(cat *.whl | sha256sum -b))
SHAOUT=${SHAOUT[0]}
if [ "$SHAOUT" = "f1266c0b87a2281aac2ddee0e368994b2de9d9c49f2660e4e264c7bf983c28dd" ]; then
    echo "Libs OK, skipping download"
else
    echo "Libs hash ($SHAOUT) did not match expected output, redownloading data"
    rm -r *.whl
    wget https://pypi.jetson-ai-lab.io/jp6/cu126/+f/62a/1beee9f2f1470/torch-2.8.0-cp310-cp310-linux_aarch64.whl
    wget https://pypi.jetson-ai-lab.io/jp6/cu126/+f/907/c4c1933789645/torchvision-0.23.0-cp310-cp310-linux_aarch64.whl
fi


#wget https://repo.download.nvidia.com/jetson/dgpu-rm/pool/main/c/cuda-cudart/cuda-toolkit-12-6-config-common_12.6.68-1_all.deb
#wget https://repo.download.nvidia.com/jetson/dgpu-rm/pool/main/c/cuda-toolkit-12-6/cuda-toolkit-12-6_12.6.1-1_arm64.deb
#wget https://repo.download.nvidia.com/jetson/common/pool/main/c/cudnn/libcudnn9-cuda-12_9.3.0.75-1_arm64.deb
#wget https://repo.download.nvidia.com/jetson/common/pool/main/libc/libcublas/libcublas-12-6_12.6.1.4-1_arm64.deb
#wget https://repo.download.nvidia.com/jetson/common/pool/main/libc/libcufile/libcufile-12-6_1.11.1.6-1_arm64.deb
#wget https://repo.download.nvidia.com/jetson/common/pool/main/libc/libcufft/libcufft-12-6_11.2.6.59-1_arm64.deb
#wget https://repo.download.nvidia.com/jetson/common/pool/main/libc/libcufile/libcufile-dev-12-6_1.11.1.6-1_arm64.deb

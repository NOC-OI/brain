#!/bin/bash
rm -rf ./docker_output
mkdir ./docker_output
docker run -v ./docker_output:/app/out --runtime nvidia -it brain/asea2-camera-if:0.0

#!/bin/bash
source .env

cd ./flask/src

export INFERENCE_SOCKET=$INFERENCE_SOCKET
export DEFAULT_ADMIN_PASSWORD=$DEFAULT_ADMIN_PASSWORD
export JWT_SECRET=$JWT_SECRET

gunicorn -w 4 main:app -b 0.0.0.0

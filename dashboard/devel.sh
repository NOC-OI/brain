#!/bin/bash
source ../.env

cd ./flask/src

export INFERENCE_SOCKET=$INFERENCE_SOCKET
export DEFAULT_ADMIN_PASSWORD=$DEFAULT_ADMIN_PASSWORD
export JWT_SECRET=$JWT_SECRET
export MANAGEMENT_PANEL_BRANDING="BRAIN Development"
export UPLOAD_FOLDER="temp"

gunicorn -w 4 main:app -b 0.0.0.0

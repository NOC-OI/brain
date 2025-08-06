import uuid
import re
import os
from datetime import datetime
from flask import request
import random
import string
import secrets
import pika
import json
import jwt
import hashlib

jwt_secret = os.environ.get("JWT_SECRET", None)
rabbitmq_credentials = pika.PlainCredentials(os.environ.get("RABBITMQ_DEFAULT_USER", "brain"), os.environ.get("RABBITMQ_DEFAULT_PASS", "brain!"))
rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
rabbitmq_port = os.environ.get("RABBITMQ_PORT", 5672)

passwords = {}

admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", None)
if admin_password is None:
    print("[WARNING] DEFAULT_ADMIN_PASSWORD environment variable not set, using \"brain!\" as password for \"admin\" account. This is unsafe!")
    admin_password = "brain!"

hash_obj = hashlib.sha256()
hash_obj.update(admin_password.encode("utf-8"))
passwords["admin"] = hash_obj.digest()

if jwt_secret is None:
    print("[WARNING] JWT_SECRET environment variable not set, using default \"deadbeef\". This is unsafe!")
    jwt_secret = "deadbeef"
frontend_globals = {
        "brand": os.environ.get("MANAGEMENT_PANEL_BRANDING", "undefined")
    }

def check_password(username, password):
    if username in passwords.keys():
        hash_obj = hashlib.sha256()
        hash_obj.update(password.encode("utf-8"))
        return passwords[username] == hash_obj.digest()
    return False

def to_snake_case(str_in):
    str_out = re.sub("(?<!^)(?<![A-Z])(?=[A-Z]+)", "_", str_in).lower() # Prepend all strings of uppercase with an underscore
    str_out = re.sub("[^a-z0-9]", "_", str_out) # Replace all non-alphanumeric with underscore
    str_out = re.sub("_+", "_", str_out) # Clean up double underscores
    str_out = re.sub("(^_)|(_$)", "", str_out) # Clean up trailing or leading underscores
    return str_out

def session_data_to_jwt(session_data):
    session_data["nonce"] = secrets.token_urlsafe(16)
    return jwt.encode(session_data, jwt_secret, algorithm="HS256")

def get_app_frontend_globals():
    return frontend_globals

def get_session_info():
    raw_jwt = None
    bearer_token = request.headers.get("authorization")
    if not bearer_token is None:
        #print(bearer_token)
        bearer_token_components = bearer_token.split(" ")
        if len(bearer_token_components) > 1:
            if bearer_token_components[0].lower() == "bearer":
                raw_jwt = bearer_token_components[1]
    if raw_jwt is None:
        raw_jwt = request.cookies.get("jwt")
    if raw_jwt is None:
        return None
    else:
        try:
            return jwt.decode(raw_jwt, jwt_secret, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            return None

def publish_message(module = "all", body = None):
    queue = "brain_" + module + "_cmd"
    body = json.dumps(body)
    print(body + " => " + queue)
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, "/", rabbitmq_credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange="", routing_key=queue, body=body)
    connection.close()

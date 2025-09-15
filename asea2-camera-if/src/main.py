import cv2
import glob
import os
import time
import numpy as np
import io
import math
import aiormq
from aiormq.abc import DeliveredMessage
import asyncio
import json
import traceback
import datetime
import csv
import base64
import requests
import subprocess
from PIL import Image


# ASEA2 is a 3:2 aspect ratio sensor with a raw resolution of 5472, 3648, so we probably want one of the following resolutions:
# 2736  1824    Full Sensor (post bayer filter)
# 2560  1700    Common 2560 horizontal resolution
# 2160  1440    Common 1440 vertical resolution
# 1920  1280    Common 1920 horizontal resolution
# 1080  720     Common 720 vertical resolution
# 960   640     DVGA
# 480   320     HVGA
# 240   160     Half QVGA
output_resolution = (1920,1280)
fps = 2
aiormq_connection = None

#cpout = subprocess.run(["whoami"], capture_output=True, text=True)
#print("whoami:" + cpout.stdout)

rabbitmq_user = os.environ.get("RABBITMQ_DEFAULT_USER", "brain")
rabbitmq_pass = os.environ.get("RABBITMQ_DEFAULT_PASS", "brain!")
rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
rabbitmq_port = os.environ.get("RABBITMQ_PORT", 5672)
internal_service_secret = os.environ.get("INTERNAL_SERVICE_SECRET", "brain")
remote_dashboard = "http://brain-dashboard:8080"
aqmp_uri = "amqp://" + rabbitmq_user + ":" + rabbitmq_pass + "@" + str(rabbitmq_host) + ":" + str(int(rabbitmq_port)) + "/"

def log(line, level=1):
    dts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")
    ll = "INFO"
    if level>1:
        ll = "WARN"
    if level>2:
        ll = "ERR "
    if level>3:
        ll = "CRIT"
    print("[" + dts + "] [" + ll + "] " + line, flush=True) # The Nvidia container runtime has an outstanding issues with buffered output, so flush after every log line

async def publish_message(module = "all", body = None):
    global aiormq_connection
    try:
        queue = "brain_" + module + "_cmd"
        body = json.dumps(body).encode("utf-8")
        channel = await aiormq_connection.channel()
        queue_declaration = await channel.queue_declare(queue)
        await channel.basic_publish(exchange="", routing_key=queue, body=body)
    except Exception:
        log("Could not connect to AMQP!", 3)
        log(traceback.format_exc(), 3)

#def set_nfs_server(resource_uri):
 #   global nfs_resource
 #   log("Setting NFS server " + resource_uri)
 #   nfs_resource = libnfs.NFS(resource_uri)

async def send_frame(frame_path):
    width = 5472
    height = 3648

    with open(frame_path, "rb") as fh:
        raw_buf = fh.read()
        raw_arr = np.ndarray(shape=(height,width),dtype=np.uint16, buffer=raw_buf)

    float_arr = np.power(raw_arr.astype(np.float32) / float(2 ** 16), 0.5)
    raw_img = (float_arr * (2 ** 16)).astype(np.uint16)
    img = cv2.cvtColor(raw_img, cv2.COLOR_BayerRGGB2BGR)
    img = cv2.resize(img, output_resolution)
    img = (img/256).astype('uint8')
    status,img_str = cv2.imencode("frame.jpg", img)
    if status == False:
        log("Error encoding frame!")
    else:
        obj_pack = {
                "cmd": "infer_frame",
                "image_data": base64.b64encode(img_str).decode("utf-8")
            }
        await publish_message("vision", obj_pack)
        log("Published frame!")



#channel.basic_consume(queue="brain_asea2_camera_if_cmd", auto_ack=True, on_message_callback=cmd_callback)


async def on_cmd(message):
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    log(f" [x] Received message {message!r}")
    log(f"Message body is: {message.body!r}")
    log("Before sleep!")
    await asyncio.sleep(5)   # Represents async I/O operations
    log("After sleep!")


async def cmd_loop_fun():
    global aiormq_connection
    # Perform connection
    aiormq_connection = None
    while aiormq_connection is None:
        try:
            log("Connecting to RabbitMQ server at " + aqmp_uri)
            aiormq_connection = await aiormq.connect(aqmp_uri)
        except aiormq.exceptions.IncompatibleProtocolError:
            log("RabbitMQ protocol error - Has the server fully booted?")
            aiormq_connection = None
            await asyncio.sleep(1)
        except aiormq.exceptions.AMQPConnectionError:
            log("Could not connect to RabbitMQ")
            aiormq_connection = None
            await asyncio.sleep(1)

    channel = await aiormq_connection.channel()
    queue_declaration = await channel.queue_declare("brain_asea2_camera_if_cmd")
    log("Connected to RabbitMQ server!")
    consume_ok = await channel.basic_consume(queue_declaration.queue, on_cmd, no_ack=True)

async def get_config():
    while True:
        try:
            url = remote_dashboard + "/api/v1/config"
            ret = requests.get(url, headers={"Content-type": "application/json"})
            return ret.json()
        except Exception:
            log("Could not get config, trying again")
            await asyncio.sleep(1)

async def set_nfs_resource(endpoint):
    mounted = False

    response = requests.post("http://host.docker.internal:8082/mount", headers={"Authorization": "Bearer {}".format(internal_service_secret)}, data={"resource": endpoint})
    if response.ok:
        while not mounted:
            await asyncio.sleep(1)
            response = requests.get("http://host.docker.internal:8082/status")
            if response.ok:
                if response.json()["mounted"]:
                    log("Mounted NFS endpoint: " + response.json()["endpoint"])
                    mounted = True
    else:
        log(response.text)
        raise requests.exceptions.HTTPError("Could not mount using helper service", response)

async def frame_loop_fun():
    global aiormq_connection
    last_frame = None

    config = await get_config()
    log("Got config!")
    app_specific_config = config["asea2-camera-if"]
    log(json.dumps(app_specific_config, indent=4))

    if "nfs_resource" in app_specific_config.keys():
        if app_specific_config["nfs_resource"] is None:
            log("Skipping mount of NFS resource as none defined")
        else:
            await set_nfs_resource(app_specific_config["nfs_resource"])
    else:
        log("Skipping mount of NFS resource as none defined")

    while True:
        if aiormq_connection is not None:
            try:
                list_of_csv = glob.glob("/mnt/nfs_cam/*.csv")
                #nfs.open('/foo-test', mode='r').read()

                #log("Scanning NFS")
                #dir_listing = nfs_resource.listdir(".")
                #log("Resources:")
                #for ent in nfs_resource.listdir("."):
                #    if ent in ['.', '..']:
                #        continue
                #    st = nfs.lstat(ent)
                #    log(str(ent))
                #    log(str(st))

                if len(list_of_csv) == 0:
                    log("No csvfile!", 1)
                else:
                    latest_csv = max(list_of_csv, key=os.path.getmtime)
                    with open(latest_csv, "rb") as fh:
                        header_row = fh.readline().decode().strip('\n')
                        first_line = fh.readline().decode().strip('\n')
                        fh.seek(0, os.SEEK_END)
                        if fh.tell() > (len(header_row) + len(first_line)):
                            fh.seek(-len(first_line)-16, os.SEEK_END)  # Move the cursor back a bit from the start, just a tad more than the length of the first row
                        else:
                            fh.seek(len(header_row))
                        partial_row = fh.readline().decode().strip('\n')
                        last_row = fh.readline().decode().strip('\n')
                    csv_string = header_row + "\n" + last_row
                    #log(csv_string)

                    fh = io.StringIO(csv_string)
                    reader = csv.DictReader(fh)
                    last_row = None
                    for row in reader:
                        last_row = row
                    if last_row is not None:
                        filename = "/mnt/nfs_cam/" + last_row["filename"][len("/media/images/"):]
                        filename = os.path.abspath(filename)
                        if filename != last_frame:
                            last_frame = filename
                            await send_frame(filename)

                await asyncio.sleep(0.1)

            except Exception:
                log(traceback.format_exc(), 3)
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

async def main():
    await asyncio.gather(asyncio.create_task(frame_loop_fun()), asyncio.create_task(cmd_loop_fun()))
    #await asyncio.gather(asyncio.create_task(frame_loop_fun()))

asyncio.run(main())







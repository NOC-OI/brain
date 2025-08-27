#!/bin/python3
import os
import subprocess
import json
import datetime
import pika
import requests
import base64
import time
import io

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


log("Testing dependencies...")

def print_elem_ok(elem, ok):
    emo = "x"
    if ok:
        emo = u"\u2713"
    log(emo + " " + elem)

remote_dashboard = "http://brain-dashboard:8080"
status_msg = {"status": "booting"}

def update_status():
    for i in range(5): # Try 5 times, then give up
        try:
            url = remote_dashboard + "/api/v1/status"
            payload = json.dumps(status_msg)
            ret = requests.post(url, headers={"Authorization": "Bearer {}".format(os.environ.get("MANAGEMENT_PUSH_SECRET", "brain!")), "Content-type": "application/json"}, data=payload)
            log("Status update success: " + ret.content.decode("utf-8"))
            break
        except Exception:
            time.sleep(1)

update_status()

from PIL import Image, ImageDraw, ImageFont
print_elem_ok("Standard dependencies loaded", True)
import torch
print_elem_ok("PyTorch CUDA support", torch.cuda.is_available())
log("PyTorch Version: " + str(torch.__version__))
log("CUDA Version: " + str(torch.version.cuda))
log("CUDA Device: " + str(torch.cuda.get_device_name(0)))
import torchvision
print_elem_ok("Torchvision loaded", True)
import cv2
print_elem_ok("OpenCV loaded", True)
from ultralytics import YOLO
print_elem_ok("Ultralytics YOLO loaded", True)
#proc = subprocess.Popen(["mount", "-t", "nfs", os.environ.get("NFS_CAMERA_MOUNT", "192.168.1.1:/srv/nfs_cam"), "/mnt/nfs_cam"])
#proc.wait()
#print_elem_ok("Mounted NFS camera feed", True)

#print("Starting inference server") -- this will be a server at some point!

model = None

def set_new_model(modelname):
    global model
    model = None
    status_msg["status"] = "busy"
    status_msg["accepting_inference"] = False
    status_msg["model_loaded"] = None
    update_status()
    log("Downloading " + modelname + "...")
    url = remote_dashboard + "/api/v1/models/" + modelname
    response = requests.get(url)
    with open("cmodel.pt", mode="wb") as fh:
        fh.write(response.content)
    log("Loading YOLO model...")
    model = YOLO("cmodel.pt")
    log("Initialising YOLO model...")
    dummy_image = Image.new('RGB', (64, 64))
    results = model(dummy_image)
    status_msg["status"] = "ok"
    status_msg["accepting_inference"] = True
    status_msg["model_loaded"] = modelname
    update_status()
    print_elem_ok("New model " + modelname + " loaded", True)

def infer_frame(frame):
    global model
    if model is not None:
        results = model(frame)
        log("Plotting boxes...")
        img = frame.copy()
        imd = ImageDraw.Draw(img)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                raw_shape = box.xyxy.cpu().detach().numpy()
                shape = raw_shape.tolist()[0]
                detected_class_id = int(box.cls.cpu().item())
                detected_class = model.names[detected_class_id]
                confidence = box.conf.cpu().detach().numpy().tolist()[0]

                position = (shape[0], shape[1] - (58 + 8))
                if position[1] < 0:
                    position = (shape[0], shape[1])
                font = ImageFont.truetype("Roboto-Regular.ttf", 60)
                text = detected_class + ": " + str(int(confidence * 100)) + "%"
                text_bbox = imd.textbbox(position, text, font=font)
                imd.rectangle(shape, fill = None, outline = "red", width=8)
                imd.rectangle(text_bbox, fill="red", outline = "red", width=8)
                imd.text(position, text, font=font, fill="black")

                log(detected_class + " (conf " + str(confidence * 100) + "%) @ " + json.dumps(shape))
        return img
    else:
        log("Asked to infer frame with no model!")
        return None

def main():
    rabbitmq_credentials = pika.PlainCredentials(os.environ.get("RABBITMQ_DEFAULT_USER", "brain"), os.environ.get("RABBITMQ_DEFAULT_PASS", "brain!"))
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
    rabbitmq_port = os.environ.get("RABBITMQ_PORT", 5672)
    log("Connecting to RabbitMQ server at " + str(rabbitmq_host) + ":" + str(int(rabbitmq_port)))
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, int(rabbitmq_port), "/", rabbitmq_credentials, heartbeat=600, blocked_connection_timeout=300))

    channel = connection.channel()
    channel.queue_declare(queue="brain_vision_cmd")

    def cmd_callback(ch, method, properties, body):
        body_object = json.loads(body.decode("utf-8"))
        #log("CMD => " + json.dumps(body_object))
        log("CMD => " + body_object["cmd"])
        if body_object["cmd"] == "set_model":
            set_new_model(body_object["file"])
        elif body_object["cmd"] == "infer_frame":
            image_data = base64.b64decode(body_object["image_data"])
            image = Image.open(io.BytesIO(image_data))
            output_frame = infer_frame(image)
            #dts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H-%M-%S")
            #ofpath = "temp/" + dts + ".jpg"
            if output_frame is None:
                log("No model to run inference!")
            else:
                log("Transferring plot to dashboard")
                #output_frame.save(ofpath)
                url = remote_dashboard + "/api/v1/upload_frame"
                img_byte_arr = io.BytesIO()
                output_frame.save(img_byte_arr, format="JPEG")
                files = {"file": io.BytesIO(img_byte_arr.getvalue())}
                response = requests.post(url, files=files)
                #log(response.text)

    channel.basic_consume(queue="brain_vision_cmd", auto_ack=True, on_message_callback=cmd_callback)

    print_elem_ok("Vision worker ready for jobs", True)

    status_msg["status"] = "ok"
    status_msg["accepting_inference"] = False
    status_msg["model_loaded"] = None
    update_status()

    channel.start_consuming()


try:
    while True:
        try:
            main()
        except pika.exceptions.IncompatibleProtocolError:
            log("RabbitMQ protocol error - Has the server fully booted?", 2)
        except pika.exceptions.AMQPConnectionError:
            log("Could not connect to RabbitMQ", 3)
        except pika.exceptions.ConnectionClosedByBroker:
            log("RabbitMQ connection lost", 4)
        time.sleep(1)
except KeyboardInterrupt:
    log('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

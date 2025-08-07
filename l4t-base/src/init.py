#!/bin/python3
import os
import subprocess
import json
import datetime
import time

print("NOC L4T (Linux 4 Tegra) base image test script")
print("")

def print_elem_ok(elem, ok):
    emo = "x"
    if ok:
        emo = u"\u2713"
    print(emo + " " + elem)

from PIL import Image, ImageDraw
print_elem_ok("Standard dependencies loaded", True)
import torch
print_elem_ok("PyTorch CUDA support", torch.cuda.is_available())
print("    PyTorch Version: " + str(torch.__version__))
print("    CUDA Version: " + str(torch.version.cuda))
print("    CUDA Device: " + str(torch.cuda.get_device_name(0)))
import torchvision
print_elem_ok("Torchvision loaded", True)
import cv2
print_elem_ok("OpenCV loaded", True)
from ultralytics import YOLO
print_elem_ok("Ultralytics YOLO loaded", True)
print("")
print("If everything comes back without error, you have configured your Jetson correctly!")
print("This is a base container, you should extend from it with your own application.")

#!/bin/python3
print("Testing dependencies...")

def print_elem_ok(elem, ok):
    emo = "x"
    if ok:
        emo = u"\u2713"
    print(emo + " " + elem)


from PIL import Image, ImageDraw
print_elem_ok("Standard dependencies loaded", True)
import torch
print_elem_ok("PyTorch CUDA support", torch.cuda.is_available())
import torchvision
print_elem_ok("Torchvision loaded", True)
import cv2
from ultralytics import YOLO
print_elem_ok("Ultralytics YOLO loaded", True)

#print("Starting inference server") -- this will be a server at some point!


print("Loading YOLO model...")
model = YOLO("yolo11n_fish_trained.pt") # https://huggingface.co/akridge/yolo8-fish-detector-grayscale
print("Initialising YOLO model...")
results = model("00008.jpg")
print("Running test...")
results = model("00099.jpg")
print("Plotting boxes...")
img = Image.open("00099.jpg")
imd = ImageDraw.Draw(img)  

for r in results:
	boxes = r.boxes
	for box in boxes:
		raw_shape = box.xyxy.cpu().detach().numpy()
		shape = raw_shape.tolist()[0]
		print(shape)
		imd.rectangle(shape, fill = None, outline = "red")

img.save("/app/out/00099_labelled.jpg")
print("Image ready!")

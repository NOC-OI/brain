import cv2
import glob
import os
import time
import numpy as np
import io
import math
from PIL import Image


#from huggingface_hub import hf_hub_download
#from ultralytics import YOLO

#model_path = hf_hub_download(repo_id="AdamCodd/YOLOv11n-face-detection", filename="model.pt")
#model = YOLO(model_path)


cv2.namedWindow("ASEA2")
fps = 8

try:

    while True:
        try:
            # sudo mount -t nfs 10.88.88.1:/srv/nfs_cam /mnt/nfs_cam
            list_of_files = glob.glob("/mnt/nfs_cam/*.raw")
            latest_file = max(list_of_files, key=os.path.getctime)
            
            width = 5472
            height = 3648

            with open(latest_file, "rb") as fh:
                raw_buf = fh.read()
                raw_arr = np.ndarray(shape=(height,width),dtype=np.uint16, buffer=raw_buf)
  
            float_arr = np.power(raw_arr.astype(np.float32) / float(2 ** 16), 0.5)
            raw_img = (float_arr * (2 ** 16)).astype(np.uint16)
            img = cv2.cvtColor(raw_img, cv2.COLOR_BayerRGGB2BGR)
            img = cv2.resize(img, (640*2, 480*2))
            cv2.imshow("ASEA2", img)

            #results = model.predict((img / (2 ** 8)).astype(np.uint8), save=True)
            #print(results)
            #print("Done!")

            cv2.waitKey(int((1/fps) * 1000))
            #cv2.waitKey(0)
            #break
        except cv2.error as e:
            print(e)
except KeyboardInterrupt:
    cv2.destroyAllWindows()



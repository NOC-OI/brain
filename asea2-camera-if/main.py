import cv2
import glob
import os
import time
import numpy as np
import io
import math
import pika
from PIL import Image


cv2.namedWindow("ASEA2")
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
            img = cv2.resize(img, output_resolution)
            cv2.imshow("ASEA2", img)


            cv2.waitKey(int((1/fps) * 1000))
            #cv2.waitKey(0)
            #break
        except cv2.error as e:
            print(e)
except KeyboardInterrupt:
    cv2.destroyAllWindows()



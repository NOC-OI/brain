import cv2
import glob
import os
import time

cv2.namedWindow("ASEA2")
fps = 10

try:

    while True:
        try:
            list_of_files = glob.glob("/mnt/nfs_cam/*.png")
            latest_file = max(list_of_files, key=os.path.getctime)
            print(latest_file)
            img = cv2.imread(latest_file)

            cv2.imshow("ASEA2", img)

            cv2.waitKey(int((1/fps) * 1000))
        except cv2.error:
            pass
except KeyboardInterrupt:
    cv2.destroyAllWindows()



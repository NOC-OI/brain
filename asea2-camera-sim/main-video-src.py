import cv2
import time
import datetime
import numpy as np

# Initialize webcam (0 = default camera)

out_dir = "/srv/nfs_cam"
fps = 1
speedup = 5
vidcap = cv2.VideoCapture("mbari_jellyfish_crop.mp4")
success,frame = vidcap.read()
frameidx = 0
while success:
    dt = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%-M-%SZ_%f")
    fshape = frame.shape
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    width = int(5472 / 2)
    height = int(3648 / 2)
    image_rgb = cv2.resize(image_rgb, (width, height))

    rgb_bytes = image_rgb.flatten("C").astype(np.uint16) * (2**8)
    output_array = np.zeros((height * 2, width * 2))
    for line in range(height):
        for row in range(width):
            idx = row + (line * width)
            r = rgb_bytes[(idx * 3) + 0]
            g = rgb_bytes[(idx * 3) + 1]
            b = rgb_bytes[(idx * 3) + 2]
            output_array[(line * 2), (row * 2)] = r
            output_array[(line * 2) + 1, (row * 2)] = g
            output_array[(line * 2), (row * 2) + 1] = g
            output_array[(line * 2) + 1, (row * 2) + 1] = b

    flat = output_array.flatten("C").astype(np.uint16)
    with open(out_dir + "/" + dt + ".raw", "wb") as binary_file:
        binary_file.write(flat)

    frameidx += int((30 * speedup) / fps)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frameidx)
    success,frame = vidcap.read()
    print('Read a new frame: ', success)

    time.sleep(1/fps)

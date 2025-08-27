import cv2
import time
import datetime
import numpy as np
import csv
import uuid
import os

# Initialize webcam (0 = default camera)
cam = cv2.VideoCapture(0)
csv_file = "/srv/nfs_cam/sim.csv"
out_dir = "/srv/nfs_cam"
run_dir = "sim"
fps = 2
os.makedirs(os.path.join(out_dir, run_dir), exist_ok=True)

with open(csv_file, "w") as csv_fh:
    field_names = ["filename","timestamp","camera_id","frame_count","height","width","error","uuid","gain","wb_red","wb_blue"]
    writer = csv.DictWriter(csv_fh, fieldnames=field_names)
    writer.writeheader()
    try:
        # Capture one frame
        while True:
            ret, frame = cam.read()

            if ret:
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
                raw_fn = os.path.join(out_dir, run_dir, dt + ".raw")
                with open(raw_fn, "wb") as binary_file:
                    binary_file.write(flat)
                simul_fn = os.path.join("/media/images", run_dir, dt + ".raw")
                a2dt = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%f")
                writer.writerow({
                    "filename": simul_fn,
                    "timestamp": a2dt,
                    "camera_id": -1,
                    "frame_count": 1,
                    "height": 3648,
                    "width": 5472,
                    "error": 0,
                    "uuid": str(uuid.uuid4()),
                    "gain": 4.00136,
                    "wb_red": 1.09863,
                    "wb_blue": 1.83105
                    })
                csv_fh.flush()
                print("Written frame " + raw_fn)
            else:
                print("Failed to capture image.")
                break
            time.sleep(1/fps)
    except KeyboardInterrupt:
        cam.release()

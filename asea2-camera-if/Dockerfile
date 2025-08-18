FROM python:3.9.20-bookworm
RUN pip install --no-cache pika==1.3.2 requests==2.32.4 opencv-python-headless numpy pillow
COPY src /app
WORKDIR /app
#RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN mkdir /mnt/nfs_cam
RUN mkdir -p temp
ENTRYPOINT ["python3", "main.py"]
STOPSIGNAL SIGQUIT


FROM python:3.9.20-bookworm
RUN pip install --no-cache pika==1.3.2 requests==2.32.4 opencv-python-headless numpy pillow
RUN apt-get update
RUN apt-get install
RUN pip install --no-cache aiormq
COPY src /app
WORKDIR /app
#RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
ENTRYPOINT ["python3", "main.py"]
STOPSIGNAL SIGQUIT


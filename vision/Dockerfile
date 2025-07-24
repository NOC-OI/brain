FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3
WORKDIR /app
SHELL ["/bin/bash", "-c"]
#RUN apt-get -y install opencv-python
RUN apt-get update 
RUN apt-get install --no-install-recommends -y gcc git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3-dev gnupg g++
RUN apt-get install --reinstall libgstreamer1.0-0
RUN mkdir -p /usr/src/ultralytics
RUN python3 -m pip install --upgrade pip wheel
RUN pip install --no-cache uwsgi flask tqdm matplotlib pyyaml psutil thop pandas hydra torch torchvision python-multipart "numpy==1.23"
RUN pip install --no-cache ultralytics --no-deps
RUN mkdir /app/yolo_conf
ENV YOLO_CONFIG_DIR="/app/yolo_conf"
COPY src /app
WORKDIR /app
RUN mkdir -p temp
ENTRYPOINT ["python3", "init.py"]
STOPSIGNAL SIGQUIT

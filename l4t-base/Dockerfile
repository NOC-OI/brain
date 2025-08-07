# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# Dockerfile based off https://gitlab.com/nvidia/container-images/l4t-jetpack/-/blob/master/Dockerfile.jetpack_6?ref_type=heads

FROM nvcr.io/nvidia/base/ubuntu:22.04_20240212

#
# Install any utils needed for execution
#
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    bc \
    bzip2 \
    can-utils \
    ca-certificates \
    gnupg2 \
    gstreamer1.0-alsa \
    gstreamer1.0-libav \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-tools \
    i2c-tools \
    iw \
    kbd \
    kmod \
    language-pack-en-base \
    libcanberra-gtk3-module \
    libdrm-dev \
    libgles2 \
    libglvnd-dev \
    libgtk-3-0 \
    libpython2.7 \
    libudev1 \
    libvulkan1 \
    libzmq5 \
    mtd-utils \
    parted \
    pciutils \
    python-is-python3 \
    python3 \
    python3-pexpect \
    python3-distutils \
    python3-numpy \
    sox \
    udev \
    vulkan-tools \
    wget \
    wireless-tools wpasupplicant \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


#
# Configure nvidia apt repo
#
RUN wget -P /etc/apt/trusted.gpg.d https://repo.download.nvidia.com/jetson/jetson-ota-public.asc
RUN wget -P /etc/apt/preferences.d https://repo.download.nvidia.com/jetson/nvidia-repo-pin-600
RUN echo "deb https://repo.download.nvidia.com/jetson/common r36.4 main" >> /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
#RUN cat /etc/apt/sources.list.d/nvidia-l4t-apt-source.list && sleep 9

#
# Install cuda-toolkit-12-6, cuda-libraries-12-6, and cuda-compat-12-6 for CUDA developer packages
# Install cuda-libraries-12-6 and cuda-compat-12-6 if need CUDA runtime only
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-toolkit-12-6 cuda-libraries-12-6 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN apt-get update && apt-get download cuda-compat-12-6 \
    && dpkg-deb -R ./cuda-compat-12-6_*_arm64.deb ./cuda-compat \
    && cp -r ./cuda-compat/usr/local/* /usr/local/ \
    && rm -rf ./cuda-compat-12-6_*_arm64.deb ./cuda-compat

#
# Install nvidia-cudnn-dev for CuDNN developer packages
# Use nvidia-cudnn if need CuDNN runtime only
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-cudnn-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

#
# Install nvidia-tensorrt-dev for TensorRT developer packages
# Use nvidia-tensorrt if need TensorRT runtime only
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-tensorrt-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

#
# Install nvidia-vpi-dev for VPI developer packages
# Use nvidia-vpi if need VPI runtime only
#
RUN mkdir -p /lib/firmware/
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-vpi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

#
# Install nvidia-opencv-dev for OpenCV developer packages
# Use nvidia-opencv if need OpenCV runtime only
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-opencv-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

#
# Install Multimedia API samples & libs
#
RUN apt-get update && apt-get download nvidia-l4t-jetson-multimedia-api \
    && dpkg-deb -R ./nvidia-l4t-jetson-multimedia-api_*_arm64.deb ./mm-api \
    && cp -r ./mm-api/usr/src/jetson_multimedia_api /usr/src/jetson_multimedia_api \
    && sed -i 's/sudo//' ./mm-api/DEBIAN/postinst \
    && ./mm-api/DEBIAN/postinst \
    && rm -rf ./nvidia-l4t-jetson-multimedia-api_*_arm64.deb ./mm-api

#
# Install DLA compiler
#
RUN apt-get update && apt-get download nvidia-l4t-dla-compiler \
    && dpkg-deb -R ./nvidia-l4t-dla-compiler_*_arm64.deb ./dla \
    && cp -r ./dla/usr/lib/* /usr/lib/ \
    && rm -rf ./nvidia-l4t-dla-compiler_*_arm64.deb ./dla

#
# Install GStreamer
#
RUN apt-get update && apt-get download nvidia-l4t-gstreamer \
    && dpkg-deb -R ./nvidia-l4t-gstreamer_*_arm64.deb ./gstreamer \
    && cp -r ./gstreamer/usr/bin/* /usr/bin/ \
    && cp -r ./gstreamer/usr/lib/* /usr/lib/ \
    && rm -rf ./nvidia-l4t-gstreamer_*_arm64.deb ./gstreamer

#Update libraries
RUN ldconfig

#
# Setup environment variables
#
ENV CUDA_HOME="/usr/local/cuda"
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

RUN echo "/usr/lib/aarch64-linux-gnu/tegra" >> /etc/ld.so.conf.d/nvidia-tegra.conf && \
    echo "/usr/lib/aarch64-linux-gnu/tegra-egl" >> /etc/ld.so.conf.d/nvidia-tegra.conf

RUN rm /usr/share/glvnd/egl_vendor.d/50_mesa.json
RUN mkdir -p /usr/share/glvnd/egl_vendor.d/ && echo '\
{\
    "file_format_version" : "1.0.0",\
    "ICD" : {\
        "library_path" : "libEGL_nvidia.so.0"\
    }\
}' > /usr/share/glvnd/egl_vendor.d/10_nvidia.json

RUN mkdir -p /usr/share/egl/egl_external_platform.d/ && echo '\
{\
    "file_format_version" : "1.0.0",\
    "ICD" : {\
        "library_path" : "libnvidia-egl-wayland.so.1"\
    }\
}' > /usr/share/egl/egl_external_platform.d/nvidia_wayland.json

RUN ldconfig

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all


# Start custom BRAIN install
RUN apt-get -y install python3-pip libopenblas0 libopenblas64-0
# Deps for pytorch:
RUN python3 -m pip install --upgrade pip wheel
RUN pip install mpmath==1.3.0 typing_extensions==4.14.1 sympy==1.14.0 pillow==11.3.0 networkx==3.4.2 MarkupSafe==3.0.2 fsspec==2025.7.0 filelock==3.18.0 Jinja2==3.1.6
COPY libs /tmp/container_build/libs
RUN pip install /tmp/container_build/libs/torchvision-0.23.0-cp310-cp310-linux_aarch64.whl /tmp/container_build/libs/torch-2.8.0-cp310-cp310-linux_aarch64.whl
RUN mkdir -p /usr/src/ultralytics
# Ultralytics deps
RUN pip install uWSGI==2.0.30 tqdm==4.67.1 PyYAML==6.0.2 psutil==7.0.0 thop==0.1.1.post2209072238 pandas==2.3.1 python-multipart==0.0.20 numpy==1.23
RUN pip install --no-cache ultralytics==8.3.175 --no-deps

RUN mkdir /app
COPY src /app
WORKDIR /app
RUN mkdir /etc/yolo_conf
ENV YOLO_CONFIG_DIR="/etc/yolo_conf"
COPY templates/yolo_conf.json /etc/yolo_conf/settings.json

#RUN pip install --no-cache pika==1.3.2 requests==2.32.4
#RUN mkdir /mnt/nfs_cam
#RUN mkdir -p temp
ENTRYPOINT ["python3", "init.py"]
STOPSIGNAL SIGQUIT


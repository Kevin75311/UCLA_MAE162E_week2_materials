#!/bin/bash

conda create -y -n week2_new python=3.12
conda init --all
source /home/pi/miniconda3/etc/profile.d/conda.sh
conda activate week2_new

conda install opencv -y
conda install -c conda-forge libstdcxx-ng -y

sudo apt update
sudo apt install -y libcamera-dev
pip install -y rpi-libcamera

sudo apt install -y libkms++-dev libfmt-dev libdrm-dev
pip install -y rpi-kms

sudo apt-get install -y libcap-dev
pip install -y picamera2

pip install -y gdown
cd ./YOLOv4/weights
gdown 18RjNcN-wpUMie2FpkYxdG0MMrF0rP5Ns

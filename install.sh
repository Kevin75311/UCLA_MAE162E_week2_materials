#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

conda create -n week2_new python=3.12
conda activate week2_new

conda install opencv
conda install -c conda-forge libstdcxx-ng -y

sudo apt update
sudo apt install -y libcamera-dev
pip install rpi-libcamera

sudo apt install -y libkms++-dev libfmt-dev libdrm-dev
pip install rpi-kms

sudo apt-get install -y libcap-dev
pip install picamera2

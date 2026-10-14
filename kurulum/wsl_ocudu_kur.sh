#!/usr/bin/env bash
# OCUDU release_26_10 kurulumu (WSL2 Ubuntu 24.04, Clang, ZMQ acik). Log: ~/ehb415/ocudu_kurulum.log
set -euxo pipefail
mkdir -p ~/ehb415 && cd ~/ehb415

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    cmake make gcc g++ clang pkg-config \
    libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev \
    libfftw3-dev libeigen3-dev libzmq3-dev ccache

[ -d ocudu ] || git clone --depth 1 --branch release_26_10 https://gitlab.com/ocudu/ocudu.git
cd ocudu
mkdir -p build && cd build
CC=clang CXX=clang++ cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
make -j4 gnb
echo "=== OCUDU BUILD OK ==="
ls -la apps/gnb/gnb
./apps/gnb/gnb --version 2>&1 | head -5 || true
echo "=== OCUDU DONE ==="

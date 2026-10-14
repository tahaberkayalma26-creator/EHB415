#!/usr/bin/env bash
# ns-3.48 + 5G-LENA v5.1 kurulumu (WSL2 Ubuntu 24.04). Log: ~/ehb415/ns3_kurulum.log
set -euxo pipefail
mkdir -p ~/ehb415 && cd ~/ehb415

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential g++ python3 python3-venv python3-pip cmake ninja-build git ccache pkg-config \
    libc6-dev sqlite3 libsqlite3-dev libeigen3-dev

[ -d ns-3-dev ] || git clone --depth 1 --branch ns-3.48 https://gitlab.com/nsnam/ns-3-dev.git
[ -d ns-3-dev/contrib/nr ] || git clone --depth 1 --branch v5.1 https://gitlab.com/cttc-lena/nr.git ns-3-dev/contrib/nr

cd ns-3-dev
./ns3 configure --enable-examples -d optimized -G Ninja
./ns3 build -j6
echo "=== NS3 BUILD OK ==="
./ns3 run cttc-nr-demo 2>&1 | tail -40
echo "=== NS3 DEMO OK ==="

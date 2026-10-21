#!/usr/bin/env bash
# NetAnim (ns-3'un resmi animasyon araci) kurulumu: Qt5 + CMake ile kaynaktan derleme.
# Log: ~/ehb415/netanim_kurulum.log   |   GUI, Windows 11'de WSLg ile ekrana gelir (DISPLAY=:0).
set -euxo pipefail
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y qtbase5-dev cmake ninja-build build-essential git
mkdir -p ~/ehb415 && cd ~/ehb415
[ -d netanim ] || git clone --depth 1 https://gitlab.com/nsnam/netanim.git
cd netanim
mkdir -p build && cd build
cmake .. -G Ninja
cmake --build . -j4
ls -la bin/netanim
echo "=== NETANIM BUILD OK ==="

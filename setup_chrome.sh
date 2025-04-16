#!/bin/bash

# Install dependencies
sudo apt update
sudo apt install -y wget unzip xvfb libxi6 libgconf-2-4 libnss3 libasound2 libgbm-dev

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb || sudo apt --fix-broken install -y
sudo dpkg -i google-chrome*.deb

# Verifikasi
google-chrome --version

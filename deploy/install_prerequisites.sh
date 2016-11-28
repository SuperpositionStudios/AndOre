#!/bin/bash
sudo apt update;
sudo apt -y upgrade;
sudo apt install -y python python3 python-pip screen vnstat nginx libffi-dev git htop python3-pip;
pip3 install --upgrade pip;
pip2 install --upgrade pip;
pip2 install sultan;
pip3 install websockets;
git config --global user.email "you@example.com";
git config --global user.name "Your Name";
cd ~;
git clone https://github.com/AI-Productions/AndOre.git;
cd AndOre;
git checkout unstable;
pip3 install -r ~/AndOre/erebus/requirements.txt;
cd deploy;
sudo chmod +x ./enable_swap.sh;
sudo ./enable_swap.sh;


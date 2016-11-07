#!/bin/bash
sudo apt install -y python python3 python-pip python3-pip screen vnstat nginx libffi-dev git htop;
pip3 install --upgrade pip;
pip2 install --upgrade pip;
pip2 install sultan;
git config --global user.email "you@example.com";
git config --global user.name "Your Name";
cd ~;
git clone https://github.com/baxter-cs/AndOre.git;
cd AndOre;
git checkout sphere;
pip3 install -r ~/AndOre/erebus/requirements.txt;
cd deploy;
sudo chmod +x ./enable_swap.sh;
sudo ./enable_swap.sh;


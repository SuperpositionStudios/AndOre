#!/bin/bash
sudo apt install -y python python3 python-pip python3-pip screen vnstat nginx libffi-dev git;
pip3 install --upgrade pip;
pip2 install --upgrade pip;
pip2 install sultan;
git config --global user.email "you@example.com";
git config --global user.name "Your Name";
git clone https://github.com/baxter-cs/AndOre.git;
pip3 install -r ~/AndOre/auth_service/requirements.txt;


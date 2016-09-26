Ubuntu 16.04 / (Probably will work on Debian & Debian Derivatives with very little changes)
===========================================================================================

1. Download the requirements
    `sudo apt install -y virtualenv python3.5 python3-pip git python3-dev libffi-dev;`
2. Clone the repo
    `cd ~; git clone https://github.com/baxter-oop/AndOre.git;`
3. Create the virtual environments and install the python requirements
    `virtualenv -p python3.5 env;`
    You might need to chown the env to install the requirements now.
    `sudo su; compgen -u; compgen -g; chown -R <user>:<group> /home/user/env`
    `source env/bin/activate; cd AndOre; pip install -r requirements.txt;`
4. Run the servers
    `source server-env/bin/activate; cd AndOre/server; python server.py;`
    `cd ~; source env/bin/activate; cd AndOre; python master_server/master_server.py;`

    Run the other serverse

5. Play at the game at http://localhost:7002

OSX
===

Ask @halstedlarsson

Windows XP/Vista/7/8/8.1/10
===========================

1. Install Ubuntu 16.04 (Xenual Xerus)
    - Go to http://www.ubuntu.com/download, download Ubuntu, setup a live cd using Rufus, and install Ubuntu with the live cd
    - Alternatively you can follow https://builtvisible.com/the-ubuntu-installation-guide/
2. Follow the setup instructions for Ubuntu seen above.

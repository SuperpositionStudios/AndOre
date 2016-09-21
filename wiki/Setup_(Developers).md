Ubuntu 16.04 / (Probably will work on Debian & Debian Derivatives with very little changes)
===========================================================================================

1. Download the requirements
    `sudo apt install -y virtualenv python3.5 git python3-dev libffi-dev;`
2. Clone the repo
    `mkdir AndOre; cd AndOre; git clone https://github.com/baxter-oop/AndOre.git;`
3. Create the virtual environments and install the python requirements
    `virtualenv -p python3.5 client-env; virtualenv -p python3.5 server-env; virtualenv -p python3.5 ai-storage-env;`
    
    `source client-env/bin/activate; cd AndOre/client; pip install -r requirements.txt; cd ../..;`
    `source server-env/bin/activate; cd AndOre/server; pip install -r requirements.txt; cd ../..;`
    `source ai-storage-env/bin/activate; d AndOre/ai_storage; pip install -r requirements.txt; cd ../..;`
4. Run the servers
    `source server-env/bin/activate; cd AndOre/server; python server.py;`
    
    and in another terminal
    
    `source client-env/bin/activate; cd AndOre/client; python client-server.py;`

    and in another terminal
    
    `source ai-storage-env/bin/activate; cd AndOre/ai_storage; python ai_server.py;`

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

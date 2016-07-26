# And/Ore
A game about gathering ore, simple enough to take a reasonable amount of time to train a neural net, yet complex enough to be fun for a human player.

## Try the game out
* You can try the game out at http://andore.iwanttorule.space:7002
* You can also play the game by setting it up to run on your own server by following the instructions below.

##Setup
1. Download the requirements
    `sudo apt install virtualenv; sudo apt install python3.5; sudo apt install git;`
2. Clone the repo
    `mkdir AndOre; cd AndOre; git clone https://github.com/baxter-oop/AndOre.git;`
3. Create the virtual environments and install the python requirements
    `virtualenv -p python3.5 client-env; virtualenv -p python3.5 server-env;`
    
    `source client-env/bin/activate; cd AndOre/client; pip install -r requirements.txt; cd ../..;`
    `source server-env/bin/activate; cd AndOre/server; pip install -r requirements.txt; cd ../..;`
4. Run the servers
    `source server-env/bin/activate; cd AndOre/server; python server.py;`
    
    and in another terminal
    
    `source client-env/bin/activate; cd AndOre/client; python server.py;`
    
5. Play at the game at http://localhost:7002

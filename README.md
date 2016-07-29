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

##Versions/Releases

###Genesis - Version 1.0 (Found in the Genesis Branch)
- Players
    -  You show up on the world as a `@`
    -  Can move by activating movement modifier key and pressing direction keys (wasd)
    -  Automatically start in a corporation with only themselvesy and choosing the player with the direction keys
    -  Mine ore by pretting the loot modifier key and pressing the direction keys to mine ore
    -  use the same keys to use a hospital for an ore cost, or to loot ore.
    -  Deploy a Fence with the fence modifier key `f`
    -  Can attack other players with the kill modifier `k` and direction keys
    -  Death 10 damage to other players
    -  Start off with 100 hp
    -  Have a health decay of 0.1 per action
    -  Can only do one action per server tick
-  Server
    -  Each server tick is 350 milliseconds
-  Corporations
    - Invite other corps to merge into your corp by pressing the invitation modifier key `i` and choosing the corp by choosing a member of that corp with the direction keys if they are directly adjacent to you
    - Have an ore bank, all ore that members gain is deposited here.
    - When a member dies, (the ore in the ore bank divided by the total number of members) is dropped as loot.
    - Members cannot attack each other
    - A member of a corporation can modify their corp's standings towards another player's corp by pressing the worsen standing modifier key `-` or improve standing modifier key `+` and choosing the player with the direction keys.
    - Other members show up as an `M`
    - Enemies show up as `E`
    - Neutrals show up as `N`
    - Allies show up as `A`
    - If a member of another corporation attacks a member of your corporation, your standings towards the attacker's corporations will worsen.
    - If a member of your corporation attacks a member of another corporation, your standings towards the victim's corporation will worsen.
-  Hospitals
    - Cost 10 ore to use
    - Heal 5 hit points
    - Impassible
    - Show up as `+`
- Ore Deposits
    - Give 3 ore per turn
    - Impassible
    - Show up as `$`
- Fences
    - Cost 50 ore to deploy
    - Have 60 hp points
    - Impassible
    - Show up as `#`
    - Can be deployed by players
- Machine Learning
    - Activate it in the client by pressing `~`, enter the name of the model which will be what is used to save and retrieve the model from the ai-storage server.
    - Clone models by going to the /ai-storage-server/clone/<original-model-name>/<new-model-name>

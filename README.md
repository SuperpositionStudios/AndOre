# And/Ore
A game about gathering ore, simple enough to take a reasonable amount of time to train a neural net, yet complex enough to be fun for a human player.

![AndOre Logo](https://raw.githubusercontent.com/baxter-oop/AndOre/master/AndOre%20Logo.png)

## Try the game out
* You can try the game out at http://ao.iwanttorule.space
* You can also play the game by setting it up to run on your own server by following the instructions below.

##Setup

See https://github.com/baxter-oop/AndOre/wiki/Setup-(Developers)
    
##Versions/Releases


###Exodus: Cold War - Version 1.3 (Found in Exodus: Cold War Branch)

Expansion Details:
We had a problem with our play testers playing the game instead of doing work, because they'd loose their progress if they closed the window. We fixed that with the addition of an Auth server that saves your game-id for you, so you can take control of your old character after closing the game, in another tab or computer. Going along with the theme of being offline/afk, we added Sentry Turrets & Spiketraps to help guard your base when you're offline. We also had some major issues in play tests where without that much work, players would obtain a massive amounts of ore, so we nerfed ore generators, and also nerfed potions so players could take on extremely upgraded players if they worked together.

We also gained a contributor, who is helping us with our art assets. Eventually, we plan to phase our our unicode symbols with icons drawn by him in the client. He created our favicon on the client as a simpler version of the logo.

Expansion Highlights:

- Corp Owned Sentry Turrets to protect your land when you're not there to fend off attackers
    - [x] https://github.com/baxter-oop/AndOre/issues/67
- User Accounts, allows players to retake control of their old character if they refresh the page / moved to another computer
    - [x] https://github.com/baxter-oop/AndOre/issues/73 
- Added Sprinting, hold down shift and press a dir key to move two cells at a time in exchange for 2 hp
    - [x] https://github.com/baxter-oop/AndOre/issues/72 
- New & Improved Client framework
    - [x] https://github.com/baxter-oop/AndOre/issues/136
- Nerfed Potions
    - [x] https://github.com/baxter-oop/AndOre/issues/124
- Nerfed Ore Generators
    - [x] https://github.com/baxter-oop/AndOre/issues/110
- Secondary Modifier Key now carries over when switching Primary Modifier Keys
    - [x] https://github.com/baxter-oop/AndOre/issues/131
- Fixed View Polling (Was broken in Exodus)
    - [x] https://github.com/baxter-oop/AndOre/issues/128
- Added Spiketraps
    - [x] https://github.com/baxter-oop/AndOre/issues/84

###Exodus - Version 1.2 (Found in Exodus Branch)

Focus of the Expansion:
As more people try out the game, they are able to identify more and more issues and give ideas for new features. This expansion addresses their bug reports and minor feature requests. Color is also introduced to the game to reduce the number of icons in the game.

Expansion Highlights:
- Starting to add content to Wiki
- Pharmacies now impassible
    - [x] https://github.com/baxter-oop/AndOre/issues/83
- You can now press your current primary modifier key again to switch to `m`
    - [x] https://github.com/baxter-oop/AndOre/issues/90
- Buildings now drop lootable wrecks when destroyed. The wrecks have 50% of the ore of the building's construction time
    - [x] https://github.com/baxter-oop/AndOre/issues/89
- Corporation inventories are now merged together when corps merge together
    - [x] https://github.com/baxter-oop/AndOre/issues/86
- Added color to building icons indicating standings
    - [x] https://github.com/baxter-oop/AndOre/issues/87
- Added doors which are game objects that are impassable to people not in the corp which owns the doors.
    - [x] https://github.com/baxter-oop/AndOre/issues/85
- Pharmacies now sell 4 potions, use `(l, 1)` for a health potion, `(l, 2)` for a health cap potion, `(l, 3)` for an attack power bonus, `(l, 4)` for a mining multiplier increase
    - [x] https://github.com/baxter-oop/AndOre/issues/71
- Added a corporation building that acts as a spawn point for members in the corporation. Build with `(l, 6)`. There can only be one per corp at a single moment (others are destroyed when a new one is placed)
    - [x] https://github.com/baxter-oop/AndOre/issues/69
- World Size changed from 31x32 to 14x64 due to there now being a LOS and a corp inventory. (Also the game is more tall than wide, but most people's screens are landscape)
    - [x] https://github.com/baxter-oop/AndOre/issues/94
- Fixed non-working monospacing in the client
    - [x] https://github.com/baxter-oop/AndOre/issues/97
- Added health decay to Ore Generators.
    - [x] https://github.com/baxter-oop/AndOre/issues/101
- You now go into movement mode after dying
    - [x] https://github.com/baxter-oop/AndOre/issues/111
- Increased the cost of Health Potions from 5 to 50
    - [x] https://github.com/baxter-oop/AndOre/issues/112

###Castor - Version 1.1 (Found in the Castor Branch)

- You can no longer attack people your corporation considers allies #70
    - This extends to buildings owned by the allies
- Corporation Owned Hospitals; Cheaper to use than a Hospital not owned by your Corporation and if non corp-members and allies use it they will pay full price and the corp will gain ore #68
- Ore Generators; Corp owned Deployable that produces ore for the corporation every tick #66
- You can no longer place Corp Owned Buildings in Impassible cells #79
- Pharmacies; Corporation Owned Building that sells Health Potions. The Health Potions go into your Corporation Inventory and anyone in the Corporation can use them instantly. #41
    - Use Health Potions by finding their spot on your corp inventory, most commenly 1. So (u, 1) will use your health potion 
- Corporation Inventory System #41
- Secondary Modifier Keys to remove some Primary Modifier Keys #41
    - Building a Fence is changed to (b, 1) from (f, *)
    - Building a Hospital is changed to (b, 2) from (h, *)
    - Building an Ore Generator is (b, 3)
    - Building a Pharmacy is (b, 4)

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

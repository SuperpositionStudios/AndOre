# Controls in And/Ore work on what we call "The Triple-Tap System." 

The Triple-Tap System involves pressing a "mode" key which determines which mode you are in, and then a modifier key to change the exact actions. The various modes and their mode keys are: 

<table>
    <tr>
        <th>Action</th>
        <th>Key</th>
    </tr>
    <tr>
        <td>Movement</td>
        <td>m</td>
    </tr>
    <tr>
        <td>Build</td>
        <td>b</td>
    </tr>
    <tr>
        <td>Loot</td>
        <td>l</td>
    </tr>
    <tr>
        <td>Kill</td>
        <td>k</td>
    </tr>
    <tr>
        <td>Corp Invite</td>
        <td>i</td>
    </tr>
    <tr>
        <td>Use Item from Inventory</td>
        <td>u</td>
    </tr>
    <tr>
        <td>Increase Corp Standing</td>
        <td>+</td>
    </tr>
    <tr>
        <td>Decrease Corp Standing</td>
        <td>-</td>
    </tr>
</table>
  
The modifier key is a number and will allow for you to switch between certain actions within a mode, for example, building a different building or using a different potion. The modes that allow for modifier keys are Loot, Build, and Use Item from Inventory. Using a modifier key in a mode that does not require a modifier key, will all have the same result. 

After selecting a mode and a modifier key, you must press W, A, S, or D to activate it. You must press the key relative to the direction you wish to use the action.

In Build mode, each modifier key allows you to build a different building.  
* (B1) is used to build a Fence.  
* (B2) is used to build a Hospital.  
* (B3) is used to build an Ore Generator.  
* (B4) is used to build a Pharmacy.  
* (B5) is used to build a Door.  
* (B6) is used to build a Corp Respawn Point.  
* (B7) is used to build a Turret.  
* (B8) is used to build a Spike Trap.

In Loot mode, each modifier key allows you to purchase a different potion from the pharmacy.
* (L1) is used to buy a Health Potion.
* (L2) is used to buy a Health Cap Potion.
* (L3) is used to buy an Attack Boost Potion.
* (L4) is used to buy a Mining Multiplier Potion. (Currently Disabled)

In Use from Inventory mode, each modifier key lets you use the potion in the slot that the modifier key equals.

Master Table:

<table>
    <tr>
        <th>Action</th>
        <th>Primary Key</th>
        <th>Secondary Key</th>
        <th>Direction</th>
    </tr>
    <tr>
        <td>Move North</td>
        <td>m</td>
        <td>*</td>
        <td>w</td>
    </tr>
    <tr>
        <td>Move West</td>
        <td>m</td>
        <td>*</td>
        <td>a</td>
    </tr>
    <tr>
        <td>Move South</td>
        <td>m</td>
        <td>*</td>
        <td>s</td>
    </tr>
    <tr>
        <td>Move East</td>
        <td>m</td>
        <td>*</td>
        <td>d</td>
    </tr>
    <tr>
        <td>Build Fence</td>
        <td>b</td>
        <td>1</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Hospital</td>
        <td>b</td>
        <td>2</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Ore Generator</td>
        <td>b</td>
        <td>3</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Pharmacy</td>
        <td>b</td>
        <td>4</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Door</td>
        <td>b</td>
        <td>5</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Corp Respawn Point</td>
        <td>b</td>
        <td>6</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Turret</td>
        <td>b</td>
        <td>7</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Build Spiketrap</td>
        <td>b</td>
        <td>8</td>
        <td>Desired Location Relative to You</td>
    </tr>
    <tr>
        <td>Buy Health Potion from Pharmacy</td>
        <td>l</td>
        <td>1</td>
        <td>Direction of Pharmacy Adjacent to You</td>
    </tr>
    <tr>
        <td>Buy Health Cap Increase Potion from Pharmacy</td>
        <td>l</td>
        <td>2</td>
        <td>Direction of Pharmacy Adjacent to You</td>
    </tr>
    <tr>
        <td>Buy Attack Boost Potion from Pharmacy</td>
        <td>l</td>
        <td>3</td>
        <td>Direction of Pharmacy Adjacent to You</td>
    </tr>
    <tr>
        <td>Buy Miner Multiplier Potion (Currently Disabled) from Pharmacy</td>
        <td>l</td>
        <td>4</td>
        <td>Direction of Pharmacy Adjacent to You</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 1</td>
        <td>u</td>
        <td>1</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 2</td>
        <td>u</td>
        <td>2</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 3</td>
        <td>u</td>
        <td>3</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 4</td>
        <td>u</td>
        <td>4</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 5</td>
        <td>u</td>
        <td>5</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 6</td>
        <td>u</td>
        <td>6</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 7</td>
        <td>u</td>
        <td>7</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 8</td>
        <td>u</td>
        <td>8</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 9</td>
        <td>u</td>
        <td>9</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Use Inventory Item in Slot 10</td>
        <td>u</td>
        <td>0</td>
        <td>*</td>
    </tr>
    <tr>
        <td>Attack Player/Building to your North</td>
        <td>k</td>
        <td>*</td>
        <td>w</td>
    </tr>
    <tr>
        <td>Attack Player/Building to your West</td>
        <td>k</td>
        <td>*</td>
        <td>a</td>
    </tr>
    <tr>
        <td>Attack Player/Building to your South</td>
        <td>k</td>
        <td>*</td>
        <td>s</td>
    </tr>
    <tr>
        <td>Attack Player/Building to your East</td>
        <td>k</td>
        <td>*</td>
        <td>d</td>
    </tr>
    <tr>
        <td>Increase Corporation Standing</td>
        <td>+</td>
        <td>*</td>
        <td>Direction of Corporation Representative Adjacent to You</td>
    </tr>
    <tr>
        <td>Decrease Corporation Standing</td>
        <td>-</td>
        <td>*</td>
        <td>Direction of Corporation Representative Adjacent to You</td>
    </tr>
    <tr>
        <td>Request/Accept Corporation Merger</td>
        <td>i</td>
        <td>*</td>
        <td>Direction of Corporation Representative Adjacent to You</td>
    </tr>

</table>

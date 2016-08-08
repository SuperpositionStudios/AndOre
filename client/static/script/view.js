//load app.js after this!
//using (from app.js) id, CallCallback

// RobG - http://stackoverflow.com/a/12690148
/* Only works for native objects, host objects are not
** included. Copies Objects, Arrays, Functions and primitives.
** Any other type of object (Number, String, etc.) will likely give
** unexpected results, e.g. copy(new Number(5)) ==> 0 since the value
** is stored in a non-enumerable property.
**
** Expects that objects have a properly set *constructor* property.
*/
function copy(source, deep) {
   var o, prop, type;

  if (typeof source != 'object' || source === null) {
    // What do to with functions, throw an error?
    o = source;
    return o;
  }

  o = new source.constructor();

  for (prop in source) {

    if (source.hasOwnProperty(prop)) {
      type = typeof source[prop];

      if (deep && type == 'object' && source[prop] !== null) {
        o[prop] = copy(source[prop]);

      } else {
        o[prop] = source[prop];
      }
    }
  }
  return o;
}

//called by app.js after id is populated, etc
var worldViewSelector = "#worldview";
var inventorySelector = "#inventory";

var firstTime = true;
var createRowID = function(row) {
    return "world_row" + row;
};
var createColumnID = function(col) {
    return "world_col" + col;
};

var createCellID = function(row, col) {
    return "world_row" + row + "world_col" + col;
};

View = function() {

};

View.prototype = {
  worldView: null,
  inventoryView: null,
  playerStatView: {
    currentHealth: null,
    healthCap: null,
    attackPower: null,
    row: null,
    column: null,
    ore: null,
    miningMultiplier: null,
    worldAge: null,
    modifierKey: null,
    secondaryModifierKey: null
  },
  infoView: {
    modeMeaning: null,
    modeMeanings: {
      m: 'Movement',
      k: 'Kill',
      l: 'Loot',
      i: 'Corp Invite',
      b: 'Build',
      u: 'Use Item From Inventory',
      '+': 'Increase Corp Standing',
      '-': 'Decrease Corp Standing'
    }
  },
  pollDelay: 333,
  SetupView : function(app, callback) {
    this.app = app;
    this.worldView = $(worldViewSelector);
    this.inventoryView = $(inventorySelector);
    this.infoView.modeMeaning = $("#infoModeMeaning");
    this.playerStatView.currentHealth = $("#statHealth");
    this.playerStatView.healthCap = $("#statHealthCap");
    this.playerStatView.attackPower = $("#statAttackPower");
    this.playerStatView.row = $("#statRow");
    this.playerStatView.column = $("#statCol");
    this.playerStatView.ore = $("#statOre");
    this.playerStatView.miningMultiplier = $("#statOreMultiplier");
    this.playerStatView.worldAge = $("#statWorldAge");
    this.playerStatView.modifierKey = $("#statModifierKey");
    this.playerStatView.secondaryModifierKey = $("#statSecondaryModifierKey");
    this.SetupInput();
    this.Poll();
    CallCallback(callback);
  },
  DrawInventory: function(inventory) {
    if (inventory == '') {
      return false;
    }

    this.inventoryView.text(inventory);
  },
  DrawWorldView: function(world) {
    if (world == '') {
      return false;
    }

    var rows = world.length;
    var cols = world[0].length;

    if (firstTime) {
      firstTime = false;

      for (var rowNum = 0; rowNum < rows; rowNum++) {
        // Creating the row div
        $(worldViewSelector).append('<div class="world_row" id="' + createRowID(rowNum) + '"></div>');

        for (var colNum = 0; colNum < cols; colNum++) {
          var cellSelector = '#' + createCellID(rowNum, colNum);
          // Creating the cell
          //console.log(createCellID(rowNum, colNum));
          if (world[rowNum][colNum].length == 2) {
            // Icon is using new format
            $('#' + createRowID(rowNum)).append('<div class="cell" id="' + createCellID(rowNum, colNum) + '">' + world[rowNum][colNum][0] + '</div>');
            $(cellSelector).css('color', world[rowNum][colNum][1]);
          } else {
            $('#' + createRowID(rowNum)).append('<div class="cell" id="' + createCellID(rowNum, colNum) + '">' + world[rowNum][colNum] + '</div>');
          }
        }
      }
    } else {
      //console.log("Updating world");
      for (var rowNum = 0; rowNum < rows; rowNum++) {
        for (var colNum = 0; colNum < cols; colNum++) {
          var cellSelector = '#' + createCellID(rowNum, colNum);
          if (world[rowNum][colNum].length == 2) {
            // Icon is using new format
            $(cellSelector).html(world[rowNum][colNum][0]);
            $(cellSelector).css('color', world[rowNum][colNum][1]);
          } else {
            $('#' + createCellID(rowNum, colNum)).html(world[rowNum][colNum]);
          }
        }
      }
    }
  },
  DrawPlayerStats: function(stats) {
    if (stats == '') {
      return false;
    }

    this.playerStatView.currentHealth.text(stats.health);
    this.playerStatView.healthCap.text(stats.health_cap);
    this.playerStatView.attackPower.text(stats.attack_power);
    this.playerStatView.row.text(stats.row);
    this.playerStatView.column.text(stats.col);
    this.playerStatView.ore.text(stats.ore_quantity);
    this.playerStatView.miningMultiplier.text(stats.ore_multiplier);
    this.playerStatView.worldAge.text(stats.world_age);
    this.playerStatView.modifierKey.text(stats.modifier_key);
    this.infoView.modeMeaning.text(this.infoView.modeMeanings[stats.modifier_key] || 'Unknown');
    this.playerStatView.secondaryModifierKey.text(stats.secondary_modifier_key);
  },
  Draw: function(data){
    if (data.world != '') {
      var world_json = copy(data.world);
      world_json.pop();
      world_json.pop();
      this.DrawWorldView(world_json);
    }

    this.DrawInventory(data.inventory);
    this.DrawPlayerStats(data.vitals);
  },
  Poll: function(){
    var self = this;
    setTimeout(function() {
      //console.log(typeof(View.prototype.Poll));
      app.GetDisplay(function() {
        self.Poll();
      });
    }, self.pollDelay);
  },
  SetupInput: function() {
    // For handling shift modifier
    var shiftCode = 16;
    $(document).on("keyup keydown", function(e) {
      switch(e.type) {
        case "keydown" :
          if (e.keyCode == shiftCode) {
            app.SendCommand("shiftDown");
          }
          break;
        case "keyup" :
          if (e.keyCode == shiftCode) {
            app.SendCommand("shiftUp");
          }
          break;
      }
    });
    // For handling dir & mod keys
    $("body").keypress(function(e){
      command = String.fromCharCode(e.which).toLowerCase();

      //console.log(app.actionsLut);
      app.SendCommand(command);
    });

  }
}

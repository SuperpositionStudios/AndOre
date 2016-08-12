//This lets us make different kinds of ais

var BaseAi = function(app) {
  this.app = app;
};

BaseAi.prototype = {
  app: null,
  actions: [
      "a",  // Direction Key
      "w",  // Direction Key
      "s",  // Direction Key
      "d",  // Direction Key
      "b",
      "l",  // Primary Modifier Key
      "k",  // Primary Modifier Key
      "m", // Primary Modifier Key
      "1","2","3","4","5","6","7",
  ],
  charCount: 256,
  charLookup: {},
  lastHealth: 0,
  lastAge: 0,
  lookRadius: 10,
  hasActed: false,
  lastAction: null,
  lastVitals: null,
  /* needed for ai lib */
  getNumStates: function() { return this.GetDataSize(); },
  getMaxNumActions: function() { return this.actions.length; },
  allowedActions: function() {
    var allowed = [];
    for(var i = 0; i < this.actions.length; i++) {
      allowed.push(i);    
      return allowed;
    }
  },
  /* needed for ai lib */

  GetDataSize: function() {
    return this.charCount * 4;

  },
  GetModel: function() {
    var self = this;
    var data = {
        'mid': prompt("What is the AI's Name?")
    };
    ai_name = data['mid'];
    if(use_ai_storage_server){
      $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          url: ai_storage_endpoint + "/retrieve",
          data: JSON.stringify(data),
          success: function(_data) {
              console.log(_data);
              self.oldBrain = JSON.parse(_data['model']);
              console.log("Retrieved and saved AI Model into memory");
              self.Start();
          }
      });
    } else {
      self.StartAi();
    }
  },
  Start: function() {
    //this.actions = this.actions.length > 0? this.actions : this.app.actions;
    var spec = { alpha: 0.01 };
    this.agent = new RL.DQNAgent(this, spec);
    if(this.oldBrain != null){
      this.agent.fromJSON(this.oldBrain);
      console.log("Parsed stored model into Agent.");
    }
    this.app.view.SetupRewardListener(this);
    this.StartTicks();
  },
  SendCommand(command){
    //does nothing right now, going to put in some AI specific commands
    
  },
  GiveSugar: function() {
    this.sugar = 5;

  },
  StartTicks: function(){
    var self = this;
    var repeat;
    repeat = function() {
      var command;
      if(self.lastAction == null){
        command = self.actions[0];
      } else {
        command = self.actions[self.lastAction];
      }
      AjaxCall("/action", {id: self.app.gameId, action: command, sendState:true}, function(data){
        var worldAge = data.vitals.world_age;
        if (worldAge > self.lastAge) {
          console.log(data.world);
          self.Update(data, repeat);
        } else {
          setTimeout(repeat, self.app.delay);
        }
      }, repeat);
    };
    repeat();
  },

  UploadModel: function(model) {
    console.log("Uploading Model...");
    var ai_model = model;
    data = {
        'mid': ai_name,
        'model': ai_model
    };
    if(!internetOff){
      $.ajax({
        url: ai_storage_endpoint + "/upload",
        type: "POST",
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(_data) {
          console.log(_data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.log("Error uploading the model");
        }
      });
    }
  },
  GetReward: function(data) {
    var maxReward = 1;
    this.lastVitals = data.vitals;
    this.lastHealth = data.vitals.health;
    var deltaHealth = data.vitals.health - this.lastHealth;
    var oreReward = Math.abs(data.vitals.delta_ore);
    var healthReward = deltaHealth - (deltaHealth < 10? 0.5 : 0);
    var reward = oreReward + healthReward;


    if(this.health >= 99) {
      reward = 0;
    }

    if(this.sugar > 0){
      reward += this.sugar;
      this.sugar = 0;
    }
    if(reward > maxReward){
      maxReward = reward;
    }
    reward /= maxReward;
    return reward;

  },
  Update: function(data, callback) {
    this.tickCount++;
    var worldView = this.worldView;
    if(this.lastVitals == null){
      this.lastVitals = data.vitals;
    }
    var world = data.world;
    if(data.world == "") {
      world = this.lastWorld;
    }
    this.world = world;
    
    worldView.Update(world, data.vitals);
    var state = worldView.GetEyesView(data.vitals.col, data.vitals.row);
    this.lastAge = data.vitals.world_age;
    this.lastVitals = data.vitals;
    this.lastHealth = data.vitals.health;

    var reward = this.GetReward(data);

    if(this.lastAction != null){
      this.agent.learn(reward);
    } else {
      this.agent.act(state);
    }

    var action = this.agent.act(state);
    if(this.lastAction != action){
      this.newAction = true;
    } else {
      this.newAction = false;
    }
    this.lastWorld = world;
    this.lastAction = action;
    this.UploadModel(this.agent.toJSON());
    callback();
  }

};

SimpleAi = function(app) {
  this.app = app;
  this.worldView = new AiWorldView(this.GetDataSize());
};
SimpleAi.prototype = $.extend(BaseAi.prototype, {
  tickCount: 0,
  lookRadius:2,
});

function AiWorldView(maxWidth, maxHeight) {
  this.maxWidth = maxWidth;
  this.maxHeight = maxHeight;
  this.dataSize = maxWidth * maxHeight;
  this.charCount = 256;
}

AiWorldView.prototype = {
  maxWidth: 0,
  maxHeight: 0,
  charLookup: {},
  Update: function(world, vitals){
    this.world = world;
    this.vitals = vitals;
    this.charLookup = {};
    var state = [];
    var y = 0;
    for (var i in world) {
      var line = world[i];
      x = 0;
      for (var key in line){
        var c = line[key][0].charCodeAt(0);
        this.CheckAddChar(c, x, y);
        x++;
      };
      y++;
    }
    //this.maxHeight = y - 1;
    //this.maxWidth = x - 1;
  },
  CheckAddChar: function(character, x, y){
    var currentArray = this.charLookup[character];
    if(currentArray == null){
      currentArray = [];
      this.charLookup[character] = currentArray;
    }
    currentArray.push({x: x, y: y});
  },
  GetFlatView: function(lookRadius) {
    var world = this.world;
    var y = 0;
    var state = [];
    var playerY = this.vitals.row;
    var playerX = this.vitals.col;
    var top = playerY - lookRadius;
    var bottom = playerY + lookRadius;
    var left = playerX - lookRadius;
    var right = playerY + lookRadius;


    for (var y = top; y < bottom; y++) {
      for (var x = left; x < right; x ++){
        if(world != null && world[y] != null && world[y][x] != null) {
          var c = world[y][x][0];
          
        } else {
          state.push[0];
        }
        x++;
      };
      y++;
    }
    while( state.length < this.dataSize) {
      state.push(" ");
    }
    while( state.length > this.dataSize) {
      state.pop();
    }
    return state;
  },
  GetEyesView: function(playerX, playerY) {
    var wasd = {
      w: this.MakeInputArray(this.GetCharAt(playerX, playerY - 1)),
      a: this.MakeInputArray(this.GetCharAt(playerX - 1, playerY)),
      s: this.MakeInputArray(this.GetCharAt(playerX, playerY + 1)),
      d: this.MakeInputArray(this.GetCharAt(playerX + 1, playerY)),
    };
    return [].concat(wasd.w)
      .concat(wasd.a)
      .concat(wasd.s)
      .concat(wasd.d);
  },
  GetCharAt: function(x, y){
    if(x < 0 || x > this.maxWidth) {
      return "";
    }
    if(y < 0 || y > this.maxHeight) {
      return "";
    }
    return this.world[y][x][0];
  },
  MakeInputArray: function(character) {
    var out = [];
    var asciiVal = character.charCodeAt(0);
    for(var i = 0; i < this.charCount; i++){
      out[i] = (i == asciiVal?  1 : 0);
    }
    return out;
  } 
}

Clamp = function(x, xmax, xmin){
  var out =  Math.max(x, xmin);
  out = Math.min(out, this.xmax);
  return out;
}

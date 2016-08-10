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
      "m"  // Primary Modifier Key
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
    return this.lookRadius * this.lookRadius * this.charCount;

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
    this.StartTicks();
  },
  SendCommand(command){
    //does nothing right now, going to put in some AI specific commands
    
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

  UploadModel: function(ai_model) {
    console.log("Uploading Model...");
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

    this.lastVitals = data.vitals;
    this.lastHealth = data.vitals.health;
    var deltaHealth = data.vitals.health - this.lastHealth;
    var oreReward = Math.abs(data.vitals.delta_ore);
    var healthReward = deltaHealth - (deltaHealth < 10? 30 : 0);
    var reward = oreReward + healthReward;


    if(this.lastHealth < 10) {
      reward = -5;
    }
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
    var state = worldView.GetFlatView(this.lookRadius);
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

function AiWorldView(dataSize) {
  this.dataSize = dataSize;
}
AiWorldView.prototype = {
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
  }
}

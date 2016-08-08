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
      "l",  // Primary Modifier Key
      "k",  // Primary Modifier Key
      "m"  // Primary Modifier Key
  ],
  charLookup: {},
  lastHealth: 0,
  lastAge: 0,
  lookRadius: 10,
  hasActed: false,
  lastAction: null,
  lastVitals: null,
  GetDataSize: function() {
    return this.lookRadius * this.lookRadius;

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
  NewEnv: function() {
    var self = this;
    return {
      getNumStates: function() { return self.lookRadius * self.lookRadius; },
      getMaxNumActions: function() { return self.actions.length; },
      allowedActions: function() {
        var allowed = [];
          for (var i = 0; i < self.actions.length; i++) {
            allowed.push(i);
          }
          return allowed;
        }
    }
  },
  Start: function() {
    //this.actions = this.actions.length > 0? this.actions : this.app.actions;
    this.env = this.NewEnv();
    var spec = { alpha: 0.01 };
    this.agent = new RL.DQNAgent(this.env, spec);
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
        //console.log(data);
        var worldAge = data.vitals.world_age;
        if (worldAge > self.lastAge) {
          console.log(data.world);
          self.Update(data, repeat);
          app.view.Draw(data);
        } else {
          app.view.Draw(data);
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
  Update: function(data, callback) {
    var env = this.env;

    if(this.lastVitals == null){
      this.lastVitals = data.vitals;
    }

    this.lastAge = data.vitals.world_age;

    var state = this.FlattenWorld(data.world, data.vitals);
    var deltaHealth = data.vitals.health - this.lastHealth;
    var reward = (data.vitals.delta_ore * 2 + deltaHealth * 1) / 3;
    console.log(data.vitals);
    /*
    if (data.vitals.row == this.lastVitals.row && data.vitals.col == this.lastVitals.col){

    } else {
      reward += 0.2;
    }

    */
    this.lastVitals = data.vitals;

    this.lastHealth = data.vitals.health;

    if(this.lastHealth < 10) {
      reward = -5;
    }

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
    this.lastAction = action;
    callback();
  },
  FlattenWorld: function(world, lastVitals){
    var charLookup = {};

    var state = [];
    var playerX = lastVitals.col;
    var playerY = lastVitals.row;
    var lookRadius = this.lookRadius;

    function checkAddChar(character, x, y){
      var currentArray = charLookup[character];
      if(currentArray == null){
        currentArray = [];
      }
      currentArray.push({x: x, y: y});
    }
    var y = 0;
    for (var i in world) {
      var line = world[i];
      x = 0;
      for (var key in line){
        var c = line[key][0].charCodeAt(0);
        checkAddChar(c);
        if(Math.abs(x - playerX) <= lookRadius && Math.abs(y - playerY <= lookRadius)) {
          state.push(c);
        }
        x++;
      };
      y++;
    }

    while( state.length < this.GetDataSize()){
      state.push(" ");
    }
    while( state.length > this.GetDataSize()){
      state.pop();
    }
    this.charLookup = charLookup;
    return state;
  }
};

SimpleAi = function(app) {
  this.app = app;
  //this.actions = [];
  //this.actions.concat(this.directionActions);
  //this.actions.concat(this.modeActions);
};
SimpleAi.prototype = $.extend(BaseAi.prototype, {
  tickCount: 0,
  lookRadius:2,
  directionActions: ["a","w","s","d"],
  modeActions: ["l", "k", "m", "b",],
  numberActions: ["0","1","2","3","4","5"],
  NewEnv: function() {
    var self = this;
    return {
      getNumStates: function() { return self.GetDataSize(); },
      getMaxNumActions: function() { return self.actions.length; },
      allowedActions: function() {
        var allowed = [];
        for(var i = 0; i < self.actions.length; i++) {
          allowed.push(i);    
          return allowed;
        }
      }
    }
  },
  Update: function(data, callback) {
    var env = this.env;
    this.tickCount++;
    if(this.lastVitals == null){
      this.lastVitals = data.vitals;
    }
    var world = data.world;
    if(data.world == "") {
      world = this.lastWorld;
    }
    this.lastAge = data.vitals.world_age;
    var state = this.FlattenWorld(world, data.vitals);
    var deltaHealth = data.vitals.health - this.lastHealth;
    var oreReward = Math.abs(data.vitals.delta_ore);
    var healthReward = deltaHealth - (deltaHealth < 10? 30 : 0);
    var reward = oreReward + healthReward;
    //console.log(data.vitals);


    this.lastVitals = data.vitals;

    this.lastHealth = data.vitals.health;
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
});


Nanny = function(){

}

Nanny.prototype = {

}

SimpleAi.prototype.prototype = BaseAi.prototype;

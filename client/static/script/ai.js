//This lets us make different kinds of ais




var BaseAi = function(app) {
  this.app = app;
}

BaseAi.prototype = {
  app: null,
  actions: [
      "a",  // Direction Key
      "w",  // Direction Key
      "s",  // Direction Key
      "d",  // Direction Key
      "l",  // Primary Modifier Key
      "k",  // Primary Modifier Key
      "m",  // Primary Modifier Key
  ],
  dataSize: 1024,
  lastHealth: 0,
  lastAge: 0,
  hasActed: false,
  lastAction: null,
  lastVitals: null,
  GetModel: function() {
    var self = this;
    data = {
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
          },
      });
    } else {
      self.StartAi();
    }
  },
  NewEnv: function() {
    var self = this;
    return {
      getNumStates: function() { return self.dataSize; },
      getMaxNumActions: function() { return self.actions.length; },
      allowedActions: function() {
        var allowed = [];
          for (var i = 0; i < self.actions.length; i++) {
            allowed.push(i);
          }
          return allowed;
        },
    }
  },
  Start: function() {
    this.actions = this.actions.length > 0? this.actions : this.app.actions;
    this.env = this.NewEnv();
    //var oldBrain = localStorage.getItem("aiModel");
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
      AjaxCall("/action", {id: userId, action: command, sendState:true}, function(data){
        var worldAge = data.vitals.world_age;
        if (worldAge > self.lastAge) {
          console.log(worldAge);
          app.view.Draw(data);
          self.Update(data, repeat);
        } else {
          app.view.Draw(data);
          setTimeout(repeat, self.delay);
        }
      }, repeat);
    }
    repeat();
  },

  UploadModel: function(ai_model) {
    console.log("Uploading Model...");
    data = {
        'mid': ai_name,
        'model': ai_model
    }
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

    var state = this.FlattenWorld(data.world);
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
  FlattenWorld: function(world){
    var state = [];
    var playerX = 0;
    var playerY = 0;
    var y = 0;
    for (var i in world){
      var line = world[i];
      x = 0;
      for (var key in line){
        var c = line[key][0].charCodeAt(0);
        state.push(c);
        if(c == '@') {
          playerX = x;
          playerY = y;
        }
        x++;
      };
      y++;
    }
    while( state.length < this.dataSize){
      state.push(" ");
    }
    while( state.length > this.dataSize){
      state.pop();
    }
    return state;
  }
}

SimpleAi = function(app) {
  this.app = app;
}
SimpleAi.prototype = $.extend(BaseAi.prototype, {
  tickCount: 0,
  directionActions: ["a","w","s","d"],
  modeActions: [
  [
    "l", "k", "m", "b",
  ],
  numberActions: [
    "0","1","2","3","4","5"
  ],
  NewEnv: function() {
    var self = this;
    return {
      getNumStates: function() { return self.dataSize; },
      getMaxNumActions: function() { return self.actions.length; },
      allowedActions: function() {
        var allowed = [];
          for (var i = 0; i < self.actions.length; i++) {
            if(self.tickCount % 4 == 0 ) {
              if( i < 4){
                allowed.push(i);
              }
            } else {
              if( i >= 4){
                allowed.push(i);
              }
            }
          }
          return allowed;
        },
    }
  },
  Update: function(data, callback) {
    var env = this.env;
    this.tickCount++;
    if(this.lastVitals == null){
      this.lastVitals = data.vitals;
    }

    this.lastAge = data.vitals.world_age;
    var state = this.FlattenWorld(data.world);
    var deltaHealth = data.vitals.health - this.lastHealth;
    var oreReward = Math.abs(data.vitals.delta_ore);
    var healthReward = deltaHealth - (deltaHealth < 10? 30 : 0);
    var reward = oreReward + healthReward;
    console.log(data.vitals);


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
    this.lastAction = action;
    callback();
  },
});

SimpleAi.prototype.prototype = BaseAi.prototype


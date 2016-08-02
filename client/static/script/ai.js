//This lets us make different kinds of ais




BaseAi = function(app) {
  this.app = app;
}

BaseAi.prototype = {
  app: null,
  actions: [], 
  dataSize: 1024,
  lastHealth: 0,
  hasActed: false,
  lastAction: null,
  lastVitals: null,
  GetModel: function() {
    var self = this;
    data = {
        'mid': prompt("What is the AI's Name?")
    };
    ai_name = data['mid'];
    if(use_ai_storage){
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
              self.StartAi();
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
      allowedActions: function() { return self.actions; },
    }
  },
  Start: function() {
    console.log(this.app.keys);
    this.actions = this.actions.length > 0? this.actions : this.app.actions;
    this.env = this.NewEnv();
    //var oldBrain = localStorage.getItem("aiModel");
    var spec = { alpha: 0.01 };
    this.agent = new RL.DQNAgent(self.env, spec);  
    if(this.oldBrain != null){
      this.agent.fromJSON(this.oldBrain);
      console.log("Parsed stored model into Agent.");
    }
    this.AiTick();
  },
  Tick: function(){
    var self = this;
    var repeat;
    repeat = function() {
      var command = self.keys[self.lastAction];
      AjaxCall("/action", {id: userId, action: command, sendState:true}, function(data){ 
        var worldAge = data.vitals.world_age;
        if (worldAge > self.lastAge) {
          view.Draw(data.world);
          self.UpdateAi(data, repeat);
        } else {
          view.Draw(data.world);
          setTimeout(repeat, self.delay);
        }
      }, repeat);
    }
    repeat();
  },
  Update: function(data) {
    var env = this.env;

    if(this.lastVitals == null){
    this.lastVitals = data.vitals;
    }

    this.lastAge = data.vitals.world_age;
      
    var state = this.FlattenWorld(data.world);
    var deltaHealth = data.vitals.health - this.lastHealth;
    var reward = (data.vitals.delta_ore * 2 + deltaHealth * 1) / 3;

    if (data.vitals.row == this.lastVitals.row && data.vitals.col == this.lastVitals.col){
      reward -= 0.5;
    } else {
      reward += 0.2;
    }


    this.lastVitals = data.vitals;

    this.lastHealth = data.vitals.health;

    if(this.lastHealth < 10) {
      reward = -5;
    }

    if(this.lastAction != null){  
      this.agent.learn(reward);      
    }

    var action = this.agent.act(this.state);
    if(this.lastAction != action){
      this.newAction = true;
    } else {
      this.newAction = false;
    }
    this.lastAction = action;    
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
  FlattenWorld: function(world){
    var state = [];
    for (var i in world){
      var line = world[i];
      for (var key in line){
        state.push(line[key].charCodeAt(0));
      }    
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




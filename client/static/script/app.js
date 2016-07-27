//load view.js before running this
//var apiUrl = "http://andore.iwanttorule.space:7001";
//also uses rl.js -- http://cs.stanford.edu/people/karpathy/reinforcejs/

var apiUrl = "http://localhost:7001";

var internetOff = false;

var app = {
  delay: 10,
  hasActed: false,
  userId: null,
  startAiKey: '~',
  env: {},
  tick: 0,
  newAction: false,
  keys: ["a", "w", "s", "d"],
  actions: [0, 1, 2, 3],
  lastAction: "a",
  lastHealth: 100,
  lastAge: 0,
  Init: function() {
  	app.GetUserId(function(){
  		view.SetupView(app.GetDisplay);
  	});
  },


  GetUserId:function(callback) {
    var self = this;
    AjaxCall("/join", {sendState: false}, function(data) {
      userId = data.id;
      $("body").keypress(function(e) {
        if (String.fromCharCode(e.which) == self.startAiKey) {
            self.StartAi();
        }
      });
      CallCallback(callback);
    });
  },
  GetDisplay: function(callback) {
  	AjaxCall("/sendState", {id: userId}, function(data){
      view.Draw(data.world);
  		CallCallback(callback);
  	});
  },
  SendCommand: function(command){
    AjaxCall("/action", {id: userId, action: command, sendState:true}, function(data){ 
      view.Draw(data.world);
    });
  },

  StartAi: function(){
    var self = this;
    this.env.getNumStates = function() { return 1024; }
    this.env.getMaxNumActions = function() { return self.actions.length; }
    this.env.allowedActions = function() { return self.actions; }

    var oldBrain = localStorage.getItem("aiModel");
    var spec = { alpha: 0.01 };
    this.agent = new RL.DQNAgent(self.env, spec);  
    if(oldBrain != null){
      this.agent.fromJSON(JSON.parse(oldBrain));
    }
    this.AiTick(); 
  },
  AiTick: function(){
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
  UpdateAi: function(data, callback){
    var env = this.env;

      if(this.lastVitals == null){
	  this.lastVitals = data.vitals;
      }
    this.lastAge = data.vitals.world_age;
      
    var states = FlattenWorld(data.world);
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

    var oldBrain = localStorage.getItem("aiModel");
    if(oldBrain != null){
      this.agent.fromJSON(JSON.parse(oldBrain));
    }

    if(this.hasActed){  
      this.agent.learn(reward);      
    }
    var action = this.agent.act(this.actions);
    if(this.lastAction != action){
      this.newAction = true;
    } else {

      this.newAction = false;
    }
    this.hasActed = true;
    this.lastAction = action;
    console.log(this.agent.toJSON());
    localStorage.setItem("aiModel",JSON.stringify(this.agent.toJSON()));
    setTimeout(callback, self.delay);
  } 
}

function CallCallback (callback){
  if(callback != null) {
    callback();
  }
}


function FlattenWorld(world){
  var state = [];
  for (var i in world){
    var line = world[i];
    for (var key in line){
      state.push(line[key].charCodeAt(0));
    }    
  }
  while( state.length < 1024){
    state.push(" ");
  }
  while( state.length > 1024){
    state.pop();
  }
  return state;

}
function AjaxCall(endpoint, data, callback, failCallback){
  if(internetOff){
    callback(testData);    
  }

  var ajax = $.ajax({
    method: "GET",
    url: apiUrl + endpoint,
    data: data,
  });
  ajax.done(function(data) {
    //console.log("from " + apiUrl + endpoint + " returned: " + data);
    callback(data);
  });
  ajax.fail(function(req, status, error){
    //console.log("bad req to " + apiUrl + endpoint + ":  " + status + " | " + error);
    if(failCallback != null){

      failCallback();      
    }
  });
}

var testData = {"id":"49f282b5-6ac9-4705-a692-fa1c23809f87","world":[["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!","!"],["h","p",":"," ","1","0","0"," ","o","r","e",":"," ","0"," ","r","o","w",":"," ","2","4"," ","c","o","l",":"," ","2","4"," "]]}


$(app.Init);

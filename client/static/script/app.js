//load view.js before running this
//also uses rl.js -- http://cs.stanford.edu/people/karpathy/reinforcejs/

var productionServerUrl = "http://ao.iwanttorule.space";
var production_game_server_endpoint = "/game-server";
var production_ai_storage_endpoint = "/ai-storage-server";
var production_auth_server_endpoint = "/auth";

var devServerUrl = "http://localhost";
var dev_game_server_endpoint = ":7001";
var dev_ai_storage_endpoint = ":7003";
var dev_auth_server_endpoint = ":7004";

var use_dev_server = true;  // Used for development
var use_ai_storage_server = true;
var internetOff = false;  // Used for testing view.js with testData.js

var ai_name = '';

var game_server_endpoint = null;
var ai_storage_endpoint = null;
var auth_server_endpoint = null;

if (use_dev_server) {
  game_server_endpoint = devServerUrl + dev_game_server_endpoint;
  ai_storage_endpoint = devServerUrl + dev_ai_storage_endpoint;
  auth_server_endpoint = devServerUrl + dev_auth_server_endpoint;
} else {
  game_server_endpoint = productionServerUrl + production_game_server_endpoint;
  ai_storage_endpoint = productionServerUrl + production_ai_storage_endpoint;
  auth_server_endpoint = productionServerUrl + production_auth_server_endpoint;
}

function ArrayToKeys(inArray) {
  var out = {};
  for (i in inArray){
    out[inArray[i].toString()] = true;
  }
  return out;
}

function App() {


}
App.prototype = {
  delay: 10,
  hasActed: false,
  authId: null,
  gameId: null,
  startAiKey: '~',
  AiStarted: false,
  oldBrain: '',
  repeats: 0,  // Times updateAI has been called since last upload
  repeatsUntilUpload: 50, // Times updateAI has to be called until the model is saved on the AI storage server
  env: {},
  tick: 0,
  newAction: false,
  actions: [
    "a", // Direction Key
    "w", // Direction Key
    "s", // Direction Key
    "d", // Direction Key
    "k", // Primary Modifier Key
    "l", // Primary Modifier Key
    "m", // Primary Modifier Key
    "i", // Primary Modifier Key
    "-", // Primary Modifier Key
    "+", // Primary Modifier Key
    "b", // Primary Modifier Key
    "u", // Primary Modifier Key
    "0", // Secondary Modifier Key
    "1", // Secondary Modifier Key
    "2", // Secondary Modifier Key
    "3", // Secondary Modifier Key
    "4", // Secondary Modifier Key
    "5", // Secondary Modifier Key
    "6", // Secondary Modifier Key
    "7", // Secondary Modifier Key
    "8", // Secondary Modifier Key
    "9"  // Secondary Modifier Key
  ],
  lastAction: "a",
  lastHealth: 100,
  lastAge: 0,
  Init: function() {
    var self = this;
    this.actionsLut = ArrayToKeys(this.actions);
    /*
  	this.GetUserId(function(){
      self.view = new View();
      self.view.SetupView(this, App.GetDisplay);
  	});*/
    self.GetAuthId(function() {
      self.GetGameId(function() {
        self.ListenToStartAi(function() {
          self.view = new View();
          self.view.SetupView(this, App.GetDisplay);
        });
      });
    })
  },
  GetAuthId: function (callback) {
    var self = this;
    $('#modal1').openModal({
      dismissible: false
    });
    $('#login').click(function() {
      var username = $('#login_username').val();
      var password = $('#login_password').val();
      var data = {
        username: username,
        password: password
      };
      $.ajax({
        method: 'POST',
        url: auth_server_endpoint + '/account/login',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            self.authId = data['uid'];
            $('#modal1').closeModal();
            CallCallback(callback);
            //console.log(auth_id);
          } else {
            console.log(data);
          }
        }

      });
    });
    $('#signup').click(function() {
      var username = $('#signup_username').val();
      var password = $('#signup_password').val();
      var data = {
        username: username,
        password: password
      };
      $.ajax({
        method: 'POST',
        url: auth_server_endpoint + '/account/create',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            self.authId = data['uid'];
            $('#modal1').closeModal();
            CallCallback(callback);
            //console.log(auth_id);
          } else {
            console.log(data);
          }
        }

      });
    });
  },
  GetGameId: function (callback) {
    var self = this;
    $('#modal2').openModal({
      dismissible: false
    });

    $('#rejoin_game').click(function() {
      var data = {
        uid: self.authId
      };
      $.ajax({
        method: 'POST',
        url: auth_server_endpoint + '/game/rejoin',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            self.gameId = data['game-id'];
            $('#modal2').closeModal();
            CallCallback(callback);
          } else {
            console.log(data);
          }
        }

      });
    });
    $('#start_anew').click(function() {
      var data = {
        uid: self.authId
      };
      $.ajax({
        method: 'POST',
        url: auth_server_endpoint + '/game/join',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            self.gameId = data['game-id'];
            $('#modal2').closeModal();
            CallCallback(callback);
          } else {
            console.log(data);
          }
        }

      });
    });
  },
  ListenToStartAi:function(callback) {
    var self = this;

    $("body").keypress(function(e) {
      if (String.fromCharCode(e.which) == self.startAiKey && self.AiStarted == false) {
        self.ai = new SimpleAi(self);
        if(use_ai_storage_server)  {
          self.ai.GetModel();
        }else {
          self.ai.Start();
        }
        self.AiStarted = true;
      }
    });
    CallCallback(callback);
  },
  GetDisplay: function(callback) {
    var self = this;
    var view = this.view;
  	AjaxCall("/sendState", {id: self.gameId}, function(data){
      view.Draw(data);
      CallCallback(callback);
  	});
  },
  SendCommand: function(command){
    var self = this;
    var view = this.view;
    AjaxCall("/action", {id: self.gameId, action: command, sendState:true}, function(data){
      view.Draw(data);
    });
  }
};

function CallCallback (callback){
  if(callback != null) {
    callback();
  }
}

function AjaxCall(endpoint, data, callback, failCallback){
  var server = game_server_endpoint;

  if(internetOff){
    callback(testData);
  }

  var ajax = $.ajax({
    method: "GET",
    url: server + endpoint,
    data: data
  });
  ajax.done(function(data) {
    //console.log("from " + server + endpoint + " returned: " + data);
    callback(data);
  });
  ajax.fail(function(req, status, error){
    console.log("bad req to " + server + endpoint + ":  " + status + " | " + error);
    if(failCallback != null){

      failCallback();
    }
  });
}


$(function(){
  app = new App();
  var ai = new BaseAi(app);
  app.Init();
});

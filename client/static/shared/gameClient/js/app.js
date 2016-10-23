//load view.js before running this
//also uses rl.js -- http://cs.stanford.edu/people/karpathy/reinforcejs/

/* Begin Settings */
var use_dev_server = true;  // Used for development
var use_ai_storage_server = true;
var internetOff = false;  // Used for testing view.js with testData.js
var useSecureHTTP = false;
var useSecureWS = false;
/* End Settings */

var productionDomain = "iwanttorule.space";
var productionSleipnirSubdomain = "sleipnir.";
var productionAbsolutionSubdomain = "absolution.";
var productionErebusSubdomain = "erebus.";
var productionSynergySubdomain = "synergy.";

var devServerUrl = "localhost";
var dev_master_node_endpoint = ":7100";
var dev_ai_storage_endpoint = ":7003";
var dev_auth_server_endpoint = ":7004";
var devSynergyEndpoint = ":7005";

var ai_name = '';

var absolutionURL = null;
var erebusURL = null;
var sleipnirURL = null;
var synergyURL = null;
var currentnodeURL = null;

if (use_dev_server) {
  if (useSecureHTTP) {
    sleipnirURL = "https://" + devServerUrl + dev_master_node_endpoint;
    absolutionURL = "https://" + devServerUrl + dev_ai_storage_endpoint;
    erebusURL = "https://" + devServerUrl + dev_auth_server_endpoint;
  } else {
    sleipnirURL = "http://" + devServerUrl + dev_master_node_endpoint;
    absolutionURL = "http://" + devServerUrl + dev_ai_storage_endpoint;
    erebusURL = "http://" + devServerUrl + dev_auth_server_endpoint;
  }

  if (useSecureWS) {
    synergyURL = "wss://" + devServerUrl + devSynergyEndpoint;
  } else {
    synergyURL = "ws://" + devServerUrl + devSynergyEndpoint;
  }
} else {
  if (useSecureHTTP) {
    sleipnirURL = "https://" + productionSleipnirSubdomain + productionDomain;
    absolutionURL = "https://" + productionAbsolutionSubdomain + productionDomain;
    erebusURL = "https://" + productionErebusSubdomain + productionDomain;
  } else {
    sleipnirURL = "http://" + productionSleipnirSubdomain + productionDomain;
    absolutionURL = "http://" + productionAbsolutionSubdomain + productionDomain;
    erebusURL = "http://" + productionErebusSubdomain + productionDomain;
  }

  if (useSecureWS) {
    synergyURL = "wss://" + productionSynergySubdomain + productionDomain;
  } else {
    synergyURL = "ws://" + productionSynergySubdomain + productionDomain;
  }
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
  delay: 300,
  hasActed: false,
  authId: null,
  gameId: null,
  synergyWS: null,
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
    "c", // Primary Modifier Key
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
    self.GetAuthId(function() {
      self.StartChat(function() {
        self.GetGameId(function() {
          self.GetNodeServer(function() {
            self.ListenToStartAi(function() {
              self.view = new View();
              self.view.SetupView(this, App.GetDisplay);
            });
          });
        });
      });
    });
  },
  StartChat: function(callback) {
    var self = this;

    var content = $('#chatBoxContent');
    var input = $('#chatBoxInput');
    var status = $('#chatBoxStatus');
    var validAid = false;

    self.synergyWS = new WebSocket('ws://localhost:7005');

    self.synergyWS.onopen = function () {
        self.synergyWS.send('/register ' + self.authId);
      status.text('Global Chat:');
    };


    self.synergyWS.onmessage = function (message) {
        try {
        var json = JSON.parse(message.data);
      } catch (e) {
        console.log('This doesn\'t look like a valid JSON: ', message.data);
        return;
      }
      if (validAid == false) {
        if (json.author == 'Synergy' && json.color == 'red') {
            if (json.message == 'Hello') {
            validAid = true;
            input.removeAttr('disabled');
          }
        }
      }
      addMessage(json.author, json.message, json.color);
    };

    input.keydown(function(e) {
      if (e.keyCode === 13) {
        var msg = $(this).val();
        if (!msg) {
          return;
        }
        // send the message as an ordinary text
        self.synergyWS.send('/chat ' + msg);
        $(this).val('');
      }
    });


    function addMessage(author, message, color) {
      content.prepend('<p><span style="color:' + color + '">' + author + '</span>: ' + message + '</p>');
    }
    CallCallback(callback);
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
      Materialize.toast("Logging in...!", 2000, 'rounded');
      $.ajax({
        method: 'POST',
        url: erebusURL + '/account/login',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            Materialize.toast("Logged in", 2000, 'rounded light-green accent-4');
            self.authId = data['uid'];
            $('#modal1').closeModal();
            CallCallback(callback);
            //console.log(auth_id);
          } else {
            console.log(data);
          }
        },
        error: function(jqXHR, exception) {
          if (jqXHR.status === 401) {
            Materialize.toast('Invalid Credentials', 3000, 'rounded red accent-4');
          } else {
            Materialize.toast('So something bad happened, but I don\'t exactly know what happened.', 3000, 'rounded red accent-4');
            console.log('Unknown Error. \n ' + jqXHR.responseText);
          }
        }
      });
    });
    $('#signup').click(function() {
      Materialize.toast("Signing up...", 2000, 'rounded');
      var username = $('#signup_username').val();
      var password = $('#signup_password').val();
      var data = {
        username: username,
        password: password
      };
      $.ajax({
        method: 'POST',
        url: erebusURL + '/account/create',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
          if (data['status'] == 'Success') {
            Materialize.toast("Signed up", 2000, 'rounded light-green accent-4');
            Materialize.toast("Logged in", 2000, 'rounded light-green accent-4');
            self.authId = data['uid'];
            $('#modal1').closeModal();
            CallCallback(callback);
            //console.log(auth_id);
          } else {
            console.log(data);
          }
        },
        error: function(jqXHR, exception) {
          if (jqXHR.status === 401) {
            Materialize.toast('Invalid Credentials', 3000, 'rounded red accent-4');
          } else {
            Materialize.toast('Unknown Error. \n ' + jqXHR.responseText, 3000, 'rounded red accent-4');
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
        url: erebusURL + '/game/rejoin',
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
        url: erebusURL + '/game/join',
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
  GetNodeServer:function(callback) {
    Materialize.toast("Finding our world...", 1000, 'rounded');
    var self = this;
    var data = {
      'id': self.gameId
    };
    $.ajax({
        method: 'GET',
        url: sleipnirURL + '/get_player_info',
        data: data,
        dataType: "json",
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        success: function(data) {
          if (data['status'] == 'Success') {
            Materialize.toast("Found our world!", 1000, 'rounded light-green accent-4');
            currentnodeURL = data['world']['server'];
            $('#currentNodeName').text(data['world']['name']);
            CallCallback(callback);
          } else {
            console.log(data);
          }
        }

      });
  },
  ListenToStartAi:function(callback) {
    var self = this;

    $("body").keypress(function(e) {
      if (String.fromCharCode(e.which) == self.startAiKey && self.AiStarted == false) {
        Materialize.toast("Starting Ai Mode!", 1500, 'rounded light-green accent-4');
        self.ai = new SimpleAi(self);
        if(use_ai_storage_server)  {
          self.ai.GetModel();
        } else {
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
    if(this.AiStarted) {
      self.ai.SendCommand(command);
    }
    if(app.actionsLut[command]) {
      AjaxCall("/action", {id: self.gameId, action: command, sendState:true}, function(data){
        view.Draw(data.world);
      });
    }
  }
};

function CallCallback (callback){
  if(callback != null) {
    callback();
  }
}

function AjaxCall(endpoint, data, callback, failCallback){
  var server = currentnodeURL;

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
  app.Init();
});

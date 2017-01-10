//load view.js before running this
//also uses rl.js -- http://cs.stanford.edu/people/karpathy/reinforcejs/

/* Begin Settings */
var use_dev_server = false; // Set back to false when comitting
var use_ai_storage_server = true;
var internetOff = false;  // Used for testing view.js with testData.js
var useSecureHTTP = false;  // Set to true if using https
var useSecureWS = false;  // Set to true if using wss
/* End Settings */

var ai_name = '';

var absolutionURL = null;
var erebusURL = null;
var sleipnirURL = null;
var synergyURL = null;
var currentnodeURL = null;

if (use_dev_server) {

	absolutionURL = "localhost:7003";
	erebusURL = "localhost:7004";
	synergyURL = "localhost:7005";
	sleipnirURL = "localhost:7100";

	if (useSecureHTTP) {
		absolutionURL = "https://" + absolutionURL;
		erebusURL = "https://" + erebusURL;
	} else {
		absolutionURL = "http://" + absolutionURL;
		erebusURL = "http://" + erebusURL;
	}

	if (useSecureWS) {
		synergyURL = "wss://" + synergyURL;
		sleipnirURL = "wss://" + sleipnirURL;
	} else {
		synergyURL = "ws://" + synergyURL;
		sleipnirURL = "ws://" + sleipnirURL;
	}

} else {

	absolutionURL = "absolution.andore.online";
	erebusURL = "erebus.andore.online";
	synergyURL = "synergy.andore.online";
	sleipnirURL = "sleipnir.andore.online/player";

	if (useSecureHTTP) {
		absolutionURL = "https://" + absolutionURL;
		erebusURL = "https://" + erebusURL;
	} else {
		absolutionURL = "http://" + absolutionURL;
		erebusURL = "http://" + erebusURL;
	}

	if (useSecureWS) {
		synergyURL = "wss://" + synergyURL;
		sleipnirURL = "wss://" + sleipnirURL;
	} else {
		synergyURL = "ws://" + synergyURL;
		sleipnirURL = "ws://" + sleipnirURL;
	}
}

function ArrayToKeys(inArray) {
	var out = {};
	for (i in inArray) {
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
	sleipnirWS: null,
	currentNodeWS: null,
	shiftKeyActive: false,
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
	Init: function () {
		var self = this;
		this.actionsLut = ArrayToKeys(this.actions);
		self.GetCynosuralVersion(null);
		self.GetAuthId(function () {
			self.StartChat(null);
			self.StartSleipnirWS(function () {
				self.ListenToStartAi(function () {
					self.view = new View();
					//self.view.SetupView(this, App.GetDisplay);
					self.view.SetupView(self, null);
				});
			});
		});
	},


	Ping: function () {
		// Requests the current node to send a Pong; Not used very frequently because it usually sends one by itself.
		var self = this;
		self.currentNodeWS.send(JSON.stringify({
			'request': 'ping'


		}));
	},
	GetCynosuralVersion: function (callback) {
		var self = this;

		$.ajax({
			method: 'GET',
			url: '/version',
			contentType: "application/json",
			success: function (data) {
				$('#client-git-version-text').text(data.git_version);
				$('#client-git-version-link').attr('href', 'https://github.com/AI-Productions/AndOre/commit/' + data.git_version);
				CallCallback(callback);
			},
			error: function (jqXHR, exception) {
				console.log("Cynosural: Failed to get git version");
			}
		});
	},
	StartChat: function (callback) {
		var self = this;

		var content = $('#chatBoxContent');
		var input = $('#chatBoxInput');
		var status = $('#chatBoxStatus');
		var validAid = false;

		self.synergyWS = new WebSocket(synergyURL);

		self.synergyWS.onopen = function () {
			self.synergyWS.send('/register ' + self.authId);
			status.text('Global Chat:');
		};


		self.synergyWS.onmessage = function (message) {
			try {
				var json = JSON.parse(message.data);
				console.log("Synergy: ", json);
			} catch (e) {
				console.log('This doesn\'t look like a valid JSON: ', message.data);
				return;
			}
			if (validAid == false) {
				if (json.author == 'Synergy' && json.color == 'red') {
					if (json.authenticated) {
						validAid = true;
						input.removeAttr('disabled');
					}
				}
			}
			addMessage(json.author, json.message, json.color);
		};

		input.keydown(function (e) {
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
		var stored_aid = localStorage.getItem('aid') || null;
		if (null == stored_aid) {
			window.location.replace('/auth/login');
		}

		$.ajax({
			method: 'GET',
			url: erebusURL + '/get/username',
			data: {
				'aid': stored_aid
			},
			dataType: "json",
			contentType: "application/json",
			success: function (data) {
				if (data['valid_aid']) {
					Materialize.toast("Logged in", 2000, 'rounded light-green accent-4');
					self.authId = stored_aid;
					CallCallback(callback);
				} else {
					console.log(data);
					window.location.replace('/auth/logout');
				}
			},
			error: function (jqXHR, exception) {
				if (jqXHR.status === 401) {
					Materialize.toast('Invalid Credentials', 3000, 'rounded red accent-4');
					window.location.replace('/auth/logout');
				} else {
					Materialize.toast('So something bad happened, but I don\'t exactly know what happened.', 3000, 'rounded red accent-4');
					console.log('Unknown Error. \n ' + jqXHR.responseText);
					window.location.replace('/auth/logout');
				}
			}
		});
	},

	StartSleipnirWS: function (callback) {
		var self = this;
		var authenticated = false;
		self.sleipnirWS = new WebSocket(sleipnirURL);
		console.log("aid: ", self.authId);
		self.sleipnirWS.onopen = function () {
			self.AlertConnectSlepnir();
			self.sleipnirWS.send(JSON.stringify({
				'request': 'register',
				'aid': self.authId
			}))
		};


		self.sleipnirWS.onclose = function () {
			self.AlertCloseSlepnir();
		};


		self.sleipnirWS.onmessage = function (message) {
			message = JSON.parse(message.data);
			console.log("Sleipnir: ", message);

			if (!authenticated && message.authenticated) {
				authenticated = true;
				self.FindCurrentNode(null);  // Join Game
			} else if (message.request == 'git_version') {
				$('#sleipnir-git-version-text').text(message.git_version);
				$('#sleipnir-git-version-link').attr('href', 'https://github.com/AI-Productions/AndOre/commit/' + message.git_version);
			} else if (message.request == 'update_node') {
				currentnodeURL = message.node_address;
				self.EstablishCurrentNodeWS(callback);
			} else if (message.request = 'numConnectedPlayers') {
				$('#number-of-players-online').text(message.numConnectedPlayers);
			}

		}
	},
	FindCurrentNode: function (callback) {
		var self = this;
		self.sleipnirWS.send(JSON.stringify({
			'request': 'join'
		}));
		CallCallback(callback);
	},
	EstablishCurrentNodeWS: function (callback) {
		var self = this;
		Materialize.toast("Finding our world...", 1000, 'rounded');
		if (self.currentNodeWS != null) {
			self.currentNodeWS.onclose = function () {
			};  // We reset the onclose function, or we get stuck in infinite loop.
			self.currentNodeWS.close()
		}
		self.currentNodeWS = new WebSocket(currentnodeURL);
		self.currentNodeWS.onmessage = function (message) {
			message = JSON.parse(message.data);
			//console.log("Region Node: ", message);

			if ('time' in message) {
				var sentTime = new Date(message.time);
				var receivedTime = new Date();
				//console.log('Region: Latency | ', 'Message Received At: ', receivedTime.getTime(), ' - ', 'Message Timestamp: ', sentTime.getTime(), ' = ', receivedTime.getTime() - sentTime.getTime());
				var roundTripLatency = (receivedTime.getTime() - sentTime.getTime()) * 2;
				$('#rtl').text(roundTripLatency);
			}

			if (message.request == 'sendState') {
				self.view.Draw(message);
			} else if (message.request == 'auth') {
				$('#currentNodeName').text(message.nodeName);
			} else if (message.request == 'send_state_client_render') {
				self.corpId = message.corp_id;
				self.view.ClientSideDraw(message);
			} else if (message.request == 'git_version') {
				$('#region-git-version-text').text(message.git_version);
				$('#region-git-version-link').attr('href', 'https://github.com/AI-Productions/AndOre/commit/' + message.git_version);
			}
		};

		self.currentNodeWS.onclose = function () {
			delete self.view;
			self.view = null;
			self.AlertCloseNode();
			self.FindCurrentNode(null);
		};

		self.currentNodeWS.onopen = function () {
			self.AlertConnectNode();
			self.currentNodeWS.send(JSON.stringify({
				'request': 'register',
				'aid': self.authId
			}));
			self.Ping();
			Materialize.toast("Found our world!", 1000, 'rounded light-green accent-4');
			console.log("(Re)Started View.");
			CallCallback(callback);  // callback always starts listening to AI & restarts view.
		};
	},
	AlertConnectNode: function () {
		$('#box_node').css('background-color', 'green');
	},
	AlertCloseNode: function () {
		$('#box_node').css('background-color', 'red');
	},
	AlertConnectSlepnir: function () {
		$('#box_sleipnir').css('background-color', 'green');
	},
	AlertCloseSlepnir: function () {
		$('#box_sleipnir').css('background-color', 'red');
	},
	ListenToStartAi: function (callback) {
		var self = this;

		$("body").keypress(function (e) {
			if (String.fromCharCode(e.which) == self.startAiKey && self.AiStarted == false) {
				Materialize.toast("Starting Ai Mode!", 1500, 'rounded light-green accent-4');
				self.ai = new SimpleAi(self);
				if (use_ai_storage_server) {
					self.ai.GetModel();
				} else {
					self.ai.Start();
				}
				self.AiStarted = true;
			}
		});
		CallCallback(callback);
	},
	/*GetDisplay: function(callback) {
	 var self = this;
	 var view = this.view;
	 self.currentNodeWS.send(JSON.stringify({
	 'request': 'send_state'
	 }));
	 CallCallback(callback);
	 },*/
	SendCommand: function (command) {
		var self = this;
		var view = this.view;
		/*if(this.AiStarted) {
		 self.ai.SendCommand(command);
		 }*/
		self.currentNodeWS.send(JSON.stringify({
			'request': 'action',
			'action': command,
			'shift_key_down': self.shiftKeyActive,
			'sendState': true
		}));
	}
};


function CallCallback(callback) {
	if (callback != null) {
		callback();
	}
}


$(function () {
	app = new App();
	app.Init();

	// User closed the tab; Emergency Disconnecting.
	window.onbeforeunload = function () {
		app.sleipnirWS.onclose = function () {
		}; // disable onclose handler first
		app.sleipnirWS.close();
		app.currentNodeWS.onclose = function () {
		};
		app.currentNodeWS.close();
		app.synergyWS.onclose = function () {
		};
		app.synergyWS.close();
	};
});

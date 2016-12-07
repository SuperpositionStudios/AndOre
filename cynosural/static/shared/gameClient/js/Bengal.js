function Bengal() {

}

Bengal.prototype = {
	currentServerResponse: null,
	aid: null,
	corp_id: null,
	standings: null,
	colors: {
		"M": "#147614",
		"A": "#04227C",
		"N": "#8C8A8C",
		"E": "#940604",
		"Nature": "#000000"
	},
	gameObjects: {
		1: {
			"name": "Fence",
			"icons": {
				"M": "#",
				"A": "#",
				"N": "#",
				"E": "#"
			},
			"render_type": 1,
			"owner": "undefined"
		},
		2: {
			"name": "Hospital",
			"icons": {
				"M": "⚕",
				"A": "⚕",
				"N": "⚕",
				"E": "⚕"
			},
			"render_type": 1,
			"owner": "undefined"
		},
		3: {
			"name": "OreGenerator",
			"icons": {
				"M": "🏭",
				"A": "🏭",
				"N": "🏭",
				"E": "🏭"
			},
			"render_type": 1,
			"owner": "undefined"
		},
		4: {
			"name": "Pharmacy",
			"icons": {
				"M": "🏥",
				"A": "🏥",
				"N": "🏥",
				"E": "🏥"
			},
			"render_type": 1,
			"owner": "undefined"
		},
		5: {
			"name": "RespawnBeacon",
			"icons": {
				"M": "𝌩",
				"A": "𝌩",
				"N": "𝌩",
				"E": "𝌩"
			},
			"render_type": 1,
			"owner": "undefined"
		},
		6: {
			"name": "Door",
			"icons": {
				"M": "=",
				"A": "=",
				"N": "=",
				"E": "="
			},
			"render_type": 2,
			"owner": "undefined"
		},
		7: {
			"name": "Player",
			"icons": {
				"S": "@",
				"M": "M",
				"A": "A",
				"N": "N",
				"E": "E"
			},
			"render_type": 5,
			"aid": "undefined",
			"owner": "undefined"
		},
		8: {
			"name": "Loot",
			"icon": "%",
			"render_type": 3
		},
		9: {
			"name": "SpikeTrap",
			"icons": {
				"M": "S",
				"A": "S",
				"N": "S",
				"E": "S"
			},
			"render_type": 2,
			"owner": "undefined"
		},
		10: {
			"name": "SentryTurret",
			"icons": {
				"M": "T",
				"A": "T",
				"N": "T",
				"E": "T"
			},
			"render_type": 2,
			"owner": "undefined"
		},
		11: {
			"name": "OreDeposit",
			"icon": "$",
			"render_type": 3
		},
		12: {
			"name": "StarGate",
			"icons": {
				'Panagoul': 'Ⓟ',
				'Ulysses': 'Ⓤ',
				'Toivo': 'Ⓣ',
				'Pedals': 'ⓟ',
				'Wojtek': 'Ⓦ',
				'Siwash': 'Ⓢ',
				'Scipio': 'ⓢ',
				'Voytek': 'Ⓥ'
			},
			"render_type": 4,
			"target_node": "undefined"
		}
	},
	Init: function (aid) {
		var self = this;
		console.log("Bengal: ", "Initializing...");
		self.aid = aid;
		console.log("Bengal: ", "aid: ", aid);
	},
	getStandingTowardsCorp: function (corp, towards_corp) {
		var self = this;

		if (corp == towards_corp) {
			return "M";
		} else {
			return (self.standings[corp] || {})[towards_corp] || "N";
		}
	},
	convertRawContentsToGameObjects: function (rawContents) {
		var self = this;

		var convertedContents = [];
		var object_types = {
			1: 1, // Fence
			2: 1,
			3: 1,
			4: 1,
			5: 1,
			6: 1,
			7: 4,  // Player
			8: 1,
			9: 1,
			10: 1,
			11: 2,  // OreDeposit
			12: 3 // StarGate
		};
		for (var i = 0; i < rawContents.length; i++) {
			var rawObject = rawContents[i];
			var rawObjectType = object_types[rawObject[0]] || null;

			var convertedObject = self.gameObjects[rawObject[0]];

			if (rawObjectType == 1) {
				convertedObject.owner = rawObject[1];
			} else if (rawObjectType == 2) {
				//
			} else if (rawObjectType == 3) {
				convertedObject.target_node = rawObject[1];
			} else if (rawObjectType == 4) {
				convertedObject.aid = rawObject[1];
				convertedObject.owner = rawObject[2];
			}
			convertedContents.push(convertedObject);
		}
		return convertedContents;
	},
	render_cell: function (contents) {
		var self = this;


		var render_priority = ['Player', 'Loot', 'SentryTurret', 'SpikeTrap', 'OreDeposit', 'Hospital', 'Pharmacy', 'OreGenerator', 'Fence', 'Door', 'RespawnBeacon', 'StarGate'];
		var icon;
		var color;

		for (var render_priority_i = 0; render_priority_i < render_priority.length; render_priority_i++) {
			var current_priority = render_priority[render_priority_i];
			for (var current_object_i = 0; current_object_i < contents.length; current_object_i++) {
				var current_object = contents[current_object_i];
				if (current_priority == current_object.name) {
					// This object will be rendered
					if (current_object.render_type == 1) {
						// For objects where the color is your standings towards the object owner
						var standings_towards_owner_corp = self.getStandingTowardsCorp(self.corp_id, current_object.owner);
						icon = current_object.icons[standings_towards_owner_corp];
						color = self.colors[standings_towards_owner_corp];

						return [icon, color];
					} else if (current_object.render_type == 2) {
						// For objects where the color is the standings of the object owner towards you
						var owner_standings_towards_you = self.getStandingTowardsCorp(current_object.owner, self.corp_id);
						icon = current_object.icons[owner_standings_towards_you];
						color = self.colors[owner_standings_towards_you];

						return [icon, color];
					} else if (current_object.render_type == 3) {
						// For items that don't have an owner (like Ore Deposits)
						icon = current_object.icon;
						color = self.colors["Nature"];

						return [icon, color];
					} else if (current_object.render_type == 4) {
						// For StarGates
						icon = current_object.icons[current_object.target_node] || "?";
						color = self.colors["Nature"];
						return [icon, color];
					} else if (current_object.render_type == 5) {
						// For Players
						//console.log(self.corp_id);
						if (current_object.aid == self.aid) {
							icon = current_object.icons["S"];
							color = self.colors["M"];
							return [icon, color];
						} else {
							//console.log(self.aid + " != " + current_object.aid);
							var standings_towards_owner_corp = self.getStandingTowardsCorp(self.corp_id, current_object.owner);
							icon = current_object.icons[standings_towards_owner_corp];
							color = self.colors[standings_towards_owner_corp];
							return [icon, color];
						}
					}
				} else {
					// Continue...
				}
			}
		}
		return [".", self.colors["N"]];
	},
	RenderWorld: function (newServerResponse) {
		var self = this;
		self.currentServerResponse = newServerResponse;
		self.standings = self.currentServerResponse.standings;
		self.corp_id = self.currentServerResponse.corp_id;

		var world = self.currentServerResponse.world;
		var rendered_world = [];
		for (var rowNum = 0; rowNum < world.length; rowNum++) {
			var rendered_row = [];
			for (var colNum = 0; colNum < world[rowNum].length; colNum++) {
				var cell = world[rowNum][colNum];
				var convertedContents = self.convertRawContentsToGameObjects(cell.contents);
				var rendered_cell = self.render_cell(convertedContents);
				rendered_row.push(rendered_cell);
			}
			rendered_world.push(rendered_row);
		}
		return rendered_world
	}
};

/*
 bengal = new Bengal();
 bengal.Init("bill", "a");

 var server_response = {
 "standings": {
 "a": {
 "b": "E",
 "c": "A"
 },
 "b": {
 "a": "E",
 "c": "A"
 },
 "c": {
 "a": "A",
 "b": "A"
 }
 },
 "world": [
 [
 {
 "contents": [
 [1, "c"]
 ]
 },
 {
 "contents": [
 [2, "b"]
 ]
 },
 {
 "contents": [
 [3, "c"]
 ]
 }
 ],
 [
 {
 "contents": [
 [4, "c"]
 ]
 },
 {
 "contents": [
 [5, "a"]
 ]
 },
 {
 "contents": [
 [6, "c"]
 ]
 }
 ],
 [
 {
 "contents": [
 [7, "aid", "c"]
 ]
 },
 {
 "contents": [
 [8, "a"]
 ]
 },
 {
 "contents": [
 [9, "c"]
 ]
 }
 ],
 [
 {
 "contents": [
 [10, "c"]
 ]
 },
 {
 "contents": [
 [11]
 ]
 },
 {
 "contents": [
 [12, "Panagoul"]
 ]
 }
 ]
 ]
 };
 console.log(bengal.RenderWorld(server_response));
 */
var apiUrl = "http://localhost:8080";
var internetOn = true;
var userId = null;


var Init = function($) {
	RetrieveUserId(function(){
		SetupInterface(GetDisplay);
	);
}


var GetUserId = function(callback) {

  CallCallback(callback);
}

var SetupInterface = function(callback) {

	CallCallback(callback);
}

var GetDisplay = function(callback) {
	AjaxCall("/sendState", {id: userId}, function(data){
		DisplayData(data);
		CallCallback(callback);
	});
}


var SendCommand = function(command){
	AjaxCall("/action", {id: userId, action: command}, function(data){ 
    DisplayData(data);
    CallCallback(callback);
	});
}

var CallCallback = function (callback){
	if(callback != null) {
		callback();
	}
}

var AjaxCall = function(endpoint, data, callback){
	var ajax = $.ajax({
		method: "GET",
		url: apiUrl + endpoint,
		data: data,
		cache: false,
	});
	ajax.done(function(data) {
  	console.log("from " + apiUrl + endpoint + " returned: " + data);
  	callback(data);
	});
	ajax.fail(function(req, status, error){
    console.log("bad req to " + apiUrl + endpoint + ":  " + status + " | " + error);
	});
}



$(init);

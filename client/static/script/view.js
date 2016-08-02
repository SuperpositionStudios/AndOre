//load app.js after this!
//using (from app.js) id, CallCallback

//called by app.js after id is populated, etc
var contentSelector = "#content span";
var pollDelay = 350;
var validKeys = {
    "w": true,  // Direction Key
    "a": true,  // Direction Key
    "s": true,  // Direction Key
    "d": true,  // Direction Key
    "m": true,  // Primary Modifier Key
    "k": true,  // Primary Modifier Key
    "l": true,  // Primary Modifier Key
    "i": true,  // Primary Modifier Key
    "-": true,  // Primary Modifier Key
    "+": true,  // Primary Modifier Key
    "b": true,  // Primary Modifier Key
    "u": true,  // Primary Modifier Key
    "0": true,  // Secondary Modifier Key
    "1": true,  // Secondary Modifier Key
    "2": true,  // Secondary Modifier Key
    "3": true,  // Secondary Modifier Key
    "4": true,  // Secondary Modifier Key
    "5": true,  // Secondary Modifier Key
    "6": true,  // Secondary Modifier Key
    "7": true,  // Secondary Modifier Key
    "8": true,  // Secondary Modifier Key
    "9": true   // Secondary Modifier Key
};
var view = {
  contentSpan: null,
  SetupView : function(callback) {
    view.contentSpan = $(contentSelector);
    view.SetupInput();
    view.Poll();
    CallCallback(callback);
  },
  Draw: function(world){
    var out = "";
    for (var rowKey in world){
      var row = world[rowKey];
      out += row.join("") + "\n";
    }
    //console.log(out);
    view.contentSpan.html(out);
  },
  Poll: function(){
    setTimeout(function() {
      app.GetDisplay(view.Poll, pollDelay);
    }, pollDelay);
  },
  SetupInput: function() {
    $("body").keypress(function(e){
      command = String.fromCharCode(e.which).toLowerCase()
      //console.log(command);
      if(validKeys[command]) {
        app.SendCommand(command);
      }
    });

  }
}

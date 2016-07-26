//load app.js after this!
//using (from app.js) id, CallCallback

//called by app.js after id is populated, etc
var contentId = "content";
var pollDelay = 350;
var validKeys = {"w":true,"a":true,"s":true,"d":true};
var view = {
  contentDiv: null,
  SetupView : function(callback) {
    view.contentDiv = $(DivNameToId(contentId));
    view.SetupInput();
    //view.Poll();
    CallCallback(callback);
  },
  Draw: function(world){
    var out = "";
    for (var rowKey in world){
      var row = world[rowKey];
      out += row.join("") + "\n";
    }
    //console.log(out);
    view.contentDiv.html(out);
  },
  Poll: function(){
    setTimeout(function() { 
      app.GetDisplay(view.Poll, pollDelay);
    }, pollDelay);
  },
  SetupInput: function() {
    $("body").keydown(function(e){
      command = String.fromCharCode(e.which).toLowerCase()
      //console.log(command);
      if(validKeys[command]) {
        app.SendCommand(command);
      }
    });

  }
}

function DivNameToId(divName) {
  return "#" + divName;
}

//load app.js after this!
//using (from app.js) id, CallCallback

//called by app.js after id is populated, etc
var contentId = "content";
var pollDelay = 200;
var view = {
  contentDiv: null,
  SetupView : function(callback) {
    view.contentDiv = $(DivNameToId(contentId));
    CallCallback(callback);
  },
  Draw: function(world){
    var out = "";
    for (var rowKey in world){
      var row = world[rowKey];
      console.log(row);
      out += row.join("") + "\n";
    }
    view.contentDiv.html(out);
  },
  Poll: function(){
    setTimeout(function() { 
      app.GetDisplay(view.Poll, pollDelay);
    });
  }
}

function DivNameToId(divName) {
  return "#" + divName;
}

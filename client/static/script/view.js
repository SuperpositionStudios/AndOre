//load app.js after this!
//using (from app.js) id, CallCallback

//called by app.js after id is populated, etc
var contentSelector = "#content";

var firstTime = true;
var createRowID = function(row) {
    return "row" + row;
};
var createColumnID = function(col) {
    return "col" + col;
}

var createCellID = function(row, col) {
    return "row" + row + "col" + col;
}

View = function() {

}

View.prototype = {
  contentDiv: null,
  pollDelay: 350,
  SetupView : function(app, callback) {
    this.app = app;
    this.contentDiv = $(contentSelector);
    this.SetupInput();
    this.Poll();
    CallCallback(callback);
  },
    Draw: function(world){
        console.log("meow");
        var rows = world.length;
        var cols = world[0].length;

        if (firstTime) {
            console.log("firstTime");
            firstTime = false;

            for (var rowNum = 0; rowNum < rows; rowNum++) {
                // Creating the row div
                $(contentSelector).append('<div class="row" id="' + createRowID(rowNum) + '"></div>');

                for (var colNum = 0; colNum < cols; colNum++) {
                    // Creating the cell
                    console.log(createCellID(rowNum, colNum));
                    $('#' + createRowID(rowNum)).append('<div class="cell" id="' + createCellID(rowNum, colNum) + '">' + world[rowNum][colNum] + '</div>');
                }
            }
        } else {
            for (var rowNum = 0; rowNum < rows; rowNum++) {
                for (var colNum = 0; colNum < cols; colNum++) {
                    $('#' + createCellID(rowNum, colNum)).html(world[rowNum][colNum]);
                }
            }
        }
    },
  Poll: function(){
    setTimeout(function() {
      app.GetDisplay(this.Poll, this.pollDelay);
    }, this.pollDelay);
  },
  SetupInput: function() {
    $("body").keypress(function(e){
      command = String.fromCharCode(e.which).toLowerCase();
      console.log(app.actionsLut);
      if(app.actionsLut[command]) {
        app.SendCommand(command);
      }
    });

  }
}

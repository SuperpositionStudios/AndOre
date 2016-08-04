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
        if (world == '') {
            //console.log("Didn't update the world because the world response was empty");
            return "Didn't update the world because the world response was empty";
        }
        var rows = world.length;
        var cols = world[0].length;

        if (firstTime) {
            firstTime = false;

            for (var rowNum = 0; rowNum < rows; rowNum++) {
                // Creating the row div
                $(contentSelector).append('<div class="row" id="' + createRowID(rowNum) + '"></div>');

                for (var colNum = 0; colNum < cols; colNum++) {
                    var cellSelector = '#' + createCellID(rowNum, colNum);
                    // Creating the cell
                    //console.log(createCellID(rowNum, colNum));
                    if (world[rowNum][colNum].length == 2) {
                        // Icon is using new format
                        $('#' + createRowID(rowNum)).append('<div class="cell" id="' + createCellID(rowNum, colNum) + '">' + world[rowNum][colNum][0] + '</div>');
                        $(cellSelector).css('color', world[rowNum][colNum][1]);
                    } else {
                        $('#' + createRowID(rowNum)).append('<div class="cell" id="' + createCellID(rowNum, colNum) + '">' + world[rowNum][colNum] + '</div>');
                    }
                }
            }
        } else {
            //console.log("Updating world");
            for (var rowNum = 0; rowNum < rows; rowNum++) {
                for (var colNum = 0; colNum < cols; colNum++) {
                    var cellSelector = '#' + createCellID(rowNum, colNum);
                    if (world[rowNum][colNum].length == 2) {
                        // Icon is using new format
                        $(cellSelector).html(world[rowNum][colNum][0]);
                        $(cellSelector).css('color', world[rowNum][colNum][1]);
                    } else {
                        $('#' + createCellID(rowNum, colNum)).html(world[rowNum][colNum]);
                    }
                }
            }
        }
    },
  Poll: function(){
    setTimeout(function() {
      //console.log(typeof(View.prototype.Poll));
      app.GetDisplay(View.prototype.Poll, this.pollDelay);
    }, this.pollDelay);
  },
  SetupInput: function() {
    $("body").keypress(function(e){
      command = String.fromCharCode(e.which).toLowerCase();
      //console.log(app.actionsLut);
      if(app.actionsLut[command]) {
        app.SendCommand(command);
      }
    });

  }
}

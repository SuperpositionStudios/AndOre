//load app.js after this!
//using (from app.js) id, CallCallback

//called by app.js after id is populated, etc
var contentSelector = "#content";
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
var view = {
  contentDiv: null,
  SetupView : function(callback) {
    view.contentDiv = $(contentSelector);
    view.SetupInput();
    view.Poll();
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
        /*
        for (var rowKey in world){
            for (var cellKey in world[rowKey]) {
                out += "<span class='cell'>" + world[rowKey][cellKey] + "</span>";
            }
            out += "<br>";
            //var row = world[rowKey];
            //out += row.join("") + "\n";
        }
        //console.log(out);
        view.contentDiv.html(out);
        */
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

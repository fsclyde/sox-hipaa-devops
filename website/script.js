/* When the user clicks on the button, 
toggle between hiding and showing the dropdown content */
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
    var env = document.getElementById("myDropdown").value
}

/* GET JSON from URL */


function gets3JSON(report, path) {

    var link = `https://s3.amazonaws.com/newwave-sox-kwjer3209/${path}/${report}.json`

    $.getJSON(link, function(result) {
        CreateTableFromJSON(result);
    });

}


// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function CreateTableFromJSON(data) {

    var myBooks = data

    // EXTRACT VALUE FOR HTML HEADER. 
    var col = [];
    for (var i = 0; i < myBooks.length; i++) {
        for (var key in myBooks[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    // CREATE DYNAMIC TABLE.
    var table = document.createElement("table");

    // CREATE HTML TABLE HEADER ROW USING THE EXTRACTED HEADERS ABOVE.

    var tr = table.insertRow(-1);                   // TABLE ROW.

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // TABLE HEADER.
        th.innerHTML = col[i];
        tr.appendChild(th);
    }

    // ADD JSON DATA TO THE TABLE AS ROWS.
    for (var i = 0; i < myBooks.length; i++) {

        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
             if (col[j] == "teams_name") {
                  var tab_str = "";
                  var team = myBooks[i][col[j]];

                  for (var k = 0; k < team.length; k++){
                    tab_str = tab_str + "<br>"+ team[k]["team_name"]+" "+team[k]["team_permission"];
                  }
                  tabCell.innerHTML = tab_str;
                  tab_str = "";
            } else if (col[j] == "team_member") {

                  var tab_str = "";
                  var team = myBooks[i][col[j]];

                  for (var k = 0; k < team.length; k++){
                    tab_str = tab_str + "<br>"+ "Username: " + team[k]["login"]+"  IsAdmin: "+team[k]["site_admin"];
                  }
                  tabCell.innerHTML = tab_str;
                  tab_str = "";

            } else {
                tabCell.innerHTML = myBooks[i][col[j]];
            }
        }
    }

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showData");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);

    // Update Last updated date
//    var d = new Date();
//    var dateStr = d.toISOString();
//    var divContainerDate = document.getElementById("showLastUpdatedFileDate");
//    divContainerDate.innerHTML = "Last Updated: " + dateStr;
}



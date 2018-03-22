/* When the user clicks on the button, 
toggle between hiding and showing the dropdown content */
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
    var env = document.getElementById("myDropdown").value
}


/* GET JSON from URL */


function gets3JSON(env) {

    var link = `https://s3.amazonaws.com/newwave-release-kwjer3209/NewWave-Release-${env}.json`
    var cucumber = `http://jenkins-tesla.nw.adesa.com/job/nw-e2e-${env}/lastBuild/cucumber-html-reports/overview-features.html`


    $.getJSON(link, function(result) {
        CreateTableFromJSON(result);
    });

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showCucumberReport");
    divContainer.innerHTML = "";
    var aTag = document.createElement('a');
    aTag.setAttribute('href',cucumber);
    aTag.innerHTML = "Quality Testing " + env.toUpperCase();
    divContainer.appendChild(aTag);
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
            if (col[j] == "build_url") {
                tabCell.innerHTML = `<a href=${myBooks[i][col[j]]}>Build</a>`;
            } else if (col[j] == "project") {
                var project = myBooks[i][col[j]];
                tabCell.innerHTML = myBooks[i][col[j]];
            } else if (col[j] == "git_sha") {
                tabCell.innerHTML = `<a href=http://github.nw.adesa.com/new-wave/${project}/commit/${myBooks[i][col[j]]}>Change</a>`;
            } else if (col[j] == "issue") {
                var issue = myBooks[i][col[j]];
                if ((issue != "None") || (issue != "null")){
                     var myOutput = "";
                     issue.split(/\s*,\s*/).forEach(function(myString) {
                        myOutput = myOutput + `<a href=https://jira.nw.adesa.com/browse/${myString}>${myString}</a>\n`
                     });
                     tabCell.innerHTML = myOutput;
                }
            } else if (col[j] == "release_version") {
                        if (typeof myBooks[i][col[j]] !== "undefined"){
                            tabCell.innerHTML = `<a href=http://github.nw.adesa.com/new-wave/${project}/releases/tag/${myBooks[i][col[j]]}> ${myBooks[i][col[j]]} </a>`;
                        } else{
                            tabCell.innerHTML = "None"
                        }
            } else {
                if (typeof myBooks[i][col[j]] !== "undefined"){
                    tabCell.innerHTML = myBooks[i][col[j]];
                } else{
                    tabCell.innerHTML = "None"
                }
            }
        }
    }

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showData");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}



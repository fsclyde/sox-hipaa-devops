
// Retrieve the last updated list of Active Directory New Wave Users
function getADUsers(title) {

    var admins = `https://s3.amazonaws.com/newwave-sox-kwjer3209/active_directory/corp-int-newwave-${title}.json`

    $.getJSON(admins, function(result) {
        formatTable(result);
    });

}

function formatTable(data) {

    var myBooks = data

    // Filter Unwanted Value
    myBooks = myBooks.filter(function( obj ) {
        var hiddenValue = ["pwdLastSet","userAccountControl","employeeID","sn","cn","givenName","displayName","dn","mail", "lockoutTime","whenCreated","initials"];
        for (row in hiddenValue) {
            delete obj[hiddenValue[row]];
        }
        return obj;
    });

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
            tabCell.innerHTML = myBooks[i][col[j]];
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

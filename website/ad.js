// Get AWS Admins users
function  getAWSAwdmins(){
    var aws_admins = `https://s3.amazonaws.com/newwave-sox-kwjer3209/active_directory/aws_admins_users.json`
        $.getJSON(aws_admins, function(results) {
        formatTable(results);
    });
}

// get db production  users
function getDBUsers() {
    var aws_admins = `https://s3.amazonaws.com/newwave-sox-kwjer3209/database/fetch-user-permission.json`
        $.getJSON(aws_admins, function(results) {
        formatTable(results);
    });
}

// IsAdmins status
function getAdmins(data, status){
    updated_data = [];
    for (var row in data) {
        data[row].AWSadmin = status
        updated_data.push(data[row])
    }
    return updated_data;
}

// Retrieve the last updated list of Active Directory New Wave Users
function getADUsers() {
    var myData = [];
    var admins = `https://s3.amazonaws.com/newwave-sox-kwjer3209/active_directory/corp-int-newwave-admins.json`
    var users = `https://s3.amazonaws.com/newwave-sox-kwjer3209/active_directory/corp-int-newwave-users.json`
    var github = `https://s3.amazonaws.com/newwave-sox-kwjer3209/users_permission/UsersAccessRepoReport.json`

    $.when(
        $.getJSON(admins, function(results) {
            adminsData = results
            adminsData = getAdmins(adminsData, true)
        }),
        $.getJSON(users, function(results) {
            usersData = results
            usersData = getAdmins(usersData, false)
        }),
        $.getJSON(github, function(results) {
            githubData = results
            console.log(githubData);
        })
    ).then(function() {
        var result = [];
        $.extend(result, usersData, adminsData);
        formatTable(result);
    });
}

function formatTable(data) {

    var myBooks = data;

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

/*

Title           : New Wave - List of Production databse Users
Description     : This will allow to get the list of Production database users and permissions

*/

// Modules
const aws = require('aws-sdk'), fs = require('fs');
const s3 = new aws.S3();
aws.config.update({region: 'us-east-1'});
const { Client } = require('pg')
const config = require('./config.json');
var util = require('util');


const databases = ["nw_watchlist", "nw_iam", "nw_ci","nw_vdp","nw_liveblock","nw_inspection","nw_media","nw_inventory","nw_announcements"];

const encrypted = {
    username: process.env['RDS_USERNAME'],
    password: process.env['RDS_PASSWORD']

}
let decrypted = {};



// upload to s3
function uploads3(fileToUpload, dataToUpload){

    s3.putObject({
        Bucket: config.s3bucket,
        Key: fileToUpload,
        Body: JSON.stringify(dataToUpload),
        ACL: 'public-read'
      },function (resp) {
        console.log('Successfully uploaded package: ' + fileToUpload);
      });
}

function initiatRdsConnection(username, password, db){

    // RDS Variables
    const client = new Client({
      host: process.env['RDS_HOST'],
      port: 5432,
      user: username,
      password: password,
      database: db
    })

    client.connect((err) => {
      if (err) {
        console.error('connection error', err.stack);
      }
    });
    return client
}


/// Main function
function processEvent(event, context, callback) {

    var client = initiatRdsConnection(decrypted.username, decrypted.password, "nw_watchlist")

    // if successfully connected
    if (client){

       // Query The database for the list of Users and Permissions
       const query = {
        //  Prepared statement
        name: 'fetch-user-permission',
        text: util.format("SELECT u.usename AS %s, u.usesysid AS %s, CASE WHEN u.usesuper AND u.usecreatedb THEN CAST('superuser, create database' AS pg_catalog.text) WHEN u.usesuper THEN CAST('superuser' AS pg_catalog.text) WHEN u.usecreatedb THEN CAST('create database' AS pg_catalog.text) ELSE CAST('' AS pg_catalog.text) END AS %s FROM pg_catalog.pg_user u ORDER BY 1;","\"User name\"","\"User ID\"","\"Attributes\"")
       }

        client.query(query, (err, res) => {
          if (err) {
            console.log(err.stack)
          } else {
            var data = res.rows
           // upload to JSON s3
           uploads3("database/fetch-user-permission.json",data)
          }
          client.end()
        })
        // Upload the script itself to s3
        fs.readFile('handler_database.js', 'utf8', function(err, data_file) {
            uploads3("scripts/handler_database.js", data_file)
        });
    }
   // Extract permission per database
//   databases.forEach(function(db) {
//        // Connection to each databases
//        var client = initiatRdsConnection(decrypted.username, decrypted.password, db)
//
//       var query = {
//        //  Prepared statement
//        name: util.format('fetch-database-%s-permission',db),
//        text: util.format("SELECT * FROM information_schema.role_table_grants")
//       }
//
//        client.query(query, (err, res) => {
//          if (err) {
//            console.log(err.stack)
//          } else {
//            var data = JSON.stringify(res.rows)
//          }
//          client.end()
//        })
//
//    });

}


// Lambda handler Managing Encrypted variables
exports.myHandler_data = function(event, context, callback) {

 try {
     if ( decrypted.username && decrypted.password ) {
                processEvent(event, context, callback);
            } else {
                const kms = new aws.KMS({region:"us-east-1"});

                const decryptPromises = [
                    kms.decrypt( { CiphertextBlob: new Buffer(encrypted.username, 'base64') } ).promise(),
                    kms.decrypt( { CiphertextBlob: new Buffer(encrypted.password, 'base64') } ).promise()
                ];

                Promise.all( decryptPromises ).then( data => {
                    decrypted.username = data[0].Plaintext.toString('ascii');
                    decrypted.password = data[1].Plaintext.toString('ascii');

                    processEvent(event, context, callback);
                })
            }
    } catch (e){
        if (e instanceof TypeError) {
            console.log("Please provide encrypted username and password variables RDS_USERNAME & RDS_PASSWORD")
        }
    }
}
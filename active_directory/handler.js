/*

Title           : Active Directory list of users
Description     : This will allows use to get the list of Active AD users

*/

// Modules
const aws = require('aws-sdk'), fs = require('fs');
const s3 = new aws.S3();
const config = require('./config.json');
const decryptEnvVars = require('aws-kms-decrypt-env');

// Environment variable
const encrypted = {
    username: process.env['USERNAME'],
    password: process.env['PASSWORD']

}
let decrypted = {};

 // AD parameters
var ActiveDirectory = require('activedirectory');
var users = {};

// Function retrieve Active Directory Users
function retrieveUsers(group, ad, cb) {

  ad.getUsersForGroup(group, function(err, users) {

      if (err) {
        console.log('ERROR: ' +JSON.stringify(err));
        return;
      }

      // Check if list of users exist and return it
      if (! users) {
        console.log('Group: ' + group + ' not found.');
      } else {
        //console.log(JSON.stringify(users));
        cb(users);
      }
  });
  return users;
}

// Upload to s3
function uploads3(fileToUpload, dataToUpload){

    // convert base64
//    var base64data = new Buffer(dataToUpload, 'binary');

    s3.putObject({
        Bucket: config.s3bucket,
        Key: config.s3folder + fileToUpload,
        Body: JSON.stringify(dataToUpload),
        ACL: 'public-read'
      },function (resp) {
        console.log('Successfully uploaded package.');
      });
}

/// Main function
function processEvent(event, context, callback) {


     // Define AD parameters
     var configLDAP = { url: config.ldapUrl,
               baseDN: config.ldapBaseDN,
               username: decrypted.username,
               password: decrypted.password
              }
    const ad = new ActiveDirectory(configLDAP);
    var adminsGroup = config.adminsGroup;
    var usersGroup = config.usersGroup;

    // Get the list of users && Upload it to s3
    retrieveUsers(config.adminsGroup, ad, function(data){
        uploads3("corp-int-newwave-admins.json", data)
    })
    retrieveUsers(config.usersGroup, ad, function(data){
        uploads3("corp-int-newwave-users.json", data)
    })

}


// Lambda handler
exports.myHandler = function(event, context, callback) {
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
            }).catch( err => {
                console.log('Decrypt error:', err);
                return callback(err);
            });
        }
}


//'use strict';
//
//module.exports.hello = (event, context, callback) => {
//  const response = {
//    statusCode: 200,
//    body: JSON.stringify({
//      message: 'Go Serverless v1.0! Your function executed successfully!',
//      input: event,
//    }),
//  };
//
//  callback(null, response);
//
//  // Use this code if you don't use the http event with the LAMBDA-PROXY integration
//  // callback(null, { message: 'Go Serverless v1.0! Your function executed successfully!', event });
//};
/*

Title           : Active Directory list of users
Description     : This will allows use to get the list of Active AD users

*/

// Modules
const aws = require('aws-sdk'), fs = require('fs');
const s3 = new aws.S3();
const config = require('./config.json');
aws.config.update({region: 'us-east-1'});

// Create the IAM service object
var iam = new aws.IAM({apiVersion: '2010-05-08'});

var params_groups = {
  GroupName: 'admin_full_mfa' /* required */
};

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
        uploads3(config.s3folder + "corp-int-newwave-admins.json", data)
    })
    retrieveUsers(config.usersGroup, ad, function(data){
        uploads3(config.s3folder + "corp-int-newwave-users.json", data)
    })

    // Upload the script itself to s3
    fs.readFile('handler.js', 'utf8', function(err, data_file) {
        uploads3("scripts/aws_permission.py", data_file)
    });


    // AWS Users in Admins groups
    var aws_admins_users = []
    iam.getGroup(params_groups, function(err, data) {
      if (err) {
        throw err;
      } else {
        var users = data.Users || [];
        users.forEach(function(user) {
          aws_admins_users.push({"Username":user.UserName,
                                 "CreateDate":user.CreateDate
                                });
        });
        uploads3(config.s3folder + "aws_admins_users.json", aws_admins_users)
      };
    });


}

// Lambda handler
exports.myHandler = function(event, context, callback) {

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
                }).catch( err => {
                    console.log("Error when trying to decrypt the object: Check AWS Access Keys");
                    return;
                });
            }
    } catch (e){
        if (e instanceof TypeError) {
            console.log("Please provide encrypted username and password variables USERNAME & PASSWORD")
        }
    }
}

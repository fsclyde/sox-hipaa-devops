import gspread
from oauth2client.service_account import ServiceAccountCredentials
import argparse, datetime
import boto3, json
import botocore
import pytz, requests
from boto.s3.key import Key
from datetime import timedelta
from requests.auth import HTTPBasicAuth
import release_tagging
from release_tagging import *


s3r = boto3.resource('s3')
s3 = boto3.client('s3')

BUCKET_NAME = "newwave-release-kwjer3209"
mybucket = s3r.Bucket(BUCKET_NAME)

JSON_FORMAT = [{
            "project": "",
            "build_data": [
                {
                    "build_no": "",
                    "approver": "",
                    "env": "",
                    "date": "",
                    "commit": "",
                    "git_sha": "",
                    "version": "",
                    "branch": "",
                    "timestamps": "",
                    "issue":""
                }
            ]
        }]


# Class Extract value
class manageExtract:
    def __init__(self, artefact):
        self.message = {}
        self.artefact = artefact

    # Extract the project name / version number / Git Commit ID / time
    def extractValue(self, position):
        extracted_value = ""

        extracted_value = self.artefact.split("_")[position]

        return extracted_value

    def getArtefact(self):

        return self.artefact


# Manage all functions
class manageRelease:
    def __init__(self):
        self.message = {}
        self.release_version = "None"


    def argsParse(self):

        # Argument for the deployment
        parser = argparse.ArgumentParser(description='Jira Values')
        parser.add_argument('-s','--story', type=str, help='issue key',  default=None, required=False)
        parser.add_argument('-b','--build', type=str, help='build number',  default=None, required=True)
        parser.add_argument('-j','--job', type=str, help='Job Name',  default=None, required=True)
        parser.add_argument('-e','--env', type=str, help='Environment',  default=None, required=True)
        parser.add_argument('-a','--artefact', type=str, help='Artefact Name',  default=None, required=True)
        parser.add_argument('-br','--branch', type=str, help='Branch Name',  default=None, required=True)
        parser.add_argument('-ap','--approver', type=str, help='Who has triggered the build',  default=None, required=True)
        parser.add_argument('-u','--build_url', type=str, help='What was the build URL',  default=None, required=True)
        parser.add_argument('-sh','--git_sha', type=str, help='The sha of the github',  default=None, required=True)
        parser.add_argument('-ce','--git_commit', type=str, help='The author of the commit',  default=None, required=True)
        parser.add_argument('-bo','--board', type=str, help='The Jira release board',  default=None, required=True)
        self.args = parser.parse_args()

        return self.args

    # Publish to google spreadsheet
    def publishGoogle(self):

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open("NewWave Release sample").sheet1

        # Extract and print all of the values
        list_of_hashes = sheet.get_all_records()
        resize_int = sheet.row_count
        sheet.resize(resize_int)

        # increment Jira Speadsheet
        """ Build Number, service (Job), Environment, Branch, artefact, Approver,  Date of the Release, Jira Issue found """
        sheet.append_row([self.args.build, self.args.job, self.args.env, self.args.branch, self.args.artefact, self.args.approver, unicode(datetime.datetime.now()), self.args.story])


    # This function will publish the information of the build into s3 bucket
    def publishS3(self, categorie, artefact):
        test = 0
        new_row = json_data = []
        new_build = {}
        file_s3 = ""

        # Get the new build
        new_build = self.getNewBuild()

        # Get JSON
        file = getFile()

        # create new file for each project
        if file:
            for file_row in file:
                if categorie in file_row:
                    file_s3 = file_row
                    # Get Json data into json_data
                    json_data = getObject(file_s3)
                else:
                    file_s3 = "NewWave-Release-{}.json".format(categorie)

        else:
            file_s3 = "NewWave-Release-{}.json".format(categorie)

        #### Check Json ####
        json_data.append(new_build)
        row_to_send = filter(None, json_data)

        return row_to_send, file_s3



    # Get the new JSON build
    def getNewBuild(self):

        # Get the artefact for the extraction
        myManageExtract = manageExtract(self.args.artefact)

        new_build = {
                "project": myManageExtract.extractValue(position=0),
                "build_no": self.args.build,
                "approver": self.args.approver,
                "env": self.args.env,
                "branch": self.args.branch,
                "date": datetime.datetime.now(pytz.timezone("America/Toronto")).strftime('%Y-%m-%d %H:%M:%S %Z%z'), # Need to configure Jenkins with UTC
                "commit": myManageExtract.extractValue(position=3).split(".")[0],
                "version": myManageExtract.extractValue(position=1),
                "artefact": myManageExtract.artefact,
                "build_url": self.args.build_url,
                "git_sha": self.args.git_sha,
                "git_commit_author": self.args.git_commit,
                "issue": self.args.story,
                "release_version": self.release_version
        }

        return new_build

    # Make JSON Unique by using key
    def makeJsonUnique(self, json_data, key):
        unique_json = []
        unique_json = {v[key]:v for v in json_data}.values()
        return unique_json


def getObject(file_s3):
    obj_key = ""
    data = []
    # if the Version already exist then work in this specific file
    obj = s3r.Object(BUCKET_NAME, file_s3)
    data = json.loads(obj.get()["Body"].read())

    return data

# get s3 Object
def getFile():
    file = [] # list of each file

    for object in mybucket.objects.all():
        file.append(object.key)

    return file


# Function upload for the new file to s3 bucket
def putObject(data, key_name):
    AWS_EXPIRY = datetime.datetime.utcnow() + timedelta(minutes=(10))
    Object  = s3r.Object(BUCKET_NAME,key_name)
    Object.put(Body=json.dumps(data), ContentType='application/json', ACL='authenticated-read')
    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key_name
        }
    )
    print(url)

# main function
def main():

    ############################################################################# Extraction Release Traktor
    # Release Traktor
    myManageRelease = manageRelease()

    # Get the argurment for the build
    args = myManageRelease.argsParse()

    ############################################################################# Extraction Release Tagging

    # Release tagging
    myManageVersion = manageVersion()

    # Get jira release
    release_version = myManageVersion.getJiraItem(payload="project/{}/versions".format(args.board))

    # get the latest release version
    latest_release_version, latest_release_date, release_id, project_id = myManageVersion.getLastestReleaseVersion(release_version)
    myManageRelease.release_version = latest_release_version

    ############################################################################# Build JSON

    # Get the artefact for the extraction
    myManageExtract = manageExtract(args.artefact)
    project_name = myManageExtract.extractValue(position=0)
    env = args.env
    artefact = myManageExtract.getArtefact()

    ############################################################################# AWS
    # Function which will publish the informations for the release the s3 bucket in AWS build environment
    json_deploy, file_s3 = myManageRelease.publishS3(project_name, artefact) # By components

    # upload the new object to s3
    putObject(json_deploy, file_s3)

    json_deploy, file_s3 = myManageRelease.publishS3(env, artefact) # By Environments

    # Make JSON unique
    unique_json_deploy = myManageRelease.makeJsonUnique(json_deploy, key='project')

    # upload the new object to s3
    putObject(unique_json_deploy, file_s3)


if __name__ == "__main__":
    context = event = {}
    main()


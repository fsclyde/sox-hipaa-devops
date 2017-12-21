#!/usr/local/bin/python
#
# All function shared
#
import datetime, json, string
import requests, os
from requests.auth import HTTPBasicAuth
import config, sys,re, boto3, base64
kms = boto3.client('kms')
from functions import *
from config import *
import csv
from datetime import timedelta


s3r = boto3.resource('s3')
s3 = boto3.client('s3')

BUCKET_NAME = "newwave-sox-kwjer3209"
mybucket = s3r.Bucket(BUCKET_NAME)

#
# This function extract github permissions per repository for audit
#
myManageFunc = functionRepo()


class manageGithub:

    # Variable initiation
    def __init__(self):
        self.message = []

    # Get team and permission
    def getTeamName(self, repo_name):
        dict_team = {}
        array_team = []

        res = myManageFunc.githubGetRequest("repos/{}/{}/teams".format(config.GITHUB_ORGANISATION,repo_name))
        data = myManageFunc.manageStatusCode(res)

        if data:
            for item in data:
                dict_team["team_name"] = item["name"]
                dict_team["team_permission"] = item["permission"]
                array_team.append(dict_team)
                dict_team = {}

        return array_team

    # Get team and members
    def getTeamNameStand(self):
        dict_team = {}
        array_team = []

        res = myManageFunc.githubGetRequest("orgs/{}/teams".format(config.GITHUB_ORGANISATION))
        data = myManageFunc.manageStatusCode(res)

        if data:
            for item in data:
                dict_team["team_name"] = item["name"]
                dict_team["team_permission"] = item["permission"]
                dict_team["team_description"] = item["description"]
                dict_team["team_member"] = self.getTeamMemb(item["id"])
                array_team.append(dict_team)
                dict_team = {}

        return array_team

    # Get team member
    def getTeamMemb(self,team_id):
        array_memb_info = []
        dict_memb_info = {}

        res = myManageFunc.githubGetRequest("teams/{}/members".format(team_id))
        data = myManageFunc.manageStatusCode(res)

        if data:
            for item in data:
                dict_memb_info["login"] = item["login"]
                dict_memb_info["site_admin"] = item["site_admin"]
                array_memb_info.append(dict_memb_info)
                dict_memb_info = {}

        return array_memb_info

    # Send reports to Slack
    def sendToSlack(self, filename):


        my_file = {
            'file': (filename, open(filename, 'rb'), 'json')
        }

        payload = {
            "filename": filename,
            "token": config.API_TOKEN,
            "channels": ['#githubot'],
        }

        r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)

# Function upload for the new file to s3 bucket
def putObject(data, key_name):
    AWS_EXPIRY = datetime.datetime.utcnow() + timedelta(minutes=(10))
    Object = s3r.Object(BUCKET_NAME, key_name)
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

# Main start
def lambda_handler(event,context):
    data_repo = {}
    tab_repo = []
    big_data = []
    test = []
    myManageGithub = manageGithub()
    nb = 1

    while nb != 4:
        res = myManageFunc.githubGetRequest("orgs/{}/repos?page={}".format(config.GITHUB_ORGANISATION,nb))
        data = myManageFunc.manageStatusCode(res)
        big_data.append(data)
        nb += 1

    # Process on repositories
    if big_data:
        for data in big_data:
            for item in data:
                repo_name = item["name"]
                status = item["private"]
                teams_name = myManageGithub.getTeamName(repo_name)

                data_repo["repo_name"] = repo_name
                data_repo["is_public"] = status
                data_repo["teams_name"] = teams_name

                tab_repo.append(data_repo)
                data_repo = {}

    # Extract team and members
    data_team = myManageGithub.getTeamNameStand()

    # Team Access
    filename = "users_permission/UsersAccessRepoReport.json"
    putObject(data_team, filename)

    # Repo Access
    filename = "repositories_permission/RepositoryAccessReport.json"
    putObject(tab_repo, filename)

    # Script That has created the reports
    filename = "github_permission.py"
    f = open(filename, "r")
    data_file = f.read()
    putObject(data_file, "scripts/"+filename)


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)
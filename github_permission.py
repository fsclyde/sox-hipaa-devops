__author__ = "Clyde Fondop"
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
                dict_team["team_description "] = item["description"]
                dict_team["team_member "] = self.getTeamMemb(item["id"])
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
    def sendToSlack(self, data, filename):
        file = open(filename, 'w+')
        file.write(json.dumps(data))
        file.close()

        my_file = {
            'file': (filename, open(filename, 'rb'), 'json')
        }

        payload = {
            "filename": filename,
            "token": config.API_TOKEN,
            "channels": ['#githubot'],
        }

        # r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)


# Main start
def lambda_handler(event,context):
    data_repo = {}
    tab_repo = []
    myManageGithub = manageGithub()
    res = myManageFunc.githubGetRequest("orgs/{}/repos".format(config.GITHUB_ORGANISATION))
    data = myManageFunc.manageStatusCode(res)

    # Process on repositories
    if data:
        for item in data:
            repo_name = item["name"]
            status = item["private"]
            teams_name = myManageGithub.getTeamName(repo_name)

            data_repo["repo_name"] = repo_name
            data_repo["status"] = status
            data_repo["teams_name"] = teams_name

            tab_repo.append(data_repo)
            data_repo = {}

    # Extract team and members
    data = myManageGithub.getTeamNameStand()

    # Send information to slack
    filename = "UsersAccessRepositoryReport_{}.json".format(datetime.datetime.now().isoformat())
    myManageGithub.sendToSlack(data, filename)

    filename = "RepositoryTeamAccessReport_{}.json".format(datetime.datetime.now().isoformat())
    myManageGithub.sendToSlack(tab_repo, filename)


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)
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
                data_repo["status"] = status
                data_repo["teams_name"] = teams_name

                tab_repo.append(data_repo)
                data_repo = {}

    filename = "RepositoryAccessReport_{}.csv".format(datetime.datetime.now().isoformat())
    with open(filename, 'wb') as csvfile:
        fieldnames = ['repo_name', 'privacy_status','team_name','team_permission']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row_repo in tab_repo:
            if row_repo["teams_name"]:
                for row_repo_team in row_repo["teams_name"]:
                    writer.writerow({'repo_name': row_repo["repo_name"],
                                     'privacy_status': row_repo["status"],
                                     'team_name': row_repo_team["team_name"],
                                     'team_permission': row_repo_team["team_permission"]})
            else:
                writer.writerow({'repo_name': row_repo["repo_name"], 'privacy_status': row_repo["status"],
                                 'team_name': "None",
                                 'team_permission': "None"})
    myManageGithub.sendToSlack(filename)

    ########################################

    # Extract team and members
    data_team = myManageGithub.getTeamNameStand()

    filename = "UsersAccessRepoReport_{}.csv".format(datetime.datetime.now().isoformat())
    with open(filename, 'wb') as csvfile:
        fieldnames = ['team_name', 'team_description','team_members','member_who_has_admin',]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row_team in data_team:
            if row_team["team_member"]:
                for row_repo_member in row_team["team_member"]:
                    writer.writerow({'team_name': row_team["team_name"],
                                     'team_description': row_team["team_description"],
                                     'team_members': row_repo_member["login"],
                                     'member_who_has_admin': row_repo_member["site_admin"]})
            else:
                writer.writerow({'team_name': row_team["team_name"], 'team_description': row_team["team_description"],
                                 'team_members': "None",
                                 'member_who_has_admin': "None"})

    myManageGithub.sendToSlack(filename)

    # Send script that has create the report
    myManageGithub.sendToSlack("github_permission.py")


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)
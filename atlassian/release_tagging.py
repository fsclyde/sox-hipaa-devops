import argparse, datetime
from datetime import timedelta
import requests, json, time
from requests.auth import HTTPBasicAuth
import re, html2text


# Manage Version
class manageVersion:

    # define attribs for all functions
    def __init__(self):
        self.message = ""
        self.file = open("/var/jenkins_home/tools/config.json", "r")
        self.config = json.loads(self.file.read())

        # Jira configuration
        self.jira_username = self.config["jira_username"]
        self.jira_password = self.config["jira_password"]
        self.jira_url = self.config["jira_url"]

        # Github configuration
        self.github_username = self.config["github_username"]
        self.github_password = self.config["github_password"]
        self.github_url = self.config["github_url"]


    def argsParse(self):

        # Argument for the deployment
        parser = argparse.ArgumentParser(description='Jira Values')
        parser.add_argument('-a','--artefact', type=str, help='Artefact Name',  default=None, required=True)
        parser.add_argument('-p','--project', type=str, help='Project Name',  default=None, required=True)

        self.args = parser.parse_args()

        return self.args


    # Get Jira Items
    def getJiraItem(self,payload):
        r = requests.get(self.jira_url.format(payload), auth=HTTPBasicAuth(self.jira_username, self.jira_password))
        data = r.json()

        return data

    # get the latest version
    def getLastestReleaseVersion(self, release_version):
        latest_release_version = latest_release_date =  release_id = project_id = ""
        newdate = "2017-01-01"

        for row in release_version:
            # Check if released
            if row["released"] == True:
                release_date = time.strptime(row["releaseDate"], "%Y-%m-%d")

                # Check the date
                if release_date > newdate:
                    latest_release_version = row["name"]
                    latest_release_date = row["releaseDate"]
                    release_id = row["id"]
                    project_id = row["projectId"]

                newdate = release_date

        return latest_release_version, latest_release_date, release_id, project_id

    # Get Github Item
    def getGithubItem(self,payload):
        r =requests.get(self.github_url.format(payload), auth=HTTPBasicAuth(self.github_username, self.github_password))
        data = r.json()

        return data


    # Create Release tag
    def postGithubItem(self,payload, release_name,release_date, project, release_note):

        sample = {
          "tag_name": release_name,
          "target_commitish": "master",
          "name": "Release {} date {} project {}".format(release_name,release_date, project),
          "body": release_note,
          "draft": False,
          "prerelease": False
        }

        r = requests.post(self.github_url.format(payload), data=json.dumps(sample),auth=HTTPBasicAuth(self.github_username, self.github_password))
        data = r.json()

        if r.status_code in [200,201,202]:
            print("the release {} has been successfully ".format(release_name))



    # check if release has been tagged already
    def checktag(self, jira, github_release):
        test = False

        if github_release:
            for row in github_release:
                if jira in row["tag_name"]:
                    test = True
        return test


    # Get release note
    def getJiraReleaseNote(self, release_id,project_id):
        release_notes = ""

        r = requests.get("https://jira.nw.adesa.com/secure/ReleaseNote.jspa?version={}&styleName=Text&projectId={}".format(release_id,project_id), auth=HTTPBasicAuth(self.jira_username, self.jira_password))
        data = r.text

        if not data:
            print("there is no release notes available of version {} and project {}".format(release_id,project_id))
        else:
            start = '<body>'
            end = '<a name="editarea"></a>'
            release_notes_html = data.split(start)[1].split(end)[0]
            release_notes =  html2text.html2text(release_notes_html)

        return release_notes


# main function
def main():

    myManageVersion = manageVersion()
    args = myManageVersion.argsParse()

    # Get jira release
    release_version = myManageVersion.getJiraItem(payload="project/{}/versions".format(args.project))

    # get the latest release version
    latest_release_version, latest_release_date, release_id, project_id = myManageVersion.getLastestReleaseVersion(release_version)
    print("This is the Jira Last Release Version: {} ".format(latest_release_version))

    # Get the Jira release note
    note = myManageVersion.getJiraReleaseNote(release_id,project_id)

    # Check if released on github
    # ARTEFACT = "nw-watchlist_0.0.1_20171201153011_d5fe911ecb.zip"
    project_name = args.artefact.split("_")[0]
    github_release = myManageVersion.getGithubItem("repos/new-wave/{}/releases".format(project_name))

    # check if already tagged
    test = myManageVersion.checktag(latest_release_version, github_release)

    # if not test then create the release
    if test:
        print("There is already a release tag for this version {} ".format(latest_release_version))
    else:
        # create a New Release tag on github -> For the specific project
        myManageVersion.postGithubItem(payload="repos/new-wave/{}/releases".format(project_name),
                                       release_name=latest_release_version,
                                       release_date=latest_release_date,
                                       project=project_name,
                                       release_note=note)

# main function
if __name__ == "__main__":
    context = event = {}
    main()

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

class functionRepo:

    # Variable initiation
    def __init__(self):
        self.message = []
        self.status_message = {}
        self.headers = {'Content-Type': 'application/json','Accept':'application/vnd.github.loki-preview+json'}

    # Make get request
    def githubGetRequest(self, url_payload):


        try:
            res = requests.get(config.GITHUB_API_URL.format(url_payload), auth=(config.USERNAME, config.PASSWORD), headers=self.headers)
            self.manageStatusCode(res)
        except requests.ConnectionError, e:
            self.status_message["error"] = "unable to make the http requests for the authentification"
            self.logging()
            sys.exit(1)

        return res


    # Make post request
    def githubPostRequest(self, url_payload, data, resource):

        res = requests.post(config.GITHUB_API_URL.format(url_payload), data=json.dumps(data), auth=(config.USERNAME, config.PASSWORD), headers=self.headers)
        self.status_message["requested_action"] = resource
        self.manageStatusCode(res)


    # Make put request
    def githubPutRequest(self, url_payload, data, resource):

        res = requests.put(config.GITHUB_API_URL.format(url_payload), data=json.dumps(data), auth=(config.USERNAME, config.PASSWORD), headers=self.headers)
        self.status_message["requested_action"] = resource
        self.manageStatusCode(res)


    # manage code status
    def manageStatusCode(self,res):
        data = {}
        self.status_message["http_status"] = res.status_code
        if self.status_message["http_status"] not in [200,201,203,204]:
            json_res = json.loads(res.content)
            self.status_message["message"] = json_res["message"]
        else:
            self.status_message["message"] = "Action successfully performed"
            data = json.loads(res.content)

        return data

    # logging information to loggly
    def logging(self):

        logging_row = ""
        for key, value in self.status_message.items():
            logging_row = logging_row + " " + '%s="%s"' % (key, value)

        value = datetime.datetime.now().isoformat() + logging_row
        print(value) # logging information


    # Get content of GET response
    def getContent(self, response):
        content = ""
        if response.status_code in [200,201]:
            content = json.loads(response.content)
        return content

    # return team ID for a specific repository
    def getTeamID(self,team_name):
        team_id = ""

        res = self.githubGetRequest('orgs/{}/teams'.format(config.GITHUB_ORGANISATION))
        json_res = self.getContent(res)

        # Read json and extract the team ID
        for item in json_res:
            if re.search(item["name"], team_name, re.IGNORECASE):
                team_id = item["id"]
                print(team_id)

        return team_id

    # Kms encrypt data
    def kmsEncryptData(self,data):
        encrypted = ""
        encrypt = kms.encrypt(Plaintext=data)
        encrypted = base64.b64encode(encrypt['CiphertextBlob']).decode("utf-8")

        return encrypted


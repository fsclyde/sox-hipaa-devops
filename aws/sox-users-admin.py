#!/usr/local/bin/python
#
# All function shared
#
import boto3, json, datetime
from datetime import timedelta

s3r = boto3.resource('s3')
s3 = boto3.client('s3')

BUCKET_NAME = "[Bucket Name]"
USERS_FILE = "aws_users/aws_production_users.json"
mybucket = s3r.Bucket(BUCKET_NAME)

#client = boto3.client('iam',aws_access_key_id="XXX",aws_secret_access_key="XXX")
client = boto3.client('iam')
users = client.list_users()
user_list = []

def lambda_handler(event,context):
    for key in users['Users']:
        result = {}
        Policies = Groups = json_aws_users = []


        #### AWS Usernames ####
        result['userName']=key['UserName']
        List_of_Policies =  client.list_user_policies(UserName=key['UserName'])


        #### AWS Policies ####
        if List_of_Policies['PolicyNames']:
            result['Policies'] = List_of_Policies['PolicyNames']
        else:
            result['Policies'] = ["None"]


        #### AWS Groups ####
        List_of_Groups =  client.list_groups_for_user(UserName=key['UserName'])

        if List_of_Groups['Groups']:
            for Group in List_of_Groups['Groups']:
                Groups.append(Group['GroupName'])
            result['Groups'] = Groups
        else:
            result['Policies'] = ["None"]

        #### MFA Devices ####
        List_of_MFA_Devices = client.list_mfa_devices(UserName=key['UserName'])

        if not len(List_of_MFA_Devices['MFADevices']):
            result['isMFADeviceConfigured']= "False"
        else:
            result['isMFADeviceConfigured']= "True"
        user_list.append(result)

    #### Build JSON ####
    for key in user_list:
        json_aws_users.append(key)

    # print(json.dumps(json_aws_users))
    putObject(json_aws_users,"{}".format(USERS_FILE))

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



if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)
import boto3, json
import botocore
from boto.s3.key import Key
import datetime
from datetime import timedelta

s3r = boto3.resource('s3')
s3 = boto3.client('s3')

BUCKET_NAME = "newwave-sox-kwjer3209"
mybucket = s3r.Bucket(BUCKET_NAME)


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

if __name__ == "__main__":
    context = event = {}
    f = open("/var/jenkins_home/workspace/sox-listofusers/jenkins_users_permissions.json","r")
    data = json.loads(f.read())
    putObject(data,"deployment_users/jenkins_users_permissions.json")


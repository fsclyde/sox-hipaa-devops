#### Settings file ####
import os, boto3
from base64 import b64decode

kms = boto3.client('kms')

# Github parameters
USERNAME = kms.decrypt(CiphertextBlob=b64decode(os.environ["USERNAME"]))['Plaintext']
PASSWORD = kms.decrypt(CiphertextBlob=b64decode(os.environ["PASSWORD"]))['Plaintext']
API_TOKEN = kms.decrypt(CiphertextBlob=b64decode(os.environ["API_TOKEN"]))['Plaintext']

GITHUB_API_URL = "http://github.nw.adesa.com/api/v3/{}"
GITHUB_ORGANISATION = "new-wave"
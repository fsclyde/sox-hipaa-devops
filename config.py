#### Settings file ####
import os, boto3, sys
from base64 import b64decode
from botocore.exceptions import ClientError

kms = boto3.client('kms')

# Github parameters
try:
    USERNAME = kms.decrypt(CiphertextBlob=b64decode(os.environ["USERNAME"]))['Plaintext']
    PASSWORD = kms.decrypt(CiphertextBlob=b64decode(os.environ["PASSWORD"]))['Plaintext']
    API_TOKEN = kms.decrypt(CiphertextBlob=b64decode(os.environ["API_TOKEN"]))['Plaintext']
except ClientError as e:
    if e.response['Error']['Code'] == 'AccessDeniedException':
        print "Decryption Error: Please check your AWS Access keys"
        sys.exit(1)
    elif e.response['Error']['Code'] == 'InvalidSignatureException':
        print "Invalid Signature for the decryption"
        sys.exit(1)
    else:
        print "Unexpected error: %s" % e
        sys.exit(1)


GITHUB_API_URL = "http://github.nw.adesa.com/api/v3/{}"
GITHUB_ORGANISATION = "new-wave"
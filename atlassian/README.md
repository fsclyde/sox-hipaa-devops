# SOX Change Control

This repository allows us to extract information during the CI/CD process. This will helps us to get the information below:

#### Source Code Controls

* [x] Repository Commit Author
* [x] Repository Pull Requests Reviewer
* [x] Commit ID

#### Deployment Pipeline Controls

* [x] Deployment user for all environment
* [x] Build Job Number
* [x] Project Name
* [x] Proof of QA Testing

#### Version Controls

* [x] Artecfact Name
* [x] Artecfact SHA
* [x] Artecfact Version

####  Change Traceability

* [x] Release TAG
* [x] Release Note
* [x] Jira Issue Number
* [x] PO Approval in UAT
* [x] QA testing Approval

The results of this script will populate data into and s3 bucket.

## Requirements

    pip install boto3 requests aws-cli html2text
    
## Preview

![ SOX Change Control ](https://github.com/fsclyde/sox-hipaa-devops/blob/master/images/change_control.png "ChangeControl")




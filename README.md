# SOX HIPAA Reports

Sox is a standards that allows companies provide Auditing Accountability, Responsibility, and Transparency on their assets. See more informations [ here ](https://en.wikipedia.org/wiki/Sarbanes%E2%80%93Oxley_Act)
This repository is a list of tools that allow the extraction of some main control of the SOX requirements.

The main objectif of this is to ensure that all SOX requirements are provided to the auditor using the Agile / Devops Framework. SOX requirements can be extracted directly from the CI/CD. More informations [ here ] (https://insights.sei.cmu.edu/devops/2015/09/-a-devops-a-day-keeps-the-auditors-away-and-helps-organizations-stay-in-compliance-with-federal-regu.html)

### design of the approach

![ SOX CI/CD ](https://github.com/fsclyde/sox-hipaa-devops/blob/master/images/soc_ci-cd.png "SOX")

### Source Code

1. Provide a system generated report of users with access rights to source code.
2. Provide evidence of quarterly reviews of users with access to code

#### results:

* [x] Output of the script: github_permissions.py

### Source Code deployment

1. Provide evidence of quarterly reviews of users with admin access to the source code repository
2. Provide evidence of quarterly reviews of users with access to promote code to production.

#### results:

* [x] Output of the script: github_permissions.py
* [x] Output of the script: promoting-users.groovy

### Production Databases Access

1. Provide reporting configuration for monitoring of events, changes, and activities to, from and in the DB environments.
2. Provide evidence of events and reporting review. Provide a report of alerts from the reporting system.
3. Provide evidence of follow-up to anomalous, excessive, unauthorized, or questionable activities. Provide ticket evidence of follow-up.
4. Provide evidence of a regular frequency DB accounts review of approved access.


#### results:

* [x] Output of the script: handler_database.js
* [x] RDS monitoring and SIEM (Loggly)

### Server Security & Passwords / Manage administrative access

1. Provide server security configuration standards.
2. Provide evidence of system monitoring for unusual account activity.
3. Provide evidence for password complexity and account settings up and down the tech stack. OS, Server, Network, Application, others

#### results:

* [x] Output of the script: handler_database.js
* [x] CloudTrail and AWS Trusted Advisor Events


###  Software / Data Changes

#### Software

1. Provide a system generated report of software changes
2. Provide evidence of business approval before release

#### Data

1. Provide a system generated report that identifies all production changes. Please include print screens of the configuration, parameters, or filters used to create the report.
2. Provide evidence of a formally documented change approval process and the approvals of all changes to production.


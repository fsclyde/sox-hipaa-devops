# SOX AWS Permissions

This Script generate a SOX report for Admins permissions on the specific element below:

    - Active Directory Users and Admins
    - AWS Users and Admins
    - AWS RDS Database admins & last SQL query


### SOX Production Databases Access

1. Provide reporting configuration for monitoring of events, changes, and activities to, from and in the DB environments.
2. Provide evidence of events and reporting review. Provide a report of alerts from the reporting system.
3. Provide evidence of follow-up to anomalous, excessive, unauthorized, or questionable activities. Provide ticket evidence of follow-up.
4. Provide evidence of a regular frequency DB accounts review of approved access.


### Requierements
    npm install -g serverless
    npm install activedirectory --save
    npm install aws-sdk --save


![ SOX Database Monitoring  ](https://github.com/fsclyde/sox-hipaa-devops/blob/master/images/monitoring.png "Database")

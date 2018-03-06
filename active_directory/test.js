// AD / AWS scripts
var reporter = require("./handler");
var event, context, callback = {}
reporter.myHandler(event, context, callback);

// RDS Production database Script
var reporter_data = require("./handler_database");
var event, context, callback = {}
reporter_data.myHandler_data(event, context, callback);

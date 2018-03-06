import hudson.model.*
import hudson.security.Permission
import hudson.EnvVars
import hudson.model.Hudson
import jenkins.*
import jenkins.model.*
import hudson.*
import com.michelin.cio.hudson.plugins.rolestrategy.RoleBasedAuthorizationStrategy
import groovy.json.JsonOutput

// Groovy helps http://grails.asia/groovy-each-examples
// upload file to s3 groovy https://gist.github.com/atomsfat/6273637


// @GrabResolver(name='jets3t', root='http://www.jets3t.org/maven2', m2Compatible='true')
// @Grab(group='net.java.dev.jets3t', module='jets3t', version='0.9.0')
// import org.jets3t.service.impl.rest.httpclient.RestS3Service
// import org.jets3t.service.security.AWSCredentials
// import org.jets3t.service.model.*


instance = Jenkins.getInstance()
globalNodeProperties = instance.getGlobalNodeProperties()
envVarsNodePropertyList = globalNodeProperties.getAll(hudson.slaves.EnvironmentVariablesNodeProperty.class)

def cleanUsers = { it.flatten().sort().unique() - "null"}
def export = {matrix, formatter -> formatter(matrix)}
def csv = { matrix -> matrix.collect{ key, value -> "\n$key, ${value.join(",").replace("true", "x").replace("false", " ")}" } + "\n" }
def authStrategy = Hudson.instance.getAuthorizationStrategy()

if(authStrategy instanceof RoleBasedAuthorizationStrategy){

   def permissions = authStrategy.roleMaps.inject([:]){map, it -> map + it.value.grantedRoles}
   def users = cleanUsers(permissions*.value)
   def permissionsByUser = users.inject([:]){ map, user ->
      map[user] =  permissions.findAll{ it.value.contains(user)}.collect{it.key.name}
      map
   }
   def usersPermissionsMatrix =[:]
   def roles = authStrategy.getRoleMap(authStrategy.GLOBAL).grantedRoles*.key.name.sort() + authStrategy.getRoleMap(authStrategy.PROJECT).grantedRoles*.key.name.sort()

   usersPermissionsMatrix["roles"] = roles
   users.each{ user ->
      usersPermissionsMatrix[user] = roles.inject([]){ list, role -> list << permissionsByUser[user].contains(role)
      }

   }
def data = export(usersPermissionsMatrix,csv)

// the maximum number of rows that will be converted, if 0 then all rows will be converted
Integer maxNumberOfRows = new Integer(0)

// the separator used for splitting the csv columns
String separator =  ","

def dataList = []
def lineCounter = 0
def headers = []
data.each() { line ->
    // skip the header; header is line 1
    if(maxNumberOfRows == 0 || lineCounter <= maxNumberOfRows) {
        if (lineCounter == 0) {
            headers = line.split(separator).collect{it.trim()}.collect{it.toLowerCase()}
        } else {
            def dataItem = [:]
            def row = line.split(separator).collect{it.trim()}.collect{it.toLowerCase()}

            headers.eachWithIndex() { header, index ->
                dataItem.put("${header}", "${row[index]}")
            }
            dataList.add(dataItem)
        }

    }
    lineCounter = lineCounter + 1
}

String output = JsonOutput.toJson(dataList)


}else{
   println "Not able to list the permissions by user"
}

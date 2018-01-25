import hudson.model.*
import hudson.security.Permission
import hudson.EnvVars
import hudson.model.Hudson
import jenkins.*
import jenkins.model.*
import hudson.*
import com.michelin.cio.hudson.plugins.rolestrategy.RoleBasedAuthorizationStrategy


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
      usersPermissionsMatrix[user] = roles.inject([]){ list, role ->
         list << permissionsByUser[user].contains(role)
      }
   }
println export(usersPermissionsMatrix,csv)

}else{
   println "Not able to list the permissions by user"
}
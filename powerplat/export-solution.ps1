###############################################################################################################
# This file uses PAC CLI to connect to a Power Platform environment, exports and unpacks the specified solution 
# and stores the solution files and unpacked source into the project directory.
# VSCode EXTENSION: https://learn.microsoft.com/en-us/power-platform/developer/howto/install-vs-code-extension
###############################################################################################################
# Get settings from Settings.json
$settings = Get-Content -Path .\powerplat\settings.json | ConvertFrom-Json
# Authenticate to source environment
pac auth create --environment $settings.sourceEnvURL
# create path variable from settings
$unmanagedPath = $settings.solutionDir + $settings.solutionName + "-" + $settings.solutionVersion + ".zip"
$managedPath = $settings.solutionDir + $settings.solutionName + "-" + $settings.solutionVersion + "managed.zip"
# Export solution files, save to project, increment version in source environment
pac solution export --path $unmanagedPath --name $settings.solutionName --managed false
pac solution export --path $managedPath --name $settings.solutionName --managed true
# increment solution version in source environment
pac solution online-version --solution-name $settings.solutionName --solution-version $settings.newSolutionVersion
# create settings file to set connection references
$deploymentSettingsPath = $settings.solutionDir + $settings.deploymentSettings
pac solution create-settings --solution-zip $managedPath --settings-file $deploymentSettingsPath
# unpack solution into source
pac solution unpack --zipfile $unmanagedPath --folder $settings.srcDir
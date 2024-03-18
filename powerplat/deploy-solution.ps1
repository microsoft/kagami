###############################################################################################################
# This file uses PAC CLI to connect to a Power Platform environment, and deploys the specified solution to that 
# target environment. 
# VSCode EXTENSION: https://learn.microsoft.com/en-us/power-platform/developer/howto/install-vs-code-extension
###############################################################################################################
# STEPS TO USE THIS SCRIPT: 
# 1. Use the settings_sample_json file to create a settings.json file in the same directory.
# 2. Update the settings.json file with the correct values for your environment.
# 3. Create connections in the target environment for Dataverse and Azure Blob Storage. Record the connection ID from the URL for each
# 3. Update the DocArchiveRequest_deploySettings.json file with the correct connection IDs https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools
# 4. Run the script.
###############################################################################################################
# Get settings from Settings.json
$settings = Get-Content -Path .\powerplat\settings.json | ConvertFrom-Json
# Authenticate to source environment
pac auth create --environment $settings.targetEnvURL
# create path variable from settings -- this will deploy the UNMANAGED version of the solution, intended to be
# deployed into a development environment for adjustment and customization to your specific needs. 
$path = $settings.solutionDir + $settings.solutionName + "-" + $settings.solutionVersion + ".zip"
# to re-use this script to deploy the MANAGED version of the solution to upper environments after adjusting for your 
# specific needs, uncomment and use the below path instead of the above (commenting in out the above path variable definition)
# $path = $settings.solutionDir + $settings.solutionName + "-" + $settings.solutionVersion + "managed.zip"
pac solution import --path $path
# use the below instead of the above to set connections while deploying. commenting out for now as this was causing an enexpected error in my target environment for some reason
# $deploymentSettingsPath = $settings.solutionDir + $settings.deploymentSettings
# pac solution import --path $path --settings-file $deploymentSettingsPath

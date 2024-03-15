###############################################################################################################
# This file uses PAC CLI to connect to a Power Platform environment, exports and unpacks the specified solution 
# and stores the solution files and unpacked source into the project directory.
# VSCode EXTENSION: https://learn.microsoft.com/en-us/power-platform/developer/howto/install-vs-code-extension
###############################################################################################################
# Get settings from Settings.json
$settings = Get-Content -Path .\powerplat\settings.json | ConvertFrom-Json
# Authenticate to source environment
pac auth create --environment $settings.targetEnvURL
# Export solution files, save to project, increment version in source environment
# create path variable from settings
$path = $settings.solutionDir + $settings.solutionName + "-" + $settings.solutionVersion + "managed.zip"
# deploy solution to target environment
pac solution import --path $path

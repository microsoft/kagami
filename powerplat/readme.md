# Power Platform Solution and Deployment Scripts

This directory contains a Power Platform Solution with Power Automate and Dataverse components that illustrate the ability to pick up a JSON blob output by the example AI document data extraction functions contained in this repo, and write it to Dataverse for further integration with other systems. Scripts and configuration files are also included to automate the deployment of the solution to a Power Platform environment.

## Contents

- `deploy-solution.ps1`: This PowerShell script connects to a Power Platform environment and deploys the specified solution to that environment.
- `settings.json`: This file contains the configuration settings for the deployment script. You need to create this file based on the `settings_sample_json` file and update it with the correct values for your environment.

## How to Use

1. Use the `settings_sample_json` file to create a `settings.json` file in the same directory.
2. Update the `settings.json` file with the correct values for your environment.
3. Create connections in the target environment for Dataverse and Azure Blob Storage. Record the connection ID from the URL for each.
4. Update the `DocArchiveRequest_deploySettings.json` file with the correct connection IDs. More information can be found [here](https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools).
5. Run the `deploy-solution.ps1` script.

## Note

The `pac` commands used in the script are part of the Power Apps CLI. You need to have the Power Apps CLI installed and added to your system's PATH. More information about the Power Apps CLI can be found [here](https://learn.microsoft.com/en-us/power-platform/developer/howto/install-vs-code-extension).
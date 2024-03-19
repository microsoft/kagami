# Power Platform Solution and Deployment Scripts

This directory contains a Power Platform Solution with Power Automate and Dataverse components that illustrate the ability to pick up a JSON blob output by the example AI document data extraction functions contained in this repo, and write it to Dataverse for further integration with other systems. Scripts and configuration files are also included to automate the deployment of the solution to a Power Platform environment.

## Contents

- `DocArchiveRequest-xxxx.zip`: Power Platform Solution, including:
    - Data model to support example integration of JSON extracted data into Dataverse
    - Primary integration flow example
        - `Process JSON DeocInfo into DV` cloud flow: triggered by a new blob created, parses JSON blob into a record in the `Archive Request` table, and a record into the `Extracted Entity` table for each key/value pair related to the created `Archive Request`
    - Secondary integration flow example
        - `Process JSON into DV key-value records` cloud flow: triggered by a new blob created, parses JSON blob into a record in the `Archive Request` table and calls the child flows to record extracted details
        - `CHILD - Process Protocol Doc` cloud flow: called to map extracted details into the `Protocol Doc` table, related to the created `Archive Request`
        - `CHILD - Process Report Doc` cloud flow: called to map extracted details into the `Report Doc` table, related to the created `Archive Request`
- `export-solution.ps1`: PowerShell script used to export solution files from the environment defined in a `settings.json` file
- `deploy-solution.ps1`: PowerShell script that deploys the specified solution to the environment defined in a `settings.json` file
- `settings.json`: This file contains the configuration settings for the deployment scripts. You need to create this file based on the `settings_sample_json` file and update it with the correct values for your environment.

## How to Use

1. Use the `settings_sample_json` file to create a `settings.json` file in the same directory.
2. Update the `settings.json` file with the correct values for your environment.
3. Create connections in the target environment for Dataverse and Azure Blob Storage. Record the connection ID from the URL for each.
4. Update the `DocArchiveRequest_deploySettings.json` file with the correct connection IDs. More information can be found [here](https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools).
5. Run the `deploy-solution.ps1` script.

## Note

The `pac` commands used in the script are part of the Power Apps CLI. You need to have the Power Apps CLI installed and added to your system's PATH. More information about the Power Apps CLI can be found [here](https://learn.microsoft.com/en-us/power-platform/developer/howto/install-vs-code-extension).
# Trade Runner

## Intro
This is a collection of Python AWS lambda functions and related AWS infrastructure, configured within the Serverless framework, which run tasks associated with financial trading and market analysis.

## Structure
Each business functionality is separated into modules. Currently, the existing modules are:
- trade_job - functionality relating to running and managing trade jobs

## Set-up
This section includes information related to setting up for development and operation

### Pre-requisites
- An AWS account
- AWS user configured with appropriate permissions
- NPM installed

### Deployment

To deploy a Serverless job on the command line:
- Move into the required directory 
- Sign into your AWS account e.g.
```
aws sso login --profile <aws_profile_name>
```
- In order to deploy, you may need to set the following environment variable to source credentials from the config file and correct profile:
```     
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=<aws_profile_name>
```
- Deploy the lambda with the following:
```
sls deploy --aws-profile <aws_profile_name> --verbose
```

## Running Tests
In the top-level directory (same as this README file) the following command can be run to run the tests of a 
particular module:
```
python -m unittest discover <module_name>/test
```
e.g. to run the tests in the `trade_job` directory the following can be run:
```
python -m unittest discover trade_job/test
```

## Useful Commands
Adding a new Serverless plugin:
```
sudo sls plugin install -n <plugin_name>
```


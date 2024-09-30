# Trade Runner

## Introduction
This is a repository which contains the code for a system that evaluates market 
data relating to a particular stock, and makes buy or sell orders based on defined conditions. 

## Structure
Currently, there is one module:
- trade_job - configuration and code files for an AWS API Gateway endpoint, Step Function and lambda 
  function (Python) for the purpose of receiving an API request containing parameters, and running the step 
  function/lambda to retrieve market data, analyse it, and make buy or sell orders. The tests for the Python code 
  are included in this directory.

## Set-up
This section includes general information related to setting up the endpoints and infrastructure in AWS for development 
and operation

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

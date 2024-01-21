# Trade Job Runner

## Intro
This is a collection of Python AWS lambda functions (serverless) which run tasks associated with financial trading and market analysis.

## Structure
Each serverless job is separated into a sub-directory

## Deployment
To deploy a serverless job on the command line:
- Move into the required directory 
- Sign into your AWS account e.g.
```
        aws sso login --profile <aws_profile_name>
```
- You may need to set the following environment variable to source credentials from the config file and correct profile:
```     
        export AWS_SDK_LOAD_CONFIG=1
        export AWS_PROFILE=<profile_name>
```
    - Deploy the lambda with the following:
        sls deploy --aws-profile <aws_profile_name> --verbose
## Useful Commands
Adding a new Serverless plugin:
sudo sls plugin install -n <plugin_name>

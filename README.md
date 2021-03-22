# Project Cicero

## Local Setup

1. Ensure NodeJS is installed and the AWS CDK toolkit is set up [correctly](https://docs.aws.amazon.com/cdk/latest/guide/work-with.html#work-with-prerequisites). To get your AWS credentials with your educate account click the account details button before signing in and copy and paste the CLI details into the .aws folder.
   ![](https://user-images.githubusercontent.com/31460379/112003536-5d314f80-8af7-11eb-8912-1a53db51ce73.png)
    `> vim ~/.aws/credentials`
2. Make sure Python 3.6 or higher is [installed](https://www.python.org/downloads/) along with pip and virtualenv packages.
3. Source virtual environment for Python packages.
    
    `> source .venv/bin/activate`
4. Install packages.

    `> pip install -r requirements.txt`
5. Profit

For more information on how to add modules and documentation on modules check out the AWS [docs](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html).

## Synthesize and Deploy
Stacks can be simply synthesized into Cloudformation templates or directly deployed from the command line.

### Synthesize
`> cdk synth`

### Deploy
`> cdk deploy`
# Deploy Microsoft SQL on Amazon FSx with AWS CDK

Welcome, this CDK code is meant to help customers to deploy all the infrastructure requirements for running Amazon FSx as a shared storage solution to Microsoft SQL server as described in the following blogpost: [link](https://aws.amazon.com/blogs/storage/simplify-your-microsoft-sql-server-high-availability-deployments-using-amazon-fsx-for-windows-file-server/)

[CDK Stacks](https://github.com/dudutwizer/MSSQL-on-FSx-With-CDK/tree/master/CDK_Stacks) folder contains the following CDK Stacks:

- [Amazon-VPC](CDK_Stacks/cdk_vpc_stack.py) : This stack will deploy a VPC with 4 subnets (2 Private and 2 Public) , NAT Gateway and Internet Gateway
- [Managed-AD](CDK_Stacks/cdk_mad.py) : This stack will generate a new password and will store it on AWS Secrets manager, then will deploy Managed AD
- [Amazon-FSX](CDK_Stacks/cdk_fsx_stack.py) : This stack will deploy Amazon FSx for Windows File Server in two Availability zones
- [EC2 Bastion Host](CDK_Stacks/cdk_ec2_bastion_stack.py) : This stack will deploy Windows 2019 machine and with the following [user-data script](user_data/bastion_user_data.ps1) in Public Subnet
- [EC2 SQL](CDK_Stacks/cdk_ec2_sql_stack.py) : This stack will deploy two Windows 2019 machines and with the following [user-data script](user_data/sql_user_data.ps1) in Private subnet


In order to change this CDK code to match your enviroment, you only need to change this file [app.py](app.py). 

# How to use this AWS CDK Code

You can use the following step to activate virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

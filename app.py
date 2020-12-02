#!/usr/bin/env python3

# CDK
from aws_cdk import core
import aws_cdk.aws_cloudformation as cfn

# Custom stacks
from CDK_Stacks.cdk_vpc_stack import CdkVpcStack, DHCPOption, SetDHCPOption
from CDK_Stacks.cdk_mad import Mad, Secret
from CDK_Stacks.cdk_fsx_stack import cdkFSxStack
from CDK_Stacks.cdk_ec2_bastion_stack import CdkEc2Bastion
from CDK_Stacks.cdk_ec2_sql_stack import CdkEc2SQL

# Params
env_EU = core.Environment(account='your-account-number', region='eu-west-1')
domain_name = 'mydomain.aws'
FSxSize = 6000
FSxMBps = 128
KeyPairName = 'sql_on_fsx'
sql_ec2_type = "m5.4xlarge"
bastion_ec2_type = "t3.medium"

app = core.App()

# First stack, VPC, 1 public and 1 private subnets in 2 AZs = 4 subnets.
vpc_stack = CdkVpcStack(app, "VPC", env=env_EU)

# Managed AD + Random password stored in Secret Manager key-name: 'Mad-Admin-Password'
secret_stack = Secret(app, 'MAD-Secret',password_object={'Domain': domain_name, 'UserID': 'Admin'},secret_name="ManagedAD-Admin-Password",description="Managed AD Aut-Generated Password",env=env_EU)
mad_stack = Mad(app, 'Managed-AD', vpc=vpc_stack.vpc,domain_name=domain_name, edition='Standard',secret=secret_stack, env=env_EU)

# FSx for Windows, joined to the active directory + multi AZ
fsx_stack = cdkFSxStack(app, 'Multi-AZ-FSx-For-SQL', vpc=vpc_stack.vpc,directory=mad_stack.ad, 
                        throughput_capacity=FSxMBps, size=FSxSize, env=env_EU)

# Change the DHCP Options of the VPC to include the Managed AD as the DNS server
dhcp_option = DHCPOption(app, 'VPC-DHCP-Options-with-MAD',directory=mad_stack.ad, vpc=vpc_stack.vpc, env=env_EU)
set_dhcp_option_to_vpc = SetDHCPOption(app, 'Apply-DHCP-Options', vpc=vpc_stack.vpc, dhcp_options=dhcp_option, env=env_EU)

# Launch two servers with Windows 2019 + FailoverCluster role + Bastion Server with management tools and domain joined.
ec2_sql_stack = CdkEc2SQL(app, "SQL-Nodes", vpc=vpc_stack.vpc,KeyPairName=KeyPairName, ec2_type=sql_ec2_type, env=env_EU)
ec2_bastion = CdkEc2Bastion(app, "Bastion-Host", vpc=vpc_stack.vpc,KeyPairName=KeyPairName, ec2_type=bastion_ec2_type, env=env_EU)

# Defining the order of the CDK Deployment
secret_stack.add_dependency(vpc_stack)
mad_stack.add_dependency(secret_stack)
fsx_stack.add_dependency(mad_stack)
dhcp_option.add_dependency(mad_stack)
set_dhcp_option_to_vpc.add_dependency(dhcp_option)
ec2_sql_stack.add_dependency(set_dhcp_option_to_vpc)
ec2_bastion.add_dependency(ec2_sql_stack)

app.synth()

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_iam as iam

windows_ami = ec2.MachineImage.latest_windows(version=ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE)  # Indicate your AMI, no need a specific id in the region

with open("./user_data/sql_user_data.ps1") as f:
    user_data = f.read()
    
class CdkEc2SQL(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc,KeyPairName,ec2_type, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create SQL instances
        azs = vpc.availability_zones
        self.sql_sg = ec2.SecurityGroup(self, 'SQL-Security-Group',vpc=vpc,allow_all_outbound=True,description='SQL-Security-Group-Nodes',security_group_name='sql-sg-'+id)
        self.role = iam.Role(self, 'ec2-sql-role',assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        
        #Grant permission to access the MAD secret
        self.role.add_managed_policy(policy=iam.ManagedPolicy.from_aws_managed_policy_name('SecretsManagerReadWrite'))

        self.node1 = ec2.Instance(self, "SQL Node1",
                                instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
                                machine_image=windows_ami,
                                vpc=vpc,
                                key_name=KeyPairName,
                                user_data=ec2.UserData.custom(user_data),
                                availability_zone=azs[0],
                                role=self.role,
                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE,one_per_az=True),
                                security_group=self.sql_sg
                                )
        self.node2 = ec2.Instance(self, "SQL Node2",
                                instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
                                machine_image=windows_ami,
                                vpc=vpc,
                                key_name=KeyPairName,
                                user_data=ec2.UserData.custom(user_data),
                                availability_zone=azs[1],
                                role=self.role,
                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE,one_per_az=True),
                                security_group=self.sql_sg
                                )

        # Open Security group - change to a reference
        self.sql_sg.add_ingress_rule(peer=ec2.Peer.ipv4('10.0.0.0/8'),connection=ec2.Port.all_traffic(),description='Allow traffic between SQL nodes + VPC')
        
        
        core.CfnOutput(self, "node1",value=self.node1.instance_private_ip)
        core.CfnOutput(self, "node2",value=self.node2.instance_private_ip)
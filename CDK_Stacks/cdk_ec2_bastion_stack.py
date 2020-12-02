from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_secretsmanager as secretsmanager

windows_ami = ec2.MachineImage.latest_windows(version=ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE)  # Indicate your AMI, no need a specific id in the region
                                
with open("./user_data/bastion_user_data.ps1") as f:
    user_data = f.read()


class CdkEc2Bastion(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, KeyPairName,ec2_type, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.role = iam.Role(self, 'ec2-bastion-role',assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        
        #Grant permission to access the MAD secret
        self.role.add_managed_policy(policy=iam.ManagedPolicy.from_aws_managed_policy_name('SecretsManagerReadWrite'))

        # Create Bastion
        self.bastion = ec2.Instance(self, id,
                                    instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
                                    machine_image=windows_ami,
                                    vpc=vpc,
                                    user_data=ec2.UserData.custom(user_data),
                                    key_name=KeyPairName,
                                    role=self.role,
                                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
                                    )

        self.bastion.connections.allow_from_any_ipv4(
            ec2.Port.tcp(3389), "Internet access RDP")

        core.CfnOutput(self, "Bastion Host",
                       value=self.bastion.instance_public_dns_name)
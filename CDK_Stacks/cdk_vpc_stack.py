from aws_cdk import core
import aws_cdk.aws_ec2 as ec2


class CdkVpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, id, max_azs=2, cidr="10.10.0.0/16",
                            # This configuration will create 2 groups in 2 AZs = 4 subnets.
                            subnet_configuration=[
                                ec2.SubnetConfiguration(
                                    subnet_type=ec2.SubnetType.PUBLIC,
                                    name="Public",
                                    cidr_mask=24
                                    ), 
                                ec2.SubnetConfiguration(
                                    subnet_type=ec2.SubnetType.PRIVATE,
                                    name="Private",
                                    cidr_mask=24
                                    )
                                ],
                            nat_gateways=2,
                            )

class DHCPOption(core.Stack):
    def __init__(self, scope: core.Construct, id: str, directory, vpc,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dhcp = ec2.CfnDHCPOptions(self,
                                    id,
                                    domain_name=directory.name,
                                    domain_name_servers=[core.Fn.import_value('mad-dns1'),core.Fn.import_value('mad-dns2')],
                                    ntp_servers=["169.254.169.123"])

class SetDHCPOption(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc,dhcp_options,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ec2.CfnVPCDHCPOptionsAssociation(self, id=id,vpc_id=vpc.vpc_id, dhcp_options_id=dhcp_options.dhcp.ref)


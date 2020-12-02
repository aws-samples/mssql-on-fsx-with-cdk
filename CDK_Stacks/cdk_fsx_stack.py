from aws_cdk import core
import aws_cdk.aws_fsx as fsx
import aws_cdk.aws_ec2 as ec2


class cdkFSxStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc,directory,size,throughput_capacity, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Select two private subnets in a VPC 
        subnets = vpc.select_subnets(subnet_type= ec2.SubnetType.PRIVATE).subnet_ids
        directoryid = directory.ref

        self.fsx = fsx.CfnFileSystem(self, id=id, file_system_type='WINDOWS',subnet_ids=subnets,
                                    windows_configuration=fsx.CfnFileSystem.WindowsConfigurationProperty(
                                                            active_directory_id=directoryid,
                                                            throughput_capacity=throughput_capacity,
                                                            preferred_subnet_id=subnets[0],
                                                            deployment_type="MULTI_AZ_1"
                                                            )
                                     ,storage_capacity=size)
        




        
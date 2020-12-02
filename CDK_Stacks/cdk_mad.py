from aws_cdk import core
import aws_cdk.aws_directoryservice as mad
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_secretsmanager as secretsmanager
import simplejson as json

class Secret(core.Stack):
     def __init__(self, scope: core.Construct, id: str, password_object: object, secret_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.password_object = password_object
        self.Secret = secretsmanager.Secret(self,id=id,
                                            generate_secret_string=secretsmanager.SecretStringGenerator(
                                                secret_string_template=json.dumps(password_object),
                                                generate_string_key='Password',
                                                exclude_punctuation=True,
                                            ),secret_name=secret_name)
        
        self.clear_text_secret = self.Secret.secret_value_from_json('Password').to_string()

class Mad(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, domain_name: str, secret: Secret, edition: str,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        subnets = vpc.select_subnets(subnet_type= ec2.SubnetType.PRIVATE).subnet_ids
        vpcSettings = mad.CfnMicrosoftAD.VpcSettingsProperty(subnet_ids=subnets,vpc_id=vpc.vpc_id)
        
        self.ad = mad.CfnMicrosoftAD(self,'MAD',
                                        name=domain_name,
                                        password=secret.clear_text_secret,
                                        vpc_settings=vpcSettings,
                                        edition=edition
                                        )
        
        # instead of importing from cf, use the entire stack reference.
        mad_dns_ip1 = core.Fn.select(0,self.ad.attr_dns_ip_addresses)
        mad_dns_ip2 = core.Fn.select(1,self.ad.attr_dns_ip_addresses)

        core.CfnOutput(self, "mad-dns1",value=mad_dns_ip1,export_name='mad-dns1')
        core.CfnOutput(self, "mad-dns2",value=mad_dns_ip2,export_name='mad-dns2')

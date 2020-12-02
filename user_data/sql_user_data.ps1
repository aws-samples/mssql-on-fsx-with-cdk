<powershell>
# SQL server configuration
Import-Module AWSPowerShell
New-NetFirewallRule -DisplayName 'Allow local VPC' -Direction Inbound -LocalAddress 10.0.0.0/8 -LocalPort Any -Action Allow
Install-WindowsFeature -Name Failover-Clustering -IncludeManagementTools

#domain join with secret from secret manager
[string]$SecretAD  = "ManagedAD-Admin-Password"
$SecretObj = Get-SECSecretValue -SecretId $SecretAD
[PSCustomObject]$Secret = ($SecretObj.SecretString  | ConvertFrom-Json)
$password   = $Secret.Password | ConvertTo-SecureString -asPlainText -Force
$username   = $Secret.UserID + "@" + $Secret.Domain
$credential = New-Object System.Management.Automation.PSCredential($username,$password)
Add-Computer -DomainName $Secret.Domain -Credential $credential -Restart -Force
</powershell>
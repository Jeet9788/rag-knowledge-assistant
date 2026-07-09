<#
Tears down the AWS resources created by deploy.ps1 to stop all charges.

Usage:
  ./destroy.ps1 -InstanceId "i-0123456789" -Region "us-east-1"
#>
param(
  [Parameter(Mandatory = $true)][string]$InstanceId,
  [string]$Region = "us-east-1",
  [string]$Name = "rag-knowledge-assistant"
)

$ErrorActionPreference = "Continue"

Write-Host "==> Terminating instance $InstanceId" -ForegroundColor Yellow
aws ec2 terminate-instances --region $Region --instance-ids $InstanceId | Out-Null
aws ec2 wait instance-terminated --region $Region --instance-ids $InstanceId

Write-Host "==> Deleting security group $Name-sg"
aws ec2 delete-security-group --region $Region --group-name "$Name-sg" 2>$null

Write-Host "==> Deleting key pair $Name"
aws ec2 delete-key-pair --region $Region --key-name $Name 2>$null

Write-Host "==> Done. All billable resources removed." -ForegroundColor Green

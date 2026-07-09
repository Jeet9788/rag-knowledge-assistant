<#
Deploys the RAG Knowledge Assistant to a single EC2 instance running docker compose.
Cheapest sane setup: one t3.small (~$15/mo) hosting backend + frontend + pgvector,
with the LLM served by the free Gemini API (no GPU needed).

Prerequisites:
  - AWS CLI installed and configured (`aws configure`) with an IAM user that can
    manage EC2 (see deploy/aws/README.md for the exact IAM policy).
  - A public GitHub repo URL for this project.
  - A Google Gemini API key (free): https://aistudio.google.com/apikey

Usage:
  ./deploy.ps1 -RepoUrl "https://github.com/<you>/rag-knowledge-assistant.git" `
               -GeminiApiKey "<key>" -Region "us-east-1"
#>
param(
  [Parameter(Mandatory = $true)][string]$RepoUrl,
  [Parameter(Mandatory = $true)][string]$GeminiApiKey,
  [string]$Region = "us-east-1",
  # t3.micro is AWS Free Tier eligible (750 hrs/month for 12 months).
  # A 2 GB swap file (added via user-data) lets the ML models run on 1 GB RAM.
  [string]$InstanceType = "t3.micro",
  [string]$Name = "rag-knowledge-assistant"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Using region $Region" -ForegroundColor Cyan

# 1. Latest Amazon Linux 2023 AMI
$ami = aws ssm get-parameters --region $Region `
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 `
  --query "Parameters[0].Value" --output text
Write-Host "==> AMI: $ami"

# 2. Key pair (saved locally as <Name>.pem)
$keyPath = Join-Path $PSScriptRoot "$Name.pem"
if (-not (Test-Path $keyPath)) {
  aws ec2 create-key-pair --region $Region --key-name $Name `
    --query "KeyMaterial" --output text | Out-File -Encoding ascii $keyPath
  Write-Host "==> Saved key to $keyPath"
}

# 3. Security group (SSH + app ports)
$sgId = aws ec2 create-security-group --region $Region `
  --group-name "$Name-sg" --description "RAG app" --query "GroupId" --output text 2>$null
if (-not $sgId) {
  $sgId = aws ec2 describe-security-groups --region $Region `
    --group-names "$Name-sg" --query "SecurityGroups[0].GroupId" --output text
}
foreach ($port in 22, 3000, 8000) {
  aws ec2 authorize-security-group-ingress --region $Region --group-id $sgId `
    --protocol tcp --port $port --cidr 0.0.0.0/0 2>$null | Out-Null
}
Write-Host "==> Security group: $sgId"

# 4. Render user-data with secrets
$dbPassword = [System.Guid]::NewGuid().ToString("N")
$userData = Get-Content (Join-Path $PSScriptRoot "user-data.sh") -Raw
$userData = $userData.Replace("__REPO_URL__", $RepoUrl)
$userData = $userData.Replace("__GEMINI_API_KEY__", $GeminiApiKey)
$userData = $userData.Replace("__DB_PASSWORD__", $dbPassword)
$userDataB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($userData))

# 5. Launch instance
$instanceId = aws ec2 run-instances --region $Region `
  --image-id $ami --instance-type $InstanceType --key-name $Name `
  --security-group-ids $sgId `
  --block-device-mappings "DeviceName=/dev/xvda,Ebs={VolumeSize=20,VolumeType=gp3}" `
  --user-data $userDataB64 `
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$Name}]" `
  --query "Instances[0].InstanceId" --output text
Write-Host "==> Launched instance: $instanceId"

aws ec2 wait instance-running --region $Region --instance-ids $instanceId
$ip = aws ec2 describe-instances --region $Region --instance-ids $instanceId `
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text

Write-Host ""
Write-Host "==> Instance is booting and building the app (first boot takes ~5-8 min)." -ForegroundColor Green
Write-Host "    Frontend:  http://$ip:3000"
Write-Host "    Backend:   http://$ip:8000/health"
Write-Host "    SSH:       ssh -i `"$keyPath`" ec2-user@$ip"
Write-Host ""
Write-Host "To tear everything down and stop charges, run:" -ForegroundColor Yellow
Write-Host "    ./destroy.ps1 -Region $Region -InstanceId $instanceId"

# Deploying to AWS

This deploys the whole stack (frontend + backend + pgvector) onto a single small
EC2 instance running `docker compose`. The LLM is served by the **free Google
Gemini API**, so no GPU instance is required. Estimated cost: **~$15/month** for a
`t3.small` (or free-tier eligible on `t3.micro` if your account qualifies, though
2 GB RAM is recommended for the embedding model).

## Architecture

```
                Internet
                   |
        +----------+-----------+
        |   EC2 (t3.small)      |
        |  docker compose:      |
        |   - frontend :3000    |
        |   - backend  :8000    |----> Gemini API (free tier)
        |   - pgvector :5432    |
        +-----------------------+
```

## Prerequisites

1. **AWS CLI** installed and configured:
   ```powershell
   aws configure   # enter Access Key, Secret, region (e.g. us-east-1)
   ```
2. An **IAM user** with permissions to manage EC2. Minimal policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       { "Effect": "Allow", "Action": ["ec2:*", "ssm:GetParameters"], "Resource": "*" }
     ]
   }
   ```
   (You can scope this down further for production.)
3. The project pushed to a **public GitHub repo**.
4. A **Gemini API key**: https://aistudio.google.com/apikey

## Deploy

```powershell
cd deploy/aws
./deploy.ps1 -RepoUrl "https://github.com/<you>/rag-knowledge-assistant.git" `
             -GeminiApiKey "<your-key>" -Region "us-east-1"
```

The script will:
- pick the latest Amazon Linux 2023 AMI,
- create a key pair (`rag-knowledge-assistant.pem`) and security group,
- launch the instance with a cloud-init script that installs Docker, clones the
  repo, writes `.env`, and runs `docker compose up -d --build`,
- print the public URLs.

First boot takes ~5-8 minutes while images build. Then open `http://<ip>:3000`.

## Tear down (stop charges)

```powershell
./destroy.ps1 -InstanceId "<i-xxxx from deploy output>" -Region "us-east-1"
```

## Production hardening (optional next steps)

- Put an HTTPS load balancer / CloudFront in front and restrict security-group ports.
- Move Postgres to **RDS** with the `vector` extension instead of a container.
- Push images to **ECR** and run on **ECS Fargate** or **App Runner** instead of a
  single EC2 (higher availability, higher cost).

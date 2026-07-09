#!/bin/bash
# Cloud-init script for Amazon Linux 2023.
# Installs Docker + Compose, clones the repo, writes .env, and starts the stack.
set -euxo pipefail

dnf update -y
dnf install -y docker git
systemctl enable --now docker

# Add a 2 GB swap file so the embedding/reranker models run on a 1 GB
# free-tier t3.micro without the OOM killer stopping containers.
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Docker Compose v2 plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

cd /opt
git clone "__REPO_URL__" app
cd app

cat > .env <<EOF
POSTGRES_USER=rag
POSTGRES_PASSWORD=__DB_PASSWORD__
POSTGRES_DB=ragdb
LLM_PROVIDER=gemini
GEMINI_API_KEY=__GEMINI_API_KEY__
GEMINI_MODEL=gemini-2.0-flash
# Leave NEXT_PUBLIC_API_URL empty so the browser derives it from the host.
NEXT_PUBLIC_API_URL=
EOF

docker compose up -d --build

#!/usr/bin/env bash
# ==============================================================================
# Hostinger VPS Automated Deployment Script for CALL-E Supply Chain Platform
# Target Domain: calle.fyro.cloud
# ==============================================================================
set -e

DOMAIN="calle.fyro.cloud"
REPO_URL="https://github.com/mohSadiq90/call-e-hackathon.git"
INSTALL_DIR="/var/www/call-e-hackathon"
SERVICE_NAME="calle"

echo "======================================================================"
echo "🚀 Deploying CALL-E Supply Chain Intelligence to ${DOMAIN}..."
echo "======================================================================"

# 1. Update system packages
echo "📦 Updating apt packages..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 2. Clone or pull repository
if [ -d "${INSTALL_DIR}/.git" ]; then
    echo "🔄 Existing repository found at ${INSTALL_DIR}. Pulling latest changes..."
    cd "${INSTALL_DIR}"
    git fetch origin main
    git reset --hard origin/main
else
    echo "📥 Cloning repository into ${INSTALL_DIR}..."
    sudo mkdir -p "${INSTALL_DIR}"
    sudo chown -R $USER:$USER "${INSTALL_DIR}"
    git clone "${REPO_URL}" "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# 3. Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "${INSTALL_DIR}/venv" ]; then
    python3 -m venv "${INSTALL_DIR}/venv"
fi
"${INSTALL_DIR}/venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

# 4. Configure .env if missing
if [ ! -f "${INSTALL_DIR}/.env" ]; then
    echo "⚙️ Creating .env from .env.production.example..."
    cp "${INSTALL_DIR}/deploy/.env.production.example" "${INSTALL_DIR}/.env"
    echo "⚠️ Please edit ${INSTALL_DIR}/.env to set your CALLE_API_KEY if making live calls."
fi

# 5. Setup Systemd service
echo "⚙️ Configuring Systemd service (${SERVICE_NAME}.service)..."
sudo cp "${INSTALL_DIR}/deploy/calle.service" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

# 6. Setup Nginx Configuration
echo "🌐 Configuring Nginx reverse proxy for ${DOMAIN}..."
sudo cp "${INSTALL_DIR}/deploy/nginx/calle.fyro.cloud.conf" "/etc/nginx/sites-available/${DOMAIN}"
sudo ln -sf "/etc/nginx/sites-available/${DOMAIN}" "/etc/nginx/sites-enabled/${DOMAIN}"

# Test Nginx syntax
sudo nginx -t

# 7. Obtain Let's Encrypt SSL certificate
echo "🔒 Requesting Let's Encrypt SSL Certificate for ${DOMAIN}..."
if sudo certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --register-unsafely-without-email; then
    echo "✅ SSL Certificate successfully installed for ${DOMAIN}!"
else
    echo "⚠️ Certbot challenge failed. Make sure DNS A record for ${DOMAIN} points to this VPS IP address."
    echo "   Reloading Nginx in HTTP mode..."
fi

sudo systemctl reload nginx

# 8. Verify Deployment
echo "🔍 Checking local application health..."
sleep 3
if curl -s http://127.0.0.1:8000/health | grep -q "healthy"; then
    echo "======================================================================"
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "• Web Dashboard: https://${DOMAIN}/"
    echo "• REST API Docs: https://${DOMAIN}/docs"
    echo "• Health Endpoint: https://${DOMAIN}/health"
    echo "======================================================================"
else
    echo "❌ Local health check failed. Check logs with: journalctl -u ${SERVICE_NAME} -n 50"
    exit 1
fi

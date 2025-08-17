#!/bin/bash

# Initial server setup script for Ubuntu 22.04
set -e

echo "Starting server setup..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install system dependencies
sudo apt install -y build-essential curl git ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create application user
sudo useradd --system --gid www-data --shell /bin/bash --home /var/www/clinical_scheduler clinical_scheduler

# Create application directory
sudo mkdir -p /var/www/clinical_scheduler
sudo chown clinical_scheduler:www-data /var/www/clinical_scheduler

# Create log directory
sudo mkdir -p /var/log/clinical_scheduler
sudo chown clinical_scheduler:www-data /var/log/clinical_scheduler

# Setup PostgreSQL
sudo -u postgres createuser --interactive --pwprompt clinical_scheduler
sudo -u postgres createdb --owner clinical_scheduler clinical_scheduler

echo "Server setup complete!"
echo "Next steps:"
echo "1. Clone your repository to /var/www/clinical_scheduler"
echo "2. Run deploy/deploy.sh"
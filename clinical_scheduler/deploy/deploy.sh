#!/bin/bash

# Deployment script
set -e

APP_DIR="/var/www/clinical_scheduler"
USER="clinical_scheduler"

echo "Starting deployment..."

# Navigate to app directory
cd $APP_DIR

# Pull latest code only if this is a git repository
if [ -d ".git" ]; then
    echo "Git repository detected, pulling latest changes..."
    git pull origin main
else
    echo "No git repository found, using local code..."
fi

# Activate virtual environment or create if doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install/update dependencies
pip install --upgrade pip
pip install -r andiehsialmft/clinical_scheduler/Requirements/base.txt

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Run migrations
python manage.py migrate --settings=config.settings.production

# Create superuser if needed (skip if exists)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'kevjou97@gmail.com', 'anping12')" | python manage.py shell --settings=config.settings.production

# Copy service files
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/sites-available/clinical_scheduler

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/clinical_scheduler /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Set permissions
sudo chown -R $USER:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Reload systemd and restart services
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment complete!"
echo "Check status with: sudo systemctl status gunicorn"
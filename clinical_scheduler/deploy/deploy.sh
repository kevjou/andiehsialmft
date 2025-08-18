#!/bin/bash

# Deployment script
set -e

APP_DIR="/var/www/clinical_scheduler"
DJANGO_DIR="$APP_DIR/andiehsialmft"
USER="clinical_scheduler"

echo "Starting deployment..."

# Navigate to app directory
cd $DJANGO_DIR

# Pull latest code only if this is a git repository
if [ -d ".git" ]; then
    echo "Git repository detected, pulling latest changes..."
    git pull origin main
else
    echo "No git repository found, using local code..."
fi

# Activate virtual environment or create if doesn't exist
if [ ! -d "$APP_DIR/venv" ]; then
    cd $APP_DIR
    python3 -m venv venv
fi
source venv/bin/activate

# Install/update dependencies
pip install --upgrade pip
pip install -r clinical_scheduler/Requirements/base.txt

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Run migrations
python manage.py migrate --settings=config.settings.production

# Create superuser if needed (skip if exists)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'kevjou97@gmail.com', 'anping12')" | python manage.py shell --settings=config.settings.production

# Go back to app directory for service files
cd $APP_DIR

# Copy service files
if [ -f "andiehsialmft/clinical_scheduler/deploy/gunicorn.service" ]; then
    sudo cp andiehsialmft/clinical_scheduler/deploy/gunicorn.service /etc/systemd/system/
    echo "Copied gunicorn.service"
else
    echo "Warning: gunicorn.service not found at andiehsialmft/clinical_scheduler/deploy/gunicorn.service"
fi

if [ -f "andiehsialmft/clinical_scheduler/deploy/nginx.conf" ]; then
    sudo cp andiehsialmft/clinical_scheduler/deploy/nginx.conf /etc/nginx/sites-available/clinical_scheduler
    echo "Copied nginx.conf"
else
    echo "Warning: nginx.conf not found at andiehsialmft/clinical_scheduler/deploy/nginx.conf"
fi

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/clinical_scheduler /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Set permissions
sudo chown -R $USER:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Update gunicorn service to use correct paths
sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$DJANGO_DIR|g" /etc/systemd/system/gunicorn.service
sudo sed -i "s|ExecStart=.*venv/bin/gunicorn|ExecStart=$APP_DIR/venv/bin/gunicorn|g" /etc/systemd/system/gunicorn.service

# Reload systemd and restart services
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment complete!"
echo "Django directory: $DJANGO_DIR"
echo "Check status with: sudo systemctl status gunicorn"
echo "Check logs with: sudo journalctl -u gunicorn -f"
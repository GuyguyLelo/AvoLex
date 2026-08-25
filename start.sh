#!/bin/bash
cd /var/www/AvoLex
source venv/bin/activate

# Variables obligatoires
export DJANGO_SETTINGS_MODULE=config.settings.prod
export SECRET_KEY="django-insecure-@v!6x&n8x!9j#q$w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6"
export ALLOWED_HOSTS="avolex.e-paie.com,41.79.235.74,127.0.0.1,localhost"
export DATABASE_URL="postgres://user_avolex_db:Mohk%40ndolo2303@localhost:5432/AvoLex_db"
export SECURE_SSL_REDIRECT="False"
export USE_X_FORWARDED_HOST="True"
export DEBUG="True"
export CSRF_TRUSTED_ORIGINS="https://avolex.e-paie.com,http://avolex.e-paie.com"
export FORCE_SCRIPT_NAME="/avolex"

echo "🚀 Starting Gunicorn with:"
echo "📋 DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "📋 SECURE_SSL_REDIRECT=$SECURE_SSL_REDIRECT"
echo "📋 DEBUG=$DEBUG"
echo "📋 FORCE_SCRIPT_NAME=$FORCE_SCRIPT_NAME"
echo "📋 ALLOWED_HOSTS=$ALLOWED_HOSTS"

exec venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8007 config.wsgi:application

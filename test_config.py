#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

sys.path.append('/var/www/AvoLex')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

try:
    django.setup()
    print("✅ Django setup successful!")
    print(f"✅ ROOT_URLCONF: {settings.ROOT_URLCONF}")
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ SECRET_KEY defined: {len(settings.SECRET_KEY) > 10}")
    print(f"✅ FORCE_SCRIPT_NAME: {settings.FORCE_SCRIPT_NAME}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

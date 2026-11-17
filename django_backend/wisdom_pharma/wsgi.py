"""
WSGI config for wisdom_pharma project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys
import logging
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_pharma.settings')

application = get_wsgi_application()

# Ensure base directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Auto-migrate and seed in production if tables are missing
try:
    from django.core.management import call_command
    from django.db import connection
    tables = connection.introspection.table_names()
    if 'medicines' not in tables or 'categories' not in tables:
        logging.info("Auto-migrating database on startup...")
        call_command('migrate', interactive=False)
        try:
            from seed_data import run as seed_run
            logging.info("Auto-seeding database on startup...")
            seed_run()
        except Exception as seed_err:
            logging.warning(f"Auto-seed error on startup: {seed_err}")
except Exception as e:
    logging.warning(f"Startup migration check: {e}")

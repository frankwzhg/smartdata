import os
import sys

#path = '/var/www/mysite'
path = '/home/frank/smartdata/smartdata'

if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'smartdata.settings'

#import django.core.handlers.wsgi

#application = django.core.handlers.wsgi.WSGIHandler() 

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

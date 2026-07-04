import os   #for tracking enriomental variables as celery is independent and it need access to django setting to grab its own config
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lecture_tracker_backend.settings")

app = Celery("lecture_tracker_backend")
app.config_from_object('django.conf:settings', namespace='CELERY') #reading config from settings, the namespace tell am make it look for var starting only with celery in the settings.py

# Automatically discover tasks.py files inside your apps
app.autodiscover_tasks()
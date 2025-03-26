import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = 'Europe/Moscow'

app.conf.beat_schedule = {
    'send-keyword-search-matches': {
        'task': 'web.apps.search.tasks.send_keyword_search_matches',
        'schedule': crontab(hour='8', minute='0')
    },

}
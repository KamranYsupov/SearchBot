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
        'schedule': 40.0 #crontab(hour='8', minute='0')
    },
    'ask-to-share-bot-task': {
        'task': 'web.apps.telegram_users.tasks.send_ask_message_to_share_bot_task',
        'schedule': 120.0 # crontab(hour='9', minute='0', day_of_month='*/5'),
    },
}
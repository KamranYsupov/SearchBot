# Generated by Django 4.2.1 on 2025-03-28 05:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramuser',
            name='keywords_chat_id',
        ),
        migrations.RemoveField(
            model_name='telegramuser',
            name='keywords_chat_link',
        ),
    ]

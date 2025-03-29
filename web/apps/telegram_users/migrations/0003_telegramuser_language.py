# Generated by Django 4.2.1 on 2025-03-29 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_users', '0002_remove_telegramuser_keywords_chat_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='language',
            field=models.CharField(choices=[('Russian', 'Русский'), ('English', 'Английский'), ('Hebrew', 'Иврит')], default='Russian', max_length=10, verbose_name='Язык'),
        ),
    ]

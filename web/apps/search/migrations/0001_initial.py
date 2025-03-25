# Generated by Django 4.2.1 on 2025-03-25 11:17

from django.db import migrations, models
import django.db.models.deletion
import web.db.model_mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bots', '0001_initial'),
        ('telegram_users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.CharField(db_index=True, default=web.db.model_mixins.ulid_default, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('chat_id', models.CharField(db_index=True, max_length=50)),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Название')),
                ('telegram_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='telegram_users.telegramuser', verbose_name='Пользователь')),
                ('user_bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='bots.userbot', verbose_name='Юзер бот')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.CharField(db_index=True, default=web.db.model_mixins.ulid_default, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('text', models.CharField(db_index=True, max_length=150, verbose_name='Текст')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='search.chat', verbose_name='Чат')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.CharField(db_index=True, default=web.db.model_mixins.ulid_default, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('message_link', models.URLField(verbose_name='Ссылка на сообщение')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search.keyword', verbose_name='Ключевое слово')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

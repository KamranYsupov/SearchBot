# Generated by Django 4.2.1 on 2025-03-29 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0002_botkeyboard_botkeyboardbutton_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='botkeyboard',
            name='slug',
            field=models.CharField(db_index=True, max_length=150, unique=True, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='botkeyboard',
            name='name',
            field=models.CharField(max_length=150, unique=True, verbose_name='Название'),
        ),
    ]

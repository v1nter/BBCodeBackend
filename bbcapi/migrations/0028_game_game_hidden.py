# Generated by Django 3.1.6 on 2021-04-14 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbcapi', '0027_game_game_needs_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_hidden',
            field=models.BooleanField(default=False),
        ),
    ]

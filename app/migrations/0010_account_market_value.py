# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-22 11:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20180319_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='market_value',
            field=models.FloatField(default=0, help_text='最新市值'),
        ),
    ]

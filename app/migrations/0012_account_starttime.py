# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-04 10:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20180330_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='starttime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

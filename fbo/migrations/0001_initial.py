# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_priority', models.TextField(blank=True, null=True, verbose_name='Ważne informacje')),
                ('info_body', models.TextField(blank=True, null=True, verbose_name='Pozostałe informacje')),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-09 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repair', '0031_auto_20181003_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridge',
            name='serial_number',
            field=models.CharField(max_length=100, unique=True, verbose_name='Модель'),
        ),
    ]

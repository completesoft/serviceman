# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-27 05:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repair', '0014_auto_20170922_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='docorderservicecontent',
            name='cost',
            field=models.PositiveIntegerField(default=0, null=True, verbose_name='Стоимость работ'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-20 14:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('repair', '0023_auto_20180720_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')),
                ('action_content', models.TextField(blank=True, default='', max_length=100, null=True, verbose_name='Выполненные работы')),
                ('executor_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель заказа')),
                ('manager_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Руководитель заказа')),
            ],
            options={
                'db_table': 'maintenance_action',
                'verbose_name_plural': 'Работы - выполненные работы',
                'verbose_name': 'Работы - выполненные работы',
                'get_latest_by': 'action_datetime',
            },
        ),
        migrations.CreateModel(
            name='MaintenanceActionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.PositiveIntegerField(choices=[(0, 'Новый'), (1, 'В работе'), (2, 'Ожидание'), (3, 'Выполнен'), (4, 'Просрочен'), (5, 'Передан клиенту')], default=0, verbose_name='Состояние')),
                ('expiry_time', models.PositiveIntegerField(default=0, help_text='в часах', verbose_name='Допустимая продолжительность статуса')),
            ],
            options={
                'db_table': 'maintenance_action_status',
                'verbose_name_plural': 'Работы - СПРАВОЧНИК состояний',
                'verbose_name': 'Работы - СПРАВОЧНИК состояний',
            },
        ),
        migrations.CreateModel(
            name='MaintenanceOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('client_position', models.CharField(default='', max_length=100, verbose_name='Размещение у клиента')),
                ('list_of_jobs', models.CharField(default='', max_length=250, verbose_name='Список работ')),
                ('order_comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='Комментарий')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='repair.Clients', verbose_name='Клиент')),
                ('client_dep', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='repair.ClientsDep', verbose_name='Отделение клиента')),
            ],
            options={
                'db_table': 'maintenance_order',
                'verbose_name_plural': 'Работы - заказы',
                'verbose_name': 'Работы - заказы',
            },
        ),
        migrations.AddField(
            model_name='maintenanceaction',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repair.MaintenanceOrder'),
        ),
        migrations.AddField(
            model_name='maintenanceaction',
            name='setting_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Установил статус заказа'),
        ),
        migrations.AddField(
            model_name='maintenanceaction',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repair.MaintenanceActionStatus', verbose_name='Статус заказа'),
        ),
    ]

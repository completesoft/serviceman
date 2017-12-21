from django.contrib.auth.models import Group
from django.contrib import admin
from .models import ( DocOrderHeader, DocOrderAction, DocOrderServiceContent,
                     DocOrderSparesContent, DirStatus, Clients, ClientsDep, Reward)
from django.core import serializers
import os


class DirStatusAdmin(admin.ModelAdmin):
    actions = ['make_fixtures']

    def make_fixtures(self, request, queryset):
        format = "json"
        fixture_file = os.path.dirname(__file__) + "\\fixtures\\"
        JSONSerializer = serializers.get_serializer(format)
        json_serializer = JSONSerializer()
        file_name = fixture_file + queryset.model.__name__+"."+format
        with open(file_name, "w") as output:
            json_serializer.serialize(queryset, stream=output)
        msg = fixture_file + ". По моделям: " + queryset.model.__name__
        queryset = Group.objects.all()
        file_name = fixture_file + queryset.model.__name__ + "." + format
        with open(file_name, "w") as output:
            json_serializer.serialize(queryset, stream=output)
        msg+=", %s"%queryset.model.__name__
        self.message_user(request, "Файл фикстур создан в директории %s"%msg)
    make_fixtures.short_description = "Фикстура по выбраным статусам + все группы пользователей"


class DocOrderHeaderAdmin(admin.ModelAdmin):
    list_display = ("order_datetime", "last_status", "order_barcode", "client", "client_corp", "device_name")




admin.site.register(DocOrderHeader, DocOrderHeaderAdmin)
admin.site.register(DocOrderAction)
admin.site.register(DocOrderServiceContent)
admin.site.register(DocOrderSparesContent)
admin.site.register(DirStatus, DirStatusAdmin)
admin.site.register(Clients)
admin.site.register(ClientsDep)
admin.site.register(Reward)
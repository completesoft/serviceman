from django.contrib import admin
from .models import DocOrderHeader, DocOrderAction, DocOrderServiceContent, DocOrderSparesContent, DirStatus, Clients, ClientsDep


admin.site.register(DocOrderHeader)
admin.site.register(DocOrderAction)
admin.site.register(DocOrderServiceContent)
admin.site.register(DocOrderSparesContent)
admin.site.register(DirStatus)
admin.site.register(Clients)
admin.site.register(ClientsDep)

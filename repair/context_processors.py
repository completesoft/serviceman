from django.conf import settings

def repair_version(request):
    return {'REPAIR_VERSION': settings.REPAIR_VERSION}
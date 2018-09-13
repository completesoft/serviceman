from datetime import timedelta, datetime
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural

@register.filter
def is_expire(datetime_registration, expiry_duration=0):
    if not int(expiry_duration):
        return False
    # to_date = datetime.strptime(datetime_registration, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=int(expiry_duration))
    to_date = datetime_registration + timedelta(hours=int(expiry_duration))
    last_date = to_date

    # for x in range((to_date - datetime.strptime(datetime_registration, format='%Y-%m-%d %H:%M:%S.%f')).days + 1):
    for x in range((to_date - datetime_registration).days + 1):
        if (to_date + timedelta(days=x)).weekday() in [5, 6]:
            last_date += timedelta(days=1)
            if last_date.weekday() in [5, 6]:
                last_date += timedelta(days=1)
    return timezone.now() > last_date

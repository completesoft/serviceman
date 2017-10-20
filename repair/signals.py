from django.core.signals import request_finished
from django.dispatch import Signal, receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
import logging
from django.contrib.auth.models import User

logger = logging.getLogger('user.activity')

#Signals




#Recivers

@receiver(user_logged_in, sender=User)
def login_in(sender, request, user, **kwargs):
    msg = "LogIN: %s"%user.get_full_name()
    logger.warning(msg)

@receiver(user_logged_out)
def login_out(sender, request, user, **kwargs):
    try:
        user_name = user.get_full_name()
    except AttributeError:
        user_name = 'User: AnonymousUser (cause: expired session)'
    msg = "LogOUT: %s"%user_name
    logger.warning(msg)
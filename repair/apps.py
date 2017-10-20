from django.apps import AppConfig
# from .signals import user_db_add, log_bd_action

class RepairConfig(AppConfig):
    name = 'repair'
    verbose_name = 'База ремонтов'

    def ready(self):
        from . import signals
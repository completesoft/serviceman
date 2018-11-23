from django.db import migrations
from repair.models import DirStatus

def populate_int_status(apps, schema_editor):

    DirStat = apps.get_model('repair', 'DirStatus')

    temp_map = {
        1: DirStatus.NEW,
        2: DirStatus.IN_WORK,
        3: DirStatus.COMPLETED,
        4: DirStatus.TO_CLIENT,
        6: DirStatus.ARCHIVE,
        8: DirStatus.WAITING,
    }
    for row in DirStat.objects.all():
        for id, stat in temp_map.items():
            if row.id == id:
                row.status_name = stat
                row.save(update_fields=['status_name'])
class Migration(migrations.Migration):
    dependencies = [
        ('repair', '0037_auto_20181120_1320'),
    ]
    operations = [
        migrations.RunPython(populate_int_status),
    ]
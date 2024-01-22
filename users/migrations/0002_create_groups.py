from django.db import migrations, models
import logging

GROUPS = {
    'ADMIN': {
        'id': 1,
        'name': 'ADMIN',
    },
    'CUSTOMER': {
        'id': 2,
        'name': 'CUSTOMER',
    },
    'RIDER':{
        'id': 3,
        'name': 'RIDER',
    }
}

def create_groups(apps, schema_editor):
    """
    Create 3 groups 
    - administrators
    - customers
    - riders
    """
    groups_model = apps.get_model("auth", "Group")
    logger = logging.getLogger('permissions_logger')

    for group in GROUPS.values():
        groups_model.objects.create(id=group['id'], name=group['name'])
        logger.info(f"Group {group['name']} created")

def reverse_create_groups(apps, schema_editor):
    """
    Delete 3 groups 
    - administrators
    - customers
    - riders
    """
    groups_model = apps.get_model("auth", "Group")
    logger = logging.getLogger('permissions_logger')

    for group in GROUPS.values():
        groups_model.objects.filter(id=group['id']).delete()
        logger.info(f"Group {group['name']} deleted")

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_create_groups),
    ]

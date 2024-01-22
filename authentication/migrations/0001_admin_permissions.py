"""
In this migration file, we are creating the admin permissions for all the models
"""

from django.db import migrations
import logging
from glik.constants import GROUPS

def create_admin_permissions(apps, schema_editor):    
  Group = apps.get_model('auth', 'Group')
  Permission = apps.get_model('auth', 'Permission')
  logger = logging.getLogger(__name__)
  
  # add permissions to ALL models
  Group.objects.get(id=GROUPS['ADMIN']['id']).permissions.set(
    Permission.objects.all()
  )

  logger.info('Created admin permissions')

def delete_admin_permissions(apps, schema_editor):
  Group = apps.get_model('users', 'Group')
  logger = logging.getLogger(__name__)

  # remove permissions to ALL models
  Group.objects.filter(id=GROUPS['ADMIN'].id).first().permissions.set(
      []
  )

  logger.info('Deleted admin permissions')

class Migration(migrations.Migration):
    """
    Create the default admin user
    """

    dependencies = [
        ('users', '0002_create_groups'),
        ('leases', '0001_initial'),
        ('products', '0001_initial'),
        ('payments', '0001_initial'),        
    ]

    operations = [
        migrations.RunPython(create_admin_permissions, delete_admin_permissions),
    ]

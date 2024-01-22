from django.db import migrations
from glik.constants import GROUPS
import logging

def create_admin_user(apps, schema_editor):
    """
    Create the default admin user
    username: glik_admin
    password: Angel123!
    """
    User = apps.get_model('users', 'User')
    Group = apps.get_model('auth', 'Group')
    logger = logging.getLogger(__name__)
    admin_user = User.objects.create(
        username='glik_admin',
        email='admin@localhost',
        is_superuser=True,
        is_staff=True,
        password='pbkdf2_sha256$600000$HFZoc2h6VDA2day0bDAIQW$0gwasC8iiDWuEYTSTuLS5TW86wKU7gWQPoHPhuVJ0wo=', 
        first_name='Admin',
        last_name='User',
        phone_number='1234567890',
        is_active=True,        
    )

    admin_user.groups.set([ Group.objects.get(id=GROUPS['ADMIN']['id']) ])

    logger.info('Created default admin user')

class Migration(migrations.Migration):
    """
    Create the default admin user
    """

    dependencies = [
        ('users', '0005_address'),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]

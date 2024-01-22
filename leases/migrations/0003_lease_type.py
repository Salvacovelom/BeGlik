# Generated by Django 4.2.3 on 2023-08-25 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0002_alter_lease_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='lease',
            name='type',
            field=models.CharField(choices=[('lease', 'Lease'), ('purchase', 'Purchase')], default='Lease', max_length=10),
            preserve_default=False,
        ),
    ]

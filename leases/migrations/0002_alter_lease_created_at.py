# Generated by Django 4.2.3 on 2023-07-23 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

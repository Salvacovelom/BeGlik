# Generated by Django 4.2.3 on 2023-08-17 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_rename_have_islr_declaration_customeruser_have_islr_declaration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdocument',
            name='url',
        ),
        migrations.AddField(
            model_name='userdocument',
            name='document',
            field=models.FileField(default='<function now at 0x7f1693e9f6d0>', upload_to='documents'),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.2.3 on 2023-08-16 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='image',
            field=models.ImageField(null=True, upload_to='product_images'),
        ),
    ]
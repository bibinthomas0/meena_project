# Generated by Django 4.2.18 on 2025-02-01 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]

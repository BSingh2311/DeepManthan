# Generated by Django 3.0.8 on 2023-01-06 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0019_auto_20230106_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_grns',
            name='InvoiceNumber',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
    ]

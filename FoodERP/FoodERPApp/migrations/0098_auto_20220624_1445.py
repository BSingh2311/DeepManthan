# Generated by Django 3.0.8 on 2022-06-24 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0097_auto_20220624_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_orders',
            name='OrderDate',
            field=models.DateField(),
        ),
    ]

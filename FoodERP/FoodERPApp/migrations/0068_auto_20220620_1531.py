# Generated by Django 3.0.8 on 2022-06-20 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0067_auto_20220620_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_employees',
            name='AadharNo',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='m_employees',
            name='Mobile',
            field=models.CharField(max_length=100),
        ),
    ]

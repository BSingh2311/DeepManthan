# Generated by Django 3.0.8 on 2023-04-07 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0035_auto_20230407_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_creditdebitnotes',
            name='NoteNo',
            field=models.IntegerField(),
        ),
    ]

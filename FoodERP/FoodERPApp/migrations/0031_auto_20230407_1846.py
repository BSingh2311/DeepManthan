# Generated by Django 3.0.8 on 2023-04-07 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0030_auto_20230407_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_creditdebitnotes',
            name='NoteNo',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

# Generated by Django 3.0.8 on 2022-11-07 15:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0006_auto_20221107_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_users',
            name='last_activity',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last activity'),
        ),
    ]

# Generated by Django 3.0.8 on 2022-07-28 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0014_auto_20220725_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_roles',
            name='isSCMRole',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='m_users',
            name='OTP',
            field=models.CharField(max_length=1002, null=True),
        ),
    ]

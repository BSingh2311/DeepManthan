# Generated by Django 3.0.8 on 2024-02-14 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0002_m_sweetposlogin_alter_m_sweetposroleaccess_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='m_sweetposlogin',
            old_name='UserName',
            new_name='UName',
        ),
        migrations.AlterField(
            model_name='m_sweetposlogin',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

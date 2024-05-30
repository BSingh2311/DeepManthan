# Generated by Django 3.0.8 on 2024-05-30 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0287_auto_20240529_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_invoices',
            name='DataRecovery',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='t_production',
            name='Remark',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

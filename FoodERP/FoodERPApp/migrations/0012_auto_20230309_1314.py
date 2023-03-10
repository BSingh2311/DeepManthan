# Generated by Django 3.0.8 on 2023-03-09 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0011_m_drivers_party'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_drivers',
            name='Company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='DCompany', to='FoodERPApp.C_Companies'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='m_drivers',
            name='Party',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='DParty', to='FoodERPApp.M_Parties'),
            preserve_default=False,
        ),
    ]

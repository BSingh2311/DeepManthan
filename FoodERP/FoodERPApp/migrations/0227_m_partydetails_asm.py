# Generated by Django 3.0.8 on 2023-12-06 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0226_m_partydetails_rh'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_partydetails',
            name='ASM',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='PartyDetailASM', to='FoodERPApp.M_Employees'),
        ),
    ]

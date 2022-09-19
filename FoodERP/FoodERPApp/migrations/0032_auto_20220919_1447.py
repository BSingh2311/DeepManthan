# Generated by Django 3.0.8 on 2022-09-19 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0031_auto_20220919_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_pricelist',
            name='DivisionType',
        ),
        migrations.AddField(
            model_name='m_pricelist',
            name='BasePriceListID',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_pricelist',
            name='Company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PriceListCompany', to='FoodERPApp.C_Companies'),
        ),
        migrations.AddField(
            model_name='m_pricelist',
            name='MkUpMkDn',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_pricelist',
            name='PLPartyType',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PriceListPartyType', to='FoodERPApp.M_PartyType'),
            preserve_default=False,
        ),
    ]

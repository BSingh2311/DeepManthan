# Generated by Django 3.0.8 on 2022-06-30 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0123_merge_20220630_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_employees',
            name='Companies',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.C_Companies'),
        ),
        migrations.AlterField(
            model_name='m_employees',
            name='Designation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_Designations'),
        ),
        migrations.AlterField(
            model_name='m_employees',
            name='EmployeeType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_EmployeeTypes'),
        ),
        migrations.AlterField(
            model_name='m_employees',
            name='State',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_States'),
        ),
        migrations.AlterField(
            model_name='t_invoices',
            name='CustomerID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Customer', to='FoodERPApp.M_Parties'),
        ),
        migrations.AlterField(
            model_name='t_invoices',
            name='OrderID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.T_Orders'),
        ),
        migrations.AlterField(
            model_name='t_invoices',
            name='PartyID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Party', to='FoodERPApp.M_Parties'),
        ),
        migrations.AlterField(
            model_name='tc_invoiceitembatches',
            name='ItemID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_Items'),
        ),
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='ItemID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_Items'),
        ),
    ]

# Generated by Django 3.0.8 on 2023-04-03 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0008_auto_20230403_1016'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_ManagementParties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Employee', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ManagementEmployee', to='FoodERPApp.M_Employees')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ManagementEmpparty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'MC_ManagementParties',
            },
        ),
    ]

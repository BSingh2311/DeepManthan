# Generated by Django 3.0.8 on 2022-08-25 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0043_auto_20220825_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_ItemsDivisions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Division', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Division', to='FoodERPApp.M_Parties')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ItemDivisiondetails', to='FoodERPApp.M_Items')),
            ],
            options={
                'db_table': 'MC_ItemDivisions',
            },
        ),
        migrations.DeleteModel(
            name='MC_ItemDivisions',
        ),
    ]

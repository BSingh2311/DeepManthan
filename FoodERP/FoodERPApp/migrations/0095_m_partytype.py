# Generated by Django 3.0.8 on 2022-06-23 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0094_m_divisiontype'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_PartyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('DivisionTypeID', models.IntegerField()),
            ],
            options={
                'db_table': 'M_PartyType',
            },
        ),
    ]

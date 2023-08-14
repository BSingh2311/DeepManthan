# Generated by Django 3.0.8 on 2023-07-28 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0090_m_masterclaim'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_masterclaim',
            name='Item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ClaimItem', to='FoodERPApp.M_Items'),
            preserve_default=False,
        ),
    ]

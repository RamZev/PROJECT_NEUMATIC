# Generated by Django 5.1.1 on 2025-02-18 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('informes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vlresumenctacte',
            options={'managed': False, 'ordering': ['razon_social'], 'verbose_name': 'Resumen de Cta. Cte.', 'verbose_name_plural': 'Resumen de Cta. Cte.'},
        ),
    ]

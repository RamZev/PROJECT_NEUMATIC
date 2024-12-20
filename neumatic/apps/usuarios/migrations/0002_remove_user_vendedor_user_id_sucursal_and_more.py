# Generated by Django 5.1.1 on 2024-11-04 18:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0003_alter_localidad_options_proveedor_id_provincia_and_more'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='vendedor',
        ),
        migrations.AddField(
            model_name='user',
            name='id_sucursal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maestros.sucursal', verbose_name='Sucursal'),
        ),
        migrations.AddField(
            model_name='user',
            name='id_vendedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maestros.vendedor', verbose_name='Vendedor'),
        ),
        migrations.AddField(
            model_name='user',
            name='punto_venta',
            field=models.IntegerField(blank=True, null=True, verbose_name='Punto de Venta'),
        ),
        migrations.AlterField(
            model_name='user',
            name='telefono',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Teléfono'),
        ),
    ]

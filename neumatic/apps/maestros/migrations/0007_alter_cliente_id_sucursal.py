# Generated by Django 5.1.1 on 2024-10-03 04:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0006_alter_cliente_tipo_persona'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='id_sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maestros.sucursal', verbose_name='Sucursal'),
        ),
    ]

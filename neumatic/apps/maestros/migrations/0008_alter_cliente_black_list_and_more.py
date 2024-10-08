# Generated by Django 5.1.1 on 2024-10-03 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0007_alter_cliente_id_sucursal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='black_list',
            field=models.BooleanField(choices=[(True, 'Si'), (False, 'No')], default=False, verbose_name='Black List'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='black_list_motivo',
            field=models.CharField(max_length=50, verbose_name='Motivo Black List'),
        ),
    ]

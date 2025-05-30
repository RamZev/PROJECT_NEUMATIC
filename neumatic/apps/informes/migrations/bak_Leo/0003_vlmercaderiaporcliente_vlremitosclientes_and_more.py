# Generated by Django 5.1.1 on 2025-01-28 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informes', '0002_delete_vlsaldosclientes'),
    ]

    operations = [
        migrations.CreateModel(
            name='VLMercaderiaPorCliente',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('numero', models.CharField(max_length=13)),
                ('fecha_comprobante', models.DateField()),
                ('nombre_producto_marca', models.CharField(max_length=50)),
                ('medida', models.CharField(max_length=15)),
                ('id_producto_id', models.IntegerField()),
                ('nombre_producto', models.CharField(max_length=50)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=7)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=12)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=6)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
            ],
            options={
                'verbose_name': 'Mercadería por Cliente',
                'verbose_name_plural': 'Mercadería por Cliente',
                'db_table': 'VLMercaderiaPorCliente',
                'ordering': ['id_cliente_id', 'fecha_comprobante'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLRemitosClientes',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_comprobante_venta_id', models.IntegerField()),
                ('codigo_comprobante_venta', models.CharField(max_length=3)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('fecha_comprobante', models.DateField()),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('numero', models.CharField(max_length=13)),
                ('nombre_producto', models.CharField(max_length=50)),
                ('medida', models.CharField(max_length=15)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=7)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=12)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=6)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
            ],
            options={
                'verbose_name': 'Remitos por Clientes',
                'verbose_name_plural': 'Remitos por Clientes',
                'db_table': 'VLRemitosClientes',
                'ordering': ['id_cliente_id', 'fecha_comprobante', 'numero_comprobante'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLResumenCtaCte',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('razon_social', models.CharField(max_length=50)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('numero', models.CharField(max_length=13)),
                ('fecha_comprobante', models.DateField()),
                ('remito', models.CharField(max_length=15)),
                ('condicion_comprobante', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('entrega', models.DecimalField(decimal_places=2, max_digits=14)),
                ('saldo', models.DecimalField(decimal_places=2, max_digits=14)),
                ('saldo_acumulado', models.DecimalField(decimal_places=2, max_digits=14)),
                ('intereses', models.DecimalField(decimal_places=2, max_digits=14)),
            ],
            options={
                'verbose_name': 'Facturas Pendientes',
                'verbose_name_plural': 'Facturas Pendientes',
                'db_table': 'VLResumenCtaCte',
                'ordering': ['razon_social'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLSaldosClientes',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('fecha_comprobante', models.DateField()),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('domicilio_cliente', models.CharField(max_length=50)),
                ('nombre_localidad', models.CharField(max_length=30)),
                ('codigo_postal', models.CharField(max_length=5)),
                ('telefono_cliente', models.CharField(max_length=15)),
                ('sub_cuenta', models.CharField(max_length=6)),
                ('id_vendedor_id', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
            ],
            options={
                'verbose_name': 'Saldos de Clientes',
                'verbose_name_plural': 'Saldos de Clientes',
                'db_table': 'VLSaldosClientes',
                'ordering': ['nombre_cliente'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLTotalRemitosClientes',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('fecha_comprobante', models.DateField()),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('domicilio_cliente', models.CharField(max_length=50)),
                ('codigo_postal', models.CharField(max_length=5)),
                ('nombre_iva', models.CharField(max_length=25)),
                ('cuit', models.IntegerField()),
                ('telefono_cliente', models.CharField(max_length=15)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
            ],
            options={
                'verbose_name': 'Totales de Remitos por Clientes',
                'verbose_name_plural': 'Totales de Remitos por Clientes',
                'db_table': 'VLTotalRemitosClientes',
                'ordering': ['nombre_cliente'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLVentaCompro',
            fields=[
                ('id_factura', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('codigo_comprobante_venta', models.CharField(max_length=3)),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('comprobante', models.CharField(max_length=17)),
                ('fecha_comprobante', models.DateField()),
                ('condicion', models.CharField(max_length=9)),
                ('id_cliente_id', models.IntegerField()),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('gravado', models.DecimalField(decimal_places=2, max_digits=14)),
                ('iva', models.DecimalField(decimal_places=2, max_digits=14)),
                ('percep_ib', models.DecimalField(decimal_places=2, max_digits=14)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('id_sucursal_id', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Ventas por Comprobantes',
                'verbose_name_plural': 'Ventas por Comprobantes',
                'db_table': 'VLVentaCompro',
                'ordering': ['comprobante'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLVentaComproLocalidad',
            fields=[
                ('id_cliente_id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_sucursal_id', models.IntegerField()),
                ('fecha_comprobante', models.DateField()),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('cuit', models.IntegerField()),
                ('codigo_postal', models.CharField(max_length=5)),
                ('codigo_comprobante_venta', models.CharField(max_length=3)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('comprobante', models.CharField(max_length=17)),
                ('gravado', models.DecimalField(decimal_places=2, max_digits=14)),
                ('exento', models.DecimalField(decimal_places=2, max_digits=14)),
                ('iva', models.DecimalField(decimal_places=2, max_digits=14)),
                ('percep_ib', models.DecimalField(decimal_places=2, max_digits=14)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('iniciales', models.CharField(max_length=3)),
            ],
            options={
                'verbose_name': 'Ventas por Localidad',
                'verbose_name_plural': 'Ventas por Localidad',
                'db_table': 'VLVentaComproLocalidad',
                'ordering': ['fecha_comprobante'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VLVentaMostrador',
            fields=[
                ('id_detalle_factura', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_comprobante_venta', models.CharField(max_length=50)),
                ('codigo_comprobante_venta', models.CharField(max_length=3)),
                ('letra_comprobante', models.CharField(max_length=1)),
                ('numero_comprobante', models.IntegerField()),
                ('comprobante', models.CharField(max_length=17)),
                ('fecha_comprobante', models.DateField()),
                ('id_cliente_id', models.IntegerField()),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('mayorista', models.BooleanField()),
                ('reventa', models.CharField(max_length=1)),
                ('id_producto_id', models.IntegerField()),
                ('nombre_producto', models.CharField(max_length=50)),
                ('tipo_producto', models.CharField(max_length=1)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=7)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=14)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('id_sucursal_id', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Ventas por Mostrador',
                'verbose_name_plural': 'Ventas por Mostrador',
                'db_table': 'VLVentaMostrador',
                'ordering': ['fecha_comprobante', 'numero_comprobante'],
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='VLSaldosClientes2',
        ),
    ]

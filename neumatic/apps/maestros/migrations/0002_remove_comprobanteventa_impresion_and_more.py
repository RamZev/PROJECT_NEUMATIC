# Generated by Django 5.1.1 on 2024-10-25 22:39

import datetime
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maestros', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comprobanteventa',
            name='impresion',
        ),
        migrations.AddField(
            model_name='productofamilia',
            name='info_michelin_auto',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin auto'),
        ),
        migrations.AddField(
            model_name='productofamilia',
            name='info_michelin_camion',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin camión'),
        ),
        migrations.AddField(
            model_name='productominimo',
            name='id_producto',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='maestros.producto', verbose_name='Producto'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='black_list_motivo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Motivo Black List'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='black_list_usuario',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Usuario Black List'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='codigo_postal',
            field=models.CharField(max_length=5, verbose_name='Código Postal*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='condicion_venta',
            field=models.IntegerField(choices=[(1, 'Contado'), (2, 'Cuenta Corriente')], default=True, verbose_name='Condición Venta*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cuit',
            field=models.IntegerField(verbose_name='CUIT*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='domicilio_cliente',
            field=models.CharField(max_length=50, verbose_name='Domicilio Cliente*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email2_cliente',
            field=models.EmailField(blank=True, max_length=50, null=True, verbose_name='Email 2'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email_cliente',
            field=models.EmailField(max_length=50, verbose_name='Email*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='estatus_cliente',
            field=models.BooleanField(choices=[(True, 'Activo'), (False, 'Inactivo')], default=True, verbose_name='Estatus*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fax_cliente',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Fax'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fecha_alta',
            field=models.DateField(default=datetime.date.today, verbose_name='Fecha Alta'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fecha_baja',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Baja'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha Nacimiento'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_actividad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.actividad', verbose_name='Actividad*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_localidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.localidad', verbose_name='Localidad*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_percepcion_ib',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.tipopercepcionib', verbose_name='Percepción IB*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.provincia', verbose_name='Provincia*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maestros.sucursal', verbose_name='Sucursal*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_tipo_documento_identidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.tipodocumentoidentidad', verbose_name='Tipo Doc. Identidad*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_tipo_iva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.tipoiva', verbose_name='Tipo de Iva*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='id_vendedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maestros.vendedor', verbose_name='Vendedor'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='mayorista',
            field=models.BooleanField(choices=[(True, 'SI'), (False, 'NO')], default=False, verbose_name='Mayorista*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='movil_cliente',
            field=models.CharField(max_length=15, verbose_name='Móvil*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nombre_cliente',
            field=models.CharField(max_length=50, verbose_name='Nombre Cliente*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='numero_ib',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Número IB'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='sexo',
            field=models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], default='M', max_length=1, verbose_name='Sexo*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='sub_cuenta',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='Sub Cuenta'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefono_cliente',
            field=models.CharField(max_length=15, verbose_name='Teléfono*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='tipo_persona',
            field=models.CharField(choices=[('N', 'Natural'), ('F', 'Física')], default='N', max_length=1, verbose_name='Tipo de Persona*'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='transporte_cliente',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Transporte'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='vip',
            field=models.BooleanField(choices=[(True, 'SI'), (False, 'NO')], default=False, verbose_name='Cliente VIP*'),
        ),
        migrations.AlterField(
            model_name='comprobantecompra',
            name='libro_iva',
            field=models.BooleanField(default=False, verbose_name='Libreo IVA'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='electronica',
            field=models.BooleanField(default=False, verbose_name='Electrónica'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='estadistica',
            field=models.BooleanField(default=False, verbose_name='Estadísticas'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='info_michelin_auto',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin auto'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='info_michelin_camion',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin camión'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='libro_iva',
            field=models.BooleanField(default=False, verbose_name='Libro IVA'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='pendiente',
            field=models.BooleanField(default=False, verbose_name='Pendiente'),
        ),
        migrations.AlterField(
            model_name='comprobanteventa',
            name='presupuesto',
            field=models.BooleanField(default=False, verbose_name='Presupuesto'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='cbu',
            field=models.CharField(max_length=22, verbose_name='CBU Bancaria*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='cbu_alias',
            field=models.CharField(max_length=50, verbose_name='CBU Alias*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='cbu_vence',
            field=models.DateField(verbose_name='Vcto. CBU*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='codigo_postal',
            field=models.CharField(max_length=4, verbose_name='Código postal*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='cuit',
            field=models.IntegerField(verbose_name='C.U.I.T.*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='domicilio_empresa',
            field=models.CharField(max_length=50, verbose_name='Domicilio*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='email_empresa',
            field=models.EmailField(max_length=50, verbose_name='Correo*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='estatus_empresa',
            field=models.BooleanField(choices=[(True, 'Activo'), (False, 'Inactivo')], default=True, verbose_name='Estatus*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='id_localidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.localidad', verbose_name='Localidad*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='id_provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.provincia', verbose_name='Provincia*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='ingresos_bruto',
            field=models.CharField(max_length=15, verbose_name='Ing. Bruto*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='inicio_actividad',
            field=models.DateField(verbose_name='Inicio de actividad*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='nombre_comercial',
            field=models.CharField(max_length=50, verbose_name='Nombre Comercial*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='nombre_fiscal',
            field=models.CharField(max_length=50, verbose_name='Nombre Fiscal*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='telefono',
            field=models.CharField(max_length=20, verbose_name='Teléfono*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='web_empresa',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Web'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='ws_archivo_crt',
            field=models.CharField(max_length=50, verbose_name='Archivo CRT WSAFIP*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='ws_archivo_key',
            field=models.CharField(max_length=50, verbose_name='Archivo KEY WSAFIP*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='ws_modo',
            field=models.IntegerField(choices=[(1, 'Homologación'), (2, 'Producción')], verbose_name='Modo*'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='ws_vence',
            field=models.DateField(verbose_name='Vcto. Certificado*'),
        ),
        migrations.AlterField(
            model_name='moneda',
            name='cotizacion_moneda',
            field=models.DecimalField(decimal_places=4, max_digits=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999999.9999)], verbose_name='Cotización'),
        ),
        migrations.AlterField(
            model_name='numero',
            name='copias',
            field=models.IntegerField(verbose_name='Copias'),
        ),
        migrations.AlterField(
            model_name='numero',
            name='lineas',
            field=models.IntegerField(verbose_name='Líneas'),
        ),
        migrations.AlterField(
            model_name='numero',
            name='numero',
            field=models.IntegerField(verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='numero',
            name='punto_venta',
            field=models.IntegerField(verbose_name='Punto de Venta'),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='cotizacion_dolar',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, verbose_name='Cotización Dólar'),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='descuento_maximo',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, verbose_name='Descuento Máximo(%)'),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='dias_vencimiento',
            field=models.IntegerField(blank=True, default=0, verbose_name='Días Vcto.'),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='interes',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, verbose_name='Intereses(%)'),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='interes_dolar',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, verbose_name='Intereses Dólar(%)'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='alicuota_iva',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='Alícuota IVA'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='cai',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='CAI'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='codigo_producto',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='Código producto'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True, verbose_name='Costo'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descuento',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='Descuento'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='despacho_1',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Despacho 1'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='despacho_2',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Despacho 2'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='fecha_fabricacion',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='Fecha fabricación'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='id_familia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.productofamilia', verbose_name='Familia'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='id_marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.productomarca', verbose_name='Marca'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='id_modelo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.productomodelo', verbose_name='Modelo'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='minimo',
            field=models.IntegerField(default=0, null=True, verbose_name='Stock mínimo'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True, verbose_name='Precio'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='stock',
            field=models.IntegerField(blank=True, null=True, verbose_name='Stock'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='unidad',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Unidad'),
        ),
        migrations.AlterField(
            model_name='productofamilia',
            name='comision_operario',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='Comisión Operario(%)'),
        ),
        migrations.AlterField(
            model_name='productomarca',
            name='info_michelin_auto',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin auto'),
        ),
        migrations.AlterField(
            model_name='productomarca',
            name='info_michelin_camion',
            field=models.BooleanField(default=False, verbose_name='Info. Michelin camión'),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='cuit',
            field=models.IntegerField(unique=True, verbose_name='C.U.I.T.'),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='ib_alicuota',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4, verbose_name='Alíc. Ing. B.'),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='id_localidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.localidad', verbose_name='Localidad'),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='id_tipo_iva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.tipoiva', verbose_name='Tipo IVA'),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='id_tipo_retencion_ib',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.tiporetencionib', verbose_name='Tipo de Retención Ib'),
        ),
        migrations.AlterField(
            model_name='sucursal',
            name='codigo_michelin',
            field=models.IntegerField(verbose_name='Código Michelin'),
        ),
        migrations.AlterField(
            model_name='sucursal',
            name='id_localidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.localidad', verbose_name='Localidad'),
        ),
        migrations.AlterField(
            model_name='sucursal',
            name='id_provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maestros.provincia', verbose_name='Provincia'),
        ),
        migrations.AlterField(
            model_name='tipodocumentoidentidad',
            name='nombre_documento_identidad',
            field=models.CharField(max_length=20, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='tipopercepcionib',
            name='alicuota',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99.99)], verbose_name='Alícuota(%)'),
        ),
        migrations.AlterField(
            model_name='tipopercepcionib',
            name='minimo',
            field=models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999999999.99)], verbose_name='Mínimo'),
        ),
        migrations.AlterField(
            model_name='tipopercepcionib',
            name='monto',
            field=models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999999999.99)], verbose_name='Monto'),
        ),
        migrations.AlterField(
            model_name='tiporetencionib',
            name='alicuota_inscripto',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99.99)], verbose_name='Alícuota Inscripto(%)'),
        ),
        migrations.AlterField(
            model_name='tiporetencionib',
            name='alicuota_no_inscripto',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99.99)], verbose_name='Alícuota No Inscripto(%)'),
        ),
        migrations.AlterField(
            model_name='tiporetencionib',
            name='minimo',
            field=models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999999999.99)], verbose_name='Mínimo'),
        ),
        migrations.AlterField(
            model_name='tiporetencionib',
            name='monto',
            field=models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999999999.99)], verbose_name='Monto'),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='col_descuento',
            field=models.IntegerField(blank=True, default=0, verbose_name='Columna Dcto.'),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='pje_auto',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='% auto'),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='pje_camion',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='% camión'),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='vence_factura',
            field=models.IntegerField(blank=True, default=0, verbose_name='Días vcto. Fact.'),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='vence_remito',
            field=models.IntegerField(blank=True, default=0, verbose_name='Días vcto. Remito'),
        ),
    ]
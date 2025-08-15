# neumatic\data_load\stockcliente_migra_final.py
import os
import sys
import django
from dbfread import DBF
from django.db import transaction
from decimal import Decimal

# Configuración básica
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.producto_models import Producto
from apps.ventas.models.factura_models import Factura
from apps.ventas.models.venta_models import StockCliente

def debug_migration():
    """Versión final con total compatibilidad entre DBF y modelo"""
    print("=== MIGRACIÓN FINAL (20 registros) ===")
    
    # Ruta del archivo DBF
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'stockcliente.DBF')
    table = DBF(dbf_path, encoding='latin-1')
    
    # Procesar solo los primeros 20 registros
    success_count = 0
    for i, record in enumerate(table, 1):
        if i > 20:
            break
            
        print("\n" + "="*50)
        print(f"PROCESANDO REGISTRO {i}")
        
        try:
            with transaction.atomic():
                # 1. Obtener relaciones
                factura = Factura.objects.get(id_factura=record['ID'])
                producto = Producto.objects.get(id_producto=record['CODIGO'])
                
                # 2. Crear instancia con mapeo exacto DBF -> Modelo
                stock = StockCliente(
                    id_factura=factura,
                    id_producto=producto,
                    cantidad=Decimal(str(record['CANTIDAD'])) if record['CANTIDAD'] is not None else None,
                    retiro=Decimal(str(record['RETIRADO'])) if record['RETIRADO'] is not None else None,
                    fecha_retiro=record['FECHA'],
                    numero=int(record['NUMERO']) if record['NUMERO'] is not None else None,
                    comentario=record['COMENTARIO'].strip() if record['COMENTARIO'] else None
                )
                
                # 3. Mostrar valores antes de guardar
                print("\nVALORES A GUARDAR:")
                print(f"CANTIDAD: {stock.cantidad} (Tipo: {type(stock.cantidad)})")
                print(f"RETIRO: {stock.retiro} (Tipo: {type(stock.retiro)})")
                print(f"FECHA_RETIRO: {stock.fecha_retiro} (Tipo: {type(stock.fecha_retiro)})")
                print(f"NUMERO: {stock.numero} (Tipo: {type(stock.numero)})")
                print(f"COMENTARIO: '{stock.comentario}' (Tipo: {type(stock.comentario)})")
                
                # 4. Guardar y verificar
                stock.save()
                saved = StockCliente.objects.get(pk=stock.pk)
                
                print("\nVALORES GUARDADOS:")
                print(f"CANTIDAD: {saved.cantidad}")
                print(f"RETIRO: {saved.retiro}")
                print(f"FECHA_RETIRO: {saved.fecha_retiro}")
                print(f"NUMERO: {saved.numero}")
                print(f"COMENTARIO: '{saved.comentario}'")
                
                success_count += 1
                print("\n✅ REGISTRO VERIFICADO CORRECTAMENTE")
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            continue
    
    # Resumen final
    print("\n" + "="*50)
    print(f"RESULTADO: {success_count}/20 registros migrados correctamente")

if __name__ == '__main__':
    debug_migration()
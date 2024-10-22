from django.core.exceptions import ValidationError
import re


def calcular_digito_verificador(cuit_base):
	coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
	cuit_digits = [int(digit) for digit in str(cuit_base)]
	suma = sum(cuit_digits[i] * coeficientes[i] for i in range(len(coeficientes)))
	resto = suma % 11
	
	if resto == 0:
		return 0
	elif resto == 1:
		return 9 if cuit_digits[0] in [2, 3] else 4
	else:
		return 11 - resto

def validar_cuit(cuit):
	cuit_str = str(cuit)
	
	#-- Validar que comience con los prefijos específicos y tenga 11 dígitos en total.
	if not re.match(r'^(20|23|24|25|26|27|30|33|34)\d{9}$', cuit_str):
		raise ValidationError("El CUIT debe comenzar con 20, 23, 24, 25, 26, 27, 30, 33 o 34, y tener 11 dígitos.")
	
	#-- Separar los primeros 10 dígitos y el dígito verificador.
	cuit_base = int(cuit_str[:-1])
	digito_verificador = int(cuit_str[-1])
	
	#-- Calcular el dígito verificador.
	digito_calculado = calcular_digito_verificador(cuit_base)
	
	#-- Validar el dígito verificador.
	if digito_verificador != digito_calculado:
		raise ValidationError("El CUIT no es válido.")

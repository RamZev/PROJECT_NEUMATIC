# generar_plantilla.py
import os
import django
import sys
<<<<<<< HEAD
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from estructuras_maestros import estructura_campos

# Agregar la ruta del directorio principal del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PERSONALSYS.settings")
=======

''' Estos imports ya no son necesarios
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
'''

from estructuras_maestros import estructura_campos

# Agregar la ruta del directorio principal del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neumatic.settings")
>>>>>>> f71623c58ffe87c8f648350694c7b54122edf9f7

django.setup()

# OJO: la estructura de datos debe venir desde el formulario
modelo = sys.argv[1]
estructura_campos = estructura_campos[modelo]
<<<<<<< HEAD
print(estructura_campos)
=======
# print(estructura_campos)
>>>>>>> f71623c58ffe87c8f648350694c7b54122edf9f7

# Validar si la estructura de de campos es válida

# Generar la estructura HTML en base a la estructura de datos
<<<<<<< HEAD
html_code = """
{% extends 'base.html' %}

<!-- Block Title  ---------------------------------------------------------------------------------------->
{% block title %}
    {% if form.instance.id_persona %}
        Editar Persona
    {% else %}
        Crear Persona
    {% endif %}
{% endblock title %}

<!-- Block Header  ---------------------------------------------------------------------------------------->
{% block header %}

{% endblock header %}

<!-- Block Main - ---------------------------------------------------------------------------------------->
{% block main %}
<div class="wrapper">
    {% block sidebar %}
        {% include 'sidebar.html' %}
    {% endblock %}

    {% block maincomponent %}
    <!-- Main Component Start -->
    <div class="main">
        {% block buttonsidebartoggle %}
            {% include 'buttonsidebartoggle.html' %}
        {% endblock %}

        {% block principalcomponent %}
        <div class="container-fluid">
            <div class="card border-light mb-3 mt-2">
                <div class="card-header text-white bg-primary opacity-75">
                    {% if form.instance.id_persona %}
                        <h3>Editar Persona</h3>
                    {% else %}
                        <h3>Crear Persona</h3>
                    {% endif %}

                </div>

                <div class="card-body bg-body-secondary">
                    <form method="post" class="needs-validation" novalidate>
                        {% csrf_token %}
                        
                        <div class="accordion" id="accordionPanelsStayOpenExample">
                        <!-- Estructura generada -->
=======
html_code = """{% extends 'maestro_form.html' %}
{% load static %}
<!-- -------------------------------------------------------------------- -->
{% block maincomponent %}
	{% block principalcomponent %}
		<div id="layoutSidenav_content">
			<main>
				<div class="container-fluid">
					
					<div class="card border-light mb-3 mt-2">
						<div class="card-header text-white bg-primary opacity-75 d-flex 
									justify-content-between">
							{{ accion }}
							<div class="flex align-items-center">
								<a 
									class="me-2 text-white" 
									data-bs-toggle="modal" 
									data-bs-target="#helpModal" 
									style="cursor: pointer;">
									<i class="bi bi-question-lg"></i></a>
								
								<button type="button" class="btn-close btn-close-white" 
									aria-label="Close"
									onclick="window.location.href='{% url list_view_name %}'">
								</button>
							</div>
						</div>
						
						<div class="card-body bg-body-secondary">
							<form method="post" enctype="multipart/form-data" novalidate>
								{% csrf_token %}
								<div class="accordion" id="accordionPanelsStayOpenExample">
									<!-- Estructura generada -->
>>>>>>> f71623c58ffe87c8f648350694c7b54122edf9f7
"""

primera_iteracion = True

for seccion, filas in estructura_campos.items():
<<<<<<< HEAD
    html_code += f"""
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button {'collapsed' if not primera_iteracion else ''}" type="button" data-bs-toggle="collapse" data-bs-target="#{seccion.replace(" ", "_")}" aria-expanded="{'true' if primera_iteracion else 'false'}" aria-controls="{seccion.replace(" ", "_")}">
                    <strong>{seccion}</strong>
                </button>
            </h2>
            <div id="{seccion.replace(" ", "_")}" class="accordion-collapse collapse {'show' if primera_iteracion else ''}">
                <div class="accordion-body bg-secondary-subtle">
    """
	
    for fila, campos in filas.items():
        html_code += '<div class="row">'
        for campo in campos:
            field_name = campo['field_name']
            columna = campo['columna']
			
            html_code += f"""
                <div class="col-md-{columna}">
                    <label for="{{{{ form.{field_name}.id_for_label }}}}" class="form-label text-primary">{{{{ form.{field_name}.label_tag }}}}</label>
                    {{{{ form.{field_name} }}}}
                    <div class="invalid-feedback">
                        {{{{ form.{field_name}.errors }}}}
                    </div>
                </div>
            """
		
        html_code += '</div>'
	
    html_code += """
                </div>
            </div>
        </div>
    """
    
    primera_iteracion = False

# Continuación del código HTML
html_code += """
                        </div>
                        
                        <div class="container mt-3">
                            <button type="submit" class="btn btn-primary">Guardar</button>
                            <a href="{% url 'persona_list' %}" class="btn btn-secondary">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        {% endblock %}
    </div>
    {% endblock %}
</div>
{% endblock main %}
"""

# Crear un objeto BeautifulSoup
soup = BeautifulSoup(html_code, "html.parser")

# Obtener el código HTML con indentación
indented_html_code = soup.prettify(formatter=HTMLFormatter(indent=4))

# Guardar el código HTML en el archivo
with open("persona3_form.html", "w", encoding="utf-8") as file:
    file.write(indented_html_code)
        
=======
		html_code += f"""
									<div class="accordion-item">
										<h2 class="accordion-header">
											<button 
												class="accordion-button {'collapsed' if not primera_iteracion else ''}" 
												type="button" 
												data-bs-toggle="collapse" 
												data-bs-target="#{seccion.replace(" ", "_")}" 
												aria-expanded="{'true' if primera_iteracion else 'false'}" 
												aria-controls="{seccion.replace(" ", "_")}">
												<strong>{seccion}</strong>
											</button>
										</h2>
										<div class="accordion-collapse collapse {'show' if primera_iteracion else ''}"
											id="{seccion.replace(" ", "_")}">
											<div class="accordion-body bg-secondary-subtle">
		"""
	
		for fila, campos in filas.items():
				html_code += '''
												<div class="row">'''
				for campo in campos:
						field_name = campo['field_name']
						columna = campo['columna']
			
						html_code += f"""
													<div class="col-md-{columna}">
														<label class="form-label text-primary">
															{{{{ form.{field_name}.label }}}}
														</label>
														{{{{ form.{field_name} }}}}
													</div>
						"""
		
				html_code += '						</div>'
	
		html_code += """
											</div>
										</div>
									</div>
		"""
		
		primera_iteracion = False

# Continuación del código HTML
html_code += """
								</div>
								
								<div class="container mt-3">
									<button class="btn btn-primary" type="submit" id="guardarBtn">
										Guardar
									</button>
									<a class="btn btn-secondary" href="{% url list_view_name %}">
										Cancelar
									</a>
								</div>
							</form>
						</div>
					</div>
				</div>
			</main>
		</div>
	{% endblock principalcomponent %}
{% endblock maincomponent %}
<!-- -------------------------------------------------------------------- -->
{% block modals %}
	<!-- Modal para mostrar errores -->
	{% include 'maestros/modal_errors.html' %}
	
	<!-- Modal para mostrar los requerimientos de los campos -->
	{% include 'maestros/modal_fields_requirements.html' %}
{% endblock modals %}
<!-- -------------------------------------------------------------------- -->
{% block footer %}
{% endblock footer %}
<!-- -------------------------------------------------------------------- -->
{% block script %}
	<script>
		document.addEventListener('DOMContentLoaded', function () {
			const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
			const modalElement = document.getElementById('errorModal');
			const hasErrors = modalElement.dataset.hasErrors === "true";
			
			// Mostrar el modal si hay errores
			if (hasErrors) {
				errorModal.show();
			}
			
			// Validación en tiempo real: remover clases al escribir.
			// Seleccionar inputs y selects.
			var inputs = document.querySelectorAll('input, select');
			console.log(inputs);
			inputs.forEach(function (input) {
				// Para los campos de tipo input (text, number, etc.)
				input.addEventListener('input', function () {
					if (input.classList.contains('is-invalid')) {
						// Eliminar la clase de borde rojo (border-danger).
						input.classList.remove('is-invalid', 'border-danger');
						// Agregar la clase de borde azul (border-primary).
						input.classList.add('border-primary');
					}
				});
				// Para los combobox (select)
				input.addEventListener('change', function () {
					if (input.classList.contains('is-invalid')) {
						// Eliminar la clase de borde rojo (border-danger).
						input.classList.remove('is-invalid', 'border-danger');
						// Agregar la clase de borde azul (border-primary).
						input.classList.add('border-primary');
					}
				});
				
			});
			
			// Al cerrar el modal, enfocar el primer campo con error
			modalElement.addEventListener('hidden.bs.modal', function () {
				// Buscar el primer campo con la clase 'is-invalid' después de que el modal esté completamente oculto
				const firstInvalidField = document.querySelector('.is-invalid');
				if (firstInvalidField) {
					firstInvalidField.focus(); // Establecer el foco en el primer campo con error
				}
			});
			
		});
	</script>
{% endblock script %}
"""

''' Este código ya no es necesario
# Crear un objeto BeautifulSoup
# soup = BeautifulSoup(html_code, "html.parser")

# Obtener el código HTML con indentación
# indented_html_code = soup.prettify(formatter=HTMLFormatter(indent=2))
'''

# Guardar el código HTML en el archivo
# with open("persona3_form.html", "w", encoding="utf-8") as file:
with open(f"{modelo}_form.html", "w", encoding="utf-8") as file:
		file.write(html_code)
		# file.write(indented_html_code)
				
>>>>>>> f71623c58ffe87c8f648350694c7b54122edf9f7
# s = '<section><article><h1></h1><p></p></article></section>'
# formatter = formatter.HTMLFormatter(indent=4)
# print(BeautifulSoup(s, 'html.parser').prettify(formatter=formatter))
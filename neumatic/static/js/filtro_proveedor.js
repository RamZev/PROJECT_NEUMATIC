// neumatic\static\js\filtro_cliente.js

document.addEventListener("DOMContentLoaded", function () {
	// Función para manejar la lógica de habilitar/deshabilitar y seleccionar automáticamente PDF
	const selectAllFormats = () => {
		const formatCheckboxes = document.querySelectorAll('[name="formato_envio"]');
		
		// Variable especifica para marcar por defecto el formato PDF
		const pdfCheckbox = document.querySelector('[name="formato_envio"][value="PDF"]');
		const emailField = document.getElementById("email");
		const celularField = document.getElementById("celular");
		const selectedOption = document.querySelector('input[name="tipo_salida"]:checked').value;
		
		formatCheckboxes.forEach((checkbox) => {
			
			// Deshabilitar o habilitar los checkboxes según la selección
			checkbox.disabled = selectedOption === "tabla" || selectedOption === "pdf_preliminar";
			if (checkbox.disabled) {
				checkbox.checked = false; // Desmarcar si están deshabilitados
				emailField.value = "";
				celularField.value = "";
			}
		});
		
		// Habilitar/deshabilitar campos según la opción seleccionada
		emailField.disabled = selectedOption !== "email";
		celularField.disabled = selectedOption !== "whatsapp";
		
		// Seleccionar el checkbox de PDF si se elige "email" o "whatsapp"
		if (selectedOption === "email" || selectedOption === "whatsapp") {
			pdfCheckbox.checked = true;
		}
	};
	
	// Inicializar el estado por defecto
	const initializeDefaults = () => {
		const formatCheckboxes = document.querySelectorAll('[name="formato_envio"]');
		const emailField = document.getElementById("email");
		const celularField = document.getElementById("celular");
		
		// Deshabilitar checkboxes
		formatCheckboxes.forEach((checkbox) => {
			checkbox.disabled = true;
			checkbox.checked = false;
		});
		
		// Deshabilitar los campos de envio
		emailField.disabled = true;
		celularField.disabled = true;
	};
	
	//evento 'change' para los cambios
	document.querySelectorAll('input[name="tipo_salida"]').forEach((radio) => {
		radio.addEventListener("change", selectAllFormats);
	});
	
	//  cargar la página
	// document.addEventListener("DOMContentLoaded", () => {
		const vistaTabla = document.querySelector('input[name="tipo_salida"][value="tabla"]');
		if (vistaTabla) {
			vistaTabla.checked = true; // Seleccionar Vista Preliminar en Tabla por defecto
		}
		initializeDefaults();
	// });
	
	// Script adicional para el botón "Generar".
	const generar = document.getElementById("generar");
	const clienteInformePdfUrl = "/informes/proveedor_vista_pdf/";      // URL para vista previa PDF.
	const clienteInformeGeneradoUrl = "/informes/proveedor_generado/";  // URL para descarga ZIP.
	
	generar.addEventListener("click", () => {
		const vistaPDFSeleccionada = document.getElementById("pdf_preliminar").checked;
		const envioEmailSeleccionado = document.getElementById("email_envio").checked;
		
		// Obtener el formulario de filtros.
		const form = document.querySelector("form");
		const formData = new URLSearchParams(new FormData(form)).toString();
		
		if (vistaPDFSeleccionada) {
			// Abrir la vista previa en PDF.
			const fullUrl = `${clienteInformePdfUrl}?${formData}&format=pdf`;
			window.open(fullUrl, "_blank");
			// window.open("{% url 'cliente_informe_pdf' %}", "_blank");
		}
		
		if (envioEmailSeleccionado) {
			// Obtener los checkboxes seleccionados
			const selectedFormats = [];
			document.querySelectorAll('input[type="checkbox"]:checked').forEach((checkbox) => {
				selectedFormats.push(checkbox.value);
			});
			
			if (selectedFormats.length === 0) {
				alert("Por favor, selecciona al menos un formato.");
				return;
			}
			
			// Crear la URL con los formatos seleccionados.
			// const baseUrl = "{% url 'cliente_informe_generado' %}";
			const queryParams = selectedFormats.map((format) => `formatos[]=${format}`).join("&");
			// const fullUrl = `${baseUrl}?${queryParams}`;
			const fullUrl = `${clienteInformeGeneradoUrl}?${queryParams}`;
			
			// Redirigir a la URL para descargar el ZIP.
			window.location.href = fullUrl;
		}
	});
	
	// -------------------------------------------------------------------------------
	// Funcionalidad para mostrar modal con los errores de validación del formulario.
	// -------------------------------------------------------------------------------
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
	// -------------------------------------------------------------------------------
	
 });

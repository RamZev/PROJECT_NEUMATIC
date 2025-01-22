// neumatic\static\js\opciones_reporte.js
	
// ---------------------------------------------------------------------------
// Función para llenar localidades basadas en la provincia seleccionada.
// ---------------------------------------------------------------------------
const updateLocalidades = async (provinciaId) => {
	const localidadSelect = document.querySelector('[name="localidad"]');
	
	// Limpiar el select de localidades.
	localidadSelect.innerHTML = '<option value="">Selecciones una localidad...</option>';
	
	if (!provinciaId) {
		return;
	}
	
	try {
		// Llamada a la vista para obtener las localidades filtradas por provincia.
		const url = `/informes/filtrar-localidad/?id_provincia=${provinciaId}`;
		const response = await fetch(url);
		
		if (response.ok) {
			const data = await response.json();
			
			const localidades = data.localidad;
			// Rellenar el select con las localidades obtenidas.
			localidades.forEach(localidad => {
				const option = document.createElement("option");
				option.value = localidad.id_localidad;
				option.textContent = localidad.nombre_completo;
				localidadSelect.appendChild(option);
			});
		} else {
			console.log("Error al obtener localidades:", response.statusText);
		}
		
	} catch (error) {
		console.log("Error en la petición de localidades:", error);
	}
};

// Event listener para el select de provincias
const provinciaSelect = document.querySelector('[name="provincia"]');
if (provinciaSelect) {
	provinciaSelect.addEventListener("change", function () {
		const selectedProvincia = this.value;
		updateLocalidades(selectedProvincia);
	});
}

// ---------------------------------------------------------------------------
// Función para manejar la lógica de habilitar/deshabilitar y seleccionar
// automáticamente PDF
// ---------------------------------------------------------------------------
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

// evento 'change' para los cambios
document.querySelectorAll('input[name="tipo_salida"]').forEach((radio) => {
	radio.addEventListener("change", selectAllFormats);
});

// cargar la página
const vistaTabla = document.querySelector('input[name="tipo_salida"][value="tabla"]');
if (vistaTabla) {
	vistaTabla.checked = true; // Seleccionar Vista Preliminar en Tabla por defecto
}
initializeDefaults();

// Script adicional para el botón "Generar".
const generar = document.getElementById("generar");

if (generar){
	generar.addEventListener("click", function (event) {
		// Previene el envío del formulario al hacer clic en "Generar".
		event.preventDefault();
		
		// Obtener el formulario de filtros.
		const form = this.closest("form");
		const formData = new FormData(form);
		const params = new URLSearchParams(formData).toString();
		
		// URLs extraídas de los atributos data-
		const clienteInformePdfUrl = this.getAttribute("data-pdf-url").split("?")[0];
		const clienteInformeGeneradoUrl = this.getAttribute("data-zip-url").split("?")[0];
		
		// Determinar si es para vista previa PDF o generación ZIP.
		const vistaPDFSeleccionada = document.getElementById("pdf_preliminar")?.checked;
		const envioEmailSeleccionado = document.getElementById("email_envio")?.checked;
		
		if (vistaPDFSeleccionada) {
			// Abrir la vista previa en PDF.
			const fullUrl = `${clienteInformePdfUrl}?${params}&format=pdf`;
			window.open(fullUrl, "_blank");
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
			
			// Crear la URL para el archivo ZIP.
			const fullUrl = `${clienteInformeGeneradoUrl}?${params}`;
			
			// Redirigir a la URL para descargar el ZIP.
			window.location.href = fullUrl;
		}
	});
}
// ---------------------------------------------------------------------------
// Funcionalidad para mostrar modal con los errores de validación
// del formulario.
// ---------------------------------------------------------------------------
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

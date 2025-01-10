// ---------------------------------------------------------------------------
// Funcionalidad Hab/Deshab combo Vendedor.
// ---------------------------------------------------------------------------
const resumenCheck = document.getElementById("id_resumen_pendiente");
const condicionCombo = document.getElementById("id_condicion_venta");
const fechaDesde = document.getElementById("id_fecha_desde");
const fechaHasta = document.getElementById("id_fecha_hasta");
const filtroCliente = document.getElementById("id_filtro_cliente");
const clienteCombo = document.getElementById("id_cliente");


// const estadoResumenCheck = () => {
// 	if (resumenCheck.checked){
// 		condicionCombo.disabled = true;
// 		fechaDesde.disabled = true;
// 		fechaHasta.disabled = true;
// 	}else{
// 		condicionCombo.disabled = false;
// 		fechaDesde.disabled = false;
// 		fechaHasta.disabled = false;
// 	}
// };
const estadoResumenCheck = () => {
    const disabled = resumenCheck.checked; // Determina si los campos deben estar deshabilitados
    [condicionCombo, fechaDesde, fechaHasta].forEach(campo => {
        campo.disabled = disabled;
    });
};

const estadoCliente = () => {
	if (filtroCliente.value === 'todos'){
		clienteCombo.disabled = true;
		clienteCombo.value = "";
	}else{
		clienteCombo.disabled = false;
	}
}


estadoResumenCheck();
estadoCliente();

resumenCheck.addEventListener("change", estadoResumenCheck);
filtroCliente.addEventListener("change", estadoCliente);
// ---------------------------------------------------------------------------
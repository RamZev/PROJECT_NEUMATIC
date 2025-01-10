// ---------------------------------------------------------------------------
// Funcionalidad Hab/Deshab combo Vendedor.
// ---------------------------------------------------------------------------
console.log("Cargado filtros_saldos_clientes.js");

const clienteVendedorCombo = document.getElementById("id_cliente_vendedor");
const vendedorCombo = document.getElementById("id_vendedor");

const estadoComboVendedor = () => {
	if (clienteVendedorCombo.value === "clientes"){
		vendedorCombo.disabled = true;
		vendedorCombo.value = "";
	}else{
		vendedorCombo.disabled = false;
	}
};

estadoComboVendedor();

clienteVendedorCombo.addEventListener("change", estadoComboVendedor);
// ---------------------------------------------------------------------------
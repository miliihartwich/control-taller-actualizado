<template>
  <div class="form-container">
    <h1 class="titulo">Servicio</h1>

    <label>Proveedor</label>
<div class="proveedor-container">
<!-- Input para buscar proveedores -->
<input
  type="text"
  ref="proveedorInput"
  v-model="searchProveedor"
  @input="filterProveedores"
  @focus="handleProveedorFocus"
  placeholder="Escriba para buscar..."
  @blur="hideDropdown"
>
<button class="btn-nuevo" @click="mostrarConfirmacion = true">Nuevo</button>
</div>

<!-- Dropdown de proveedores filtrados -->
<ul v-if="showDropdown && filteredProveedores.length" class="dropdown">
<li
  v-for="proveedor in filteredProveedores"
  :key="proveedor.rut_ci"
  @mousedown="selectProveedor(proveedor)"
>
  {{ proveedor.nombre }} - {{ proveedor.rut_ci }}
</li>
</ul>

<!-- Mostrar el proveedor seleccionado -->
<p v-if="selectedProveedor">Proveedor seleccionado: {{ selectedProveedor.nombre }} - {{ selectedProveedor.rut_ci }}</p>

  <div v-if="mostrarConfirmacion" class="confirmacion">
    <p>¿Crear un nuevo proveedor?</p>
    <button @click="irAProveedorForm">Crear</button>
    <button @click="mostrarConfirmacion = false">Cancelar</button>
  </div>

  <label>Nro de factura</label>
  <input type="text" v-model="servicio.numero_factura">

  <label>Fecha</label>
  <input type="date" v-model="servicio.fecha">

  <label>Moneda</label>
  <select v-model="servicio.moneda">
    <option value="UYU">UYU</option>
    <option value="USD">USD</option>
  </select>

  <label>Importe</label>
  <input type="number" v-model="servicio.importe">

<label>Tipo de IVA</label>
<select v-model.number="servicio.tipo_iva">
  <option :value="22">Básico (22%)</option>
  <option :value="10">Mínimo (10%)</option>
  <option :value="0">Exento (0%)</option>
</select>

  <label>Tipo de cambio</label>
  <input type="number" v-model="servicio.tipo_cambio" :disabled="servicio.moneda === 'UYU'">

  <label>Importe pesos</label>
  <input type="number" v-model="servicio.importe_pesos" disabled>

  <label>Descripción del servicio </label>
  <input type="text" v-model="servicio.descripcion_servicio">

  <!-- División -->
  <label>División Orden asociada</label>
      <select v-model="servicio.division" @change="cargarTipos">
        <option v-for="division in divisiones" :key="division" :value="division">
          {{ division }}
        </option>
      </select>

<!-- Tipo -->
<label>Tipo Orden asociada</label>
<select v-model="servicio.tipo" @change="cargarDescripciones">
<option v-for="tipo in tipos" :key="tipo" :value="tipo">
  {{ tipo }}
</option>
</select>


<!-- Descripción -->
<label>Descripción Orden asociada</label>
<select v-model="servicio.descripcion">
<option v-for="descripcion in descripciones" :key="descripcion" :value="descripcion">
  {{ descripcion }}
</option>
</select>


    <div class="buttons-container">
      <button class="btn" @click="guardarServicio">GUARDAR</button>
      <button @click="goTo('MenuPage')" class="btn">Menú</button>
    </div>

    <div v-if="mensajeEstado" :class="['mensaje', tipoMensaje]">
{{ mensajeEstado }}
</div>

  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      servicio: {
        proveedor_rut_ci: '',
        numero_factura: '',
        fecha: '',
        moneda: '',
        importe: '',
        tipo_iva: '',
        tipo_cambio: 1,
        importe_pesos: '',
        descripcion_servicio: '',
        division: '',
        tipo: '',
        descripcion: ''
      },
      searchProveedor: '',
      proveedores: [],
      filteredProveedores: [],
      showDropdown: false,
      mostrarConfirmacion: false,
      mostrarCampo:false,
      mensajeEstado: '',
      tipoMensaje: '', // "exito" | "error"
      divisiones: [],
      tipos: [],
      descripciones: [],
      bloqueandoDropdownProveedor: false,
    };
  },

  watch: {
    'servicio.moneda'(val) {
      if (val === 'UYU') {
        this.servicio.tipo_cambio = 1;
        this.servicio.importe_pesos = this.servicio.importe;
      } else if (val === 'USD') {
        this.servicio.tipo_cambio = null;
        this.servicio.importe_pesos = this.servicio.importe * (this.servicio.tipo_cambio || 0);
      }
    },
    'servicio.importe'(val) {
      if (this.servicio.moneda === 'UYU') {
        this.servicio.importe_pesos = val;
      } else if (this.servicio.moneda === 'USD') {
        this.servicio.importe_pesos = val * (this.servicio.tipo_cambio || 0);
      }
    },
    'servicio.tipo_cambio'(val) {
      if (this.servicio.moneda === 'USD') {
        this.servicio.importe_pesos = this.servicio.importe * (val || 0);
      }
    }
  },

  methods: {
    // --- catálogos ---
    async fetchProveedores() {
      try {
        const data = await apiFetch('/proveedores');
        this.proveedores = data;
        this.filteredProveedores = data;
      } catch (e) {
        console.error('Error obteniendo proveedores:', e.message);
      }
    },
    async cargarDivisiones() {
      try {
        const data = await apiFetch('/divisiones'); // array de strings
        this.divisiones = data;
      } catch (e) {
        console.error('Error al cargar divisiones:', e.message);
      }
    },
    async cargarTipos() {
      if (!this.servicio.division) return;
      try {
        const data = await apiFetch(`/tipos_por_division/${encodeURIComponent(this.servicio.division)}`);
        this.tipos = data;
      } catch (e) {
        console.error('Error al cargar tipos:', e.message);
      }
    },
    async cargarDescripciones() {
      if (!this.servicio.tipo) return;
      try {
        const data = await apiFetch(`/descripcion_por_tipo/${encodeURIComponent(this.servicio.tipo)}`);
        this.descripciones = data;
      } catch (e) {
        console.error('Error al cargar descripciones:', e.message);
      }
    },

    // --- UI búsqueda proveedor ---
    handleProveedorFocus() {
      if (!this.bloqueandoDropdownProveedor) this.showDropdown = true;
    },
    filterProveedores() {
      if (this.searchProveedor) {
        const q = this.searchProveedor.toLowerCase();
        const starts = this.proveedores.filter(p =>
          p.nombre.toLowerCase().startsWith(q) || String(p.rut_ci).toLowerCase().startsWith(q)
        );
        const contains = this.proveedores.filter(p =>
          !p.nombre.toLowerCase().startsWith(q) &&
          !String(p.rut_ci).toLowerCase().startsWith(q) &&
          (p.nombre.toLowerCase().includes(q) || String(p.rut_ci).toLowerCase().includes(q))
        );
        this.filteredProveedores = [...starts, ...contains];
      } else {
        this.filteredProveedores = this.proveedores;
      }
      this.showDropdown = true;
    },
    selectProveedor(proveedor) {
      this.searchProveedor = `${proveedor.nombre} - ${proveedor.rut_ci}`;
      this.servicio.proveedor_rut_ci = proveedor.rut_ci;
      this.showDropdown = false;
    },
    hideDropdown() { setTimeout(() => { this.showDropdown = false; }, 200); },
    irAProveedorForm() { this.$router.push('/proveedor-form'); },

    // --- guardar ---
    validarServicio() {
      if (!this.servicio.proveedor_rut_ci ||
          !this.servicio.numero_factura ||
          !this.servicio.fecha ||
          !this.servicio.importe ||
          !this.servicio.descripcion_servicio ||
          !this.servicio.division ||
          !this.servicio.tipo ||
          !this.servicio.descripcion) {
        this.mostrarMensaje('Todos los campos son obligatorios', 'error');
        return false;
      }
      return true;
    },

    async guardarServicio() {
      if (!this.validarServicio()) return;

      const payload = {
        proveedor_rut_ci: this.servicio.proveedor_rut_ci,
        numero_factura: this.servicio.numero_factura,
        fecha: this.servicio.fecha,
        moneda: this.servicio.moneda,
        importe: this.servicio.importe,
        tipo_iva: this.servicio.tipo_iva,
        tipo_cambio: this.servicio.tipo_cambio,
        importe_pesos: this.servicio.importe_pesos,
        descripcion_servicio: this.servicio.descripcion_servicio,
        division: this.servicio.division,
        tipo: this.servicio.tipo,
        descripcion: this.servicio.descripcion
      };

      try {
        const data = await apiFetch('/registrar_servicio', { method: 'POST', body: payload });
        this.mensajeEstado = data.message || 'Servicio registrado exitosamente';
        this.tipoMensaje = 'exito';
        setTimeout(() => { this.mensajeEstado = ''; }, 3000);
        setTimeout(() => { this.limpiarFormulario(); }, 2000);
      } catch (e) {
        this.mensajeEstado = e.message || 'Error al guardar';
        this.tipoMensaje = 'error';
      }
    },

    mostrarMensaje(msg, tipo) {
      this.mensajeEstado = msg;
      this.tipoMensaje = tipo;
      setTimeout(() => { this.mensajeEstado = ''; this.tipoMensaje = ''; }, 3000);
    },

    limpiarFormulario() {
      this.servicio = {
        proveedor_rut_ci: '',
        numero_factura: '',
        fecha: '',
        moneda: '',
        importe: '',
        tipo_iva: '',
        tipo_cambio: 1,
        importe_pesos: '',
        descripcion_servicio: '',
        division: '',
        tipo: '',
        descripcion: ''
      };
      this.searchProveedor = '';
      this.tipos = [];
      this.descripciones = [];
    },

    goTo(routeName) { this.$router.push({ name: routeName }); },
  },

  mounted() {
    this.fetchProveedores();
    this.cargarDivisiones();
  }
};
</script>


<style scoped>

.form-container {
  width: 50%;
  margin: 0 auto;
}

.titulo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  text-align: center;
  border-radius: 4px;
}

.input-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 1.2rem;
}

input, select {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.buttons-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.btn {
  background-color: #b53b3b;
  color: white;
  font-size: 1.2rem;
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
}
.mensaje {
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  margin-top: 10px;
}

.exito {
  background-color: #4CAF50;
  color: white;
}

.error {
  background-color: #f44336;
  color: white;
}

.nuevo-rubro-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.nuevo-rubro-container input {
  flex-grow: 1;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.btn-guardar, .btn-cerrar {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-cerrar {
  background-color: #f44336;
}
</style>
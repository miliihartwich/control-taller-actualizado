<template>
  <div class="form-container">
    <div class="titulo">COMPRAS</div>

    <label>Proveedor</label>
    <div class="proveedor-container">
      <!-- 👇 NUEVO wrapper SOLO para proveedor -->
      <div class="autocomplete">
        <input
          type="text"
          ref="proveedorInput"
          v-model="searchProveedor"
          @input="filterProveedores"
          @focus="onProveedorFocus"
          @blur="hideProveedorDropdown"
          placeholder="Escriba para buscar..."
          autocomplete="off"
        />
        <!-- 👇 MOVIDO adentro del wrapper -->
        <ul v-if="showDropdown" class="dropdown">
          <li v-if="cargandoProveedores" class="hint">Cargando proveedores…</li>
          <li
            v-for="p in filteredProveedores"
            :key="p.rut_ci || p.id || p.nombre"
            @mousedown.prevent="selectProveedor(p)"
          >
            {{ p.nombre }} - {{ p.rut_ci }}
          </li>
          <li v-if="!cargandoProveedores && !filteredProveedores.length" class="hint">
            Sin resultados
          </li>
        </ul>
      </div>

      <button class="btn-nuevo" @click="mostrarConfirmacion = true">Nuevo</button>
    </div>

    <div v-if="mostrarConfirmacion" class="confirmacion">
      <p>¿Crear un nuevo proveedor?</p>
      <button @click="irAProveedorForm">Crear</button>
      <button @click="mostrarConfirmacion = false">Cancelar</button>
    </div>

    <label>Nro de factura</label>
    <input type="text" v-model="compra.numero_factura" />

    <label>Fecha</label>
    <input type="date" v-model="compra.fecha" />

    <label>Moneda</label>
    <select v-model="compra.moneda">
      <option value="UYU">UYU</option>
      <option value="USD">USD</option>
    </select>

    <label>Importe</label>
    <input type="number" v-model="compra.importe" />

    <label>Tipo de IVA</label>
    <select v-model="compra.tipo_iva">
      <option>Básico</option>
      <option>Mínimo</option>
      <option>Exento</option>
    </select>

    <label>Tipo de cambio</label>
    <input type="number" v-model="compra.tipo_cambio" :disabled="compra.moneda === 'UYU'" />

    <label>Importe pesos</label>
    <input type="number" v-model="compra.importe_pesos" disabled />

    <label for="bien">Bienes</label>
    <div class="bien-container">
      <input
        type="text"
        ref="bienInput"
        v-model="searchBien"
        @input="filterBienes"
        @focus="showAllBienes"
        @blur="handleBlurBien"
        placeholder="Escriba para buscar bien..."
        autocomplete="off"
      />
      <ul v-if="showDropdownBien" class="dropdown">
        <li
          v-for="bien in filteredBienes"
          :key="bien.nombre"
          @mousedown.prevent="selectBien(bien)"
        >
          {{ bien.nombre }}
        </li>
        <li v-if="!filteredBienes.length" class="hint">Sin resultados</li>
      </ul>
    </div>

    <div class="button-container">
      <button class="btn btn-secondary" @click="crearNuevoBien">Crear Nuevo Bien</button>
      <button @click="goTo('MenuPage')" class="btn">Menú</button>
    </div>

    <div v-if="mostrarCampo">
      <input type="text" v-model="nuevoBien" placeholder="Nombre del bien" />
      <button class="btn btn-secondary" @click="agregarNuevoBien">Crear</button>
    </div>

    <div v-if="bienesAgregados && bienesAgregados.length">
      <table class="table-bienes">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Cantidad</th>
            <th>Costo Unitario</th>
            <th>Unidad</th>
            <th>Moneda</th>
            <th>Numero de factura</th>
            <th>Eliminar?</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(bien, index) in bienesAgregados" :key="index">
            <td>{{ bien.nombre }}</td>
            <td><input type="number" v-model.number="bien.cantidad" /></td>
            <td><input type="number" v-model.number="bien.costo_unitario" /></td>
            <td>
              <select v-model="bien.unidad" :disabled="!bien.esNuevo">
                <option value="Unidad">Unidad</option>
                <option value="Metros">Metros</option>
                <option value="Kilos">Kilos</option>
              </select>
            </td>
            <td>
              <select v-model="bien.moneda">
                <option value="UYU">UYU</option>
                <option value="USD">USD</option>
              </select>
            </td>
            <td><input v-model="compra.numero_factura" type="text" disabled /></td>
            <td><button @click="eliminarBien(index)" class="btn-eliminar">❌</button></td>
          </tr>
        </tbody>
      </table>

      <button class="btn" @click="guardarCompra">Guardar Todo</button>
      <button @click="goTo('MenuPage')" class="btn">Menú</button>

      <div v-if="mensajeEstado" :class="['mensaje', tipoMensaje]">{{ mensajeEstado }}</div>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      compra: {
        proveedor_rut_ci: '',
        numero_factura: '',
        fecha: '',
        moneda: 'UYU',
        importe: '',
        tipo_iva: '',
        tipo_cambio: 1,
        importe_pesos: '',
        bienes: []
      },

      // estados buscador proveedores
      searchProveedor: '',
      proveedores: [],
      filteredProveedores: [],
      showDropdown: false,
      cargandoProveedores: false,

      // bienes
      bienes: [],
      bienesAgregados: [],
      searchBien: '',
      filteredBienes: [],
      showDropdownBien: false,

      // UI
      mostrarConfirmacion: false,
      mostrarCampo: false,
      mensajeEstado: '',
      tipoMensaje: '',

      // auxiliares
      numeroFactura: '',
      nuevoBien: '',

      // moneda por defecto para items
      cantidad: 0,
      costo_unitario: 0,
      unidad: 'Unidad',
      moneda: 'UYU'
    };
  },

  watch: {
    'compra.moneda'(m) {
      if (m === 'UYU') {
        this.compra.tipo_cambio = 1;
        this.compra.importe_pesos = Number(this.compra.importe) || 0;
      } else if (m === 'USD') {
        this.compra.importe_pesos =
          (Number(this.compra.importe) || 0) * (Number(this.compra.tipo_cambio) || 0);
      }
    },
    'compra.importe'(v) {
      const val = Number(v) || 0;
      this.compra.importe_pesos =
        this.compra.moneda === 'UYU'
          ? val
          : val * (Number(this.compra.tipo_cambio) || 0);
    },
    'compra.tipo_cambio'(tc) {
      if (this.compra.moneda === 'USD') {
        this.compra.importe_pesos = (Number(this.compra.importe) || 0) * (Number(tc) || 0);
      }
    }
  },

  methods: {
    // -------- Normalización robusta --------
    _pickArray(payload) {
      if (Array.isArray(payload)) return payload;
      if (!payload || typeof payload !== 'object') return [];
      const candidates = ['data', 'items', 'results', 'rows', 'proveedores', 'lista', 'list', 'content'];
      for (const k of candidates) if (Array.isArray(payload[k])) return payload[k];
      for (const v of Object.values(payload)) if (Array.isArray(v)) return v;
      return [];
    },
    _normalizeProveedor(p) {
      const e = Object.fromEntries(Object.entries(p || {}).map(([k, v]) => [k.toLowerCase(), v]));
      return {
        nombre: String(e.nombre ?? e.proveedor ?? e.razon_social ?? ''),
        rut_ci: String(e.rut_ci ?? e.rut ?? e.ci ?? e.documento ?? '')
      };
    },
    _normalizeBien(b) {
      const e = Object.fromEntries(Object.entries(b || {}).map(([k, v]) => [k.toLowerCase(), v]));
      return { nombre: String(e.nombre ?? ''), unidad: String(e.unidad ?? 'Unidad') };
    },

    // -------- Proveedores --------
    async fetchProveedores() {
      this.cargandoProveedores = true;
      try {
        const raw = await apiFetch('proveedores');
        const arr = this._pickArray(raw).map(this._normalizeProveedor)
          .filter(p => p.nombre || p.rut_ci);
        this.proveedores = arr;
        this.filteredProveedores = [...this.proveedores];
      } catch (e) {
        console.error('Error obteniendo proveedores:', e?.message || e);
        this.proveedores = [];
        this.filteredProveedores = [];
      } finally {
        this.cargandoProveedores = false;
      }
    },
    onProveedorFocus() {
      if (!this.proveedores.length && !this.cargandoProveedores) {
        this.fetchProveedores().then(() => {
          this.filteredProveedores = [...this.proveedores];
          this.showDropdown = true;
        });
      } else {
        if (!this.searchProveedor.trim()) {
          this.filteredProveedores = [...this.proveedores];
        } else {
          this.filterProveedores();
        }
        this.showDropdown = true;
      }
    },
    hideProveedorDropdown() {
      setTimeout(() => (this.showDropdown = false), 150);
    },
    filterProveedores() {
      const q = (this.searchProveedor || '').toLowerCase().trim();
      if (!q) {
        this.filteredProveedores = [...this.proveedores];
        return;
      }
      const starts = this.proveedores.filter(
        p => p.nombre.toLowerCase().startsWith(q) || p.rut_ci.toLowerCase().startsWith(q)
      );
      const contains = this.proveedores.filter(
        p =>
          !p.nombre.toLowerCase().startsWith(q) &&
          !p.rut_ci.toLowerCase().startsWith(q) &&
          (p.nombre.toLowerCase().includes(q) || p.rut_ci.toLowerCase().includes(q))
      );
      this.filteredProveedores = [...starts, ...contains];
    },
    selectProveedor(p) {
      this.searchProveedor = `${p.nombre} - ${p.rut_ci}`;
      this.compra.proveedor_rut_ci = p.rut_ci;
      this.showDropdown = false;
    },
    irAProveedorForm() {
      this.$router.push('/proveedor-form');
    },

    // -------- Bienes --------
    async cargarBienes() {
      try {
        const raw = await apiFetch('bienes-nombres');
        this.bienes = this._pickArray(raw).map(this._normalizeBien);
        this.filteredBienes = [...this.bienes];
      } catch (e) {
        console.error('Error cargando bienes:', e?.message || e);
        this.bienes = [];
        this.filteredBienes = [];
      }
    },
    showAllBienes() {
      this.filteredBienes = [...this.bienes];
      this.showDropdownBien = true;
    },
    filterBienes() {
      const q = (this.searchBien || '').trim().toLowerCase();
      if (!q) {
        this.filteredBienes = [...this.bienes];
        this.showDropdownBien = true;
        return;
      }
      const starts = this.bienes.filter(b => b.nombre.toLowerCase().startsWith(q));
      const contains = this.bienes.filter(
        b => !b.nombre.toLowerCase().startsWith(q) && b.nombre.toLowerCase().includes(q)
      );
      this.filteredBienes = [...starts, ...contains];
      this.showDropdownBien = true;
    },
    selectBien(b) {
      this.searchBien = b.nombre;
      this.bienesAgregados.push({
        nombre: b.nombre,
        unidad: b.unidad,
        cantidad: '',
        costo_unitario: '',
        moneda: this.moneda,
        numero_factura: this.compra.numero_factura
      });
      this.showDropdownBien = false;
      setTimeout(() => this.$refs?.bienInput?.focus(), 0);
    },
    handleBlurBien() {
      setTimeout(() => {
        if (this.searchBien && !this.bienes.some(b => b.nombre === this.searchBien)) {
          this.searchBien = '';
        }
        this.showDropdownBien = false;
      }, 150);
    },
      // --- NUEVO: crear / agregar bien ---
crearNuevoBien() {
  // muestra el input "nuevoBien" para que escribas el nombre
  this.mostrarCampo = true;
},

agregarNuevoBien() {
  const nombre = (this.nuevoBien || '').trim();
  if (!nombre) {
    alert('Ingrese el nombre del bien.');
    return;
  }

  // fila editable en la tabla
  const nuevoBien = {
    nombre,
    cantidad: 0,
    costo_unitario: 0,
    unidad: this.unidad,                  // usa la unidad por defecto del form
    moneda: this.moneda,                  // usa la moneda por defecto del form
    numero_factura: this.compra.numero_factura,
    esNuevo: true                         // habilita el <select> de unidad
  };

  // lo sumamos al catálogo para que también aparezca en el buscador
  this.bienes.push({ nombre, unidad: this.unidad });

  // y lo agregamos a la compra para que se vea en la tabla
  this.bienesAgregados.push(nuevoBien);

  // reset UI
  this.nuevoBien = '';
  this.mostrarCampo = false;
  this.filteredBienes = [...this.bienes];
},

    // -------- Compra --------
    async guardarCompra() {
      const bienesParaEnviar = this.bienesAgregados.map(b => {
        const copy = { ...b };
        delete copy.esNuevo;
        return copy;
      });

      if (!this.validarCompra()) return;

      const compraData = {
        proveedor_rut_ci: this.compra.proveedor_rut_ci,
        numero_factura: this.compra.numero_factura,
        fecha: this.compra.fecha,
        moneda: this.compra.moneda,
        importe: this.compra.importe,
        tipo_iva: this.compra.tipo_iva,
        tipo_cambio: this.compra.tipo_cambio,
        importe_pesos: this.compra.importe_pesos,
        bienes: bienesParaEnviar
      };

      try {
        const data = await apiFetch('compras', { method: 'POST', body: compraData });
        this.mensajeEstado = data?.message || 'Compra guardada';
        this.tipoMensaje = 'exito';
        setTimeout(() => (this.mensajeEstado = ''), 3000);
        setTimeout(() => this.limpiarFormulario(), 2000);
      } catch (e) {
        this.mensajeEstado = e?.message || 'Error al guardar la compra';
        this.tipoMensaje = 'error';
      }
    },
    validarCompra() {
      if (!this.compra.proveedor_rut_ci || !this.compra.numero_factura || !this.compra.fecha || !this.compra.importe) {
        this.mostrarMensaje('Todos los campos de la compra son obligatorios', 'error');
        return false;
      }
      if (!this.bienesAgregados.length) {
        this.mostrarMensaje('Debe agregar al menos un bien', 'error');
        return false;
      }
      return true;
    },
    mostrarMensaje(msg, tipo) {
      this.mensajeEstado = msg;
      this.tipoMensaje = tipo;
      setTimeout(() => {
        this.mensajeEstado = '';
        this.tipoMensaje = '';
      }, 3000);
    },
    limpiarFormulario() {
      this.compra = {
        proveedor_rut_ci: '',
        numero_factura: '',
        fecha: '',
        moneda: 'UYU',
        importe: '',
        tipo_iva: '',
        tipo_cambio: 1,
        importe_pesos: '',
        bienes: []
      };
      this.bienesAgregados = [];
      this.searchProveedor = '';
      this.searchBien = '';
      this.filteredBienes = [];
    },
    goTo(routeName) {
      this.$router.push({ name: routeName });
    }
  },



  mounted() {
    this.fetchProveedores();
    this.cargarBienes();
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
  padding: 20px;
  text-align: center;
  border-radius: 4px;
  font-size: 2rem;
  font-weight: bold;
}

.proveedor-container {
  display: flex;
  gap: 10px;
}

/* 👇 NUEVO: wrapper relativo SOLO para proveedor */
.proveedor-container .autocomplete {
  position: relative;
  flex: 1;           /* que el input ocupe todo el ancho disponible */
  min-width: 0;
}

.btn-nuevo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  flex: 0 0 auto;    /* NUEVO */
  margin-left: 12px; /* NUEVO */
}

.confirmacion {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-top: 10px;
  text-align: center;
}

.confirmacion button {
  margin: 5px;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirmacion button:first-child {
  background-color: #4CAF50;
  color: white;
}

.confirmacion button:last-child {
  background-color: #b53b3b;
  color: white;
}

label {
  display: block;
  font-size: 1.2rem;
  margin-top: 10px;
}

input, select {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-top: 5px;
}
.btn-eliminar {
  background: none;
  border: none;
  color: red;
  font-size: 18px;
  cursor: pointer;
}

.btn-eliminar:hover {
  color: darkred;
}

.btn {
  background-color: #b53b3b;
  color: white;
  font-size: 1.2rem;
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  text-align: center;
  margin-top: 20px;
}

/* estilos generales existentes del dropdown (se mantienen) */
.dropdown {
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  position: absolute;
  width: calc(50% - 20px);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  list-style: none;
  padding: 0;
  margin: 0;
}

/* 👇 OVERRIDE SOLO para el dropdown de proveedor (debajo del input y ancho completo del input) */
.proveedor-container .dropdown {
  top: calc(100% + 4px);  /* debajo del input */
  left: 0;
  right: 0;
  width: 100%;            /* igual ancho que el input */
  box-shadow: 0 6px 16px rgba(0,0,0,.08);
  align-items: center; /* NUEVO */
}

.dropdown li {
  padding: 10px;
  cursor: pointer;
}

.dropdown li:hover {
  background-color: #f1f1f1;
}

.mensaje {
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}

.exito {
  background-color: #4CAF50;
  color: white;
}

.error {
  background-color: #b53b3b;
  color: white;
}

.botones-container {
  display: flex;
  gap: 20px;
}

.btn:first-child {
  margin-right: 20px;
}
.form-group select {
  display: block;
  width: 100%;
  margin-bottom: 10px;
}

.button-container {
  display: flex;
  justify-content: flex-start;
  gap: 20px;
  margin-top: 10px;
}

.btn {
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background-color: #a02424;
  color: white;
}

.btn-secondary {
  background-color: #5a5a5a;
  color: white;
}

.btn-danger {
  background-color: #d9534f;
  color: white;
}

.tabla-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.guardar-btn {
  margin-top: 10px;
  align-self: flex-start;
}

.table-bienes {
  width: 100%;
  table-layout: auto;
  border-collapse: separate;
  border-spacing: 0 8px;
}

.table-bienes th,
.table-bienes td {
  min-width: 120px;
  border: 1px solid #ccc;
  padding: 4px 8px;
  text-align: left;
  box-sizing: border-box;
}

.table-bienes th {
  text-align: center;
}

.table-bienes input,
.table-bienes select {
  width: 100%;
  box-sizing: border-box;
}
</style>

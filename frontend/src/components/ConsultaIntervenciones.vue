<template>
  <div class="empleados-container">
    <h1 class="titulo">INTERVENCIONES POR EMPLEADO</h1>

    <!-- Filtros -->
    <div class="filtros">
      <label>Empleado</label>
      <div class="empleado-container">
        <input
          type="text"
          v-model="searchEmpleado"
          @input="filterEmpleados"
          @focus="showDropdown = true"
          @blur="hideDropdown"
          placeholder="Escriba para buscar..."
          class="busqueda"
        />
        <ul v-show="showDropdown && filteredEmpleados.length" class="dropdown">
          <li
            v-for="empleado in filteredEmpleados"
            :key="empleado.cedula"
            @mousedown.prevent="selectEmpleado(empleado)"
          >
            {{ empleado.nombre }}
          </li>
        </ul>
      </div>

      <label>Desde</label>
      <input type="date" v-model="fechaDesde" class="busqueda" />

      <label>Hasta</label>
      <input type="date" v-model="fechaHasta" class="busqueda" />

      <button @click="buscarIntervenciones" class="menu-boton">Buscar</button>
    </div>

    <!-- Tabla -->
    <div class="tabla-intervenciones" v-if="intervenciones.length">
      <table class="empleados-tabla">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>División</th>
            <th>Descripción</th>
            <th>Horas</th>
            <th>Costo</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="intervencion in intervenciones"
            :key="intervencion.numero_orden"
          >
            <td>{{ intervencion.tipo }}</td>
            <td>{{ intervencion.division }}</td>
            <td>{{ intervencion.descripcion }}</td>
            <td>{{ intervencion.horas_trabajadas }}</td>
            <td>{{ intervencion.costo_intervencion }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3"></td>
            <td>
              <div class="total-label">Total Horas</div>
              <div class="total-value">{{ totalHoras }}</div>
            </td>
            <td>
              <div class="total-label">Total Costo</div>
              <div class="total-value">{{ totalCosto }}</div>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <button @click="goTo('MenuPage')" class="botones">Menú</button>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      empleados: [],
      filteredEmpleados: [],
      empleadoSeleccionado: '',
      searchEmpleado: '',
      fechaDesde: '',
      fechaHasta: '',
      intervenciones: [],
      totalHoras: '00:00',
      totalCosto: 0,
      showDropdown: false,
    };
  },

  mounted() {
    this.obtenerEmpleados();
  },

  methods: {
    async obtenerEmpleados() {
      const data = await apiFetch('/obtener_empleados');
      this.empleados = data;
      this.filteredEmpleados = data;
    },

    filterEmpleados() {
      const q = this.searchEmpleado.toLowerCase();
      this.filteredEmpleados = q
        ? this.empleados.filter(e => e.nombre.toLowerCase().includes(q))
        : this.empleados;
      this.showDropdown = true;
    },

    selectEmpleado(empleado) {
      this.searchEmpleado = empleado.nombre;
      this.empleadoSeleccionado = empleado.cedula;
      this.showDropdown = false;
    },

    hideDropdown() {
      setTimeout(() => (this.showDropdown = false), 200);
    },

    async buscarIntervenciones() {
      if (!this.empleadoSeleccionado || !this.fechaDesde || !this.fechaHasta) {
        alert('Seleccione empleado y rango de fechas');
        return;
      }

      const qs = new URLSearchParams({
        empleado_id: this.empleadoSeleccionado,
        fecha_desde: this.fechaDesde,
        fecha_hasta: this.fechaHasta
      });

      const data = await apiFetch(`/get_intervenciones?${qs}`);

      this.intervenciones = data.intervenciones || [];
      this.totalHoras = data.total_horas || '00:00';
      this.totalCosto = data.total_costo ?? 0;
    },

    goTo(route) {
      this.$router.push({ name: route });
    }
  }
};
</script>


<style scoped>
.empleados-container {
  width: 100%;
  margin: 20px auto;
  text-align: center;
}
.titulo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  font-weight: bold;
}
.busqueda {
  width: 100%;
  padding: 8px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.empleado-container {
  position: relative;
  display: flex;
  flex-direction: column;
}
.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  padding: 0;
  margin: 0;
  z-index: 100;
}
.dropdown li {
  padding: 10px;
  cursor: pointer;
  list-style: none;
  transition: background-color 0.2s;
}
.dropdown li:hover {
  background-color: #f0f0f0;
}
.empleados-tabla {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.empleados-tabla th, .empleados-tabla td {
  border: 1px solid #000;
  padding: 8px;
  text-align: left;
}
.empleados-tabla thead {
  background-color: #b53b3b;
  color: white;
}
.filtros label {
  display: block;
  font-weight: bold;
  text-align: left;
  margin-bottom: 5px;
}
button {
  background-color: red;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}
.botones {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}
.total-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.total-label {
  font-weight: bold;
  font-size: 14px;
  color: #555;
}

.total-value {
  font-size: 16px;
  font-weight: bold;
  margin-top: 4px;
}


</style>

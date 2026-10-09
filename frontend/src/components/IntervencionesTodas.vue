<template>
  <div class="empleados-container">
    <h1 class="titulo">TODAS LAS INTERVENCIONES</h1>

    <button @click="cargar" class="menu-boton">Recargar</button>

    <div class="tabla-intervenciones" v-if="intervenciones.length">
      <table class="empleados-tabla">
        <thead>
          <tr>
            <th>División</th>
            <th>Tipo</th>
            <th>Descripción</th>
            <th>Fecha</th>
            <th>Hora inicio</th>
            <th>Hora fin</th>
            <th>Empleado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(it, idx) in intervenciones" :key="idx">
            <td>{{ it.division }}</td>
            <td>{{ it.tipo }}</td>
            <td>{{ it.descripcion || '-' }}</td>
            <td>{{ formatearFecha(it.fecha) }}</td>
            <td>{{ it.hora_inicio || '-' }}</td>
            <td>{{ it.hora_fin || 'Abierta' }}</td>
            <td>{{ it.empleado_nombre }} ({{ it.empleado_cedula }})</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else style="margin-top: 12px;">
      No hay intervenciones para mostrar.
    </div>

    <button @click="goTo('MenuPage')" class="botones">Menú</button>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      intervenciones: []
    };
  },
  mounted() {
    this.cargar();
  },
  methods: {
    async cargar() {
      try {
        const data = await apiFetch('/intervenciones/todas');
        this.intervenciones = data?.intervenciones || [];
      } catch (e) {
        console.error('Error cargando intervenciones:', e.message);
        this.intervenciones = [];
      }
    },
    formatearFecha(iso) {
      if (!iso) return '-';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    },
    goTo(routeName) {
      this.$router.push({ name: routeName });
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

.empleados-tabla th,
.empleados-tabla td {
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

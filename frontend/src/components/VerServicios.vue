<template>
  <div class="servicios-container">
    <h1 class="titulo">Lista de Servicios</h1>
    
    <!-- Barra de Búsqueda -->
    <input 
      type="text" 
      v-model="filtroDescripcion" 
      placeholder="Buscar por descripción..." 
      class="busqueda"
    />
    
    <!-- Tabla de Servicios -->
    <table class="servicios-tabla">
      <thead>
        <tr>
          <th>Nº Factura</th>
          <th>RUT/CI Proveedor</th>
          <th>Fecha</th>
          <th>Descripción</th>
          <th>Moneda</th>
          <th>Importe</th>
          <th>Tipo IVA</th>
          <th>T. Cambio</th>
          <th>Importe $</th>
          <th>Nº Orden</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="servicio in serviciosFiltrados" :key="servicio.numero_factura">
          <td>{{ servicio.numero_factura }}</td>
          <td>{{ servicio.rut_ci_proveedor }}</td>
          <td>{{ formatearFecha(servicio.fecha) }}</td>
          <td>{{ servicio.descripcion }}</td>
          <td>{{ servicio.moneda }}</td>
          <td>{{ formatearImporte(servicio.importe) }}</td>
          <td>{{ servicio.tipo_iva }}</td>
          <td>{{ formatearImporte(servicio.tipo_cambio) }}</td>
          <td>{{ formatearImporte(servicio.importe_pesos) }}</td>
          <td>{{ servicio.numero_orden }}</td>
        </tr>
      </tbody>
    </table>
    
    <!-- Mensaje cuando no hay resultados -->
    <div v-if="serviciosFiltrados.length === 0 && !cargando" class="sin-resultados">
      No se encontraron servicios que coincidan con la búsqueda.
    </div>
    
    <!-- Indicador de carga -->
    <div v-if="cargando" class="cargando">
      Cargando datos...
    </div>
  </div>

  <!-- Botón de Menú -->
  <div class="menu-boton-container">
    <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      servicios: [],
      filtroDescripcion: "",
      cargando: true,
      error: null
    };
  },

  computed: {
    serviciosFiltrados() {
      const filtro = this.filtroDescripcion.toLowerCase().trim();
      if (!filtro) return this.servicios;

      const empiezaCon = this.servicios.filter(s =>
        s.descripcion && s.descripcion.toLowerCase().startsWith(filtro)
      );

      const contiene = this.servicios.filter(s =>
        s.descripcion &&
        s.descripcion.toLowerCase().includes(filtro) &&
        !s.descripcion.toLowerCase().startsWith(filtro)
      );

      return [...empiezaCon, ...contiene];
    }
  },

  mounted() {
    this.obtenerServicios();
  },

  methods: {
    async obtenerServicios() {
      this.cargando = true;
      this.error = null;
      try {
        const data = await apiFetch('/get_servicios'); // ← usa base URL de env
        this.servicios = Array.isArray(data) ? data : [];
      } catch (e) {
        console.error("Error al obtener servicios:", e.message);
        this.error = "No se pudieron cargar los servicios. Por favor, intente nuevamente.";
      } finally {
        this.cargando = false;
      }
    },

    formatearFecha(fechaISO) {
      if (!fechaISO) return '-';
      try {
        const fecha = new Date(fechaISO);
        return fecha.toLocaleDateString('es-ES');
      } catch {
        return fechaISO;
      }
    },

    formatearImporte(valor) {
      if (valor === null || valor === undefined) return '-';
      return Number(valor).toLocaleString('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    }
  }
};
</script>


<style scoped>
/* Contenedor principal */
.servicios-container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  text-align: center;
}

/* Estilos del título */
.titulo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  font-weight: bold;
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 15px;
}

/* Input de búsqueda */
.busqueda {
  width: 100%;
  padding: 8px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
}

/* Estilos de la tabla */
.servicios-tabla {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 12px;
  overflow-x: auto;
}

.servicios-tabla thead {
  background-color: #b53b3b;
  color: white;
}

.servicios-tabla th, .servicios-tabla td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
  font-size: 12px;
}

/* Mensaje de sin resultados */
.sin-resultados {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 5px;
  color: #666;
}

/* Indicador de carga */
.cargando {
  margin: 20px 0;
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 5px;
  color: #666;
}

/* Botón de menú */
.menu-boton-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  margin-top: 20px;
}

.menu-boton {
  background-color: #992f2f;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 5px;
}

.menu-boton:hover {
  background-color: #7a2424;
}

/* Responsive para dispositivos móviles */
@media (max-width: 768px) {
  .servicios-container {
    width: 95%;
    overflow-x: auto;
  }
  
  .servicios-tabla {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>
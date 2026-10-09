<template>
  <div class="ver-stock-root">
    <div class="stock-container">
      <h1 class="titulo">Lista de Stock</h1>

      <!-- Barra de Búsqueda -->
      <input 
        type="text" 
        v-model="filtroNombre" 
        placeholder="Buscar por nombre de bien..." 
        class="busqueda"
      />

      <!-- Tabla de Stock -->
      <table class="stock-tabla">
        <thead>
          <tr>
            <th>Bien</th>
            <th>Unidades Disponibles</th>
            <th>Unidad</th>
            <th>Costo Unitario</th>
            <th>Moneda</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="producto in stockFiltrado" :key="producto.nombre_bien">
            <td>{{ producto.nombre_bien }}</td>
            <td>{{ producto.unidades_disponibles }}</td>
            <td>{{ producto.unidad }}</td>
            <td>{{ producto.costo_unitario }}</td>
            <td>{{ producto.moneda }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>
  </div>
</template>

  
<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      stock: [],
      filtroNombre: "",
    };
  },
  computed: {
    stockFiltrado() {
      const filtro = this.filtroNombre.toLowerCase().trim();
      if (!filtro) return this.stock;

      const empiezaCon = this.stock.filter(
        p => p?.nombre_bien?.toLowerCase().startsWith(filtro)
      );
      const contiene = this.stock.filter(
        p => p?.nombre_bien?.toLowerCase().includes(filtro) &&
             !p?.nombre_bien?.toLowerCase().startsWith(filtro)
      );
      return [...empiezaCon, ...contiene];
    }
  },
  mounted() {
    this.obtenerStock();
  },
  methods: {
    async obtenerStock() {
      try {
        const data = await apiFetch('/get_stock');
        this.stock = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Error al obtener stock:", error.message);
        this.stock = [];
      }
    },
    goTo(routeName) {
      this.$router.push({ name: routeName });
    }
  }
};
</script>

  
  <style scoped>
  /* Estilos para la página */
  .stock-container {
    width: 90%;
    max-width: 1200px;
    margin: 20px auto;
    text-align: center;
  }
  
  /* Estilo para el título */
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    font-weight: bold;
    font-size: 1.5rem;
    text-align: center;
    margin-bottom: 15px;
  }
  
  /* Barra de búsqueda */
  .busqueda {
    width: 100%;
    padding: 8px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 1rem;
  }
  
  /* Estilos de la tabla */
  .stock-tabla {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 12px;
  }
  
  .stock-tabla thead {
    background-color: #b53b3b;
    color: white;
  }
  
  .stock-tabla th, .stock-tabla td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
    font-size: 12px;
  }
  
  .menu-boton-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px;
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
    background-color: #992f2f;
  }
  </style>
  
  
  <style scoped>
  /* Contenedor principal */
  .stock-container {
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
  .stock-tabla {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 12px;
  }
  
  .stock-tabla thead {
    background-color: #b53b3b;
    color: white;
  }
  
  .stock-tabla th, .stock-tabla td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
    font-size: 12px;
  }
  
  .menu-boton-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px;
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
    background-color: #992f2f;
  }
  </style>
  
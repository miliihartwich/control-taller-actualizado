<template>
    <div class="empleados-container">
      <h1 class="titulo">Lista de Empleados</h1>
      
      <!-- Barra de Búsqueda -->
      <input 
        type="text" 
        v-model="filtroNombre" 
        placeholder="Buscar por nombre..." 
        class="busqueda"
      />
      
      <!-- Tabla de Empleados -->
      <table class="empleados-tabla">
        <thead>
          <tr>
            <th>Cédula</th>
            <th>Nombre</th>
            <th>Dirección</th>
            <th>Celular</th>
            <th>Remuneración</th>
            <th>Factor</th>
            <th>Fecha Vencimiento Carnet</th>
            <th>Estado</th>
          <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="empleado in empleadosFiltrados" :key="empleado.cedula">
            <td>{{ empleado.cedula }}</td>
            <td>{{ empleado.nombre }}</td>
            <td>{{ empleado.direccion }}</td>
            <td>{{ empleado.celular }}</td>
            <td>{{ empleado.remuneracion }}</td>
            <td>{{ empleado.factor }}</td>
            <td>{{ formatearFecha(empleado.fecha_vencimiento_carnet) }}</td>
            <td>{{ empleado.estado }}</td>
            <td class="acciones">
              <button @click="toggleEstado(empleado)" class="toggle-btn">
  {{ empleado.estado === 'Activo' ? 'Desactivar' : 'Activar' }}
</button>
          <button @click="editarEmpleado(empleado)" class="edit-btn">✏️ Editar</button>
        </td>
      </tr>
        </tbody>
      </table>

          <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>
  </div>
  <div v-if="empleadoEditando !== null" class="modal">
    <div class="modal-contenido">
      <h2 class="titulo">Editar Empleado</h2>

      <form @submit.prevent="guardarEdicion" class="formulario">
        <label>Nombre</label>
        <input v-model="empleadoEditando.nombre" class="input-field" placeholder="Nombre">

        <label>Celular</label>
        <input v-model="empleadoEditando.celular" class="input-field" placeholder="Celular">

          <label>Dirección</label>
        <input v-model="empleadoEditando.direccion" class="input-field" placeholder="Dirección">

        <label>Remuneración</label>
        <input v-model="empleadoEditando.remuneracion" class="input-field" placeholder="Remuneración">

        <label>Factor</label>
        <input v-model="empleadoEditando.factor" class="input-field" placeholder="Factor">

        <label>Fecha de Vencimiento Carnet</label>
<input v-model="empleadoEditando.fecha_vencimiento_carnet" type="date" class="input-field">


        <div class="botones">
          <button type="submit" class="btn btn-guardar">Guardar</button>
          <button type="button" @click="empleadoEditando = null" class="btn btn-cerrar">Cerrar</button>
        </div>
      </form>
    </div>
    
    <div v-if="mensaje" class="mensaje">{{ mensaje }}</div>
  </div>


  </template>
  
<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      empleados: [],
      filtroNombre: "",
      empleadoEditando: null,
      mensaje: "",
    };
  },

  computed: {
    empleadosFiltrados() {
      const filtro = this.filtroNombre.toLowerCase().trim();
      if (!filtro) return this.empleados;

      return this.empleados
        .map(empleado => {
          const nombre = (empleado.nombre || "").toLowerCase();
          const comienzaCon = nombre.startsWith(filtro);
          const contiene = nombre.includes(filtro);
          return { empleado, prioridad: comienzaCon ? 1 : contiene ? 2 : 3 };
        })
        .filter(x => x.prioridad < 3)
        .sort((a, b) => a.prioridad - b.prioridad)
        .map(x => x.empleado);
    }
  },

  mounted() {
    this.obtenerEmpleados();
  },

  methods: {
    async obtenerEmpleados() {
      try {
        const data = await apiFetch('/get_empleado'); // [{cedula,nombre,direccion,celular,remuneracion,factor,fecha_vencimiento_carnet,estado}]
        this.empleados = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Error al obtener empleados:", error.message);
      }
    },

    // Formatea fecha a dd/mm/yyyy para mostrar (si lo usas en la vista)
    formatearFecha(fecha) {
      if (!fecha) return '';
      const d = new Date(fecha);
      return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
    },

    editarEmpleado(empleado) {
      this.empleadoEditando = {
        ...empleado,
        // para el <input type="date">
        fecha_vencimiento_carnet: empleado.fecha_vencimiento_carnet
          ? new Date(empleado.fecha_vencimiento_carnet).toISOString().split('T')[0]
          : ''
      };
    },

    async guardarEdicion() {
      const password = prompt("Ingrese la contraseña para confirmar:");
      if (password !== "1234") {
        alert("Contraseña incorrecta.");
        return;
      }
      if (!this.empleadoEditando) return;

      const e = this.empleadoEditando;

      // Tu backend espera exactamente estos campos en el body del UPDATE
      const body = {
        nombre: e.nombre,
        direccion: e.direccion,
        celular: e.celular,
        remuneracion: e.remuneracion,
        factor: e.factor,
        fecha_vencimiento_carnet: e.fecha_vencimiento_carnet || null,
        estado: e.estado // "Activo" | "Inactivo"
      };

      try {
        await apiFetch(`/update_empleado/${encodeURIComponent(e.cedula)}`, {
          method: 'PUT',
          body
        });

        alert("Empleado editado correctamente");
        await this.obtenerEmpleados();
        this.empleadoEditando = null;
      } catch (error) {
        alert("Error al editar: " + (error.message || 'desconocido'));
      }
    },

    async toggleEstado(empleado) {
      const confirmacion = prompt("Ingrese la contraseña para confirmar:");
      if (confirmacion !== "1234") {
        alert("Contraseña incorrecta");
        return;
      }

      const nuevoEstado = empleado.estado === "Activo" ? "Inactivo" : "Activo";

      // Para el UPDATE también debemos enviar todos los campos requeridos
      const body = {
        nombre: empleado.nombre,
        direccion: empleado.direccion,
        celular: empleado.celular,
        remuneracion: empleado.remuneracion,
        factor: empleado.factor,
        fecha_vencimiento_carnet: empleado.fecha_vencimiento_carnet || null,
        estado: nuevoEstado
      };

      try {
        await apiFetch(`/update_empleado/${encodeURIComponent(empleado.cedula)}`, {
          method: 'PUT',
          body
        });

        // Actualiza en memoria sin recargar toda la lista
        const i = this.empleados.findIndex(e => e.cedula === empleado.cedula);
        if (i !== -1) {
          this.empleados[i] = { ...this.empleados[i], estado: nuevoEstado };
          this.empleados = [...this.empleados]; // fuerza re-render
        }
      } catch (error) {
        alert("Error al actualizar estado: " + (error.message || 'desconocido'));
      }
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  },
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
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  thead {
    background-color: #b53b3b;
    color: white;
  }
  
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }
  .empleados-tabla {
  font-size: 12px; /* Tamaño de fuente más pequeño */
}

.empleados-tabla th, .empleados-tabla td {
  padding: 8px;
}

.empleados-tabla th {
  text-align: left;
}

/* Clase para hacer más pequeña la fuente de la fecha */
.empleados-tabla td {
  font-size: 12px; /* Ajustar tamaño de la fuente */
}
/* Estilos para el botón de Menú */
.menu-boton-container {
  margin-top: 20px;
  text-align: center;
}

.menu-boton {
  padding: 10px 20px;
  font-size: 14px;
  background-color: #b53b3b;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.menu-boton:hover {
  background-color: #b53b3b;
}
.modal {
  position: fixed; /* Hace que el modal flote sobre la pantalla */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Oscurece el fondo */
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-contenido {
  background: white;
  padding: 20px;
  width: 90%;
  max-width: 400px; /* Controla el ancho */
  border-radius: 8px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.formulario {
  display: flex;
  flex-direction: column;
  gap: 10px; /* Espacio entre campos */
}

.input-field {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.botones {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.btn {
  padding: 10px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.btn-guardar {
  background-color: #28a745;
  color: white;
}

.btn-cerrar {
  background-color: #dc3545;
  color: white;
}

  </style>
  